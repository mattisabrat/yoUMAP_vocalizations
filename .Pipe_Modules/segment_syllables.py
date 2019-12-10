#!/usr/bin/env/python3
 
#Imports
from scipy.io import wavfile
import numpy as np
import matplotlib.pyplot as plt
from glob import glob
import pandas as pd
from datetime import datetime, timedelta
import os
import sys
import IPython.display
import pickle
from sklearn.externals.joblib import Parallel, delayed
from PIL import Image
import hdbscan 
from skimage.transform import resize
import umap
import time 
import seaborn as sns
import getopt
import configparser
import warnings 
warnings.filterwarnings('ignore')

#AVGN Imports
from avgn.segment_song.preprocessing import *
import avgn.segment_song.wav_to_syllables as w2s
import avgn.spectrogramming.spectrogramming as sg


##Front end
#Read opts
opts, args = getopt.getopt(sys.argv[1:], 'i:o:n:s:c:')

for opt, arg in opts:
    if   opt in ('-i'): wav_list    = str(arg)
    elif opt in ('-o'): output_path = str(arg)
    elif opt in ('-n'): nThreads    = int(arg)
    elif opt in ('-s'): name        = str(arg)
    elif opt in ('-c'): config_path = str(arg)

#Split the input_paths into vectors we can iterate on
wav_list  = wav_list.split('__SPLIT__')

##Read in params
#define our config file
config = configparser.ConfigParser(strict=False, allow_no_value=True)
config.read(config_path)

#Read the config into the dictionary
syll_size = int(  config.get('segment_syllables', 'syll_size'))
param_dict = {
    'species': str(config.get('segment_syllables', 'species')),
    
    # filtering
    'highcut': float(config.get('segment_syllables', 'highcut')),
    'lowcut' : float(config.get('segment_syllables', 'lowcut')),
    
    # spectrograms
    'mel_filter'          : bool( config.get('segment_syllables', 'mel_filter')), 
    'num_mels'            : syll_size,
    'num_freq'            : int(  config.get('segment_syllables', 'num_freq')), 
    'num_freq_final'      : syll_size, 
    'sample_rate'         : float(config.get('segment_syllables', 'sample_rate')), 
    'preemphasis'         : float(config.get('segment_syllables', 'preemphasis')), 
    'min_silence_for_spec': float(config.get('segment_syllables', 'min_silence_for_spec')), 
    'frame_shift_ms'      : float(config.get('segment_syllables', 'frame_shift_ms')),
    'frame_length_ms'     : float(config.get('segment_syllables', 'frame_length_ms')),
    'min_level_db'        : float(config.get('segment_syllables', 'min_level_db')),
    'spec_thresh_min'     : float(config.get('segment_syllables', 'spec_thresh_min')),
    'spec_thresh_delta'   : float(config.get('segment_syllables', 'spec_thresh_delta')),
    'ref_level_db'        : float(config.get('segment_syllables', 'ref_level_db')),
    'sample_rate'         : float(config.get('segment_syllables', 'sample_rate')), 
    'fmin'                : float(config.get('segment_syllables', 'fmin')), 
    #'fmax'                : float(config.get('segment_syllables', 'fmax')),
    'fmax': None,
    
    # Vocal Envelope
    'smoothing'      : str(  config.get('segment_syllables', 'smoothing')),
    'envelope_signal': str(  config.get('segment_syllables', 'envelope_signal')), 
    'gauss_sigma_s'  : float(config.get('segment_syllables', 'gauss_sigma_s')),
    'FOI_min'        : int(  config.get('segment_syllables', 'FOI_min')), 
    'FOI_max'        : int(  config.get('segment_syllables', 'FOI_max')), 
    
    # Silence Thresholding
    'silence_threshold': float(config.get('segment_syllables', 'silence_threshold')), 
    'min_len'          : float(config.get('segment_syllables', 'min_len')),
    'power_thresh'     : float(config.get('segment_syllables', 'power_thresh')), 
    
    # Syllabification
    'min_syll_len_s'   : float(config.get('segment_syllables', 'min_syll_len_s')), 
    'segmentation_rate': float(config.get('segment_syllables', 'segmentation_rate')),
    'threshold_max'    : float(config.get('segment_syllables', 'threshold_max')),
    'min_num_sylls'    : int(  config.get('segment_syllables', 'min_num_sylls')), 
    'slow_threshold'   : float(config.get('segment_syllables', 'slow_threshold')),
    'max_size_syll'    : syll_size,
    'resize_samp_fr'   : int(syll_size*5.0),
    
    # Sencond pass syllabification
    'second_pass_threshold_repeats': int(config.get('segment_syllables', 'second_pass_threshold_repeats')), 
    'ebr_min'       : float(config.get('segment_syllables', 'ebr_min')), 
    'ebr_max'       : float(config.get('segment_syllables', 'ebr_max')), 
    'max_thresh'    : float(config.get('segment_syllables', 'max_thresh')), 
    'thresh_delta'  : float(config.get('segment_syllables', 'thresh_delta')), 
    'slow_threshold': float(config.get('segment_syllables', 'slow_threshold')), 
    'pad_length'    : syll_size, 
    
    # spectrogram inversion
    'max_iters'        : int(  config.get('segment_syllables', 'max_iters')),
    'griffin_lim_iters': int(  config.get('segment_syllables', 'griffin_lim_iters')),
    'power'            : float(config.get('segment_syllables', 'power')),

    # Thresholding out noise
    'mel_noise_filt': float(config.get('segment_syllables', 'mel_noise_filt'))
}

#Define a mel basis from these params
_mel_basis = sg._build_mel_basis(param_dict)

#Init lists for the data
key_list = (
            'wav_file', # Wav file that the syllable came from
            'spectrograms', # spectrogram of syllable
            'starts', # time that this syllable occured
            'start_rel_to_file', # time relative to bout file that this 
            'lengths' # length of the syllable
           ) 
animal_data = {key : [] for key in key_list}
#Parallelize across files
with Parallel(n_jobs=nThreads, verbose=0) as parallel:
    animal_data_packed = parallel(
        delayed(w2s.process_bout)(wav_file,_mel_basis,hparams=param_dict,
                                  submode=True, visualize = False) 
            for wav_file in wav_list)
        
#Reformat the data
for dtype, darray in zip(key_list, list(zip(*animal_data_packed))):
    [animal_data[dtype].extend(element) for element in darray] 
    animal_data[dtype] = np.array(animal_data[dtype])

#Save the data
w2s.save_dataset(output_path, 
                 animal_data['spectrograms'], 
                 animal_data['starts'].astype('object'),
                 animal_data['lengths'], 
                 animal_data['wav_file'].astype('object'),
                 animal_data['start_rel_to_file'],
                 name
                 )
