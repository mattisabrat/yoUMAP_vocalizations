#!/usr/bin/env bash

##---------------------------------------------------------------------
# Handle everything that needs to be compiled
# wget 
# tar 
# configure 
# make 
# rm 
##---------------------------------------------------------------------
#Save the head directory path
BasePath="$( cd "$(dirname "$0")" ; pwd -P )"

#echo "installing R \n\n"
#First R
wget http://cran.r-project.org/src/base/R-3/R-3.6.1.tar.gz
tar -xzf R-3.6.1.tar.gz
cd R-3.6.1/
./configure --prefix $BasePath/.bin/R
make && make install
cd $BasePath
rm R-3.6.1.tar.gz
rm -rf R-3.6.1/

#echo "installing Python \n\n"
#Next Python
wget https://www.python.org/ftp/python/3.7.3/Python-3.7.3.tgz 
tar -xzf Python-3.7.3.tgz 
cd Python-3.7.3/
./configure --prefix $BasePath/.bin/Python
make && make install
cd $BasePath
rm Python-3.7.3.tgz
rm -rf Python-3.7.3/


##---------------------------------------------------------------------
# Execute the package installing scripts in R and Python
##---------------------------------------------------------------------
#Set up necessary path variables for the package installer scripts
export PATH=$BasePath/.bin/R/bin:$PATH
export PATH=$BasePath/.bin/Python/bin:$PATH

#Execute the package installer scripts
Rscript --vanilla $BasePath/.Install_Scripts/R_packages.R
.$BasePath/.Install_Scripts/Python_packages.sh 


##---------------------------------------------------------------------
# Self Destruct
##---------------------------------------------------------------------
mv $0 .Install.sh
