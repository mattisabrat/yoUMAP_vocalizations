#!/usr/bin/env bash

#This script sets up paths, reads flags, handles incorrect usage, and executes the pipeline file

#--------------------------------------------------------------------------
#Set up the Path so that all aspects of the pipeline are invocable
#Setting the path within the pipeline instead of within the environment
#adds portability and prevents user error. 
#Make sure you put your paths at the front of $PATH not the end
#--------------------------------------------------------------------------

PATH=$(getconf PATH)
java_dir="$(which java)"
java_dir=${java_dir%java}
export PATH="$java_dir":$PATH
export PATH=$PWD/.bin/bds:$PATH
export PATH=$PWD/.bin/R/bin:$PATH
export PATH=$PWD/.bin/Python/bin:$PATH
export PYTHONPATH=$PWD/.bin/Python/bin:$PYTHONPATH


#-------------------------------------------------------------------------
#Read in flags 
#Experimental Directory supplied on the mandatory -e flag
#Threads per task supplied on the -n flag, defaults to 1
#Override default flags with user supplied flags using -f
#-------------------------------------------------------------------------

Provided_Dir=false
mode=1
nThreads=1
config=$PWD/.Defaults.config

while getopts ':e:n:m:c:' flag; do
  case "${flag}" in
    e) Provided_Dir=true; Experiment="${OPTARG}";;  #mandatory flag
    n) nThreads="${OPTARG}" ;;
    m) mode="${OPTARG}";;
    c) config="${OPTARG}";;
  esac
done

#Handle incorrect -e usage
if [ "${Provided_Dir}" = false ]; then 
	echo "ERROR: Pipeline requires -e Experimental Directory"
	exit 1
elif [ ! -d "${Experiment}" ]; then
    echo "ERROR: Provided Experimental Directory doesn't exist"
    exit 2
else
	echo "Running ${Experiment}"
fi 

#--------------------------------------------------------------------------
#Execute the pipeline on the specified directory
#--------------------------------------------------------------------------
bds -c $PWD/.bin/bds/bds.config ./.yoUMAP_vocalizations.bds -e ${Experiment}  -n ${nThreads} -m ${mode}
