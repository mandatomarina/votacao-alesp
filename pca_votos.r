library(ggplot2)
library(ggbiplot)
library(dplyr)
library(tidyr)
library(stringr)
library(ggrepel)
raw <- read.csv2(file="~/devel/mandato/votacao/resultado.csv", sep=",", header=FALSE)


data <- raw %>%
  select(-V3) %>%
  mutate(V4=as.character(V4)) %>%
  mutate(V4=ifelse(V2=="CAUÊ MACRIS",1,V4)) %>%
  group_by(V2,V1) %>%
  distinct(V1, .keep_all=TRUE) %>%
  dplyr::mutate(ind = row_number()) %>%
  spread(V1, V4) %>%
  select(-ind)


set.seed(20)
model <- data %>%
  ungroup() %>%
  select(-V2) %>%
  mutate_all(funs(replace(.,. %in% c(1, "Sim", "Abstenção"),1))) %>%
  mutate_all(funs(replace(.,.!=1,0))) %>%
  mutate_all(funs(as.numeric(.)))
  
model[is.na(model)] <- 0

model.k <- model %>%
  kmeans(., 9, nstart = 20, iter.max=1000)
model.pca = prcomp(model,center = TRUE, scale = FALSE)

model.lista <- data.frame(data$V2)
model.lista$cluster <- model.k$cluster

g <- ggbiplot(model.pca, 
              groups = as.factor(model.k$cluster),
              var.axes = FALSE,
              obs.scale = 1, var.scale = 1, ellipse = TRUE, circle = TRUE)

  g <- g + 
    geom_text_repel(aes(label=data$V2, colour=groups), size=3) +
    theme_void(base_size=16)
print(g)