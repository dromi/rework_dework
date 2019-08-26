import json
import re
import time
from multiprocessing import Process

import pandas as pd
from numpy import nan

from alpha_vantage_service import AlphaVantageService
from data_retriever import DataRetriever
from data_presenter import DataPresenter
from database.db_dude import DBDude
from datetime import datetime
import feedparser

from database.financial import Financial
from database.political import Political

NEWS_SRCS = "sources/political.json"
STOCK_SRCS = "sources/stock.json"
CRED_FILE = "sources/credentials.json"
FIN_CSV = "sources/financial.csv"

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


def fetch_financial():
    dude = DBDude()
    financial_df = pd.read_csv(FIN_CSV)
    # Private Companies
    private_rows = financial_df.loc[financial_df.TYPE == 'Private']
    db_privates = dude.select_all_financial_private()
    db_companies = [db_pri.company for db_pri in db_privates]
    for row in private_rows.iterrows():
        private = row[1]
        if private.EVALUATION is not nan and private.COMPANY.upper() not in db_companies:
            private_financial = Financial.create_private(company=private.COMPANY, industry=private.INDUSTRY,
                                                         price=private.EVALUATION, currency=private.CURRENCY)
            dude.create_financial(private_financial)

    # Public Companies
    public_rows = financial_df.loc[financial_df.TYPE == 'Public']
    alpha = AlphaVantageService()
    db_publics = dude.select_all_financial_public()
    db_companies = [db_pub.company for db_pub in db_publics]
    unqouted_stocks = public_rows.loc[~public_rows.COMPANY.isin(db_companies)]
    if len(unqouted_stocks) > 0:
        for row in unqouted_stocks[:5].iterrows():
            public = row[1]
            av_price, av_change = alpha.get_stock_quote(public['AV SYMBOL'])
            public_financial = Financial.create_public(company=public.COMPANY, industry=public.INDUSTRY,
                                                       price=av_price,
                                                       change=av_change, currency=public.CURRENCY,
                                                       symbol=public['AV SYMBOL'])
            dude.create_financial(public_financial)
    else:
        # Find the 5 oldert entries and update them
        oldest = sorted(db_publics, key=lambda x: x.timestamp)[:5]
        for stock in oldest:
            av_price, av_change = alpha.get_stock_quote(stock.symbol)
            price_number = Financial.convert_str_price(av_price)
            change_number = Financial.convert_str_price(av_change)
            dude.update_financial((price_number, change_number, datetime.now(), stock.company))


if __name__ == '__main__':
    data_retriever = DataRetriever('config.ini')
    data_presenter = DataPresenter('config.ini')
    p_retrieve = Process(target=data_retriever.run)
    p_present = Process(target=data_presenter.run)
    p_retrieve.start()
    p_present.start()
