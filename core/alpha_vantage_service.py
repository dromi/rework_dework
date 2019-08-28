import json
import logging

import requests


class AlphaVantageService:
    def __init__(self, credentials_file_path):
        with open(credentials_file_path) as file:
            self.api_key = json.load(file)['alpha_vantage_api_key']
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.INFO)

    def get_stock_quote(self, symbol):
        self.logger.info(f"Performing GLOBAL_QUOTE GET Request for symbol: {symbol}")
        response = requests.get("https://www.alphavantage.co/query", params={"function": "GLOBAL_QUOTE",
                                                                             "symbol": symbol,
                                                                             "apikey": self.api_key})
        json_data = json.loads(response.content)
        if self._validate_quote_response(json_data):
            self.logger.info(f"Got response: {json_data}")
            quote = json_data['Global Quote']
            return quote['05. price'], quote['09. change']
        else:
            self.logger.warning(f"Symbol {symbol} received improper quote response {json_data}")

    def _convert_to_cents(self, amount):
        return int(round(float(amount) * 100))

    def _validate_quote_response(self, quote):
        if 'Global Quote' in quote:
            if '05. price' in quote['Global Quote'] and '09. change' in quote['Global Quote']:
                return True
        return False
