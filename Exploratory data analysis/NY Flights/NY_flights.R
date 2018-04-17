install.packages('nycflights13')
library(ggplot2)
library(dplyr)
library(nycflights13)


#
names(flights)
summary(flights)

flights$carrier <- factor(flights$carrier)
flights$month <- factor(flights$month)

ggplot( data = flights, aes(x = month, y = dep_delay) ) + 
  geom_point(alpha = 0.3, color = 'blue')

# Histogram
flights_sub <- subset(flights, !is.na(dep_delay), !is.na(arr_delay) )
                      
ggplot(aes(x = dep_delay), data = subset(flights_sub, dep_delay >= 0 & dep_delay <= quantile(dep_delay, .90) ) ) +
  geom_histogram(aes(fill = month), binwidth = 1) + 
  facet_wrap(~carrier) #+
  #scale_fill_brewer(palette="RdYlGn")


by_carrier <- flights_sub %>%
  group_by(carrier) %>%
  summarise(mean_dep_delay = mean(dep_delay),
            median_dep_delay = median(dep_delay),
            n = n()) %>%
  arrange(desc(mean_dep_delay))
  
ggplot(aes(x = carrier, y = mean_dep_delay), data = by_carrier) +
  geom_point()

ggplot(aes(x = carrier, y = dep_delay),
       data = flights_sub) + 
  geom_point(color = 'brown', stat = 'summary', fun.y = mean) + 
  geom_point(color = 'blue', stat = 'summary', fun.y = median)


ggplot(aes(x = dep_delay, y = arr_delay), data = flights_sub ) +
  geom_point(aes(color = carrier), alpha = 0.4)

# Troublesome day or month?

# Group by month
by_month <- flights_sub %>%
  group_by(month) %>%
  summarise(mean_dep_delay = mean(dep_delay),
            n = n()) %>%
  arrange(desc(mean_dep_delay))

# Histogram plot for July

July <- subset(flights, month == 7)
July <- subset(July, !is.na(dep_delay), !is.na(arr_delay) )

ggplot(aes(x = day, y = dep_delay), data = July ) +
  geom_point(aes(color = carrier))

# 
ggplot(aes(x = day, y = dep_delay), data = flights_sub ) +
  geom_point(alpha = 0.1, color = 'brown') + 
  facet_wrap(~month)

