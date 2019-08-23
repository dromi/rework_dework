import json
import requests

CRED_FILE = "sources/credentials.json"


class AlphaVantageService:
    def __init__(self):
        with open(CRED_FILE) as file:
            self.api_key = json.load(file)['alpha_vantage_api_key']

    def get_stock_quote(self, symbol):
        print("Performing AlphaVantage GET Request: ", {"function": "GLOBAL_QUOTE","symbol": symbol,"apikey": self.api_key})
        response = requests.get("https://www.alphavantage.co/query", params={"function": "GLOBAL_QUOTE",
                                                                             "symbol": symbol,
                                                                             "apikey": self.api_key})
        json_data = json.loads(response.content)
        if self._validate_quote_response(json_data):
            print("Success: AlphaVantage Got response:")
            print(json_data)
            quote = json_data['Global Quote']
            return quote['05. price'], quote['09. change']
        else:
            print("Error: AlphaVantage did not provide proper quote response. Got response:")
            print(json_data)

    def _convert_to_cents(self, amount):
        return int(round(float(amount) * 100))

    def _validate_quote_response(self, quote):
        if 'Global Quote' in quote:
            if '05. price' in quote['Global Quote'] and '09. change' in quote['Global Quote']:
                return True
        return False
