 #!/usr/bin/env Rscript
#imports 
library("getopt")
library("dplyr")

#the Compose function from the functional package
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


a<-as.data.frame(read.csv(input_paths[[1]]))

#loop through and load the dataframes into a list
#dfs <- lapply(X = input_paths, FUN = read.csv)
dfs <- lapply(X = input_paths, FUN = Compose(read.csv, as.data.frame))

#reformat so z is accessible
dfs <- lapply(X = dfs, FUN = function(df){
  df %>%
    group_by(X) %>%
    mutate(z1 = unlist(z_to_floats(z))[1],
           z2 = unlist(z_to_floats(z))[2]) %>%
    mutate(z = NULL)
           
  })


names(dfs) <- samples

saveRDS(dfs, file = opt$output_path)
