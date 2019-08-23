import json
import re
import time
from configparser import ConfigParser
from datetime import datetime

import feedparser
import pandas as pd
import requests
from bs4 import BeautifulSoup
from numpy import nan

from alpha_vantage_service import AlphaVantageService
from database.db_dude import DBDude
from database.environmental import Environmental
from database.financial import Financial
from database.political import Political


class DataFetcher:
    def __init__(self, config_path):
        self.dude = DBDude()
        self.alpha = AlphaVantageService()

        self.config = ConfigParser()
        self.config.read(config_path)

        self.political_sources_path = self.config['sources']['political']
        self.environmental_sources_path = self.config['sources']['environmental']
        self.financial_sources_path = self.config['sources']['financial']
        self.round_sleep_time = self.config.getint('general', 'data_fetcher_sleep_time')

    def retrieve_political(self):
        with open(self.political_sources_path) as file:
            political_sources = json.load(file)

        political_keywords = political_sources['keywords']
        # Go through rss feeds
        for feed in political_sources["rss_feeds"]:
            feed_response = feedparser.parse(feed)
            for ent in feed_response.entries:
                # Remove html tags from summary
                summary = re.sub('<[^<]+?>', '', ent.summary).replace('\n', '')
                ent_text = ent.title + " " + summary
                if any(pol_kw in ent_text.lower() for pol_kw in political_keywords):
                    publish_datetime = datetime.fromtimestamp(time.mktime(ent.published_parsed))
                    self.dude.create_political_if_not_exists(Political(ent.id, ent.title, summary, feed, publish_datetime))

    def retrieve_environmental(self):
        with open(self.environmental_sources_path) as file:
            environmental_sources = json.load(file)

        # Find the ones not already present in the db
        db_environmental = self.dude.select_all_environmental()
        db_env_names = [db_env.name for db_env in db_environmental]
        absent_environmental = dict(filter(lambda env: env[0] not in db_env_names, environmental_sources.items()))

        for env_name, env_url in absent_environmental.items():
            env_response = requests.get(env_url)
            if env_response.status_code != 200:
                # TODO: log error here
                print("Bad response code")
                return

            env_html = BeautifulSoup(env_response.content, features="html.parser")
            big_counter = env_html.find('div', class_='big-counter')
            # Get pretty name
            h2_header = big_counter.find('h2')
            sub_title = self._first_lower(h2_header.find_next_sibling('p').text.replace('\n', ''))
            pretty_name = h2_header.text.replace('\n', '') + " " + sub_title
            # Get increment and base_value
            script = big_counter.find('script')
            types = re.search('number_interval\((-?[\d\.e\-]+), (-?[\d\.e\-]+)', script.text)
            base_value, increment = types.groups()
            self.dude.create_environmental(Environmental(env_name, pretty_name, base_value, increment, datetime.now()))

    def _first_lower(self, s):
        if len(s) == 0:
            return s
        else:
            return s[0].lower() + s[1:]

    def retrieve_financial(self):
        financial_df = pd.read_csv(self.financial_sources_path)
        # Private Companies
        private_rows = financial_df.loc[financial_df.TYPE == 'Private']
        db_privates = self.dude.select_all_financial_private()
        db_companies = [db_pri.company for db_pri in db_privates]
        for row in private_rows.iterrows():
            private = row[1]
            if private.EVALUATION is not nan and private.COMPANY.upper() not in db_companies:
                private_financial = Financial.create_private(company=private.COMPANY, industry=private.INDUSTRY,
                                                             price=private.EVALUATION, currency=private.CURRENCY)
                self.dude.create_financial(private_financial)

        # Public Companies
        public_rows = financial_df.loc[financial_df.TYPE == 'Public']
        db_publics = self.dude.select_all_financial_public()
        db_companies = [db_pub.company for db_pub in db_publics]

        unqouted_stocks = public_rows.loc[~public_rows.COMPANY.str.upper().isin(db_companies)]
        if len(unqouted_stocks) > 0:
            for row in unqouted_stocks[:5].iterrows():
                public = row[1]
                # AlphaVantage might return blank if calls are used up
                av_response = self.alpha.get_stock_quote(public['AV SYMBOL'])
                if av_response is None:
                    continue
                av_price, av_change = av_response
                public_financial = Financial.create_public(company=public.COMPANY, industry=public.INDUSTRY,
                                                           price=av_price,
                                                           change=av_change, currency=public.CURRENCY,
                                                           symbol=public['AV SYMBOL'])
                self.dude.create_financial(public_financial)
        else:
            # Find the 5 oldest entries and update them
            oldest = sorted(db_publics, key=lambda x: x.timestamp)[:5]
            for stock in oldest:
                # AlphaVantage might return blank if calls are used up
                av_response = self.alpha.get_stock_quote(stock.symbol)
                if av_response is None:
                    continue
                av_price, av_change = av_response
                price_number = Financial.convert_str_price(av_price)
                change_number = Financial.convert_str_price(av_change)
                self.dude.update_financial((price_number, change_number, datetime.now(), stock.company))

    def run(self):
        self.retrieve_political()
        self.retrieve_environmental()
        self.retrieve_financial()
        time.sleep(self.round_sleep_time)

if __name__ == '__main__':
    fetcher = DataFetcher('config.ini')
    fetcher.run()
