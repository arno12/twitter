library(tidyverse)

twitter <- read_tsv("https://raw.githubusercontent.com/arno12/twitter/master/results/twitter_searches_incremental.tsv")

twitter %>% 
  group_by(lubridate::as_date(created_at)) %>% 
  summarize(n = n(),
            uniques = n_distinct(id)) %>%
  filter(uniques != n)

twitter2 <- twitter %>% 
  group_by(id) %>% 
  summarize(queried_at = min(queried_at))

output <- twitter %>% 
  inner_join(twitter2, by = c("id","queried_at")) 

output_last_30 <- output %>% filter(created_at > lubridate::today()-lubridate::days(31))

write_tsv(output, "self_dev/twitter_api_test/results/twitter_searches_incremental.tsv")
write_tsv(output_last_30, "self_dev/twitter_api_test/results/twitter_searches_last_31_days.tsv")

