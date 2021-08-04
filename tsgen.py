import os
import sys
import logging
import time
import utils
import pandas as pd
import numpy as np
import outsourcing as out
import matplotlib.pyplot as plt
import concurrent.futures

from PIL import Image
from datetime import datetime
from scipy.signal import argrelextrema
from scipy import stats
from sklearn.cluster import DBSCAN

from matplotlib import gridspec

import matplotlib
import matplotlib.cm as cm
from nc_explorer import NcExplorer


class TsGenerator:

    def __init__(self):
        # Setting up information logs
        logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO)

    exp = NcExplorer(external_use=True)
    imgdpi = 100
    rcparam = [14, 5.2]
    glint = 12.0

    norm_s3_bands = ['Oa01_reflectance:float',
                     'Oa02_reflectance:float',
                     'Oa03_reflectance:float',
                     'Oa04_reflectance:float',
                     'Oa05_reflectance:float',
                     'Oa06_reflectance:float',
                     'Oa07_reflectance:float',
                     'Oa08_reflectance:float',
                     'Oa09_reflectance:float',
                     'Oa10_reflectance:float',
                     'Oa11_reflectance:float',
                     'Oa12_reflectance:float',
                     'Oa16_reflectance:float',
                     'Oa17_reflectance:float',
                     'Oa18_reflectance:float',
                     'Oa21_reflectance:float']

    bname_dict = {'B1-400': 'Oa01: 400 nm',
                  'B2-412.5': 'Oa02: 412.5 nm',
                  'B3-442.5': 'Oa03: 442.5 nm',
                  'B4-490': 'Oa04: 490 nm',
                  'B5-510': 'Oa05: 510 nm',
                  'B6-560': 'Oa06: 560 nm',
                  'B7-620': 'Oa07: 620 nm',
                  'B8-665': 'Oa08: 665 nm',
                  'B9-673.75': 'Oa09: 673.75 nm',
                  'B10-681.25': 'Oa10: 681.25 nm',
                  'B11-708.75': 'Oa11: 708.75 nm',
                  'B12-753.75': 'Oa12: 753.75 nm',
                  'B16-778.75': 'Oa16: 778.75 nm',
                  'B17-865': 'Oa17: 865 nm',
                  'B18-885': 'Oa18: 885 nm',
                  'B21-1020': 'Oa21: 1020 nm'}

    int_flags = [1, 2, 4, 8, 8388608, 16777216, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536,
                 131072, 262144, 524288, 2097152, 33554432, 67108864, 134217728, 268435456, 4294967296, 8589934592,
                 17179869184, 34359738368, 68719476736, 137438953472, 274877906944, 549755813888, 1099511627776,
                 2199023255552, 4398046511104, 8796093022208, 17592186044416, 35184372088832, 70368744177664,
                 140737488355328, 281474976710656, 562949953421312, 1125899906842624, 2251799813685248,
                 4503599627370496, 9007199254740992, 18014398509481984, 36028797018963968]

    str_flags = ['INVALID', 'WATER', 'LAND', 'CLOUD', 'CLOUD_AMBIGUOUS', 'CLOUD_MARGIN', 'SNOW_ICE', 'INLAND_WATER',
                 'TIDAL', 'COSMETIC', 'SUSPECT', 'HISOLZEN', 'SATURATED', 'MEGLINT', 'HIGHGLINT', 'WHITECAPS', 'ADJAC',
                 'WV_FAIL', 'PAR_FAIL', 'AC_FAIL', 'OC4ME_FAIL', 'OCNN_FAIL', 'KDM_FAIL', 'BPAC_ON', 'WHITE_SCATT',
                 'LOWRW', 'HIGHRW', 'ANNOT_ANGSTROM', 'ANNOT_AERO_B', 'ANNOT_ABSO_D', 'ANNOT_ACLIM', 'ANNOT_ABSOA',
                 'ANNOT_MIXR1', 'ANNOT_DROUT', 'ANNOT_TAU06', 'RWNEG_O1', 'RWNEG_O2', 'RWNEG_O3', 'RWNEG_O4',
                 'RWNEG_O5', 'RWNEG_O6', 'RWNEG_O7', 'RWNEG_O8', 'RWNEG_O9', 'RWNEG_O10', 'RWNEG_O11', 'RWNEG_O12',
                 'RWNEG_O16', 'RWNEG_O17', 'RWNEG_O18', 'RWNEG_O21']

    # bin_to_flag = {}
    # for n, i in enumerate(int_flags):
    #     bin = "{0:b}".format(i)
    #     print(f'{n} | {str_flags[n]} - {i} - {bin} - {(len(bin))}')
    #     bin_to_flag[len(bin) - 1] = str_flags[n]
    #
    # # https://sentinel.esa.int/web/sentinel/technical-guides/sentinel-3-olci/level-2/quality-and-science-flags-op

    bin2flag = {0: 'INVALID',
                1: 'WATER',
                2: 'LAND',
                3: 'CLOUD',
                23: 'CLOUD_AMBIGUOUS',
                24: 'CLOUD_MARGIN',
                4: 'SNOW_ICE',
                5: 'INLAND_WATER',
                6: 'TIDAL',
                7: 'COSMETIC',
                8: 'SUSPECT',
                9: 'HISOLZEN',
                10: 'SATURATED',
                11: 'MEGLINT',
                12: 'HIGHGLINT',
                13: 'WHITECAPS',
                14: 'ADJAC',
                15: 'WV_FAIL',
                16: 'PAR_FAIL',
                17: 'AC_FAIL',
                18: 'OC4ME_FAIL',
                19: 'OCNN_FAIL',
                21: 'KDM_FAIL',
                25: 'BPAC_ON',
                26: 'WHITE_SCATT',
                27: 'LOWRW',
                28: 'HIGHRW',
                32: 'ANNOT_ANGSTROM',
                33: 'ANNOT_AERO_B',
                34: 'ANNOT_ABSO_D',
                35: 'ANNOT_ACLIM',
                36: 'ANNOT_ABSOA',
                37: 'ANNOT_MIXR1',
                38: 'ANNOT_DROUT',
                39: 'ANNOT_TAU06',
                40: 'RWNEG_O1',
                41: 'RWNEG_O2',
                42: 'RWNEG_O3',
                43: 'RWNEG_O4',
                44: 'RWNEG_O5',
                45: 'RWNEG_O6',
                46: 'RWNEG_O7',
                47: 'RWNEG_O8',
                48: 'RWNEG_O9',
                49: 'RWNEG_O10',
                50: 'RWNEG_O11',
                51: 'RWNEG_O12',
                52: 'RWNEG_O16',
                53: 'RWNEG_O17',
                54: 'RWNEG_O18',
                55: 'RWNEG_O21'}

    def get_flags(self, val):
        """
        # TODO: Write docstrings.
        """
        if isinstance(val, float):
            binexval = "{0:b}".format(int(val))
        elif isinstance(val, int):
            binexval = "{0:b}".format(val)
        else:
            print('Input must be of type int or float.')
            return False
        if binexval != '11111111111111111111111111111110':
            flags = [self.bin2flag[n] for n, e in enumerate(binexval[::-1]) if e == '1']
        else:
            return False

        return flags

    # -----------------------------------------------------------------------------------
    # DEFINITION OF FLAGS TO KEEP AND REMOVE
    remove = ['INVALID',
              'CLOUD',
              'CLOUD_AMBIGUOUS',
              'CLOUD_MARGIN',
              'SNOW_ICE',
              'SUSPECT',
              'SATURATED',
              'AC_FAIL',
              'MEGLINT',  # experimental
              'HIGHGLINT',  # experimental
              'LOWRW']  # experimental

    # 'ADJAC',  # Meaningless – reserved for future use.

    # MUST HAVE
    keep = ['INLAND_WATER']

    def get_quality(self, checklist):
        """
        # TODO: Write docstrings.
        """
        if checklist:
            if all(i in checklist for i in self.keep):
                if any(i in checklist for i in self.remove):
                    return 0
                else:
                    return 1
            else:
                return 0
        else:
            return 0

    @staticmethod
    def calc_nd_index(df, band1, band2, column_name='nd_index'):
        idx = (df[band1] - df[band2]) / (df[band1] + df[band2])
        df[column_name] = idx
        pass

    @staticmethod
    def _gettxt():
        print('v-fin')
        pass

    @staticmethod
    def _normalize(df, bands, norm_band):
        df = df.copy()
        df[bands] = df[bands].to_numpy() - df[norm_band].to_numpy()[..., None]
        return df

    @staticmethod
    # concentração = 759,12 * (NIR /RED)^1,92
    def _spm_modis(nir, red):
        return 759.12 * ((nir / red) ** 1.92)

    @staticmethod
    def _power(x, a, b, c):
        return a * (x) ** (b) + c

    def get_spm(self, band665, band865, cutoff_value=0.027, cutoff_delta=0.007, low_params=None, high_params=None):

        b665 = band665 / np.pi
        b865 = band865 / np.pi

        if cutoff_delta == 0:
            transition_coef = np.where(b665 <= cutoff_value, 0, 1)

        else:
            transition_range = (cutoff_value - cutoff_delta, cutoff_value + cutoff_delta)
            transition_coef = (b665 - transition_range[0]) / (transition_range[1] - transition_range[0])

            transition_coef = np.clip(transition_coef, 0, 1)

        # if params are not passed, use default params obtained from the Amazon dataset
        low_params = [2.79101975e+05, 2.34858344e+00, 4.20023206e+00] if low_params is None else low_params
        high_params = [848.97770516, 1.79293191, 8.2788616] if high_params is None else high_params

        # low = Fit.power(b665, *low_params).fillna(0)
        # high = Fit.power(b865/b665, *high_params).fillna(0)

        low = self._power(b665, *low_params).fillna(0)
        # high = power(b865/b665, *high_params).fillna(0)
        high = self._spm_modis(b865, b665)

        spm = (1 - transition_coef) * low + transition_coef * high
        return spm

    @staticmethod
    def get_glint(df):
        """
        Calculates glint angle based on paper:
        An Enhanced Contextual Fire Detection Algorithm for MODIS
        https://www.sciencedirect.com/science/article/pii/S0034425703001846
        https://doi.org/10.1016/S0034-4257(03)00184-6
        """
        df['GLINT'] = np.degrees(np.arccos(np.cos(np.deg2rad(df['OZA:float'])) *
                                           np.cos(np.deg2rad(df['SZA:float'])) -
                                           np.sin(np.deg2rad(df['OZA:float'])) *
                                           np.sin(np.deg2rad(df['SZA:float'])) *
                                           np.cos(np.deg2rad(abs(df['SAA:float'] - df['OAA:float'])))))

        # excel version
        # =GRAUS(ACOS(COS(RADIANOS(OZA))*COS(RADIANOS(SZA))-SEN(RADIANOS(OZA))*SEN(RADIANOS(SZA))*COS(RADIANOS(ABS(SAA-OAA)))))
        pass

    def add_flags_to_df(self, df):
        """
        # TODO: Write docstrings.
        """
        df['FLAGS'] = df['WQSF_lsb:double'].apply(self.get_flags)
        df['QUALITY'] = df['FLAGS'].apply(self.get_quality)
        pass

    def update_df(self, df, ir_min_threshold=False, ir_max_threshold=False,
                  max_aot=False, cams_val=False, normalize=False):

        # Delete indexes for which Oa01_reflectance is saturated:
        indexNames = df[df['Oa01_reflectance:float'] == 1.0000184].index
        df.drop(indexNames, inplace=True)

        # This should represent 100% of the pixels inside the SHP area before applying the filters.
        df['ABSVLDPX'] = len(df)

        #####################################
        # Normalization based on B21-1020nm #
        #####################################
        if normalize:
            df = self._normalize(df, self.norm_s3_bands, norm_band='Oa21_reflectance:float')

        # In case the reflectance of water pixels should not be below 0.001
        # in the NIR Band (Oa17:865nm), we will drop using the threshold:
        if ir_min_threshold:
            indexNames = df[df['Oa17_reflectance:float'] < ir_min_threshold].index
            # Delete these row indexes from dataFrame
            df.drop(indexNames, inplace=True)

        # Assuming that the reflectance of water pixels should not be above 0.2
        # in the NIR Band (Oa17:865nm), we will drop using the threshold:
        if ir_max_threshold:
            indexNames = df[df['Oa17_reflectance:float'] > ir_max_threshold].index
            # Delete these row indexes from dataFrame
            df.drop(indexNames, inplace=True)

        ##############
        # CAMS PROXY #
        ##############
        if cams_val:
            # CAMS observations tend to be always bellow that of S3 AOT 865
            # handle observations that does not follow this rule as outliers
            df = df[df['T865:float'] > cams_val]

        # Add new FLAGS and QUALITY cols
        self.add_flags_to_df(df)

        # Delete indexes for which QUALITY = 0
        indexNames = df[df['QUALITY'] == 0].index
        df.drop(indexNames, inplace=True)

        # Delete indexes for which FLAGS = False
        indexNames = df[df['FLAGS'] == False].index  # TODO: verify why the use of 'is' instead of '==' breaks the code.
        df.drop(indexNames, inplace=True)

        if max_aot:  # 0.6
            # Delete the indexes for which T865 (Aerosol optical depth) is thicker than 0.6
            indexNames = df[df['T865:float'] >= max_aot].index
            df.drop(indexNames, inplace=True)

        ################################
        # FILTER NEGATIVE REFLECTANCES #
        ################################
        # df.loc[df['Oa01_reflectance:float'] < 0, 'Oa01_reflectance:float'] = np.nan
        # df.loc[df['Oa02_reflectance:float'] < 0, 'Oa02_reflectance:float'] = np.nan
        # df.loc[df['Oa03_reflectance:float'] < 0, 'Oa03_reflectance:float'] = np.nan
        # df.loc[df['Oa04_reflectance:float'] < 0, 'Oa04_reflectance:float'] = np.nan
        # df.loc[df['Oa05_reflectance:float'] < 0, 'Oa05_reflectance:float'] = np.nan
        df.loc[df['Oa06_reflectance:float'] <= 0, 'Oa06_reflectance:float'] = np.nan
        df.loc[df['Oa07_reflectance:float'] <= 0, 'Oa07_reflectance:float'] = np.nan
        df.loc[df['Oa08_reflectance:float'] <= 0, 'Oa08_reflectance:float'] = np.nan
        df.loc[df['Oa09_reflectance:float'] <= 0, 'Oa09_reflectance:float'] = np.nan
        df.loc[df['Oa10_reflectance:float'] <= 0, 'Oa10_reflectance:float'] = np.nan
        # df.loc[df['Oa11_reflectance:float'] < 0, 'Oa11_reflectance:float'] = np.nan
        # df.loc[df['Oa12_reflectance:float'] < 0, 'Oa12_reflectance:float'] = np.nan
        # df.loc[df['Oa16_reflectance:float'] < 0, 'Oa16_reflectance:float'] = np.nan
        df.loc[df['Oa17_reflectance:float'] <= 0, 'Oa17_reflectance:float'] = np.nan
        # df.loc[df['Oa18_reflectance:float'] < 0, 'Oa18_reflectance:float'] = np.nan
        # df.loc[df['Oa21_reflectance:float'] < 0, 'Oa21_reflectance:float'] = np.nan

        ###############################
        # DROP EVERY NAN REFLECTANCES #
        ###############################
        df.dropna(inplace=True)

        #####################
        # CURVE SHAPE RULES #
        #####################
        # Oa16 must always be above Oa12, for Oa12 is an atmospheric attenuation window
        # df = df[df['Oa16_reflectance:float'] > df['Oa12_reflectance:float']]

        # Oa11 must always be higher than Oa12
        df = df[df['Oa11_reflectance:float'] > df['Oa12_reflectance:float']]

        ##########################
        # Calculate GLINT for DF #
        ##########################
        self.get_glint(df)
        row_idx = df[df['GLINT'] <= self.glint].index
        df.drop(row_idx, inplace=True)

        ##########################
        # Add MNDWI / NDWI Index #
        ##########################
        self.calc_nd_index(df, 'Oa06_reflectance:float', 'Oa21_reflectance:float', column_name='MNDWI')  # Green / SWIR
        self.calc_nd_index(df, 'Oa06_reflectance:float', 'Oa17_reflectance:float', column_name='NDWI')  # Green / IR
        valid_mndwi = (df['MNDWI'] > -0.99) & (df['MNDWI'] < 0.99)
        valid_ndwi = (df['NDWI'] > -0.99) & (df['NDWI'] < 0.99)
        df = df[valid_mndwi & valid_ndwi]

        ############################
        # CLASS TEST FOR T865/A865 #
        ############################

        # lowelim = 0.4
        # upperlim = 0.6
        #
        # indexNames = df[df['T865:float'] < lowelim].index
        # df.drop(indexNames, inplace=True)
        # indexNames = df[df['T865:float'] > upperlim].index
        # df.drop(indexNames, inplace=True)

        ################################################
        # DROP OUTSIDE 25% OF THE MEDIAN FOR T865/A865 #
        ################################################

        # Get values 25% below or above the median for T865
                # T865_median = np.nanmedian(df['T865:float'], axis=0)
        # T865_upper_lim = T865_median + (0.25 * T865_median)
        # T865_lower_lim = T865_median - (0.25 * T865_median)

        # # Get values 25% below or above the median for A865
        # A865_median = np.nanmedian(df['A865:float'], axis=0)
        # A865_upper_lim = A865_median + (0.25 * A865_median)
        # A865_lower_lim = A865_median - (0.25 * A865_median)

        # Drop data outside bounds for T865:
        # indexNames = df[df['T865:float'] > T865_upper_lim].index
        # df.drop(indexNames, inplace=True)
        # indexNames = df[df['T865:float'] < T865_lower_lim].index
        # df.drop(indexNames, inplace=True)

        # # Drop data outside bounds for A865:
        # indexNames = df[df['A865:float'] > A865_upper_lim].index
        # df.drop(indexNames, inplace=True)
        # indexNames = df[df['A865:float'] < A865_lower_lim].index
        # df.drop(indexNames, inplace=True)

        #####################################
        # Fix the indexing of the dataframe #
        #####################################
        df.reset_index(drop=True, inplace=True)

        ###########
        # Get SPM #
        ###########
        df['SPM'] = self.get_spm(band865=df['Oa17_reflectance:float'], band665=df['Oa08_reflectance:float'])

        return df
    # manacapuru 0.2
    # negro 0.001
    def update_csvs(self, csv_path, glint=12.0, savepath=False,
                    ir_min_threshold=False,
                    ir_max_threshold=0.2,
                    max_aot=0.6,
                    kde=False,
                    GPT=False,
                    cams_val=False,
                    normalize=False):
        """
        Given an CSV of pixels extracted using GPT(SNAP), filter the dataset and add some new columns.

        Input:
            csv_path (string): complete path to the CSV to be updated.
            ex: "D:\\sentinel3\\inputs\\S3B_OL_2_WFR____20191002T140633_subset_masked.txt"

            savepath (string): system folder where to save the modified csv.
            ex: "D:\\sentinel3\\outputs"

            When savepath is not given, the new DF will no be saved, but it will still be returned.

        Output:
            df (pandas dataframe): in-memory version of the input data that was read and modified from csv_path.
        """
        # read text file and convert to pandas dataframe
        if GPT:
            raw_df = pd.read_csv(csv_path, sep='\t', skiprows=1)
        else:
            raw_df = pd.read_csv(csv_path, sep=',')
        self.glint = glint
        df = self.update_df(df=raw_df,
                            ir_min_threshold=ir_min_threshold,
                            ir_max_threshold=ir_max_threshold,
                            max_aot=max_aot,
                            cams_val=cams_val)

        #########################
        # KDE TEST FOR Oa08 RED #
        #########################
        if kde:
            if (len(df['Oa08_reflectance:float'].unique()) < 2) and (len(df) < 4):
                file_id_date_name = os.path.basename(csv_path).split('____')[1].split('_')[0]
                print(f'Skipping KDE stats for lack of data @ {file_id_date_name}')
                return 'KDE_fail', file_id_date_name

            x = df['Oa08_reflectance:float'].copy()
            pk, xray, yray, kde_res = self.kde_local_maxima(x)
            xmean = np.mean(x)
            kdemaxes = [m for m in xray[pk]]
            kdemaxes.append(xmean)
            drop_threshold = min(kdemaxes)
            drop_threshold_upper_lim = drop_threshold + (0.1 * drop_threshold)
            # drop_threshold_upper_lim = drop_threshold + (0.25 * drop_threshold)
            # drop_threshold_lower_lim = drop_threshold - (0.25 * drop_threshold)

            # Drop data outside bounds for drop_threshold:
            indexNames = df[df['Oa08_reflectance:float'] > drop_threshold_upper_lim].index
            df.drop(indexNames, inplace=True)
            # indexNames = df[df['Oa08_reflectance:float'] < drop_threshold_lower_lim].index
            # df.drop(indexNames, inplace=True)

        #####################################
        # Fix the indexing of the dataframe #
        #####################################
        df.reset_index(drop=True, inplace=True)



        # Save V2
        if savepath:
            full_saving_path = os.path.join(savepath, os.path.basename(csv_path))
            print(f'Saving dataset: {full_saving_path}')
            df.to_csv(full_saving_path)
            return full_saving_path, df
            # if len(df) > 3:
            #     print(f'Saving dataset: {full_saving_path}')
            #     df.to_csv(full_saving_path)
            #     return full_saving_path, df
            # else:
            #     print(f'Skipping empty dataset: {os.path.basename(csv_path)}')
            #     return full_saving_path, df

        else:
            return 'unsaved', df

    @staticmethod
    def kde_local_maxima(x):
        """
        # TODO: Write docstrings.
        """
        kernel = stats.gaussian_kde(dataset=x, bw_method='silverman')

        kde_res = kernel(x)

        xs, ys = zip(*sorted(zip(x, kde_res)))

        xray = np.array(xs)
        yray = np.array(ys)

        ma = argrelextrema(yray, np.greater)[0]
        peak_position = list(ma)
        return peak_position, xray, yray, kde_res

    @staticmethod
    def get_mean_and_clean(image_path):
        """
        # TODO: Write docstrings.
        """
        # read text file and convert to pandas dataframe
        df = pd.read_csv(image_path)

        # Columns to keep
        keep = ['Oa01_reflectance:float',
                'Oa02_reflectance:float',
                'Oa03_reflectance:float',
                'Oa04_reflectance:float',
                'Oa05_reflectance:float',
                'Oa06_reflectance:float',
                'Oa07_reflectance:float',
                'Oa08_reflectance:float',
                'Oa09_reflectance:float',
                'Oa10_reflectance:float',
                'Oa11_reflectance:float',
                'Oa12_reflectance:float',
                'Oa16_reflectance:float',
                'Oa17_reflectance:float',
                'Oa18_reflectance:float',
                'Oa21_reflectance:float',
                'latitude:double',
                'longitude:double',
                'OAA:float',
                'OZA:float',
                'SAA:float',
                'SZA:float',
                'A865:float',
                'T865:float',
                'GLINT',
                'ABSVLDPX']

        # Drop columns not present in the list
        df = df.filter(keep)

        # get the std deviation of the specific column
        glintstd = df.loc[:, 'GLINT'].std(skipna=True)
        result_dict = {}

        if len(df) > 0:
            # get the % of valid pixels in DF
            validpx = df['ABSVLDPX'][0]
            pctvalidpx = (len(df) * 100) / validpx

            # drop lon/lat columns
            df = df.drop(['latitude:double', 'longitude:double', 'ABSVLDPX'], axis=1)

            for colname in df:
                result_dict[colname] = df[colname].mean(skipna=True)

            result_dict['median_IR'] = np.nanmedian(df['Oa17_reflectance:float'])
            result_dict['AbsVldPx'] = validpx
            result_dict['VldPx.pct'] = pctvalidpx
            result_dict['GLINT.std'] = glintstd

            # https://sentinel.esa.int/web/sentinel/technical-guides/sentinel-3-olci/level-2/aerosol-optical-thickness
            t865_desc = df.loc[:, 'T865:float'].describe()

            result_dict['T865.count'], \
            result_dict['T865.mean'], \
            result_dict['T865.std'], \
            result_dict['T865.min'], \
            result_dict['T865.25%ile'], \
            result_dict['T865.50%ile'], \
            result_dict['T865.75%ile'], \
            result_dict['T865.max'] = list(t865_desc)

            # https://sentinel.esa.int/web/sentinel/technical-guides/sentinel-3-olci/level-2/aerosol-angstrom-exponent
            a865_desc = df.loc[:, 'A865:float'].describe()

            result_dict['A865.count'], \
            result_dict['A865.mean'], \
            result_dict['A865.std'], \
            result_dict['A865.min'], \
            result_dict['A865.25%ile'], \
            result_dict['A865.50%ile'], \
            result_dict['A865.75%ile'], \
            result_dict['A865.max'] = list(a865_desc)

        else:
            result_dict['Oa01_reflectance:float'] = 0
            result_dict['Oa02_reflectance:float'] = 0
            result_dict['Oa03_reflectance:float'] = 0
            result_dict['Oa04_reflectance:float'] = 0
            result_dict['Oa05_reflectance:float'] = 0
            result_dict['Oa06_reflectance:float'] = 0
            result_dict['Oa07_reflectance:float'] = 0
            result_dict['Oa08_reflectance:float'] = 0
            result_dict['Oa09_reflectance:float'] = 0
            result_dict['Oa10_reflectance:float'] = 0
            result_dict['Oa11_reflectance:float'] = 0
            result_dict['Oa12_reflectance:float'] = 0
            result_dict['Oa16_reflectance:float'] = 0
            result_dict['Oa17_reflectance:float'] = 0
            result_dict['Oa18_reflectance:float'] = 0
            result_dict['Oa21_reflectance:float'] = 0
            result_dict['median_IR'] = 0
            result_dict['OAA:float'] = 0
            result_dict['OZA:float'] = 0
            result_dict['SAA:float'] = 0
            result_dict['SZA:float'] = 0
            result_dict['A865.mean'] = 0
            result_dict['A865.std'] = 0
            result_dict['A865.min'] = 0
            result_dict['A865.max'] = 0
            result_dict['A865.25%ile'] = 0
            result_dict['A865.50%ile'] = 0
            result_dict['A865.75%ile'] = 0
            result_dict['T865.mean'] = 0
            result_dict['T865.std'] = 0
            result_dict['T865.min'] = 0
            result_dict['T865.max'] = 0
            result_dict['T865.25%ile'] = 0
            result_dict['T865.50%ile'] = 0
            result_dict['T865.75%ile'] = 0
            result_dict['GLINT'] = 0
            result_dict['GLINT.std'] = 0
            result_dict['AbsVldPx'] = 0
            result_dict['VldPx.pct'] = 0

        return result_dict



    @staticmethod
    def netcdf_kml_slicer(gpt_path, kml_path, input_imgs_folder, output_folder):
        """
        This function takes in a folder containing several Sentienl-3 L2 WFR images (input_imgs_folder) and makes subsets
        for each one of them by using a input KML file (kml_path) that can be generated at google earth engine.
        To make it work the user also needs to input where in the system it is installed
        the GPT tool that comes along with ESA-SNAP (gpt_path).
        (output_folder) is where do you want to save the extracted images.
        By the end of the execution, the function returns a list with each CSV extracted this way.

        gpt_path: where in your system is the SNAP-gpt tool.
            unix: '/d_drive_data/snap/bin/gpt'
            wind: 'C:\Program Files\snap\bin\gpt.exe'

        kml_path: where is the Google Earth KML delimited region to be used.

        input_imgs_folder: where is your sentinel 3 images. expects something like:
            unix: '/d_drive_data/L2_WFR'
            wind: 'E:\S3\L2_WFR'

        output_folder: where to save the processed files. Expects something like:
            unix: '/d_drive_data/processing/MANACAPURU/'
            wind: 'D:\\processing\\win\\COARI'

        """
        t1 = time.perf_counter()
        work_dir = input_imgs_folder

        logging.info(f'Importing GPTBridge...\n')
        gpt = out.GPTBridge(gpt_sys_path=gpt_path, output_path=output_folder, kml_path=kml_path)

        # adding every image inside the working directory to a list
        field_files = os.listdir(work_dir)

        # adding the complete path to each image folder listed
        field_files = [os.path.join(work_dir, image) for image in field_files]

        total = len(field_files)
        logging.info(f'Total files identified in folder: {total}\n')

        # Asynchronous-processing: (DISCLAIMER: this can be a REALLY INTENSIVE computation, be careful.)
        with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count() - 1) as executor:
            try:
                result = list(executor.map(gpt.get_pixels_by_kml, field_files))
            except concurrent.futures.process.BrokenProcessPool as ex:
                logging.error(f"{ex} This might be caused by limited system resources. "
                              f"Try increasing system memory or disable concurrent processing. ")

        # # Synchronous-processing: (DEPRECATED)
        # for n, image in enumerate(field_files):
        #
        #     file_name = os.path.join(work_dir, image)
        #     print(f'Processing image {n} of {total}:\n{image}\n')
        #     gpt.get_pixels_by_kml(file_name)

        # s3frbr_output_files = os.listdir(work_dir)
        # sorted_s3frbr_output_files = sorted(os.listdir(work_dir), key=lambda s: s[16:31])

        t2 = time.perf_counter()
        logging.info(f'>>> Finished in {round(t2 - t1, 2)} second(s). <<<')

        final_result = [os.path.join(output_folder, subset) for subset in result]
        return final_result

    @staticmethod
    def build_list_from_subset(work_dir):
        """
        Creates a python list containing the accumulated data from all the extracted areas by the kml file.
        """
        sorted_s3frbr_output_files = sorted(os.listdir(work_dir), key=lambda s: s[16:31])

        return sorted_s3frbr_output_files

    def generate_time_series_data(self, work_dir, sorted_list):
        """
        # TODO: Write docstrings.
        """
        Oa01_reflectance_tms = []
        Oa02_reflectance_tms = []
        Oa03_reflectance_tms = []
        Oa04_reflectance_tms = []
        Oa05_reflectance_tms = []
        Oa06_reflectance_tms = []
        Oa07_reflectance_tms = []
        Oa08_reflectance_tms = []
        Oa09_reflectance_tms = []
        Oa10_reflectance_tms = []
        Oa11_reflectance_tms = []
        Oa12_reflectance_tms = []
        Oa16_reflectance_tms = []
        Oa17_reflectance_tms = []
        Oa18_reflectance_tms = []
        Oa21_reflectance_tms = []

        Oa17_median_tms = []

        OAA_tms = []
        OZA_tms = []
        SAA_tms = []
        SZA_tms = []

        A865_tms = []
        A865std_tms = []
        A865min_tms = []
        A865max_tms = []
        A865tile25_tms = []
        A865tile50_tms = []
        A865tile75_tms = []

        T865_tms = []
        T865std_tms = []
        T865min_tms = []
        T865max_tms = []
        T865tile25_tms = []
        T865tile50_tms = []
        T865tile75_tms = []

        glint_tms = []
        glintstd_tms = []
        absvldpx_tms = []
        pctvlddpx_tms = []
        datetime_labels = []
        string_labels = []
        quality_labels = []
        qlinfo_labels = []

        total = len(sorted_list)

        for n, image in enumerate(sorted_list):
            figdate = os.path.basename(image).split('____')[1].split('_')[0]
            dtlbl = datetime.strptime(figdate, '%Y%m%dT%H%M%S')
            print(f'Extracting image {n + 1}/{total} - {dtlbl}...')

            file_name = os.path.join(work_dir, image)

            strlbl = figdate

            means_dict = self.get_mean_and_clean(file_name)

            if means_dict['AbsVldPx'] == 0:
                quality = 0
                qobs = 'Empty DataFrame, processing skipped.'
            elif means_dict['VldPx.pct'] < 5.0:
                quality = 2
                qobs = 'Less than 5% of valid pixels.'
            else:
                quality = 1
                qobs = 'Pass.'

            Oa01_reflectance_tms.append(means_dict['Oa01_reflectance:float'])
            Oa02_reflectance_tms.append(means_dict['Oa02_reflectance:float'])
            Oa03_reflectance_tms.append(means_dict['Oa03_reflectance:float'])
            Oa04_reflectance_tms.append(means_dict['Oa04_reflectance:float'])
            Oa05_reflectance_tms.append(means_dict['Oa05_reflectance:float'])
            Oa06_reflectance_tms.append(means_dict['Oa06_reflectance:float'])
            Oa07_reflectance_tms.append(means_dict['Oa07_reflectance:float'])
            Oa08_reflectance_tms.append(means_dict['Oa08_reflectance:float'])
            Oa09_reflectance_tms.append(means_dict['Oa09_reflectance:float'])
            Oa10_reflectance_tms.append(means_dict['Oa10_reflectance:float'])
            Oa11_reflectance_tms.append(means_dict['Oa11_reflectance:float'])
            Oa12_reflectance_tms.append(means_dict['Oa12_reflectance:float'])
            Oa16_reflectance_tms.append(means_dict['Oa16_reflectance:float'])
            Oa17_reflectance_tms.append(means_dict['Oa17_reflectance:float'])
            Oa18_reflectance_tms.append(means_dict['Oa18_reflectance:float'])
            Oa21_reflectance_tms.append(means_dict['Oa21_reflectance:float'])

            Oa17_median_tms.append(means_dict['median_IR'])

            OAA_tms.append(means_dict['OAA:float'])
            OZA_tms.append(means_dict['OZA:float'])
            SAA_tms.append(means_dict['SAA:float'])
            SZA_tms.append(means_dict['SZA:float'])

            A865_tms.append(means_dict['A865.mean'])
            A865std_tms.append(means_dict['A865.std'])
            A865min_tms.append(means_dict['A865.min'])
            A865max_tms.append(means_dict['A865.max'])
            A865tile25_tms.append(means_dict['A865.25%ile'])
            A865tile50_tms.append(means_dict['A865.50%ile'])
            A865tile75_tms.append(means_dict['A865.75%ile'])

            T865_tms.append(means_dict['T865.mean'])
            T865std_tms.append(means_dict['T865.std'])
            T865min_tms.append(means_dict['T865.min'])
            T865max_tms.append(means_dict['T865.max'])
            T865tile25_tms.append(means_dict['T865.25%ile'])
            T865tile50_tms.append(means_dict['T865.50%ile'])
            T865tile75_tms.append(means_dict['T865.75%ile'])

            glint_tms.append(means_dict['GLINT'])
            glintstd_tms.append(means_dict['GLINT.std'])
            absvldpx_tms.append(means_dict['AbsVldPx'])
            pctvlddpx_tms.append(means_dict['VldPx.pct'])
            datetime_labels.append(dtlbl)
            string_labels.append(strlbl)
            quality_labels.append(quality)
            qlinfo_labels.append(qobs)

            d = {'filename': sorted_list,
                 'Datetime': datetime_labels,
                 'Date-String': string_labels,
                 'B1-400': Oa01_reflectance_tms,
                 'B2-412.5': Oa02_reflectance_tms,
                 'B3-442.5': Oa03_reflectance_tms,
                 'B4-490': Oa04_reflectance_tms,
                 'B5-510': Oa05_reflectance_tms,
                 'B6-560': Oa06_reflectance_tms,
                 'B7-620': Oa07_reflectance_tms,
                 'B8-665': Oa08_reflectance_tms,
                 'B9-673.75': Oa09_reflectance_tms,
                 'B10-681.25': Oa10_reflectance_tms,
                 'B11-708.75': Oa11_reflectance_tms,
                 'B12-753.75': Oa12_reflectance_tms,
                 'B16-778.75': Oa16_reflectance_tms,
                 'B17-865': Oa17_reflectance_tms,
                 'B18-885': Oa18_reflectance_tms,
                 'B21-1020': Oa21_reflectance_tms,

                 'IR-median': Oa17_median_tms,

                 'OAA': OAA_tms,
                 'OZA': OZA_tms,
                 'SAA': SAA_tms,
                 'SZA': SZA_tms,

                 'A865': A865_tms,
                 'A865.std': A865std_tms,
                 'A865.min': A865min_tms,
                 'A865.max': A865max_tms,
                 'A865.25%tile': A865tile25_tms,
                 'A865.50%tile': A865tile50_tms,
                 'A865.75%tile': A865tile75_tms,

                 'T865': T865_tms,
                 'T865.std': T865std_tms,
                 'T865.min': T865min_tms,
                 'T865.max': T865max_tms,
                 'T865.25%tile': T865tile25_tms,
                 'T865.50%tile': T865tile50_tms,
                 'T865.75%tile': T865tile75_tms,

                 'meanGlint': glint_tms,
                 'Glintstd': glintstd_tms,
                 'abs-vld-px': absvldpx_tms,
                 'pct-vld-px': pctvlddpx_tms,
                 'quality': quality_labels,
                 'qality-info': qlinfo_labels}

        return d

    def s3l2_custom_reflectance_plot(self, df, figure_title=None, save_title=None, cbar=False, c_lbl='T865'):
        """
        # TODO: Write docstrings.
        """
        plt.rcParams['figure.figsize'] = self.rcparam
        colnms = ['T865:float',
                  'Oa01_reflectance:float',
                  'Oa02_reflectance:float',
                  'Oa03_reflectance:float',
                  'Oa04_reflectance:float',
                  'Oa05_reflectance:float',
                  'Oa06_reflectance:float',
                  'Oa07_reflectance:float',
                  'Oa08_reflectance:float',
                  'Oa09_reflectance:float',
                  'Oa10_reflectance:float',
                  'Oa11_reflectance:float',
                  'Oa12_reflectance:float',
                  'Oa16_reflectance:float',
                  'Oa17_reflectance:float',
                  'Oa18_reflectance:float',
                  'Oa21_reflectance:float']

        # create a list with the value in (nm) of the 16 Sentinel-3 bands for L2 products.
        s3_bands_tick = list(self.exp.s3_bands_l2.values())

        # create a list with the name of the 16 Sentinel-3 bands for L2 products.
        s3_bands_tick_label = list(self.exp.s3_bands_l2.keys())

        plt.rcParams['figure.figsize'] = [12, 6]

        fig = plt.figure()
        # fig.show()
        ax1 = fig.add_subplot(111)

        ax1.set_xlabel('Wavelenght (nm)')
        ax1.set_ylabel('Reflectance')

        if figure_title:
            ax1.set_title(figure_title, y=1, fontsize=16)

        # creating color scale based on T865
        lst = df['T865:float']
        # lst = df['minus_cams']
        minima = min(lst)
        maxima = max(lst)
        norm = matplotlib.colors.Normalize(vmin=minima, vmax=maxima, clip=True)
        mapper = cm.ScalarMappable(norm=norm, cmap=cm.viridis)
        # mapper = cm.ScalarMappable(norm=norm, cmap=cm.Spectral_r)

        for _, row in df[colnms].iterrows():
            # ax1.plot(s3_bands_tick, list(row))
            t865c = mapper.to_rgba(row[0])
            ax1.plot(s3_bands_tick, list(row[1:]), alpha=0.4, c=t865c)

        ax1.axhline(y=0, xmin=0, xmax=1, linewidth=0.5, color='black', linestyle='--')
        ax1.set_xticks(s3_bands_tick)
        ax1.set_xticklabels(s3_bands_tick)
        ax1.tick_params(labelrotation=90, labelsize='small')

        ax2 = ax1.twiny()
        ax2.plot(s3_bands_tick, [0] * (len(s3_bands_tick)), alpha=0.0)
        ax2.set_xticks(s3_bands_tick)
        ax2.set_xticklabels(s3_bands_tick_label)
        ax2.tick_params(labelrotation=90, labelsize='xx-small')
        ax2.set_title('Sentinel-3 Oa Bands', y=0.93, x=0.12, fontsize='xx-small')

        if cbar:
            cbar = fig.colorbar(ax1, ax=ax1)
            cbar.set_label(c_lbl)

        if save_title:
            plt.savefig(save_title, dpi=self.imgdpi, bbox_inches='tight')
            plt.close(fig)
        else:
            plt.show()

    def plot_kde_hist(self, title, xray, yray, x, kde_res, pk, svpath_n_title=None):
        plt.rcParams['figure.figsize'] = [16, 6]
        fig = plt.figure()
        ax = plt.axes()
        ax.set_title(title, fontsize=16)

        ax.plot(xray, yray, color='k', label='Fitted KDE', zorder=11)
        ax.plot(xray[pk], yray[pk], 'or', zorder=11, label='KDE Local Maxima')
        ax.hist(x, 100, color='lightblue', label='Histogram')
        ax.scatter(x, kde_res, zorder=10, marker='x', label='Observations')

        ax.set_xlabel('Reflectance - Oa08:665nm', fontsize=16)
        ax.set_ylabel('Frequency', fontsize=16)

        # Get the mean
        ax.axvline(x.mean(), color='g', label='Mean')
        # Get the std. dev.
        ax.axvline(x=np.mean(x) - np.std(x), ls="--", color='g', alpha=0.7, label='Std.Deviation')
        ax.axvline(x=np.mean(x) + np.std(x), ls="--", color='g', alpha=0.7)


        ax.legend()

        for m in xray[pk]:
            ax.axvline(m, color='r')
        if svpath_n_title:
            plt.savefig(svpath_n_title, dpi=self.imgdpi)
            plt.close(fig)

        if not svpath_n_title:
            plt.show()

    def plot_kde_histntable(self, xray, yray, x, kde_res, pk, title=None, svpath_n_title=None):
        """
        # TODO: Write docstrings.
        """
        plt.rcParams['figure.figsize'] = self.rcparam
        fig = plt.figure()
        # gridspec: https://stackoverflow.com/questions/10388462/matplotlib-different-size-subplots
        gs = gridspec.GridSpec(1, 2, width_ratios=[2.5, 1])
        gs.wspace = 0.01
        ax = fig.add_subplot(gs[0])

        if title:
            ax.set_title(title, fontsize=16)

        ax.plot(xray, yray, color='k', label='Fitted KDE', zorder=11)
        ax.plot(xray[pk], yray[pk], 'or', zorder=11, label='KDE Local Maxima')
        ax.hist(x, 100, color='lightblue', label='Histogram')
        ax.scatter(x, kde_res, zorder=10, marker='x', label='Observations')

        ax.set_xlabel('Reflectance - Oa08:665nm')
        ax.set_ylabel('Frequency')

        # Get the mean
        ax.axvline(x.mean(), color='g', label='Mean')
        # Get the std. dev.
        ax.axvline(x=np.mean(x) - np.std(x), ls="--", color='g', alpha=0.7, label='Std.Deviation')
        ax.axvline(x=np.mean(x) + np.std(x), ls="--", color='g', alpha=0.7)

        ax.legend()

        for m in xray[pk]:
            ax.axvline(m, color='r')

        ax2 = fig.add_subplot(gs[1])

        cv = (np.std(x) / np.mean(x)) * 100
        cv = round(cv, 6)
        std = round(np.std(x), 6)
        xmean = round(np.mean(x), 6)
        kdemaxes = [round(m, 3) for m in xray[pk]]
        # plt table: https://chadrick-kwag.net/matplotlib-table-example/
        table_data = [
            ["Mean", str(xmean)],
            ["Std. Deviation", str(std)],
            ["KDE Local max.", str(kdemaxes)],
            ["Coeff. of variation", str(round(cv, 2))+'%']
        ]

        table = ax2.table(cellText=table_data, loc='center')
        # table.set_fontsize(20)
        table.scale(1, 1.5)
        ax2.axis('off')

        if svpath_n_title:
            plt.savefig(svpath_n_title, dpi=self.imgdpi, bbox_inches='tight')
            plt.close(fig)

        if not svpath_n_title:
            plt.show()

    def plot_single_sktr(self, xdata, ydata, xlabel, ylabel, color, clabel, title, savepathname):
        """
        # TODO: Write docstrings.
        """
        plt.rcParams['figure.figsize'] = [9.4, 8]
        fig = plt.figure()
        ax = plt.axes()
        ax.set_title(title)

        img = ax.scatter(xdata, ydata, s=3, c=color)
        cbar = fig.colorbar(img, ax=ax)
        cbar.set_label(clabel)

        ax.plot([-1, 1], [-1, 1], 'k-', linewidth=1)
        ax.plot([0, 0], [-1, 1], c='grey', linestyle='dashed', linewidth=1)
        ax.plot([-1, 1], [0, 0], c='grey', linestyle='dashed', linewidth=1)

        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        # TODO: add label in the colorbar

        ax.set_xlim(-0.02, 0.2)
        ax.set_ylim(-0.02, 0.2)
        plt.text(0.160, 0.003, '% Reflectance')

        plt.savefig(savepathname, dpi=self.imgdpi)

        plt.close(fig)

    # GENERATES COMPARATIVE SCATTERPLOTS
    def plot_overlap_sktr(self, x1_data, y1_data, x2_data, y2_data, x_lbl, y_lbl, c1_data, c1_lbl, c2_data, c2_lbl, title,
                          savepathname):
        """
        # TODO: Write docstrings.
        """
        plt.rcParams['figure.figsize'] = [12, 8]
        fig = plt.figure()
        ax = plt.axes()
        ax.set_title(title)

        img = ax.scatter(x2_data, y2_data, s=5, c=c2_data, cmap='winter_r')
        cbar = fig.colorbar(img, ax=ax)
        cbar.set_label(c2_lbl)

        img = ax.scatter(x1_data, y1_data, s=5, c=c1_data, cmap='autumn_r')
        cbar = fig.colorbar(img, ax=ax)
        cbar.set_label(c1_lbl)

        ax.plot([-1, 1], [-1, 1], 'k-', linewidth=1)
        ax.plot([0, 0], [-1, 1], c='grey', linestyle='dashed', linewidth=1)
        ax.plot([-1, 1], [0, 0], c='grey', linestyle='dashed', linewidth=1)

        ax.set_xlabel(x_lbl)  # RED: Oa08 (865nm)
        ax.set_ylabel(y_lbl)  # NIR: Oa17 (665nm)

        ax.set_xlim(-0.02, 0.2)
        ax.set_ylim(-0.02, 0.2)
        plt.text(0.160, 0.003, '% Reflectance')

        plt.savefig(savepathname, dpi=self.imgdpi)

        plt.close(fig)

    # GENERATES COMPARATIVE SCATTERPLOTS
    def plot_sidebyside_sktr(self,
                             x1_data, y1_data, x2_data, y2_data, x_lbl, y_lbl, c1_data, c1_lbl, c2_data, c2_lbl,
                             cmap1='viridis', cmap2='viridis',
                             title=None,
                             savepathname=None):
        """
        # TODO: Write docstrings.
        """
        plt.rcParams['figure.figsize'] = [14, 5.2]
        fig, (ax1, ax2) = plt.subplots(1, 2)

        if title:
            fig.suptitle(title)

        skt1 = ax1.scatter(x1_data, y1_data, s=3, c=c1_data, cmap=cmap1)
        cbar = fig.colorbar(skt1, ax=ax1)
        cbar.set_label(c1_lbl)

        skt2 = ax2.scatter(x2_data, y2_data, s=3, c=c2_data, cmap=cmap2)
        cbar = fig.colorbar(skt2, ax=ax2)
        cbar.set_label(c2_lbl)

        ax1.plot([-0.02, 0.2], [-0.02, 0.2], 'k-', linewidth=1)
        ax1.plot([0.01, 0.01], [-0.02, 0.2], c='red', linestyle='dashed', linewidth=1)
        ax1.plot([-0.02, 0.2], [0.01, 0.01], c='red', linestyle='dashed', linewidth=1)
        ax1.plot([0, 0], [-0.02, 0.2], c='grey', linestyle='dashed', linewidth=1)
        ax1.plot([-0.02, 0.2], [0, 0], c='grey', linestyle='dashed', linewidth=1)

        ax2.plot([-0.02, 0.2], [-0.02, 0.2], 'k-', linewidth=1)
        ax2.plot([0.01, 0.01], [-0.02, 0.2], c='red', linestyle='dashed', linewidth=1)
        ax2.plot([-0.02, 0.2], [0.01, 0.01], c='red', linestyle='dashed', linewidth=1)
        ax2.plot([0, 0], [-0.02, 0.2], c='grey', linestyle='dashed', linewidth=1)
        ax2.plot([-0.02, 0.2], [0, 0], c='grey', linestyle='dashed', linewidth=1)

        ax1.set_xlabel(x_lbl)  # RED: Oa08 (865nm)
        ax1.set_ylabel(y_lbl)  # NIR: Oa17 (665nm)
        ax2.set_xlabel(x_lbl)

        ax1.set_xlim(-0.02, 0.2)
        ax1.set_ylim(-0.02, 0.2)

        ax2.set_xlim(-0.02, 0.2)
        ax2.set_ylim(-0.02, 0.2)

        if savepathname:
            plt.savefig(savepathname, dpi=self.imgdpi, bbox_inches='tight')
            plt.close(fig)

        if not savepathname:
            plt.show()

    def plot_time_series(self, tms_dict, tms_key, fig_title, save_title=None):
        """
        # TODO: Write docstrings.
        """
        plt.rcParams['figure.figsize'] = [16, 6]
        # fig = plt.figure()
        ax = plt.axes()
        ax.set_title(fig_title, fontsize=16)
        ax.plot(tms_dict['Datetime'], tms_dict[tms_key], marker='o', markersize=5, label=self.bname_dict[tms_key])
        ax.set_xlabel('Date', fontsize=16)
        ax.set_ylabel('Reflectance', fontsize=16)
        ax.legend()
        if save_title:
            plt.savefig(save_title, dpi=self.imgdpi)
        plt.show()

    def plot_multiple_time_series(self, tms_dict, tms_keys, fig_title, save_title=None):
        """
        # TODO: Write docstrings.
        """
        plt.rcParams['figure.figsize'] = [16, 6]
        fig = plt.figure()
        ax = plt.axes()
        ax.set_title(fig_title, fontsize=16)
        for element in tms_keys:
            ax.plot(tms_dict['Datetime'], tms_dict[element], marker='o', markersize=5, label=self.bname_dict[element])
        ax.set_xlabel('Date', fontsize=16)
        ax.set_ylabel('Reflectance', fontsize=16)
        ax.legend()
        if save_title:
            plt.savefig(save_title, dpi=self.imgdpi)
        plt.show()

    def plot_ts_from_csv(self, csv_path, tms_key, fig_title, save_title=None):
        """
        # TODO: Write docstrings.
        """
        tms_dict = pd.read_csv(csv_path, parse_dates=['Datetime'])
        self.plot_time_series(tms_dict, tms_key, fig_title, save_title)

    def plot_multi_ts_from_csv(self, csv_path, tms_keys, fig_title, save_title=None):
        """
        # TODO: Write docstrings.
        """
        tms_dict = pd.read_csv(csv_path, parse_dates=['Datetime'])
        self.plot_multiple_time_series(tms_dict, tms_keys, fig_title, save_title)

    @staticmethod
    def save_tms_to_csv(tms_dicst, csv_file_name):
        """
        # TODO: Write docstrings.
        """
        logging.info(f'Saving time-series DataFrame @ {csv_file_name}')
        df = pd.DataFrame(data=tms_dicst)
        df.to_csv(csv_file_name)
        logging.info(f'Done.')

    def raw_report(self, full_csv_path, img_id_date, raw_df, filtered_df, output_rprt_path=None):
        """
        This function will ingest RAW CSVs from S3-FRBR > outsourcing.py > GPTBridge.get_pixels_by_kml(), convert them
        into Pandas DataFrames, filter them and generate a PDF report.

        # TODO: Update docstrings.
        """

        figdate = img_id_date
        df = raw_df
        fdf = filtered_df
        RAW_CSV = full_csv_path

        if output_rprt_path:
            aux_figs_path = os.path.join(output_rprt_path, 'aux_'+figdate)

        else:
            aux_figs_path = os.path.join(RAW_CSV, 'aux_'+figdate)

        os.mkdir(aux_figs_path)

        # Generating the saving path of the individual report images so we can fetch it later.
        svpt1 = os.path.join(aux_figs_path, 'a.png')
        svpt2 = os.path.join(aux_figs_path, 'b.png')
        svpt3 = os.path.join(aux_figs_path, 'c.png')
        svpt4 = os.path.join(aux_figs_path, 'd.png')
        svpt5 = os.path.join(aux_figs_path, 'e.png')
        svpt_report = os.path.join(output_rprt_path, 'report_'+figdate+'.pdf')

        # IMG A - Scatter MAP
        plt.rcParams['figure.figsize'] = self.rcparam
        fig = plt.figure()
        ax = plt.axes()
        ax.set_title(figdate, fontsize=16)
        sktmap = ax.scatter(df['longitude:double'], df['latitude:double'], c=df['T865:float'], cmap='viridis', s=3)
        cbar = fig.colorbar(sktmap, ax=ax)
        cbar.set_label('Aer. Optical Thickness (T865)')

        ax.set_xlim(-61.34, -60.46)
        ax.set_ylim(-3.65, -3.25)
        ax.set_xlabel('LON')
        ax.set_ylabel('LAT')

        plt.savefig(svpt1, dpi=self.imgdpi, bbox_inches='tight')

        # IMG B - RAW Scatter
        self.plot_sidebyside_sktr(x1_data=df['Oa08_reflectance:float'],
                                   y1_data=df['Oa17_reflectance:float'],
                                   x2_data=df['Oa08_reflectance:float'],
                                   y2_data=df['Oa17_reflectance:float'],
                                   x_lbl='RED: Oa08 (665nm)',
                                   y_lbl='NIR: Oa17 (865nm)',
                                   c1_data=df['A865:float'],
                                   c1_lbl='Aer. Angstrom Expoent (A865)',
                                   c2_data=df['T865:float'],
                                   c2_lbl='Aer. Optical Thickness (T865)',
                                   # title=f'MANACAPURU v6 WFR {figdate} RED:Oa08(665nm) x NIR:Oa17(865nm)',
                                   savepathname=svpt2)

        # IMG C - Filtered Scatter
        self.plot_sidebyside_sktr(x1_data=fdf['Oa08_reflectance:float'],
                                   y1_data=fdf['Oa17_reflectance:float'],
                                   x2_data=fdf['Oa08_reflectance:float'],
                                   y2_data=fdf['Oa17_reflectance:float'],
                                   x_lbl='RED: Oa08 (665nm)',
                                   y_lbl='NIR: Oa17 (865nm)',
                                   c1_data=fdf['A865:float'],
                                   c1_lbl='Aer. Angstrom Expoent (A865)',
                                   c2_data=fdf['T865:float'],
                                   c2_lbl='Aer. Optical Thickness (T865)',
                                   # title=f'MANACAPURU v6 WFR {figdate} RED:Oa08(665nm) x NIR:Oa17(865nm)',
                                   savepathname=svpt3)

        # IMG C - KD Histogram
        x = fdf['Oa08_reflectance:float'].copy()

        pk, xray, yray, kde_res = self.kde_local_maxima(x)

        self.plot_kde_histntable(xray=xray,
                                 yray=yray,
                                 x=x,
                                 kde_res=kde_res,
                                 pk=pk,
                                 svpath_n_title=svpt4)

        # IMG D - Reflectance
        self.s3l2_custom_reflectance_plot(df=fdf,
                                          # figure_title=figdate,
                                          save_title=svpt5)

        # Report
        images = [Image.open(x) for x in [svpt1, svpt2, svpt3, svpt4, svpt5]]
        report = utils.pil_grid(images, 1)

        if output_rprt_path:
            report.save(svpt_report, resolution=100.0)

        plt.close('all')

        return report

    def full_reports(self, raw_csv_dir, save_reports_dir):
        """
        Given a path of RAW Sentinel3 CSV subsets, filter and generate reports.
        """
        todo = self.build_list_from_subset(raw_csv_dir)
        todo_fullpath = [os.path.join(raw_csv_dir, csv) for csv in todo]

        t1 = time.perf_counter()
        skiplst = []
        donelst = []
        img_report_list = []

        total = len(todo_fullpath)
        for n, img in enumerate(todo_fullpath):

            figdate = os.path.basename(img).split('____')[1].split('_')[0]

            print(f'>>> Loading CSV: {n + 1} of {total} ... {figdate}')

            df = pd.read_csv(img, sep='\t', skiprows=1)

            # TODO: There should not need to be 2 tests doing the same thing :(
            try:
                upd_msg, fdf = self.update_csvs(csv_path=img, threshold=0.2)
            except Exception as e:
                print("type error: " + str(e))
                skiplst.append(img)
                continue

            # The KDE needs at least two different reflectance values to work.
            if upd_msg == 'KDE_fail':
                skiplst.append(img)
                continue

            donelst.append(img)
            img_report = self.raw_report(full_csv_path=img,
                                         img_id_date=figdate,
                                         raw_df=df,
                                         filtered_df=fdf,
                                         output_rprt_path=save_reports_dir)

            img_report_list.append(img_report)

        print('Merging images to generate full report...')

        pdf_report_filename = os.path.join(save_reports_dir, 'full_report.pdf')

        img_report_list[0].save(pdf_report_filename,
                                "PDF",
                                resolution=100.0,
                                save_all=True,
                                append_images=img_report_list[1:])

        t2 = time.perf_counter()
        print(f'>>> Finished in {round(t2 - t1, 2)} second(s). <<<')
        return skiplst, donelst

if __name__ == '__main__':
    logging.info(f'Arguments received:\n{sys.argv}\n')

    tsgen = TsGenerator()

    # DEPRECATED ?
    # if len(sys.argv) > 2:
    #     logging.info(f'Running Time-series generator.\n'
    #                  f'SNAP-GPT folder: {sys.argv[1]}\n'
    #                  f'using KML file: {sys.argv[2]}\n'
    #                  f'Input folder: {sys.argv[3]}\n'
    #                  f'Output folder: {sys.argv[4]}\n')
    #
    #     extracted_list = tsgen.netcdf_kml_slicer(gpt_path=sys.argv[1],
    #                                              kml_path=sys.argv[2],
    #                                              input_imgs_folder=sys.argv[3],
    #                                              output_folder=sys.argv[4])
    # else:
    #     logging.info('Execution is over: Insufficient number of arguments.')

    sorted_files = tsgen.build_list_from_subset(sys.argv[1])

    ts_dict = tsgen.generate_time_series_data(sys.argv[1], sorted_files)

    output_file = sys.argv[2]

    tsgen.save_tms_to_csv(ts_dict, output_file)

    # =========================================================================
    # PLOTTING STUFF
    area = sys.argv[1].split('\\')[-1]  # "D:\processing\win\COARI" -> 'COARI'
    save_file = sys.argv[3]

    # tsgen.plot_ts_from_csv(csv_path=output_file,
    #                        tms_key='B8-665',
    #                        fig_title='{area}: S3-WFR Oa08 Reflectance (665nm) time-series from 2019-03-09 to 2020-03-31')

    tsgen.plot_multi_ts_from_csv(csv_path=output_file,
                                 tms_keys=['B8-665', 'B17-865'],
                                 fig_title=f'{area}: S3-WFR Reflectance time-series from 2019-03-09 to 2020-03-31',
                                 save_title=save_file)

    # python tsgen.py "D:\processing\win\COARI" "D:\processing\win\coari-ts.csv" "D:\processing\win\coari-ts-plot.png"

{'20160228': 181.99,
 '20160228': 236.76,
 '20160228': 310.31,
 '20160228': 425.33,
 '20160228': 198.97,
 '20170206': 216.14,
 '20170206': 258.87,
 '20170206': 151.97,
 '20170410': 76.60,
 '20170410': 104.40,
 '20170410': 48.20,
 '20171006': 77.89,
 '20171006': 102.13,
 '20171006': 86.14,
 '20180203': 178.80,
 '20180203': 319.23,
 '20180203': 216.56,
 '20180316': 149.20,
 '20180316': 198.00,
 '20180316': 178.80,
 '20180316': 100.60,
 '20180426': 147.20,
 '20180426': 189.60,
 '20180426': 169.20,
 '20180426': 102.40,
 '20180525': 103.00,
 '20180525': 119.40,
 '20180525': 66.00,
 '20180525': 66.80,
 '20180614': 76.00,
 '20180614': 70.80,
 '20180614': 114.60,
 '20180614': 60.20,
 '20180722': 8.20,
 '20180722': 7.20,
 '20180722': 71.60,
 '20180722': 42.40,
 '20180904': 40.80,
 '20180904': 64.60,
 '20180904': 85.00,
 '20180904': 40.20,
 '20190214': 121.40,
 '20190214': 172.80,
 '20190214': 215.80,
 '20190214': 133.80,
 '20190312': 98.00,
 '20190312': 174.20,
 '20190312': 119.80,
 '20190312': 71.80,
 '20190421': 50.60,
 '20190421': 23.00,
 '20190421': 49.60,
 '20190421': 19.80,
 '20190517': 27.60,
 '20190517': 59.60,
 '20190517': 54.80,
 '20190517': 30.60,
 '20190621': 28.60,
 '20190621': 40.60,
 '20190621': 35.80,
 '20190621': 18.80,
 '20190718': 34.60,
 '20190718': 46.00}

vld_andre_rrs = {
05/12/17
05/12/17
05/12/17
05/12/17
05/12/17
05/12/17
05/12/17
05/12/17
05/12/17
05/12/17
05/12/17
05/12/17
05/12/17
05/12/17
05/12/17
05/12/17
05/12/17
05/12/17
05/12/17
05/12/17
05/12/17
05/12/17
05/12/17
05/12/17
05/12/17
05/12/17
05/12/17
05/12/17
05/12/17
05/12/17
05/12/17
05/12/17
05/12/17
14/02/19
14/02/19
14/02/19
14/02/19
14/02/19
14/02/19
14/02/19
14/02/19
14/02/19
14/02/19
14/02/19
14/02/19
14/02/19
14/02/19
14/02/19
14/02/19
14/02/19
14/02/19
14/02/19
14/02/19
14/02/19
14/02/19
14/02/19
14/02/19
14/02/19
14/02/19
14/02/19
14/02/19
14/02/19
14/02/19
14/02/19
14/02/19
13/03/19
13/03/19
13/03/19
13/03/19
13/03/19
13/03/19
13/03/19
13/03/19
13/03/19
13/03/19
13/03/19
13/03/19
13/03/19
13/03/19
13/03/19
26/04/18
26/04/18
26/04/18
26/04/18
26/04/18
26/04/18
26/04/18
26/04/18
26/04/18
26/04/18
26/04/18
26/04/18
26/04/18
26/04/18
26/04/18
26/04/18
26/04/18
26/04/18
26/04/18
26/04/18
26/04/18
26/04/18
26/04/18
26/04/18
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
21/04/19
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
25/05/18
17/05/19
17/05/19
17/05/19
17/05/19
17/05/19
17/05/19
17/05/19
17/05/19
17/05/19
17/05/19
17/05/19
17/05/19
17/05/19
17/05/19
17/05/19
17/05/19
17/05/19
17/05/19
17/05/19
17/05/19
17/05/19
17/05/19
17/05/19
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
14/06/18
04/09/18
04/09/18
04/09/18
04/09/18
04/09/18
04/09/18
04/09/18
04/09/18
04/09/18
04/09/18
04/09/18
04/09/18
04/09/18
04/09/18
04/09/18
04/09/18
04/09/18
04/09/18
04/09/18
04/09/18
04/09/18
04/09/18
04/09/18
04/09/18
04/09/18
04/09/18
04/09/18
04/09/18
04/09/18
04/09/18
04/09/18
04/09/18
04/09/18

}
