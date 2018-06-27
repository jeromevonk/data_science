library(ggplot2)
library(dplyr)

df = read.csv('C:/datasets/IMDb/title_basics.tsv', header = TRUE, sep = "\t", na.strings = "\\N")
head(df)

# Get only the movies
df_movies <- subset(df, titleType == 'movie')
head(df_movies)

# Exclude variables endYear and genres
myvars <- names(df_movies) %in% c("endYear", "genres", "titleType", "primaryTitle", "isAdult") 
df_movies <- df_movies[!myvars]
head(df_movies)

# Remove movies from 2018 on
df_movies <- subset(df_movies, startYear <= 2017)
df_movies <- arrange(df_movies, startYear)
tail(df_movies)

# Change variable runtimeMinutes to numeric
df_movies$runtimeMinutes <- as.numeric(as.character(df_movies$runtimeMinutes))

# Remove observations of runTimeMinutes which are NA
df_movies <- dplyr::filter(df_movies,  !is.na(runtimeMinutes))
summary(df_movies$runtimeMinutes)

# Write to a tsv file
write.table(df_movies, file = "C:/datasets/IMDb/title_subset.tsv", row.names = FALSE, dec = ".", sep = "\t", quote = FALSE)
