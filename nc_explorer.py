import os
import xarray as xr
import datetime as dt  # Python standard library datetime  module
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import mpl_toolkits.axisartist as AA
from mpl_toolkits.axes_grid1 import host_subplot

from netCDF4 import Dataset  # http://code.google.com/p/netcdf4-python/
from mpl_toolkits.basemap import Basemap, addcyclic, shiftgrid

from sympy.solvers.diophantine import length


class NcExplorer:
    """
    This class is intended to provide methods to manipulate NetCDF data from Sentinel-3
    """
    def __init__(self, input_nc_data=None):
        self.inputnc = input_nc_data

    @staticmethod
    def extract_band_data(full_nc_path):
        '''
        Assumes the NetCDF file to be a Sentinel-3 band file, like the one below:
        D:\S3\S3A_OL_1_EFR____20190830T140112_20190830T140412_20190831T183009_0179_048_338_3060_LN1_O_NT_002.SEN3\Oa01_radiance.nc
        '''
        nc_file = Dataset(full_nc_path, 'r')
        bname = full_nc_path.split('\\')
        bname = bname[-1].split('.')[0]
        extrated_band = nc_file.variables[bname][:]
        nc_file.close() # it is good practice to close the netcdf after using it (:
        return bname, extrated_band

    @staticmethod
    def ncdump(nc_fid, verb=True):
        # ported from py2.7 to py3 from:
        # http://schubert.atmos.colostate.edu/~cslocum/netcdf_example.html#code
        """
        ncdump outputs dimensions, variables and their attribute information.
        The information is similar to that of NCAR's ncdump utility.
        ncdump requires a valid instance of Dataset.

        Parameters
        ----------
        nc_fid : netCDF4.Dataset
            A netCDF4 dateset object
        verb : Boolean
            whether or not nc_attrs, nc_dims, and nc_vars are printed

        Returns
        -------
        nc_attrs : list
            A Python list of the NetCDF file global attributes
        nc_dims : list
            A Python list of the NetCDF file dimensions
        nc_vars : list
            A Python list of the NetCDF file variables
        """
        def print_ncattr(key):
            """
            Prints the NetCDF file attributes for a given key

            Parameters
            ----------
            key : unicode
                a valid netCDF4.Dataset.variables key
            """
            try:
                print("\t\ttype:", repr(nc_fid.variables[key].dtype))
                for ncattr in nc_fid.variables[key].ncattrs():
                    print('\t\t%s:' % ncattr, repr(nc_fid.variables[key].getncattr(ncattr)))
            except KeyError:
                print("\t\tWARNING: %s does not contain variable attributes" % key)

        # NetCDF global attributes
        nc_attrs = nc_fid.ncattrs()
        if verb:
            print("NetCDF Global Attributes:")
            for nc_attr in nc_attrs:
                print('\t%s:' % nc_attr, repr(nc_fid.getncattr(nc_attr)))
        nc_dims = [dim for dim in nc_fid.dimensions]  # list of nc dimensions
        # Dimension shape information.
        if verb:
            print("NetCDF dimension information:")
            for dim in nc_dims:
                print("\tName:", dim)
                print("\t\tsize:", len(nc_fid.dimensions[dim]))
                print_ncattr(dim)
        # Variable information.
        nc_vars = [var for var in nc_fid.variables]  # list of nc variables
        if verb:
            print("NetCDF variable information:")
            for var in nc_vars:
                if var not in nc_dims:
                    print('\tName:', var)
                    print("\t\tdimensions:", nc_fid.variables[var].dimensions)
                    print("\t\tsize:", nc_fid.variables[var].size)
                    print_ncattr(var)
        return nc_attrs, nc_dims, nc_vars

    @staticmethod
    def _temp():
        print('temp')

    @staticmethod
    def _temp_plot(lon, lat, plot_var, roi_lon=None, roi_lat=None):
        # Miller projection:
        m = Basemap(projection='mill',
                    lat_ts=10,
                    llcrnrlon=lon.min(),
                    urcrnrlon=lon.max(),
                    llcrnrlat=lat.min(),
                    urcrnrlat=lat.max(),
                    resolution='c')

        # BR bbox
        # m = Basemap(projection='mill',
        #             llcrnrlat=-60,
        #             llcrnrlon=-90,
        #             urcrnrlat=20,
        #             urcrnrlon=-25)

        x, y = m(lon, lat)
        # x, y = m(lon, lat, inverse=True)

        m.pcolormesh(x, y, plot_var, shading='flat', cmap=plt.cm.jet)
        m.colorbar(location='right')  # ('top','bottom','left','right')

        # dd_lon, dd_lat = -60.014493, -3.158980  # Manaus
        # if roi_lon is not None and roi_lat is not None:
        xpt, ypt = m(roi_lon, roi_lat)
        m.plot(xpt, ypt, 'rD')  # https://matplotlib.org/api/_as_gen/matplotlib.pyplot.plot.html
        # m.drawcoastlines()
        plt.show()
        # plt.figure()

    @staticmethod
    def get_radiance_in_bands(bands_dictionary, lon=None, lat=None, target_lon=None, target_lat=None):

        # # [pos for pos, x in np.ndenumerate(np.array(lat)) if x == -0.21162]
        # x_lon, y_lon = np.unravel_index((np.abs(lon - target_lon)).argmin(), lon.shape)
        # x_lat, y_lat = np.unravel_index((np.abs(lat - target_lat)).argmin(), lat.shape)
        # print(f'x_lon:{x_lon} y_lon:{y_lon} \n'
        #       f'x_lat:{x_lat} y_lat:{y_lat}')
        #
        # relative_lat = y_lon + int((y_lat - y_lon) / 2)
        # relative_lon = x_lat + int((x_lon - x_lat) / 2)

        # Mauricio's multidimensional wichcraft
        lat = lat[:, :, np.newaxis]
        lon = lon[:, :, np.newaxis]
        grid = np.concatenate([lat, lon], axis=2)
        vector = np.array([target_lat, target_lon]).reshape(1, 1, -1)
        subtraction = vector - grid
        dist = np.linalg.norm(subtraction, axis=2)
        result = np.where(dist == dist.min())
        target_x_y = result[0][0], result[1][0]

        rad_in_bands = []
        for b in bands_dictionary:
            rad = bands_dictionary[b][target_x_y]
            rad_in_bands.append(rad)

        return target_x_y, rad_in_bands


    @staticmethod
    def plot_radiances(radiance_list):
        plt.plot(radiance_list)
        plt.show()

if __name__ == "__main__":
    print("hello s3-frbr:nc_explorer!")
    exp = NcExplorer()
    work_dir = 'D:\processing\\'
    # LV1
    # file_name = work_dir + 'S3A_OL_1_EFR____20190830T140112_20190830T140412_20190831T183009_0179_048_338_3060_LN1_O_NT_002.SEN3'
    # LV2 WFR
    file_name = work_dir + 'S3A_OL_2_WFR____20190830T140112_20190830T140412_20190831T221607_0179_048_338_3060_MAR_O_NT_002.SEN3'
    # retrieve all files in folder
    files = os.listdir(file_name)

    # extract LAT LON from NetCDF
    coords = '\\geo_coordinates.nc'
    nc_coord = Dataset(file_name + coords, 'r')
    # ds = xr.open_dataset(file_name + coords) # needs improving
    lat = nc_coord.variables['latitude'][:]
    lat = lat.data
    lon = nc_coord.variables['longitude'][:]
    lon = lon.data

    # extract only NetCDFs from the file list
    nc_files = [f for f in files if f.endswith('.nc')]
    # extract only the radiometric bands from the NetCDF list
    nc_bands = [b for b in nc_files if b.startswith('Oa')]

    bands = {}
    total = len(nc_bands)
    for x, i in enumerate(nc_bands):
        print(f'extracting band: {nc_bands[x]} -- {x+1} of {total}')
        band_name, df = exp.extract_band_data(file_name + '\\' + nc_bands[x])
        # df = df.data
        bands[band_name] = df

    # Where is Manaus in the lat lon netcdf matrix?
    query_lon, query_lat = -60.014493, -3.158980

    exp._temp_plot(lon, lat, df, query_lon, query_lat)

    mat_x_y, band_radiances = exp.get_radiance_in_bands(bands, lon, lat, query_lon, query_lat)

    s3_bands = {'Oa1':  400,
                'Oa2':  412.5,
                'Oa3':  442.5,
                'Oa4':  490,
                'Oa5':  510,
                'Oa6':  560,
                'Oa7':  620,
                'Oa8':  665,
                'Oa9':  673.75,
                'Oa10': 681.25,
                'Oa11': 708.75,
                'Oa12': 753.75,
                'Oa13': 761.25,
                'Oa14': 764.375,
                'Oa15': 767.5,
                'Oa16': 778.75,
                'Oa17': 865,
                'Oa18': 885,
                'Oa19': 900,
                'Oa20': 940,
                'Oa21': 1020}

    wfr_s3_bands = {'Oa1': 400,
                    'Oa2': 412.5,
                    'Oa3': 442.5,
                    'Oa4': 490,
                    'Oa5': 510,
                    'Oa6': 560,
                    'Oa7': 620,
                    'Oa8': 665,
                    'Oa9': 673.75,
                    'Oa10': 681.25,
                    'Oa11': 708.75,
                    'Oa12': 753.75,
                    'Oa16': 778.75,
                    'Oa17': 865,
                    'Oa18': 885,
                    'Oa21': 1020}

    ### L1B
    # fig, ax1 = plt.subplots()
    # ax1.set_xlabel('Wavelenght (nm)')
    # ax1.set_ylabel('Radiance')
    # ax1.plot(list(s3_bands.values()), band_radiances)
    # ax1.set_xticks(list(s3_bands.values()))
    # ax1.set_xticklabels(list(s3_bands.values()))
    # ax1.tick_params(labelrotation=90, labelsize='small')
    #
    # ax2 = ax1.twiny()
    # ax2.plot(np.linspace(min(list(s3_bands.values())),
    #                      max(list(s3_bands.values())),
    #                      num=len(s3_bands)), band_radiances, alpha=0.0)
    # ax2.set_xticks(list(s3_bands.values()))
    # ax2.set_xticklabels(list(s3_bands.keys()))
    #
    # ax2.tick_params(labelrotation=90, labelsize='xx-small')
    # ax2.grid()
    # # ax2.set_visible(False)
    # plt.show()

    ### L2 WFR
    fig, ax1 = plt.subplots()
    ax1.set_xlabel('Wavelenght (nm)')
    ax1.set_ylabel('Reflectance')
    ax1.plot(list(wfr_s3_bands.values()), band_radiances)
    ax1.set_xticks(list(wfr_s3_bands.values()))
    ax1.set_xticklabels(list(wfr_s3_bands.values()))
    ax1.tick_params(labelrotation=90, labelsize='small')

    ax2 = ax1.twiny()
    ax2.plot(np.linspace(min(list(wfr_s3_bands.values())),
                         max(list(wfr_s3_bands.values())),
                         num=len(wfr_s3_bands)), band_radiances, alpha=0.0)
    ax2.set_xticks(list(wfr_s3_bands.values()))
    ax2.set_xticklabels(list(wfr_s3_bands.keys()))

    ax2.tick_params(labelrotation=90, labelsize='xx-small')
    ax2.grid()
    # ax2.set_visible(False)
    plt.show()