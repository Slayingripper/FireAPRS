from sympy import N
import feedparser
from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')
rss = config.get('newsfeed','link')
keyword = config.get('newsfeed','keyword')
print(keyword)
print(rss)
#grab the rss feed from the config file
NewsFeed = feedparser.parse(rss)
# search through all titles in the rss feed
def newsfinder() :
    for entry in NewsFeed.entries:
        #grab the title of the rss feed
        title = entry.title
        #check if the keyword is in the title
        if keyword in title:
            #print(entry.link)
            newslink = entry.link
            #print(newslink)
            return newslink
        else:
            #print("No link found")
            newslink = "No link found"
            return newslink