import os
import sys
import main  # import SEN3R entrypoint


if __name__ == "__main__":

    input = sys.argv[1]
    output = sys.argv[2]
    roi = sys.argv[3]

    # normpath = remove trailing slashes
    # basename = last path element
    # split = drop the .geojson and grab only the file name
    outpath = os.path.basename(os.path.normpath(roi)).split('.')[0]
    output = os.path.join(output, outpath)

    print(f'Org. params: {sys.argv}')
    cmdlist = [sys.argv[0], '-i', input, '-o', output, '-r', roi]
    # artificially modify the input params
    sys.argv = cmdlist
    print(f'Mod. params: {sys.argv}')

    # call sen3r using new params
    main.main()
