#Given a spectrogram as a factor, returns the matrix and produces the image
image_spectrogram <- function(spectrogram_as_factor,show=TRUE){
  #split based on the comma
  splits <- as.list(strsplit(x = as.character(spectrogram_as_factor),
                             split = '], [',
                             fixed = TRUE)[[1]])
  
  #remove the brackets and convert to numeric
  splits <- lapply(X = splits,
                   FUN = function(r){
                       r <- gsub('[[', '', r, fixed=TRUE)
                     r <- gsub(']]', '', r, fixed=TRUE)
                     r <- strsplit(x=r, split=',', fixed=TRUE)
                     r <- unlist(lapply(X=r, FUN=as.numeric))
                     return(r)}
  )
  #build the matrix
  spec <- (do.call(cbind,splits))
  
  #return the spectrogram
  if (show) {image(spec, useRaster=TRUE, axes=FALSE, col=hcl.colors(max(spec)))}
  return(spec)
}

#Returns n spectrogram images sampled randomly from cluster_label
sample_cluster <- function(syll_tbl, cluster_label, n, r_seed=42, show=TRUE){
  require('dplyr')
  #Set random seed
  set.seed(r_seed)
  
  #Filter for the cluster
  df <- syll_tbl %>%
    filter(labels == cluster_label)
  
  #Randomly sample
  df2 <-df[runif(n,1,nrow(df)), ]

  #Get spectrogrms
  specs <- lapply(X=as.list(df2$spectrograms), FUN=image_spectrogram, show=show)
}

#Scatter plot, Color is cluster label
scatter_clusters <- function(syll_tbl, show=TRUE, size=0.5, alpha=1, filter_unlabled=TRUE){
  require('ggplot2')
  require('dplyr')
  
  #Get name
  if (length((unique(syll_tbl$animal)))>1) {
    plt_ttl <- 'All_Samples'
  }else {
    plt_ttl <- as.character(syll_tbl$animal[1])
  }
  
  #Filter unlabeled sylls
  if (filter_unlabled){
    df <- syll_tbl %>%
      filter(labels>=0)
  }else{
    df <- syll_tbl
  }
  
  
  #plot
  plt <- ggplot(data = df, aes( x = z1, y =z2, color=as.factor(labels))) +
    geom_point(size=size,alpha=alpha) +
    labs(color= 'Cluster Label') +
    ggtitle(plt_ttl)+
    theme_dark()
  
  if(show){show(plt)}
  return(plt)
}

#Line plot of sequences in low dim space
line_seqs <- function(syll_tbl, show=TRUE, alpha=0.05){
  require('ggplot2')
  require('dplyr')
  
  #Get name
  plt_ttl <- as.character(syll_tbl$animal[1])
  
  #Filter unlabeled sylls
  df <- syll_tbl %>%
    filter(labels>=0) %>%
    group_by(sequence_num) %>%
    arrange(sequence_syllable, .by_group = TRUE) 
  
  #plot
  plt <- ggplot(data = df, aes(group=sequence_num, x = z1, y =z2)) +
    geom_path(alpha=alpha, color='white') +
    ggtitle(plt_ttl)+
    theme_dark()
  
  if(show){show(plt)}
  return(plt)
}
