from datetime import datetime


class Environmental:
    def __init__(self, name, pretty_name, base_value, increment, retrieval, id=None):
        self.name = name
        self.pretty_name = pretty_name
        self.base_value = base_value
        self.increment = increment
        self.retrieval = retrieval
        self.id = id

    def __str__(self):
        return self.pretty_name.upper() + ": " + str(round(self.measure_current_value(), 2))

    @staticmethod
    def from_tuple(data_tuple):
        id = data_tuple[0]
        name = data_tuple[1]
        pretty_name = data_tuple[2]
        base_value = data_tuple[3]
        increment = data_tuple[4]
        retrieval = data_tuple[5]
        return Environmental(name, pretty_name, base_value, increment, retrieval, id)

    def to_tuple_insert(self):
        return self.name, self.pretty_name, self.base_value, self.increment, self.retrieval

    def measure_current_value(self):
        time_delta = datetime.now() - datetime.strptime(self.retrieval, '%Y-%m-%d %H:%M:%S.%f')
        return self.base_value + (self.increment * time_delta.seconds)

    def produce_id(self):
        return f"env_{self.id}"
