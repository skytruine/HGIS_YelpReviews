#Yelp Review Crawler - Yifan
This project contains two web crawler for yelp business and attached reviews.
The first one is web page based, you can acees its colab version at: https://colab.research.google.com/drive/15PorPHQqN0efunRNiEBSyead_o0B5h6m#scrollTo=BI0dv8p-ld6G
The second one is offical API based, you can acees its colab version at: https://colab.research.google.com/drive/1vryTPQ2KT5gW9PaFAJOC0f8WVAtFe0kx#scrollTo=LTu5g9Mo_Hyi
The core components of two crawlers are inside "yelp_reviews_crawler.py", you can use it in a simple way.

## Web based Yelp review crawler

Our ip address will be blocked if we run too fast or send too many request to the server of Yelp, resulting in returning error. If you encounter this kind of problem, please restart your server, enlarge the pause time and reduce the total numer (content & comments) you ask.

One advanced technique to bypass the anti-cralwer tech "IP block" is "IP pool", which means we collect a large number of IP addresses, and send requests using different IPs, so the workload for each IP is small, while one single IP address is less likely to be blocked, when one IP is blocked, we always have alternative IP to use. In this demo notebook, we wouldn't use any advanced tech.

