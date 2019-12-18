# yoUMAP_vocalizations
Automated and parallelized pipeline for segmentation, dimesionality reduction, and clustering of animal vocalizations.

## What does it do?
This pipeline uses [BigDataScript (BDS)](https://pcingola.github.io/BigDataScript/) to wrap the [Animal Vocalization Generative Network (AVGN)](https://github.com/timsainb/AVGN) segmentation, [Uniform Manifold Approximation and Projection (UMAP)](https://umap-learn.readthedocs.io/en/latest/) dimensionality redction, and [Hierarchical Density-Based Spatial Clustering of Applications with Noise (HDBSCAN)](https://hdbscan.readthedocs.io/en/latest/) clustering workflow from the AVGN example notebooks. This workflow is used extensively throughout this [awesome preprint](https://www.biorxiv.org/content/10.1101/870311v1) from [Tim Sainburg](https://github.com/timsainb) of the [Gentner Lab](https://github.com/gentnerlab). 

## Credit Where Credit is Due
This pipeline is a wrapper for awesome code other people wrote and which I had no part in developing. Check them out:
* [AVGN](https://github.com/timsainb/AVGN)
* [umap-learn](https://umap-learn.readthedocs.io/en/latest/)
* [HDBSCAN](https://hdbscan.readthedocs.io/en/latest/)

## Prerequisites
* Java - required for [BDS](https://pcingola.github.io/BigDataScript/)

## Installation - Local Machine
Super easy, it self deploys. Give it like 30 minutes:

      git clone https://github.com/mattisabrat/yoUMAP_vocalizations.git
      cd yoUMAP_vocalizations
      ./Install.sh
      

## Installation - Cluster Environment
Maybe not SUPER easy, but still pretty easy as far as cluster implementations go. 
* Follow the directions for local installation
* Edit the bds config file found at yoUMAP_vocalizations/.bin/bds/bds.config according the appropriate [BDS docs on Cluster Options](https://pcingola.github.io/BigDataScript/manual/site/bdsconfig/#cluster-options) for your cluster environment
  * Generic cluster scripts for some common environments can be found on the [BDS github](https://github.com/pcingola/BigDataScript/tree/master/config)
  * I included the scripts I use to interface with SLURM in yoUMAP_vocalizations/.bin/bds_clusterGeneric_SLURM/

## Usage

      ./yoUMAP_vocalizations -e $Path_to_Experimental_Directory -n $Threads_per_Task -c Path_to_Config_File

## Input Structure / Experimental Directory Formatting

## Output Structure / Getting Up and Running in R

## Configuration
This is where the beast lives. 

## Tuning Segmentation

## Tests

