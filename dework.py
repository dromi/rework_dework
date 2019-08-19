import json
import re
import time

from alpha_vantage_service import AlphaVantageService
from database.db_dude import DBDude
from datetime import datetime
import feedparser

from database.political import Political

NEWS_SRCS = "sources/news.json"
STOCK_SRCS = "sources/stock.json"
CRED_FILE = "sources/credentials.json"

def list_rss():
    dude = DBDude()
    news_keywords = ['forest', 'deforestation', 'soya', 'palm oil', 'amazon', 'plantation', 'tropical forest']
    with open(NEWS_SRCS) as file:
        news = json.load(file)

    #Go through rss feeds
    for feed in news["rss_feeds"]:
        # print("FROM FEED:", feed)
        d = feedparser.parse(feed)
        for ent in d.entries:
            summary = re.sub('<[^<]+?>', '', ent.summary).replace('\n', '')
            ent_text = ent.title + " " + summary
            if any(nkw in ent_text.lower() for nkw in news_keywords):
                publish = time.strftime("%d.%m.%Y - %H:%M", ent.published_parsed)
                publish_datetime = datetime.fromtimestamp(time.mktime(ent.published_parsed))
                print(publish, ent.title)
                dude.create_political_if_not_exists(Political(ent.id, ent.title, summary, feed, publish_datetime))


def list_environmental():
    dude = DBDude()
    environmentals = dude.select_all_environmental()
    for env in environmentals:
        time_delta = datetime.now() - datetime.strptime(env.retrieval, '%Y-%m-%d %H:%M:%S.%f')
        current_value = env.base_value + (env.increment * time_delta.seconds)
        print(f"{env.pretty_name} - {current_value}")


def list_stock():
    dude = DBDude()
    with open(STOCK_SRCS) as file:
        stocks = json.load(file)

    alpha = AlphaVantageService()
    for symbol, company in stocks.items():
        quote = alpha.get_stock_quote(symbol, company)
        dude.create_financial(quote)

if __name__ == '__main__':
    # list_environmental()
    # list_rss()
    list_stock()