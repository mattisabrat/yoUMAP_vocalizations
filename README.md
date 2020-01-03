# yoUMAP_vocalizations
Automated and parallelized pipeline for segmentation, dimesionality reduction, and clustering of animal vocalizations.

## What does it do?
This pipeline uses [BigDataScript (BDS)](https://pcingola.github.io/BigDataScript/) to wrap the [Animal Vocalization Generative Network (AVGN)](https://github.com/timsainb/AVGN) segmentation, [Uniform Manifold Approximation and Projection (UMAP)](https://umap-learn.readthedocs.io/en/latest/) dimensionality redction, and [Hierarchical Density-Based Spatial Clustering of Applications with Noise (HDBSCAN)](https://hdbscan.readthedocs.io/en/latest/) clustering workflow from the AVGN example notebooks. This workflow is used extensively throughout this [awesome preprint](https://www.biorxiv.org/content/10.1101/870311v1) from [Tim Sainburg](https://github.com/timsainb) of the [Gentner Lab](https://github.com/gentnerlab). 

## Credit Where Credit is Due
This pipeline is a wrapper for awesome code other people wrote and which I had no part in developing. Check them out:
* [AVGN](https://github.com/timsainb/AVGN)
* [umap-learn](https://umap-learn.readthedocs.io/en/latest/)
* [HDBSCAN](https://hdbscan.readthedocs.io/en/latest/)

## System Prerequisites
* Should work on any Linux or Mac capable of running Java. I have it running locally on Ubuntu 19.10 (Eoan) and Red Hat Enterprise Linux Server 7.2 (Maipo) on the cluster.
* Java - required for [BDS](https://pcingola.github.io/BigDataScript/)

## Installation - Local Machine
Super easy, it self deploys. Give it like 30 minutes:

      git clone https://github.com/mattisabrat/yoUMAP_vocalizations.git
      cd yoUMAP_vocalizations
      ./Install.sh
      

## Installation - Cluster Environment
Maybe not SUPER easy, but still pretty easy as far as cluster implementations go. 
* Follow the directions for local installation
* Edit the bds config file found at *yoUMAP_vocalizations/.bin/bds/bds.config* according the appropriate [BDS docs on Cluster Options](https://pcingola.github.io/BigDataScript/manual/site/bdsconfig/#cluster-options) for your cluster environment
  * Generic cluster scripts for some common environments can be found on the [BDS github](https://github.com/pcingola/BigDataScript/tree/master/config)
  * I included the scripts I use to interface with SLURM in *yoUMAP_vocalizations/.bin/bds_clusterGeneric_SLURM/*

## Usage

      ./yoUMAP_vocalizations -e /Path/to/Experimental/Directory/ -n Threads_per_Task -c Path/to/Config/File

* -n: Defaults to 1
  * For more information on task structure and thread allocation, see **Resource Usage and Parallelization** below
* -c: Defaults to  *yoUMAP_vocalizations/Defaults.config*

## Input Structure / Experimental Directory Formatting
Your *Experimental_Directory/* must be correctly formatted for the pathway to run. The *Experimental_Directory/* must contain a sudirectory *Experimental_Directory/Raw_Inputs/*. *Raw_Inputs/* should contain a subdirectory for each sample, lets call them *sample_folder/* s, with the sample's name as the *sample_folder/* name. This *sample_folder/* name will be taken by the pipeline as the sample's name in the output. Each sample_folder should contain all the **.wav** files associated with that sample. **The *sample_folder/* name CANNOT include *"wav"*.** It will break the code, so don't do it. I don't feel rewriting  that step without regular expressions.

### Example
* Experimental_Directory/
  * Raw_Inputs/
    * Bird_1/
      * 1.wav
      * 2.wav
      * ...
    * .../

## Output Structure 
The final output of the pipeline can be found at */Experimental_Directory/yoUMAPped_syllables.rds*. 

### Example
* Experimental_Directory/
  * Raw_Inputs/
  * Segmented_Songs/
    * Bird_1/
      * song_chk.txt
      * Bird_1/
        * wavs/
          * 1000-01-01_00-00-00-000000.wav
          * ...
        * specs/
          * 1000-01-01_00-00-00-000000.png
          * ...
        * csv/
          * 1000-01-01_00-00-00-000000.csv
          * ...
    * .../
  * Segmented_Syllables/
    * Bird_1/
      * Bird_1_segmented_syllables.hdf5
    * .../
  * Clustered_Syllables/
    * Bird_1/
      * Bird_1_clustered_syllables.csv
    * .../
  * yoUMAPped_syllables.rds

## Getting Up and Running in R
The output data can be loaded into R using:
      
      syll_tbls <- readRDS('Path/To/Experimental_Directory/yoUMAPped_syllables.rds')
      
This produces a named list of [tibbles](https://tibble.tidyverse.org/) with the following column names:

     names(syll_tbls[['Bird_1']])

     [1] "spectrograms"       "syll_length_s"      "start_time_rel_wav" "animal"             "labels"             "sequence_syllable"  "sequence_num"      
     [8] "z1"                 "z2"                 "seg_song_wav"       "orig_wav"                   

* spectrograms : Matrix of the spectrogram as a Factor. Can be converted to matrix, see **Functions**
* syll_length_s : Length of syllable in seconds
* start_time_rel_wav : Start time of syllable within *seg_song_wav*
* animal : Animal name, same as list element name, inherited from the *sample_folder/* name
* labels : HDBSCAN assigned cluster label, -1 is unassigned
* sequence_syllable : Syllable's ordinal position within it's sequence
* sequence_number : Sequence identifier
* z1 : Component 1 of syllable's representation in low dimensional space 
* z2 : Component 2 of syllabel's representation in low dimensional space
* seg_song_wav : Location of the segmented song containing the syllable
* orig_wav : Location of raw input containing the syllable

### Functions
To load the supplied R functions, run:

      source('/Path/to/yoUMAP_vocalizations/.bin/r_functions.R')
 
 #### Descriptions
      
      image_spectrogram(spectrogram_as_factor,show=TRUE)
* Returns the input spectrogram as a matrix 
* Displays the spectrogram if show=TRUE

      sample_cluster(syll_tbl, cluster_label, n, r_seed=42, show=TRUE)
* Returns n randomly sampled spectrograms from cluster_label in syll_tbl as matrices
* Displays the spectrograms if show=TRUE
* Set the random seed with r_seed

      scatter_clusters(syll_tbl, show=TRUE, size=0.5, alpha=1, filter_unlabled=TRUE)
* Scatter plot of syllables in low dimensional space, colored by syll_tbl$labels

      line_seqs <- function(syll_tbl, show=TRUE, alpha=0.05)
* Line plot of syllable sequences in low dimensional space

### Data processing using lapply
I intentionally made the output a list of tibble to simplify data processing across all samples using lapply in combination with the tidyverse. For example:

      lapply(X=syll_tlbs, FUN=scatter_clusters)
      
returns the scatter plots for all samples in the list. Similarly:
      
      library('dplyr')
      syll_tbls <- lapply(X=syll_tbls, FUN=function(syll_tbl){
          new_syll_tbl <- syll_tbl %>%
              mutute(new_col = some_function(z1,z2))
          return(new_syll_tbl)
      })

Adds a column, "new_col" to all tibbles in syll_tlbs. This "new_col" is some_function of the syllable's position in low dimenstional space. This could also be used to map additional experimental variables such as "days_post_lesion" or "optogenetic_state" using the orig_wav column.

## To Do
  * Animal level clustering
  * Include test files and an automatic test upon install
  * Turn the R functions into a proper R package. Does that have to be its own repo?
  * Figure out exactly how to assist users in tuning the segmentation parameters. Probably a jupyter notebook capable of writing out to the config file.

