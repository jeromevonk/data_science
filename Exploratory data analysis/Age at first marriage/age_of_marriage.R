# Load the plot library
library(ggplot2)

# Load the data
marriage <- read.csv('age_marriage.csv')

# Initial checks
names(marriage)
summary(marriage)


# Histogram for 2005 data
summary(marriage$X2005)
qplot(x = X2005, 
      data = marriage, 
      binwidth = 1,
      ylab = "Number of occurences",
      xlab = "Age of first marriage for women (2005)",
      color = I('black'), 
      fill = I('#0010F1') )  +
  scale_x_continuous(breaks = seq(16,34,1), limits=c(16,34)) +
  facet_wrap(~continent, scales = "free_y") +
  ggsave('age_of_first_marriage(2005).png')

