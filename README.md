# Twitter
This is an ongoing exercise using the Twitter API to gather tweets about Cafeyn brands - Cafeyn, Blendle and MiLibris.
A cron job is running on a Raspberry pi every day to collect new tweets about the company and store them in a csv. 

## Visualizing results
The second part is done in R and ggplot. The teets are analyzed and outputed into static charts that can be uploaded on a website.
Ideally, we could have a setup where the graphs are hosted on the Raspberry via Shiny, and a website could access them in a dynamic way.

## Next steps
1. Have a minimal working example of a setup where the tweets are gathered, processed and outputed on a page from [my website](https://www.polegato.me/data)
2. Make the graphs dynamic, probably hosting the stored file on S3 or GCS to learn that setup too
3. Extend Twitter API calls to a wider spectrum than just Twitter search results
4. Expand analysis onto NLP when there is more content
