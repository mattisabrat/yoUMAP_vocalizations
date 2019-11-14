#!/usr/bin/env/python3
 
#Imports
from scipy.io import wavfile
import numpy as np
import matplotlib.pyplot as plt
%matplotlib inline
from glob import glob
import pandas as pd
from datetime import datetime, timedelta
import os
import sys
import IPython.display
import pickle
from sklearn.externals.joblib import Parallel, delayed
from PIL import Image

import warnings 
warnings.filterwarnings('ignore')

#AVGN Imports
from avgn.segment_song.preprocessing import *
import avgn.segment_song.wav_to_syllables as w2s
import avgn.spectrogramming.spectrogramming as sg


##Front end
#Read opts
opts, args = getopt.getopt(sys.argv[1:], 'i:m:o:n:s:c:e:')

for opt, arg in opts:
    if   opt in ('-i'): wav_list    = str(arg)
    elif opt in ('-m'): csv_list    = str(arg)
    elif opt in ('-o'): output_path = str(arg)
    elif opt in ('-n'): nThreads    = int(arg)
    elif opt in ('-s'): name        = str(arg)
    elif opt in ('-c'): config_path = str(arg)
    elif opt in ('-e'): dset        = str(arg)

#Split the input_paths into vectors we can iterate on
wav_paths = wav_list.split('__SPLIT__')
csv_paths = csv_list.split('__SPLIT__')

##Read in params
#define our config file
config = configparser.ConfigParser()
config.read(config_path)
#Read the config into the dictionary
param_dict = {}
param_dict[dset] = {
    {
    'species': dset,
    # filtering
    'highcut':15000,
    'lowcut':500,
    
    # spectrograms
    'mel_filter': True, # should a mel filter be used?
    'num_mels':syll_size, # how many channels to use in the mel-spectrogram
    'num_freq':512, # how many channels to use in a spectrogram 
    'num_freq_final': syll_size, # how many channels to use in the resized spectrogram
    'sample_rate':44100, # what rate are your WAVs sampled at?
    'preemphasis':0.97, 
    'min_silence_for_spec': 0.5, #minimum length of silence for a spectrogram to be considered a good spectrogram
    'frame_shift_ms':0.5, # step size for fft
    'frame_length_ms':6, # frame length for fft
    'min_level_db':-95, # minimum threshold db for computing spe 
    'spec_thresh_min': -40, # (db)
    'spec_thresh_delta': 5, # (db) what 
    'ref_level_db':20, # reference db for computing spec
    'sample_rate':44100, # sample rate of your data
    'fmin': 300, # low frequency cutoff for mel filter
    'fmax': None, # high frequency cutoff for mel filter
    
    # Vocal Envelope
    'smoothing' : 'gaussian', # 'none', 
    'envelope_signal' : "spectrogram", # spectrogram or waveform, what to get the vocal envelope from
    'gauss_sigma_s': .0001,
    'FOI_min': 4, # minimum frequency of interest for vocal envelope (in terms of mel)
    'FOI_max': 24, # maximum frequency of interest for vocal envelope (in terms of mel)
    
    # Silence Thresholding
    'silence_threshold' : 0, # normalized threshold for silence
    'min_len' : 5., # minimum length for a vocalization (fft frames)
    'power_thresh': .3, # Threshold for which a syllable is considered to be quiet weak and is probably noise

    # Syllabification
    'min_syll_len_s' : 0.03, # minimum length for a syllable
    'segmentation_rate': 0.0,#0.125, # rate at which to dynamically raise the segmentation threshold (ensure short syllables)
    'threshold_max': 0.25,
    'min_num_sylls': 20, # min number of syllables to be considered a bout
    'slow_threshold':0.0,#0.02, # second slower threshold
    'max_size_syll': syll_size, # the size of the syllable
    'resize_samp_fr': int(syll_size*5.0), # (frames/s) the framerate of the syllable (in compressed spectrogram time components)
    
    # Sencond pass syllabification
    'second_pass_threshold_repeats':50, # the number of times to repeat the second pass threshold
    'ebr_min': 0.05, # expected syllabic rate (/s) low 
    'ebr_max':  0.2, # expected syllabic rate (/s) high 
    'max_thresh':  0.02, # maximum pct of syllabic envelope to threshold at in second pass
    'thresh_delta':  0.005, # delta change in threshold to match second pass syllabification
    'slow_threshold': 0.005, # starting threshold for second pass syllabification
    
    'pad_length' : syll_size, # length to pad spectrograms to 
    
    # spectrogram inversion
    'max_iters':200,
    'griffin_lim_iters':60,
    'power':1.5,

    # Thresholding out noise
    'mel_noise_filt' : 0.15, # thresholds out low power noise in the spectrum - higher numbers will diminish inversion quality
}
    }
