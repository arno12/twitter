
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
