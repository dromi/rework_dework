import json

import requests

from database.financial import Financial

CRED_FILE = "sources/credentials.json"


class AlphaVantageService:
    def __init__(self):
        with open(CRED_FILE) as file:
            self.api_key = json.load(file)['alpha_vantage_api_key']

    def get_stock_quote(self, symbol, company_name):
        response = requests.get("https://www.alphavantage.co/query", params={"function": "GLOBAL_QUOTE",
                                                                             "symbol": symbol,
                                                                             "apikey": self.api_key})
        quote = json.loads(response.content)['Global Quote']
        price = self._convert_to_cents(quote['05. price'])
        change = self._convert_to_cents(quote['09. change'])
        return Financial(symbol, company_name, price, change)

    def _convert_to_cents(self, amount):
        return int(round(float(amount) * 100))
