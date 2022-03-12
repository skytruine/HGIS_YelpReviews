import requests
import lxml
import lxml.etree
import json
import pandas as pd
import time
import math


#Construct a real-like request hearder, so the server is likely to consider it as a human being's request
useragent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
header = {
    'user-agent': useragent,
    'cookie': 'your cookie'
}


def getYelpSearchList(query="Restaurants",location="Seattle, WA 98104",max_pages=24):
  """Extract the detail page urls of Yelp search result (By Yifan)

  Retrieves the urls for detials in research result of Yelp, by giving the key word and location limitation.
  one example: https://www.yelp.com/search?find_desc=Restaurants&find_loc=Seattle, WA 98104&start=0
  
  Args:
    query: the key word used in searching, querying
    location: the area/location limitation for the query
    max_pages: the list is limited to 24 pages, resulting in maxinum 240 items; since frequent will be blocked, I don't think to try it in a large value
  Returns:
    A list, which contains the url for detalied pages

  """
  # construct the query url for Yelp
  # one example: https://www.yelp.com/search?find_desc=Restaurants&find_loc=Seattle, WA 98104&start=0
  # param- start: the start number of the result list, each pages contains 10 items, and the list is limited to 24 pages, resulting in maxinum 240 items
  starts=[i*10 for i in range(max_pages)]
  url_list=[]
  qstr="https://www.yelp.com/search?find_desc={}&find_loc={}&start=".format(query,location)
  for start in starts:
    url=qstr+str(start)
    url_list.append(url)

  #Extract the information in the first-level pages
  detail_urls=[]
  for url in url_list:
    print(url)
    time.sleep(0.5)
    response = requests.get(url, headers=header) # get the response of a request for a certain url, header is defined in the beginning
    html = lxml.etree.HTML(response.text) # turn the response's html text into a element-tree which then can be searched using xpath grammer
    if not html.xpath('//h3[contains(string(),"is unavailable")]'): # in case there is less than 240 items of our result, make the code robust
      itms=html.xpath('//h4/span[contains(string(),".")]/a')
      if itms is None:  # Frequent request causing IP blocking, then the return should be a error page, form which we can get nothing
          print('IP Block, your need to restart the server')
      for i in itms:
        detail_url="https://www.yelp.com/"+i.xpath('@href')[0]
        detail_urls.append(detail_url)
  return detail_urls

def getYelpDetails(detail_url="https://www.yelp.com//biz/the-pink-door-seattle-4?osq=Restaurants"):
  """Extract information from one specific Yelp detail page (By Yifan)

  Retrieves content_id,name,rate,review,tags,address,city,state,postcode of a bussiness place, by giving a detail page url.
  one example: https://www.yelp.com//biz/the-pink-door-seattle-4?osq=Restaurants
  
  Args:
    detail_url: url of Yelp detail page

  Returns:
    A list, which contains 9 items (content_id,name,rate,review,tags,address,city,state,postcode)
    the content_id is important - we need it to further request comments
  """

  #devle into detail_url to get more information
  response = requests.get(detail_url, headers=header)
  html = lxml.etree.HTML(response.text)

  try:
    name=html.xpath("//h1//text()")[0]
    address=html.xpath("//address/a/p//text()")[0]
    region=html.xpath("//address/p//text()")[-1]
    city=region.split(',')[0]
    state=region.split(',')[1].split()[0]
    postcode=region.split(',')[1].split()[1]
    rate=float(html.xpath("//h1/../../div[2]/div[1]//div[@role='img']/@aria-label")[0].split()[0])
    review=int(html.xpath("//h1/../../div[2]/div[2]//span/text()")[0].split()[0])
    content_id=html.xpath("//meta[@name='yelp-biz-id']/@content")[0]
    tags=';'.join(html.xpath("//h1/../../span[3]//a//text()"))
  except Exception as e:
    print('IP blocked:'+detail_url,e)
    content_id,name,rate,review,tags,address,city,state,postcode=None,None,None,None,None,None,None,None,None
  return [content_id,name,rate,review,tags,address,city,state,postcode]

  

def getYelpComments(content_id="VOPdG8llLPaga9iJxXcMuQ",max_comments=10,pause=0.5):
  """Extract comments of one specific content in Yelp (By Yifan)

  Retrieves content_id,name,rate,review,tags,address,city,state,postcode of a bussiness place, by giving a detail page url.
  one example: https://www.yelp.com//biz/the-pink-door-seattle-4?osq=Restaurants
  
  Args:
    content_id: the Yelp id of the content, it's a string and can be find when examine the source code of a detail page
    max_comments: how many comments do you want? It can be a larger number, since when it's larger than total comments num, we will use total comments num
    pause: speed contral, single pause time (s) for avoiding IP blocking

  Returns:
    A list, which contains 9 items (content_id,name,rate,review,tags,address,city,state,postcode)
    the content_id is important - we need it to further request comments
  """

  def extractComments(content_id='VOPdG8llLPaga9iJxXcMuQ',page=0): 
    #example of a detail page: https://www.yelp.com//biz/the-pink-door-seattle-4?osq=Restaurants
    #By analyzing the traffic flow of the detail page of Yelp, we find the data package of the dynamic page
    #the target data package API: https://www.yelp.com/biz/VOPdG8llLPaga9iJxXcMuQ/review_feed?rl=en&q=&sort_by=relevance_desc&start=0   
    url="https://www.yelp.com/biz/{}/review_feed?rl=en&q=&sort_by=relevance_desc&start={}".format(content_id,page*10)
    response = requests.get(url, headers=header)
    data = json.loads(response.text) #turn json string to dictionary

    total_num=data['pagination']['totalResults']
    rst=[]
    page_num=len(data['reviews'])
    for i in range(page_num):
      cmt=data['reviews'][i]
      comment_id=cmt['id']
      user_id=cmt['userId']
      user_name=cmt['user']['markupDisplayName']
      location=cmt['user']['displayLocation'].split(',')
      if len(location)>1:
        display_city=location[0]
        display_state=location[1]
      elif len(location)>0:
        display_city=location[0]
        display_state=None
      else:
        display_city,display_state=None,None
      rating=cmt['rating']
      date=cmt['localizedDate']
      if 'feedback' in cmt and 'counts' in cmt['feedback']:
        feedback_useful=cmt['feedback']['counts']['useful']
        feedback_funny=cmt['feedback']['counts']['funny']
        feedback_cool=cmt['feedback']['counts']['cool']
      else:
        feedback_useful,feedback_funny,feedback_cool=None,None,None
      if 'comment' in cmt and 'text' in cmt['comment']:
        comment=cmt['comment']['text']
      else:
        comment=None
      rst.append([content_id,comment_id,user_id,user_name,display_city,display_state,rating,date,feedback_useful,feedback_funny,feedback_cool,comment])
    return total_num,rst
  
  total_num,trst=extractComments(content_id,0)
  if total_num<max_comments:
    max_comments=total_num
  if max_comments%10==0:
    maxPages=int(max_comments/10)
  else:
    maxPages=int(max_comments/10)+1
  #start of the outer function
  if maxPages>1:
    print('********start to extract comments of {}********'.format(content_id))
  rst=[]
  rst=rst+trst
  for page in range(maxPages-1):
    page=page+1
    print("coments: page {}/{}".format(page+1,maxPages))
    time.sleep(pause)
    try:
      _,trst=extractComments(content_id,page)
    except Exception as e:
      print('IP Blocked')
      time.pause(pause*5)
      try:
        _,trst=extractComments(content_id,page)
      except Exception as e:
        trst=[None]*12
    rst=rst+trst
  rst=rst[0:max_comments]
  if maxPages>1:
    print('********finish extractting comments of {}********'.format(content_id))
  return rst

  

def getYelpInfo_noComments(query="Restaurants",location="Seattle, WA 98104",max_pages=3,pause=0.5):
  """Download formatted Yelp search results without comments(By Yifan)

  Retrieves basic information of a Yelp Search. Your can use the function directly to get max 240 records of one single Yelp search

  Args:
    query: the key word used in searching, querying
    location: the area/location limitation for the query
    max_pages: the list is limited to 24 pages, resulting in maxinum 240 items; since frequent will be blocked, I don't think to try it in a large value
    pause: speed contral, single pause time (s) for avoiding IP blocking
  Returns:
    A pandas dataframe, which contains 9 columns ('content_id','name','rate','review','tags','address','city','state','postcode')
  """
  detail_urls=getYelpSearchList(query,location,max_pages)
  print('*****Extracting {} at {}****'.format(query,location)) 
  num=len(detail_urls)
  rst=[]
  for i,detail_url in zip(range(num),detail_urls):
    if (i+1)%5==0:
      print('Retrieve Info: {}/{}'.format(i+1,num))  #It's a nice habit to print status of your web crawler
      time.sleep(pause*5)
    trst=getYelpDetails(detail_url)
    if trst[0]==None:
      print('IP Block: '+detail_url)
      time.sleep(pause)
    rst.append(trst)
  print('***finish****')
  df=pd.DataFrame(data=rst,columns=['content_id','name','rate','review','tags','address','city','state','postcode'])  # re-format your results to a dataframe, if your like you can download the results or upload them to your remote databse
  df=df.loc[df['content_id'].notnull()] #drop none records which may be caused by IP blocking
  return df


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

  tdf=getYelpInfo_noComments(query,location,max_pages,pause)
  rst=[]
  for content_id in tdf['content_id']:
    trst=getYelpComments(content_id,max_comments=3,pause=0.5)
    rst=rst+trst
  cdf=pd.DataFrame(data=rst,columns=['content_id','comment_id','user_id','user_name','display_city','display_state','rating','date','feedback_useful','feedback_funny','feedback_cool','comment'])
  cdf=cdf.loc[cdf['content_id'].notnull()]
  df=pd.merge(tdf,cdf,on='content_id')
  return df

  # API Path
BUSINESS_SEARCH="https://api.yelp.com/v3/businesses/search"
REVIEWS="https://api.yelp.com/v3/businesses/id/reviews"

# API Key (Pleace change to your own key)
# See https://www.yelp.com/developers/v3/manage_app
API_KEY='F7eyhzh9kdJQ3y6xBR__OPi7MtYzT2r-4Vhq-KrI5IINHnzfYcNLVnuDaHiNk7OacZ-dcBWxIA7eRZvdKfXclV2cewyw53NadneXbpspHZGO1GVxC9hoJNznKYzJYXYx'
HEADER = {
      'Authorization': 'Bearer %s' % API_KEY,
  }

# constant params
MAX=1000
LIMIT=50


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

  params = {
        'term': term, 
        'location': location,
        'limit': LIMIT,
        }
  #determine how many term are at the location and how many we chan get
  # the "total" in current API is limited to 240, in other words, it no long reflect the real number of bussiness in the area
  # if it works, the alternative code for "total=MAX" should work
  #--------------------alternative code----------
  # total= json.loads(requests.request('GET',BUSINESS_SEARCH, headers=headers,params=params).text)['total']
  # print('there are {} {} at {}'.format(total,term,location))
  # if total>MAX:
  #   total=MAX
  
  total=MAX
  
  #calculate the offset list we need to retrive the research list
  offsets=[i*LIMIT for i in range(math.ceil(total/LIMIT))]
  
  # initial the result list
  rst=[]
  print('**********Start**********')
  #retrive data according to offset list
  for offset in offsets:
    print("Retrieving: {}/{}".format(offset,total))
    time.sleep(pause)
    params['offset']=offset
    response = requests.request('GET',BUSINESS_SEARCH, headers=HEADER,params=params)
    data = json.loads(response.text)['businesses'] # turn the responese's json string to dictionary
    for item in data:             # extract data we need in loop
      # get basic information
      content_id=item['id']
      name=item['name']
      rating=item['rating']
      reviews=item['review_count']
      phone=item['phone']
      address=item['location']['address1']
      city=item['location']['city']
      state=item['location']['state']
      country=item['location']['country']
      postcode=item['location']['zip_code']
      latitude=item['coordinates']['latitude']
      longitude=item['coordinates']['longitude']
      rst.append([content_id,name,rating,reviews,phone,address,city,state,country,postcode,latitude,longitude])
  # rst=rst[0:total] #drop redundant duplicates which is due to the mechanism of offset
  # reformate the result list to a pandas dataframe
  df=pd.DataFrame(data=rst,columns=["content_id","name","rating","reviews",
                                    "phone","address","city","state","country",
                                    "postcode","latitude","longitude"])
  df.drop_duplicates('content_id','first',inplace=True)
  print("{} {} at {} Retrieved.".format(len(df),term,location))
  #retrive additional comments
  if includeComments:
    rst=[]
    for i,content_id in zip(range(len(df['content_id'])),df['content_id']):
      if (i+1)%5==0:
        print("Comments Retrieving: {}/{}".format(i+1,len(df['content_id'])))
        time.sleep(pause)
      response = requests.request('GET',REVIEWS.replace('id',content_id), headers=HEADER)
      data = json.loads(response.text)['reviews']
      cmts=[]
      for comment in data:
        comment_id=comment['id']
        user_id=comment['user']['id']
        user_name=comment['user']['name']
        user_rating=comment['rating']
        comment=comment['text']
        rst.append([content_id,comment_id,user_id,user_name,user_rating,comment])
    cdf=pd.DataFrame(data=rst,columns=["content_id","comment_id","user_id",
                                     "user_name","user_rating","comment"])
    print('{} attached comments retrieved.'.format(len(cdf)))
    df=pd.merge(df,cdf,on='content_id')
  print('**********FINISH**********')
  return df

if __name__ == "__main__":
    #Excute Demo (page based): Download formatted Yelp search results with comments
    rdf=getYelpInfo_includeComments(query="Restaurants",location="Seattle, WA 98104",max_pages=2,max_comments=10,pause=0)
    print(rdf)
    #Excute Demo (API based): Extract basic information with comments of Yelp search result
    df1=yelp_search(term='bar',location='Seattle, WA',pause=0.25,includeComments=True)
    print(df1)
