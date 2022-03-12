#Yelp Review Crawler - Yifan
This project contains two web crawler for **yelp business and attached reviews.**
The first one is web page based, you can acees its colab version at: https://colab.research.google.com/drive/15PorPHQqN0efunRNiEBSyead_o0B5h6m#scrollTo=BI0dv8p-ld6G
The second one is offical API based, you can acees its colab version at: https://colab.research.google.com/drive/1vryTPQ2KT5gW9PaFAJOC0f8WVAtFe0kx#scrollTo=LTu5g9Mo_Hyi
The core components of two crawlers are inside "yelp_reviews_crawler.py", you can use it in a simple way.

## Web based Yelp review crawler

```python
def getYelpInfo_includeComments(query="Restaurants",location="Seattle, WA 98104",max_pages=3,max_comments=3,pause=0.5):
  """Download formatted Yelp search results with comments(By Yifan)

  Retrieves basic information of a Yelp Search. Your can use the function directly to get max 240 place items and infinite comments with them (as long as there is a comment)
  However, without advanced tech called IP pool, I don't suggest you dowload a large amount of comments.....

  Args:
    query: the key word used in searching, querying
    location: the area/location limitation for the query
    max_pages: the list is limited to 24 pages, resulting in maxinum 240 items; since frequent will be blocked, I don't think to try it in a large value
    max_comments: how many comments do you want for one single content? It can be a larger number, since when it's larger than total comments num, we will use total comments num
    pause: speed contral, single pause time (s) for avoiding IP blocking
  Returns:
    A pandas dataframe, which contains 20 columns ('content_id','name','rate','review','tags','address','city','state','postcode','comment_id','user_id','user_name','display_city','display_state','rating','date','feedback_useful','feedback_funny','feedback_cool','comment')
  """

```
Our ip address will be blocked if we run too fast or send too many request to the server of Yelp, resulting in returning error. If you encounter this kind of problem, please restart your server, enlarge the pause time and reduce the total numer (content & comments) you ask.

One advanced technique to bypass the anti-cralwer tech "IP block" is "IP pool", which means we collect a large number of IP addresses, and send requests using different IPs, so the workload for each IP is small, while one single IP address is less likely to be blocked, when one IP is blocked, we always have alternative IP to use. In this demo notebook, we wouldn't use any advanced tech.


## API based Yelp review crawler
```python
def yelp_search(term='bar',location='Seattle, WA',pause=0.25,includeComments=False):
  """Extract information of Yelp (By Yifan)

  Retrieves basic information (max 1000 items) and attached comments (max 3 comments each item) of Yelp search
  Key reference: https://www.yelp.com/developers/documentation/v3/business_search
  
  Args:
    term: Search term, for example "food" or "restaurants". The term may also be business names, such as "Starbucks".
    location: Geographic area to be used when searching for businesses. Examples: "New York City", "NYC", "350 5th Ave, New York, NY 10118". Businesses returned in the response may not be strictly within the specified location.
    pause: Speed contral, single pause time (s) for avoiding overheated QPS
    includeComments: whether to retrived attached comments

  Returns:
    A pandas dataframe
    if includesComments=False: the dataframe will contains 12 columns(content_id,name,rating,reviews,phone,address,city,state,country,postcode,latitude,longitude)
    else: the dataframe will contains addtional 5 columns (comment_id,user_id,user_name,user_rating,comment)
    A list, which contains 9 items (content_id,name,rate,review,tags,address,city,state,postcode)
    the content_id is important - we need it to further request comments
  """
```
