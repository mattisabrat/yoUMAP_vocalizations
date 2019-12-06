 #!/usr/bin/env Rscript
#imports 
library("getopt")

#the Compose function from the functional package
Compose <- function (...) {
    fs <- list(...)
    if (!all(sapply(fs, is.function))) 
        stop("Argument is not a function")
    function(...) Reduce(function(x, f) f(x), fs, ...)
}

#read in opts
spec <- matrix(c(
      'input_paths', 'i', 1, 'character',
      'output_path', 'o', 1, 'character',
      'nThreads',    'n', 1, 'integer'
      ), byrow=TRUE, ncol=4)
opt <- getopt(spec) 

#vectorize paths
input_paths <- as.list(strsplit(x = opt$input_paths, split = '__SPLIT__', fixed = TRUE)[[1]])

a<-as.data.frame(read.csv(input_paths[[1]]))

#loop through and load the dataframes into a list
#dfs <- lapply(X = input_paths, FUN = read.csv)
dfs <- lapply(X =input_paths, FUN = Compose(read.csv, as.data.frame))

names(dfs) <- c('1','2','3')

saveRDS(dfs, file = opt$output_path)
