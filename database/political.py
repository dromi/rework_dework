class Political:
    def __init__(self, external_id, title, summary, feed, published, id=None):
        self.external_id = external_id
        self.title = title
        self.summary = summary
        self.feed = feed
        self.published = published
        self.id = id

    @staticmethod
    def from_tuple(data_tuple):
        id, external_id, title, summary, feed, published = data_tuple
        return Political(external_id, title, summary, feed, published, id)

    def to_tuple_insert(self):
        return self.external_id, self.title, self.summary, self.feed, self.published