library(tidyverse)
library(extrafont)
library(ggrepel)
library(scales) # to access break formatting functions
library(tidymodels)
library(tidytext)
library(stopwords)

twitter <- read_csv("~/self_dev/Python/twitter_api_test/results/twitter_searches_incremental_tmp.csv") %>% 
  mutate(from_owned_account = str_detect(tolower(screen_name),'blendle|cafeyn|milibris')) 

twitter %>% 
  group_by(date_clean = lubridate::date(queried_at),
           company) %>% 
  count() %>% 
  ggplot(aes(date_clean,n, fill = company)) +
  geom_col()

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
  filter(!from_owned_account) %>% 
  group_by(screen_name,iso_language_code,company) %>% 
  summarize(n_tweets = n_distinct(id),
            favorites = sum(favorite_count),
            retweets = sum(retweet_count),
            .groups = 'drop') %>% 
  arrange(desc(favorites+retweets)) %>% 
  ungroup() %>% 
  dplyr::slice_head(n=30) %>% 
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
    subtitle = "",
    x = "Tweets about company",
    y = "Favorites and Retweets (Log10)",
    caption = "Source: Twitter | Viz: @NosyOwl",
    fill = "Tweet language"
  ) +
  theme(
    text = element_text(family = "Tw Cen MT", size = 14),
    axis.text = element_text(face = "bold"),
    legend.position = "top"
  ) +
  facet_grid(~company) 

ggsave(
    "self_dev/Python/twitter_api_test/test.png",
    dpi = 320,
    height = 8,
    width = 12
  )


stopwords_nl <- stopwords::stopwords("nl", source = "snowball")
stopwords_en <- stopwords::stopwords("en", source = "snowball")
stopwords_de <- stopwords::stopwords("de", source = "snowball")
stopwords_fr <- stopwords::stopwords("fr", source = "snowball")
stopwords_misc <- c("https","t.co")

stopwords <- c(stopwords_nl,stopwords_en,stopwords_de,stopwords_fr,stopwords_misc) %>% 
  as_tibble() 

# Break down the comments 
twitter_text <- twitter %>% 
  unnest_tokens(words,text) %>% 
  anti_join(stopwords, by = c('words' = 'value'))

twitter_text %>% 
  count(words, sort=T) 

# Create a proportion mapping of every word
frequency <- twitter_text %>% 
  filter(company != 'Milibris') %>% 
  mutate(word = str_extract(words, "[a-z']+")) %>%
  count(company, word) %>%
  group_by(company) %>%
  mutate(proportion = n / sum(n)) %>% 
  select(-n) %>% 
  spread(company, proportion) %>% 
  gather(company, proportion, Blendle) %>% 
  filter(nchar(word)>1)

# plot the prominent words inside one company and not the other
ggplot(frequency, aes(x = proportion, y = Cafeyn, 
                      color = abs(Cafeyn - proportion))) +
  geom_abline(color = "gray40", lty = 2) +
  geom_jitter(alpha = 0.1, size = 2.5, width = 0.3, height = 0.3) +
  geom_text(aes(label = word), check_overlap = TRUE, vjust = 1.5) +
  scale_x_log10(labels = percent_format()) +
  scale_y_log10(labels = percent_format()) +
  scale_color_gradient(limits = c(0, 0.001), 
                       low = "darkslategray4", high = "gray75") +
  theme(legend.position="none") +
  labs(y = "Cafeyn", x = NULL)
