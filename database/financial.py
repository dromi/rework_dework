from datetime import datetime


class Financial:
    def __init__(self, symbol, name, price, change, timestamp=None, id=None):
        self.symbol = symbol
        self.name = name
        self.price = price
        self.change = change
        self.timestamp = timestamp
        self.id = id
        if self.timestamp is None:
            self.timestamp = datetime.now()

    @staticmethod
    def from_tuple(data_tuple):
        id, symbol, name, price, change, timestamp = data_tuple
        return Financial(symbol, name, price, change, timestamp, id)

    def to_tuple_insert(self):
        return self.symbol, self.name, self.price, self.change, self.timestamp

    def get_percent_change(self):
        return self.change / self.price
