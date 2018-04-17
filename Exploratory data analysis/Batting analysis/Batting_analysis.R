library(Lahman)
library(dplyr)
library(ggplot2)

data(Batting)
head(Batting)

grouped <- Batting %>%
           group_by(playerID) %>%
           summarise( games = sum(G),
                      home_runs = sum(HR),
                      strikeouts = sum(SO))
           

grouped = arrange(grouped, desc(games))
head(grouped)

# 3. Correlations

with(grouped, cor.test(games, home_runs))
with(grouped, cor.test(games, strikeouts))
with(grouped, cor.test(home_runs, strikeouts))
with(grouped, cor.test(home_runs/games, strikeouts/games))


# Plots

ggplot(aes(x = games, y = home_runs), data = grouped) +
  geom_point(alpha = 0.1, color = 'orange')

ggplot(aes(x = games, y = strikeouts), data = grouped) +
  geom_point(alpha = 0.1, color = 'blue')


ggplot(aes(x = home_runs, y = strikeouts), data = grouped) +
  geom_point(alpha = 0.1, color = 'pink')

ggplot(aes(x = home_runs/games, y = strikeouts/games), data = grouped) +
  geom_point(alpha = 0.1, color = 'brown') + 
  geom_smooth(method = 'lm', color = 'blue')
