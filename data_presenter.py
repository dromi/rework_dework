from configparser import ConfigParser
from random import choices, choice
import time

from database.db_dude import DBDude

WEIGHTS = {
    'financial_private': 1.0,
    'financial_public': 1.0,
    'environmental': 1.0,
    'political': 1.0
}


class DataPresenter():
    def __init__(self, config_path):
        self.config = ConfigParser()
        self.config.read(config_path)

        self.round_sleep_time = self.config.getint('presenter', 'sleep_time')

        self.dude = DBDude(self.config['general']['db_file'])

    def fetch_next(self):
        category = choices(list(WEIGHTS.keys()), weights=WEIGHTS.values())[0]
        if category == 'financial_public':
            return choice(self.dude.select_all_financial_public())
        elif category == 'financial_private':
            return choice(self.dude.select_all_financial_private())
        elif category == 'environmental':
            return choice(self.dude.select_all_environmental())
        elif category == 'political':
            return choice(self.dude.select_all_political())
        else:
            print("Error: Choice not recognized")

    def run(self):
        #TODO find better condition
        while True:
            next_item = self.fetch_next()
            print(next_item)
            time.sleep(self.round_sleep_time)
