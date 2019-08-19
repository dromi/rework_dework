class Environmental:
    def __init__(self, name, pretty_name, base_value, increment, retrieval, id=None):
        self.name = name
        self.pretty_name = pretty_name
        self.base_value = base_value
        self.increment = increment
        self.retrieval = retrieval
        self.id = id

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
