import sys
import time
import sen3r
import argparse

from sen3r.sen3r import Core
from sen3r.commons import Utils


def main():
    """
    Entry point for the SEN3R package. Call sen3r -h or --help to see further options.
    """
    # ,--------------,
    # | Start timers |--------------------------------------------------------------------------------------------------
    # '--------------'
    Utils.tic()
    t1 = time.perf_counter()

    parser = argparse.ArgumentParser(
        description='SEN3R (Sentinel-3 Reflectance Retrieval over Rivers) '
                    'enables extraction of reflectance time series from Sentinel-3 L2 WFR images over water bodies.')
    parser.add_argument("-i", "--input", help="The products input folder. Required.", type=str)
    parser.add_argument("-o", "--out", help="Output directory. Required.", type=str)
    parser.add_argument("-r", "--roi", help="Region of interest (SHP, KML or GeoJSON). Required", type=str)
    parser.add_argument("-p", "--product", help='Currently only WFR is available.', default='WFR', type=str)
    parser.add_argument("-c", "--cams", help="Path to search for auxiliary CAMS file. Optional.", type=str)
    parser.add_argument("-min", "--irmin", help="Default bottom dropping threshold for IR. Optional.", default="99",
                        type=str)
    parser.add_argument("-max", "--irmax", help="Default upper dropping threshold for IR. Optional.", default="0.2",
                        type=str)
    parser.add_argument("-k", "--cluster", help="Which method to use for clustering. Optional.", default='M4', type=str)
    # parser.add_argument('-ng', '--no-graphics', help='Do not generate graphical reports.', action='store_true')
    # parser.add_argument('-np', '--no-pdf', help='Do not generate PDF report.', action='store_true')
    parser.add_argument("-s", "--single",
                        help="Single mode: run SEN3R over only one image instead of a whole directory."
                             " Optional.", action='store_true')
    parser.add_argument('-v', '--version', help='Displays current package version.', action='store_true')

    # ,--------------------------------------,
    # | STORE INPUT VARS INSIDE SEN3R OBJECT |--------------------------------------------------------------------------
    # '--------------------------------------'
    args = parser.parse_args().__dict__  # Converts the input arguments from Namespace() to dict

    # Cast user typed strings to float
    try:
        args['irmin'] = float(args['irmin'])  # default = 99.0 (99.0 will be later converted to False)
        args['irmax'] = float(args['irmax'])  # default = 0.2
    except ValueError as e:
        print(f'Invalid Infrared threshold value: {e}')
        print(f'Try again with a valid number between range 0.0 and 1.0')
        print(f'(If you want to force-disable the limits use 99 instead.)')
        sys.exit(1)

    # Test if user wants to disable the upper and/or bottom values
    if args['irmax'] == 99.0:
        args['irmax'] = False
    if args['irmin'] == 99.0:
        args['irmin'] = False
    '''
    Here we are assuming that water leaving reflectance should not be above 0.2 (20%) but this is not a rigid rule.
    Ideal threshold values needs to be tested by the user for each specific case. This may be improved in future.
    irmax = 0.001 # Negro
    irmax = 0.08 # Fonte Boa
    irmin = 0.001 # Manacapuru
    irmax = 0.2 # Manacapuru
    '''  # TODO: fix threshold values to set them automatically in the future.

    if args['version']:
        print(f'SEN3R version: {sen3r.__version__}')

    elif (args['input'] is None) or (args['out'] is None) or (args['roi'] is None):
        print('Please specify required INPUT/OUTPUT folders and REGION of interest (-i, -o, -r)')

    else:
        # ,------------,
        # | LOG SETUP  |------------------------------------------------------------------------------------------------
        # '------------'
        # args['logfile'] = os.path.join(args['out'], 'sen3r_'+datetime.now().strftime('%Y%m%dT%H%M%S')+'.log')
        # args['logger'] = Utils.create_log_handler(args['logfile'])
        s3r = Core(args)  # Declare a SEN3R Core Object
        print(f'Starting SEN3R - LOG operations saved at:{s3r.arguments["logfile"]}')
        s3r.log.info(f'Starting SEN3R {s3r.VERSION} ({sen3r.__version__})')
        s3r.log.info('------')
        s3r.log.info('Input arguments:')
        for key in args:
            s3r.log.info(f'{key}: {args[key]}')
        s3r.log.info('------')

        if args['single']:  # Single mode
            band_data, img_data, doneList = s3r.build_single_csv()

        else:  # Default mode: several images
            doneList = s3r.build_raw_csvs()
            print('cams_args:', s3r.arguments['cams'])
            if s3r.arguments["cams"]:
                s3r.process_csv_list(raw_csv_list=doneList, irmax=args['irmax'], irmin=args['irmin'], use_cams=True,
                                     k_method=s3r.arguments['cluster'])
            else:
                s3r.process_csv_list(raw_csv_list=doneList, irmax=args['irmax'], irmin=args['irmin'],
                                     k_method=s3r.arguments['cluster'])

    # ,------------------------------,
    # | End timers and report to log |----------------------------------------------------------------------------------
    # '------------------------------'
    t_hour, t_min, t_sec = Utils.tac()
    t2 = time.perf_counter()
    outputstr = f'Finished in {round(t2 - t1, 2)} second(s).'
    final_message = f'Elapsed execution time: {t_hour}h : {t_min}m : {t_sec}s'
    print(outputstr)
    print(final_message)

    pass


if __name__ == '__main__':
    # ,-----,
    # | RUN |-----------------------------------------------------------------------------------------------------------
    # '-----'
    main()

