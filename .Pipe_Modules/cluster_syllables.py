#!/usr/bin/env/python3

#imports
import getopt
import sys
from os import path

#Front end
opts, args = getopt.getopt(sys.argv[1:], 'i:o:n:s:')

for opt, arg in opts:
    if   opt in ('-i'): input_path    = str(arg)
    elif opt in ('-o'): output_path   = str(arg)
    elif opt in ('-n'): nThreads      = int(arg)
    elif opt in ('-s'): name          = str(arg)
    
#
