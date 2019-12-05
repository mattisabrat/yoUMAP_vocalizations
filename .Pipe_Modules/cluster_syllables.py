#!/usr/bin/env/python3

#imports
from IPython.display import clear_output
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import os
import sys
from tqdm import tqdm_notebook as tqdm
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from skimage.transform import resize
from sklearn.externals.joblib import Parallel, delayed
import hdbscan 
import umap
import logging
from datetime import datetime
import getopt
import configparser

#AVGN imports
from avgn.network_analysis.network_analysis import cluster_data, split_times_into_seqs, syllables_to_sequences, draw_transition_diagram
from avgn.network.training import load_from_hdf5

#Define necessary functions
#function which takes the contents of the hdf files and appends the syllable and sequence dataframes from that file onto provided lists. For parrallelization.

##Front end
#Read opts
opts, args = getopt.getopt(sys.argv[1:], 'i:o:n:s:c:m:p:')

for opt, arg in opts:
    if   opt in ('-i'): hdf_list      = str(arg)
    elif opt in ('-o'): syllable_path = str(arg)
    elif opt in ('-p'): sequence_path = str(arg)
    elif opt in ('-n'): nThreads      = int(arg)
    elif opt in ('-s'): animal        = str(arg)
    elif opt in ('-c'): config_path   = str(arg)
    elif opt in ('-m'): mode          = str(arg)

#Split the input list into a vecotr we can iterate on
hdf_list = hdf_list.split('__SPLIT__')


##Read in params
#define our config file
config = configparser.ConfigParser(strict=False)
config.read(config_path)

#Read the config
cluster_pct    = float(config.get('cluster_syllables', 'cluster_fraction'))
min_syls       = int(  config.get('cluster_syllables', 'min_syllables'))
resize_dim     = int(  config.get('cluster_syllables', 'resize_dim'))
n_neighbors    = int(  config.get('cluster_syllables', 'n_neighbors'))
min_dist       = float(config.get('cluster_syllables', 'min_dist'))
n_components   = int(  config.get('cluster_syllables', 'n_components'))
random_state   = int(  config.get('cluster_syllables', 'random_state'))
max_timedelta  = float(config.get('sequence_syllables', 'max_timedelta'))
seq_len_cutoff = int(  config.get('sequence_syllables', 'seq_len_cutoff'))

#define the hdf fields
to_load     = ['spectrograms', 'lengths', 'start', 'wav_file', 'syll_start_rel_wav']

#load the hdfs into a list then convert to dataframe
hdf_content_list = [load_from_hdf5([hdf_loc], to_load) for hdf_loc in hdf_list]
hdf_content_list = [pd.DataFrame({
        'spectrograms':       contents['spectrograms'].tolist(), 
        'syllable_time':     [datetime.strptime(i[0], '%d/%m/%y %H:%M:%S.%f') for i in contents['start'].astype('str').tolist()] , 
        'syll_length_s':      contents['lengths'].tolist(), 
        'start_time_rel_wav': contents['syll_start_rel_wav'].tolist(), 
        'original_wav':       contents['wav_file'].tolist(), 
        'animal':             contents['name'].tolist()    
    }) for contents in hdf_content_list]

#merge the conent of the dataframes in the list
#handles the experiment level clustering
hdf_content = pd.concat(hdf_content_list)
#Handle the not enough syllables case
if ( len(hdf_content['animal']) < min_syls):
    logging.error('%s has %s syllables,  min is %s , will not cluster.' %
                  (animal, len(hdf_content['animal']), min_syls,))
    sys.exit(1)
# embed spectrograms in low dim space
#resize
x = np.asarray(hdf_content['spectrograms'])
x_small = [resize(np.asarray(i), [16,16]) for i in x]
x_small = np.array(x_small).reshape((len(x_small), np.prod(np.shape(x_small)[1:])))
x_small = [(i*255).astype('uint8') for i in x_small]

#embed
hdf_content['z'] = umap.UMAP(
    n_neighbors  = n_neighbors,
    min_dist     = min_dist,
    n_components = n_components,
    random_state = random_state,
).fit_transform(x_small).tolist()

#Convert the spectrograms to a list for consistency

#define min num of syls per cluster
min_cluster_size = int(len(hdf_content['animal'])*cluster_pct)

#cluster z
hdf_content['labels'] = cluster_data(np.array(list(hdf_content.z.values)),
                                 hdbscan.HDBSCAN,
                                 (),
                                 {'min_cluster_size':min_cluster_size,  'min_samples':1},
                                 verbose = False)

#Document the fraction that went unclustered
frac_unlabelled = np.sum(hdf_content['labels'] == -1)/len(hdf_content['labels'])
logging.info('%s had %s/1 of syllables unlabelled' % (animal, frac_unlabelled,))
    
#Add sequence info to the dataframe
content = split_times_into_seqs(hdf_content, max_timedelta, seq_len_cutoff)

#Create dataframe of sequences
seq_content = syllables_to_sequences( hdf_content, ['labels','z','original_wav',
                                                 'spectrograms','start_time_rel_wav',
                                                 'syll_length_s']).rename(columns={
                                                     'labels': 'sequence'
                                                         })
seq_content['lens'] = [len(i) for i in seq_content.sequence.values]


#save the dataframes
hdf_content.to_csv(syllable_path)
seq_content.to_csv(sequence_path)
