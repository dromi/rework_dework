import json
import logging
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
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.dude = DBDude()
        self.alpha = AlphaVantageService()

        self.config = ConfigParser()
        self.config.read(config_path)

        self.political_sources_path = self.config['sources']['political']
        self.environmental_sources_path = self.config['sources']['environmental']
        self.financial_sources_path = self.config['sources']['financial']
        self.round_sleep_time = self.config.getint('general', 'data_fetcher_sleep_time')

    def retrieve_political(self):
        self.logger.info("Starting political retrieval")
        with open(self.political_sources_path) as file:
            political_sources = json.load(file)

        political_keywords = political_sources['keywords']
        # Go through rss feeds
        db_rss_political = self.dude.select_all_political()
        db_rss_political_ids = [dbp.external_id for dbp in db_rss_political]
        total_stories = 0
        for feed in political_sources["rss_feeds"]:
            try:
                feed_response = feedparser.parse(feed)
                total_stories += len(feed_response.entries)
                for ent in feed_response.entries:
                    # Remove html tags from summary
                    summary = re.sub('<[^<]+?>', '', ent.summary).replace('\n', '')
                    ent_text = ent.title + " " + summary
                    if any(pol_kw in ent_text.lower() for pol_kw in political_keywords) \
                            and ent.id not in db_rss_political_ids:
                        self.logger.info(f"Discovered new political rss story: {ent.id}")
                        publish_datetime = datetime.fromtimestamp(time.mktime(ent.published_parsed))
                        self.dude.create_political_if_not_exists(Political(ent.id, ent.title, summary, feed,
                                                                           publish_datetime))
                        self.logger.info(f"story {ent.id} added to DB")
            except Exception:
                self.logger.error(f"Unable to retrieve or parse from rss feed: {feed}", exc_info=True)
        print("TOTAL FEED STORIES:", total_stories)

    def retrieve_environmental(self):
        self.logger.info("Starting environmental retrieval")
        with open(self.environmental_sources_path) as file:
            environmental_sources = json.load(file)

        # Find the ones not already present in the db
        db_environmental = self.dude.select_all_environmental()
        db_env_names = [db_env.name for db_env in db_environmental]
        absent_environmental = dict(filter(lambda env: env[0] not in db_env_names, environmental_sources.items()))
        if len(absent_environmental) == 0:
            self.logger.info("No new environmentals to retrieve")

        for env_name, env_url in absent_environmental.items():
            try:
                env_response = requests.get(env_url)
                if env_response.status_code != 200:
                    self.logger.warning(f"Bad response code. Received code {env_response.status_code} from {env_url}")
                    continue

                self.logger.info(f"Discovered new environmental: {env_name}")
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
                self.dude.create_environmental(Environmental(env_name, pretty_name, base_value, increment,
                                                             datetime.now()))
                self.logger.info(f"environmental {env_name} - {pretty_name} added to DB")

            except Exception:
                self.logger.error(f"Unable to retrieve or parse environmental: {env_name} - {env_url}", exc_info=True)

    def _first_lower(self, s):
        if len(s) == 0:
            return s
        else:
            return s[0].lower() + s[1:]

    def retrieve_financial(self):
        self.logger.info("Starting financial retrieval")
        financial_df = pd.read_csv(self.financial_sources_path)
        # Private Companies
        self.logger.info("Retrieving private financial evaluations")
        private_rows = financial_df.loc[financial_df.TYPE == 'Private']
        db_privates = self.dude.select_all_financial_private()
        db_companies = [db_pri.company for db_pri in db_privates]
        for row in private_rows.iterrows():
            try:
                private = row[1]
                if private.EVALUATION is not nan and private.COMPANY.upper() not in db_companies:
                    self.logger.info(f"Discovered new private financial: {private.COMPANY.upper()}")
                    private_financial = Financial.create_private(company=private.COMPANY, industry=private.INDUSTRY,
                                                                 price=private.EVALUATION, currency=private.CURRENCY)
                    self.dude.create_financial(private_financial)
                    self.logger.info(f"Private financial {private_financial.company} added to DB")
            except Exception:
                self.logger.error(f"Unable to retrieve or parse private financial: {row}", exc_info=True)

        # Public Companies
        self.logger.info("Retrieving public financial quotes")
        public_rows = financial_df.loc[(financial_df.TYPE == 'Public') & (financial_df.IGNORE != "T")]
        db_publics = self.dude.select_all_financial_public()
        db_companies = [db_pub.company for db_pub in db_publics]

        unqouted_stocks = public_rows.loc[~public_rows.COMPANY.str.upper().isin(db_companies)]
        if len(unqouted_stocks) > 0:
            self.logger.info(f"Found {len(unqouted_stocks)} unquoted stocks")
            for row in unqouted_stocks[:5].iterrows():
                try:
                    public = row[1]
                    # AlphaVantage might return blank if calls are used up
                    av_response = self.alpha.get_stock_quote(public['AV SYMBOL'])
                    if av_response is None:
                        continue
                    av_price, av_change = av_response
                    self.logger.info(f"Discovered new public financial: {public.COMPANY.upper()} "
                                     f"{av_price} {av_change}")
                    public_financial = Financial.create_public(company=public.COMPANY, industry=public.INDUSTRY,
                                                               price=av_price,
                                                               change=av_change, currency=public.CURRENCY,
                                                               symbol=public['AV SYMBOL'])
                    self.dude.create_financial(public_financial)
                    self.logger.info(f"Public financial {public_financial.company} added to DB")
                except Exception:
                    self.logger.error(f"Unable to retrieve or parse new public financial: {row}", exc_info=True)

        else:
            self.logger.info("No unquoted stocks found")
            # Find the 5 oldest entries and update them
            # TODO test if I need to reverse the sort order
            oldest = sorted(db_publics, key=lambda x: x.timestamp)[:5]
            self.logger.info(f"Renewing public quotes for: {oldest}")
            for stock in oldest:
                try:
                    # AlphaVantage might return blank if calls are used up
                    av_response = self.alpha.get_stock_quote(stock.symbol)
                    if av_response is None:
                        continue
                    av_price, av_change = av_response
                    price_number = Financial.convert_str_price(av_price)
                    change_number = Financial.convert_str_price(av_change)
                    self.dude.update_financial((price_number, change_number, datetime.now(), stock.company))
                    self.logger.info(f"Public financial {stock.company} updated in DB")
                except Exception:
                    self.logger.error(f"Unable to retrieve or parse existing public financial: {stock}", exc_info=True)

    def run(self):
        try:
            self.retrieve_political()
        except Exception:
            self.logger.error('Unexpected error occurred during retrieve_political', exc_info=True)
        try:
            self.retrieve_environmental()
        except Exception:
            self.logger.error('Unexpected error occurred during retrieve_environmental', exc_info=True)
        try:
            self.retrieve_financial()
        except Exception:
            self.logger.error('Unexpected error occurred during retrieve_financial', exc_info=True)
        time.sleep(self.round_sleep_time)

if __name__ == '__main__':
    fetcher = DataFetcher('config.ini')
    fetcher.run()
