library(ggplot2)
v <- read.csv('atleast.csv')
ggplot(v, aes(x=ntests, y=nmutants)) + geom_point() + scale_y_continuous(limit = c(0, 10000))

v <- read.csv('ratios.csv')
ggplot(v, aes(x=index, y=ratio)) + geom_point()+ scale_y_continuous(limit = c(0, 1))
