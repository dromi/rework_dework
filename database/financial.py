from datetime import datetime

from dateutil import parser


class Financial:
    def __init__(self, company: str, type: str, industry: str, price: int, change: int, currency: str,
                 symbol: str=None, timestamp: datetime=None, id: int=None):
        self.symbol = symbol
        self.company = company.upper()
        self.type = type
        self.industry = industry
        self.price = price
        self.change = change
        self.currency = currency.upper()
        self.timestamp = timestamp
        self.id = id
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def __str__(self):
        if self.type == 'public':
            return f"{self.company} {self.price/100} {self.currency} {self.print_growth()}{self.change/100} ({self.get_percent_change()}%)"
        elif self.type == 'private':
            return self.company + " " + self._pretty_price(self.price) + " " + self.currency

    @staticmethod
    def from_tuple(data_tuple):
        id, symbol, company, type, industry, price, currency, change, timestamp = data_tuple
        timestamp_formatted = parser.parse(timestamp)
        return Financial(company=company, type=type, industry=industry, price=price, currency=currency, change=change,
                         symbol=symbol, timestamp=timestamp_formatted, id=id)

    def to_tuple_insert(self):
        return self.symbol, self.company, self.type, self.industry, self.price, self.currency, self.change, \
               self.timestamp

    @staticmethod
    def create_private(company, industry, price, currency, timestamp=None):
        # Convert price from string to number
        price_number = Financial.convert_str_price(price)
        return Financial(company=company, type='private', industry=industry, price=price_number, change=0,
                         currency=currency, timestamp=timestamp)

    @staticmethod
    def create_public(company, industry, price, change, currency, symbol, timestamp=None):
        # Convert price from string to number
        price_number = Financial.convert_str_price(price)
        change_number = Financial.convert_str_price(change)
        return Financial(company=company, type='public', industry=industry, price=price_number, change=change_number,
                         symbol=symbol, currency=currency, timestamp=timestamp)

    def get_percent_change(self):
        return round((self.change / self.price) * 100, 2)

    @staticmethod
    def convert_str_price(price_str):
        split_price = price_str.split()
        if len(split_price) == 2:
            number, scalar = split_price
            scalar_dict = {
                'million': 10**6,
                'billion': 10**9,
            }
            price = float(number) * scalar_dict[scalar]
            return Financial._convert_to_cents(price)
        else:
            return Financial._convert_to_cents(float(split_price[0]))

    @staticmethod
    def _convert_to_cents(amount):
        return int(round(float(amount) * 100))

    @staticmethod
    def _pretty_price(price):
        main_unit_price = int(Financial._convert_to_main_units(price))
        price_length = len(str(main_unit_price))
        if price_length > 9:
            return str(main_unit_price/10**9) + " Bill."
        elif price_length > 6:
            return str(main_unit_price/10**6) + " Mill."
        else:
            return str(main_unit_price)

    @staticmethod
    def _convert_to_main_units(amount):
        return amount/100

    def print_growth(self):
        return "+" if self.change >= 0 else ""

    def produce_id(self):
        return f"fin_{self.id}"
