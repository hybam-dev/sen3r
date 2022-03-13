import os
import sys
import json
import subprocess

from pathlib import Path
from osgeo import ogr, osr


class Footprinter:

    @staticmethod
    def _xml2dict(xfdumanifest):
        '''
        Internal function that reads the .SEN3/xfdumanifest.xml and generates a dictionary with the relevant data.
        '''
        result = {}
        with open(xfdumanifest) as xmlf:
            # grab the relevant contents and add them to a dict
            for line in xmlf:
                if "<gml:posList>" in line:
                    result['gml_data'] = f'<gml:Polygon xmlns:gml="http://www.opengis.net/gml" ' \
                                    f'srsName="http://www.opengis.net/def/crs/EPSG/0/4326">' \
                                    f'<gml:exterior><gml:LinearRing>{line}</gml:LinearRing>' \
                                    f'</gml:exterior></gml:Polygon>'
                # get only the values between the tags
                if '<sentinel3:rows>' in line:
                    result['rows'] = int(line.split('</')[0].split('>')[1])
                if '<sentinel3:columns>' in line:
                    result['cols'] = int(line.split('</')[0].split('>')[1])
        return result

    @staticmethod
    def _gml2shp(gml_in, shp_out):
        '''
        given a .GML file (gml_in), convert it to a .SHP (shp_out).
        '''
        # https://pcjericks.github.io/py-gdalogr-cookbook/vector_layers.html#create-a-new-layer-from-the-extent-of-an-existing-layer
        # Get the Layer's Geometry
        inGMLfile = gml_in
        inDriver = ogr.GetDriverByName("GML")
        inDataSource = inDriver.Open(inGMLfile, 0)
        inLayer = inDataSource.GetLayer()
        feature = inLayer.GetNextFeature()
        geometry = feature.GetGeometryRef()

        # Get the list of coordinates from the footprint
        json_footprint = json.loads(geometry.ExportToJson())
        footprint = json_footprint['coordinates'][0]

        # Create a Polygon from the extent tuple
        ring = ogr.Geometry(ogr.wkbLinearRing)

        for point in footprint:
            ring.AddPoint(point[0], point[1])

        poly = ogr.Geometry(ogr.wkbPolygon)
        poly.AddGeometry(ring)

        # Save extent to a new Shapefile
        outShapefile = shp_out
        outDriver = ogr.GetDriverByName("ESRI Shapefile")

        # Remove output shapefile if it already exists
        if os.path.exists(outShapefile):
            outDriver.DeleteDataSource(outShapefile)

        # create the spatial reference, WGS84
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)

        # Create the output shapefile
        outDataSource = outDriver.CreateDataSource(outShapefile)
        outLayer = outDataSource.CreateLayer("s3_footprint", srs, geom_type=ogr.wkbPolygon)

        # Add an ID field
        idField = ogr.FieldDefn("id", ogr.OFTInteger)
        outLayer.CreateField(idField)

        # Create the feature and set values
        featureDefn = outLayer.GetLayerDefn()
        feature = ogr.Feature(featureDefn)
        feature.SetGeometry(poly)
        feature.SetField("id", 1)
        outLayer.CreateFeature(feature)
        feature = None

        # Save and close DataSource
        inDataSource = None
        outDataSource = None
        pass

    def manifest2shp(self, xfdumanifest, filename):
        '''
        Given a .SEN3/xfdumanifest.xml and a filename, generates a .shp and a .gml
        '''
        # get the dict
        xmldict = self._xml2dict(xfdumanifest)
        # add path to "to-be-generated" gml and shp files
        xmldict['gml_path'] = filename + '.gml'
        xmldict['shp_path'] = filename + '.shp'
        # write the gml_data from the dict to an actual .gml file
        with open(xmldict['gml_path'], 'w') as gmlfile:
            gmlfile.write(xmldict['gml_data'])
        # DEPRECATED:
        # call the ogr2ogr.py script to generate a .shp from a .gml
        # ogr2ogr.main(["", "-f", "ESRI Shapefile", xmldict['shp_path'], xmldict['gml_path']])

        self._gml2shp(xmldict['gml_path'], xmldict['shp_path'])
        return xmldict

    @staticmethod
    def _shp_extent(shp):
        '''
        Reads a ESRI Shapefile and return its extent as a str separated by spaces.
        e.x. output: '-71.6239 -58.4709 -9.36789 0.303954'
        '''
        ds = ogr.Open(shp)
        layer = ds.GetLayer()
        feature = layer.GetNextFeature()
        geometry = feature.GetGeometryRef()
        extent = geometry.GetEnvelope()  # ex: (-71.6239, -58.4709, -9.36789, 0.303954)
        # cast the 4-elements tuple into a list of strings
        extent_str = [str(i) for i in extent]
        return ' '.join(extent_str)

    def manifest2tiff(self, xfdumanifest):
        '''
        Reads .SEN3/xfdumanifest.xml and generates a .tiff raster.
        '''
        # get the complete directory path but not the file base name
        img_path = xfdumanifest.split('/xfdu')[0]
        # get only the date of the img from the complete path, ex: '20190904T133117'
        figdate = os.path.basename(img_path).split('____')[1].split('_')[0]
        # add an img.SEN3/footprint folder
        footprint_dir = os.path.join(img_path, 'footprint')
        Path(footprint_dir).mkdir(parents=True, exist_ok=True)
        # ex: img.SEN3/footprint/20190904T133117_footprint.tiff
        path_file_tiff = os.path.join(footprint_dir, figdate+'_footprint.tiff')
        # only '20190904T133117_footprint' nothing else.
        lyr = os.path.basename(path_file_tiff).split('.')[0]
        # img.SEN3/footprint/20190904T133117_footprint (without file extension)
        fname = path_file_tiff.split('.tif')[0]
        # get the dict + generate .shp and .gml files
        xmldict = self.manifest2shp(xfdumanifest, fname)
        cols = xmldict['cols']
        rows = xmldict['rows']
        shp = xmldict['shp_path']
        extent = self._shp_extent(shp)
        # generate the complete cmd string
        cmd = f'gdal_rasterize -l {lyr} -burn 1.0 -ts {cols}.0 {rows}.0 -a_nodata 0.0 -te {extent} -ot Float32 {shp} {path_file_tiff}'
        # call the cmd
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        proc.wait()
        print(f'{figdate} done.')
        return True

    @staticmethod
    def touch_test(footprint_shp, roi_shp):
        """
        Given two input shapefiles (one Sentinel-3 image footprint and
        the user region of interest), test if the touch each other.
        """
        inDriver = ogr.GetDriverByName("ESRI Shapefile")

        foot_ds = inDriver.Open(footprint_shp, 0)
        layer_foot = foot_ds.GetLayer()
        feature_foot = layer_foot.GetNextFeature()
        geometry_foot = feature_foot.GetGeometryRef()

        data = ogr.Open(roi_shp)

        # Adapted from https://gist.github.com/CMCDragonkai/e7b15bb6836a7687658ec2bb3abd2927
        for layer in data:
            # this is the one where featureindex may not start at 0
            layer.ResetReading()
            for feature in layer:
                geometry_roi = feature.geometry()
                intersection = geometry_roi.Intersection(geometry_foot)
                if not intersection.IsEmpty():
                    return True

        # This will only run if no geometry from the ROI touched the S3 footprint.
        return False


if __name__ == "__main__":
    fp = Footprinter()
    print(f'Parameters: {sys.argv}')
    target_folder = sys.argv[1]
    result = list(Path(target_folder).rglob("xfdumanifest.xml"))
    for r in result:
        print(r)
        destination = os.path.join(r.parent, 'footprint')
        xmldict = fp.manifest2shp(r, destination)
