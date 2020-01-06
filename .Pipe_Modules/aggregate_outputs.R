 #!/usr/bin/env Rscript
#imports 
library("getopt")
library("dplyr")

#Define functions-------------------------------------------------------------------------------------
#Compose function from the functional package,
Compose <- function (...) {
    fs <- list(...)
    if (!all(sapply(fs, is.function))) 
        stop("Argument is not a function")
    function(...) Reduce(function(x, f) f(x), fs, ...)
}

#define a function to format z coords
z_to_floats <- function(z_factor){
  #split based on the comma
  splits <- as.list(strsplit(x = as.character(z_factor),
                             split = ',',
                             fixed = TRUE)[[1]])
  
  #remove the brackets and convert
  z_floats <- c(as.numeric(gsub('[', '', splits[[1]], fixed=TRUE)),
                as.numeric(gsub(']', '', splits[[2]], fixed=TRUE))
                ) 
  return(z_floats)
}

#Function to reformat the seg_song paths
path_to_char <- function(path_factor){
  wav_path <- as.character(path_factor)
  wav_path <- gsub("['", '', wav_path, fixed=TRUE)
  wav_path <- gsub("']", '', wav_path, fixed=TRUE)
  return(wav_path)
}

#Given a seg song_path returns the orig_wav
get_orig_wav <- function(seg_song_path){
  csv_path <- gsub('wavs','csv', seg_song_path, fixed=TRUE)
  csv_path <- gsub('wav','csv', csv_path, fixed=TRUE)
  csv_path <- as.character(read.csv(csv_path, header=FALSE)$V2)
  return(csv_path)
}

#Map seg_songs to orig_wavs using a conversion table
map_to_orig <- function(seg_song_path, convert_df){
    mapping_row<-convert_df %>%
      filter(seg_song_paths==seg_song_path)
    return(as.character(mapping_row$orig_wav_paths[1]))
}

#Front end------------------------------------------------------------------------------------------
#read in opts
spec <- matrix(c(
      'input_paths', 'i', 1, 'character',
      'output_path', 'o', 1, 'character',
      'nThreads',    'n', 1, 'integer',
      'samples',     's', 1, 'character'
      ), byrow=TRUE, ncol=4)
opt <- getopt(spec) 

#vectorize paths
input_paths <- as.list(strsplit(x = opt$input_paths, split = '__SPLIT__', fixed = TRUE)[[1]])
samples     <- as.list(strsplit(x = opt$samples    , split = '__SPLIT__', fixed = TRUE)[[1]])

#loop through and load the dataframes into a list
#dfs <- lapply(X = input_paths, FUN = read.csv)
dfs <- lapply(X = input_paths, FUN = Compose(read.csv, as.data.frame))


#Build a dataframe to map syllables to their orig_wavs based on the seg_song column-------------------------
#get the unique paths
unique_path_lists  <- lapply(X = dfs, FUN = function(df){return(unique(df$original_wav))})
unique_path_lists  <- lapply(X = unique_path_lists, FUN = function(path_list){
  lapply(X = path_list, FUN = path_to_char)
})

unique_paths<-unlist(unique_path_lists, recursive = FALSE)
orig_wavs <- lapply(X = unique_paths, FUN = get_orig_wav)

#Flatten the nested lists and put them in a dataframe for easier handling
convert_table <- data.frame(seg_song_paths = as.character(unique_paths),
                            orig_wav_paths = as.character(orig_wavs))

#reformat---------------------------------------------------------------------------------------------------
dfs <- lapply(X = dfs, FUN = function(df){
  df %>% 
    group_by(X) %>%
    #split z into two cols
    mutate(z1 = unlist(z_to_floats(z))[1],
           z2 = unlist(z_to_floats(z))[2]) %>%
    
    #convert paths to strings
    mutate(seg_song_wav = path_to_char(original_wav)) %>%
    
    #Get the orig_wavs
    mutate(orig_wav = map_to_orig(seg_song_wav, convert_table))%>%
    
    #Delete undeeded cols
    mutate(z  = NULL,
           day_num = NULL,
           original_wav = NULL,
           syllable_time = NULL) 
})

#apply sample names
names(dfs) <- samples

#Save it--------------------------------------------------------------------------------------------------
saveRDS(dfs, file = opt$output_path)
