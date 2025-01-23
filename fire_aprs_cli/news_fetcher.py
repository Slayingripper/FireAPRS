# fire_aprs_cli/news_fetcher.py

import logging
import feedparser

class NewsFetcher:
    def __init__(self, rss_url, keyword):
        self.rss_url = rss_url
        self.keyword = keyword.lower()

    def fetch_feed(self):
        try:
            feed = feedparser.parse(self.rss_url)
            if feed.bozo:
                logging.warning(f"Encountered issues parsing the RSS feed: {feed.bozo_exception}")
            return feed
        except Exception as e:
            logging.error(f"Failed to fetch or parse RSS feed: {e}")
            return None

    def find_news_link(self):
        feed = self.fetch_feed()
        if not feed or 'entries' not in feed:
            logging.error("No entries found in the RSS feed.")
            return "No link found"

        for entry in feed.entries:
            title = entry.get('title', '').lower()
            if self.keyword in title:
                newslink = entry.get('link', 'No link found')
                logging.info(f"Keyword '{self.keyword}' found in title: '{entry.get('title', '')}'. Link: {newslink}")
                return newslink

        logging.info(f"Keyword '{self.keyword}' not found in any entry titles.")
        return "No link found"
