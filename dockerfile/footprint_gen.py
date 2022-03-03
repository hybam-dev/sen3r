import os
import sys
sys.path.append('../')
from sen3r.commons import Footprinter
from pathlib import Path

fp = Footprinter()

if __name__ == "__main__":
    print(f'Parameters: {sys.argv}')
    target_folder = sys.argv[1]
    result = list(Path(target_folder).rglob("xfdumanifest.xml"))
    for r in result:
        print(r)
        destination = os.path.join(r.parent, 'footprint')
        xmldict = fp.manifest2shp(r, destination)
