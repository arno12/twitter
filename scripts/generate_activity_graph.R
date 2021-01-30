library(tidyverse)
library(extrafont)
library(ggrepel)
library(scales) # to access break formatting functions
library(tidymodels)
library(tidytext)
library(stopwords)

# Load data
twitter <- read_csv("../results/twitter_searches_incremental.csv") %>% 
  mutate(from_owned_account = str_detect(tolower(screen_name),'blendle|cafeyn|milibris')) 

# 1. Show tweets collected over time
twitter %>% 
  group_by(date_clean = lubridate::date(queried_at),
           company) %>% 
  count() %>% 
  ggplot(aes(date_clean,n, fill = company)) +
  geom_col() +
  theme_minimal() +
  scale_fill_viridis_d() +
  labs(
    title = "Tweets collected over time",
    subtitle = "",
    x = "Date",
    y = "Tweets mentioning one company",
    caption = "Source: Twitter | Viz: @NosyOwl",
    fill = "Company"
  ) +
  theme(
    text = element_text(family = "Tw Cen MT", size = 14),
    axis.text = element_text(face = "bold"),
    legend.position = "top")

ggsave(
  str_c("../graphs/",format(Sys.time(), "%Y-%m-%d-%Hh%M"),"_tweets_over_time.png"),
  dpi = 320,
  height = 8,
  width = 8
)

# Determine max n of tweets for graph scaling
max_n_tweets <- twitter %>% 
  filter(!from_owned_account) %>% 
  group_by(screen_name) %>% 
  summarize(n_tweets = n_distinct(id),
            favorites = sum(favorite_count),
            retweets = sum(retweet_count)) %>% 
  slice_max(n_tweets, with_ties = FALSE) %>% 
  select(n_tweets) %>% 
  as.integer()

# Create and save a nice viz that we could also post on Twitter
twitter %>% 
  filter(!from_owned_account,
         iso_language_code != 'und') %>% 
  group_by(screen_name,iso_language_code,company) %>% 
  summarize(n_tweets = n_distinct(id),
            favorites = sum(favorite_count),
            retweets = sum(retweet_count),
            .groups = 'drop') %>% 
  arrange(desc(favorites+retweets)) %>% 
  group_by(company) %>% 
  mutate(rn = row_number()) %>% 
  filter(rn <= 20) %>% 
  ggplot(aes(n_tweets, log(favorites+retweets), label = str_c("@",screen_name), fill = str_to_upper(iso_language_code))) +
  geom_point() + 
  geom_label_repel(size = 3,
                   alpha = .8) +
  theme_minimal() +
  scale_x_log10(n.breaks = 10) +
  scale_y_log10(n.breaks = 10,) +
  scale_fill_viridis_d() +
  labs(
    title = "Most Impactful Tweets about Cafeyn group brands",
    subtitle = "Top 20 tweets for each brand",
    x = "Tweets about company",
    y = "Favorites and Retweets (Log10)",
    caption = "Source: Twitter | Viz: @NosyOwl",
    fill = "Tweet language"
  ) +
  theme(
    text = element_text(family = "Tw Cen MT", size = 12),
    axis.text = element_text(face = "bold"),
    legend.position = "top"
  ) +
  facet_wrap(~company, ncol = 1)

ggsave(
    str_c("../graphs/",format(Sys.time(), "%Y-%m-%d-%Hh%M"),"_tweet_users.png"),
    dpi = 320,
    height = 14,
    width = 6
  )

