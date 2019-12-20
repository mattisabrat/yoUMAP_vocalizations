#!/usr/bin/env/python3

#system imports
import getopt
import sys
from os import path
import numpy as np
import sys
import os
from tqdm import tqdm_notebook as tqdm
from glob import glob
import re 
from datetime import datetime as dt
import pandas as pd 
from sklearn.externals.joblib import Parallel, delayed
import configparser

#avgn imports
from avgn.segment_song.preprocessing import *
import avgn.segment_song.preprocessing as pp


##Front end
#Read opts
opts, args = getopt.getopt(sys.argv[1:], 'i:o:n:s:c:')

for opt, arg in opts:
    if   opt in ('-i'): wav_list    = str(arg)
    elif opt in ('-o'): output_path = str(arg)
    elif opt in ('-n'): nThreads    = int(arg)
    elif opt in ('-s'): sample      = str(arg)
    elif opt in ('-c'): config_path = str(arg)

#Split the input_paths and animal names into vectors
wav_list     = wav_list.split('__SPLIT__')
animal_names = [sample] * len(wav_list)

#Create the vecotr of elast edited time.
wav_times = []
n_no_date = 0
for wav_file in wav_list:
        # default give up method
        dt = datetime(1000, 1, 1, 0, 0) + timedelta(days=n_no_date)
        n_no_date+=1
        wav_times.append(dt)    
        


# Make a pandas dataframe with the file paths, date_times, and names 
wav_df = pd.DataFrame.from_dict({'filename': wav_list,
                                 'wav_time': wav_times,
                                 'name': animal_names})

##Read in params
#define our config file
config = configparser.ConfigParser(strict=False, allow_no_value=True)
config.read(config_path)

#Read the config into the dictionary
param_dict = {
    # Filtering and padding
    'lowcut' : float(config.get('segment_songs', 'lowcut')), 
    'highcut': float(config.get('segment_songs', 'highcut')),

    'rms_window'     : float(config.get('segment_songs', 'rms_window')), 
    'rms_stride'     : float(config.get('segment_songs', 'rms_stride')), 
    'noise_thresh'   : float(config.get('segment_songs', 'noise_thresh')), 
    'segment_padding': float(config.get('segment_songs', 'segment_padding')), 
    'rms_padding'    : float(config.get('segment_songs', 'rms_padding')), 
   
    'min_amp_val'         : float(config.get('segment_songs', 'min_amp_val')), 
    'min_segment_length_s': float(config.get('segment_songs', 'min_segment_length_s')), 
    'max_segment_length_s': float(config.get('segment_songs', 'max_segment_length_s')), 
    'min_silence_pct'     : float(config.get('segment_songs', 'min_silence_pct')),  

    #FFT (we create a spectrogram here to filter out noise)
    'num_freq'        : int(  config.get('segment_songs', 'num_freq')), 
    'sample_rate'     : int(  config.get('segment_songs', 'sample_rate')), 
    'preemphasis'     : float(config.get('segment_songs', 'preemphasis')), 
    'ref_level_db'    : float(config.get('segment_songs', 'ref_level_db')), 
    'min_level_db'    : float(config.get('segment_songs', 'min_level_db')),
    'max_power_f_min' : float(config.get('segment_songs', 'max_power_f_min')),
    'frame_shift_ms'  : float(config.get('segment_songs', 'frame_shift_ms')), 
    'frame_length_ms' : float(config.get('segment_songs', 'frame_length_ms')), 
    
    #Filter based upon power-frequency envelope
    'vocal_freq_min' : float(config.get('segment_songs', 'vocal_freq_min')),
    'vocal_freq_max' : float(config.get('segment_songs', 'vocal_freq_max'))
    }


#Segment the files
with Parallel(n_jobs=nThreads, verbose=0) as parallel:
    parallel(
        delayed(pp.process_bird_wav)(row['name'], 
                                     row['filename'],
                                     row['wav_time'],
                                     param_dict,
                                     output_path,
                                     verbose = False,
                                     visualize= False,
                                     skip_created= True,
                                     save_spectrograms= True) 
            for idx, row in wav_df.iterrows())
