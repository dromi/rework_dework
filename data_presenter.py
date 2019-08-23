from random import choices, choice
from time import sleep

from database.db_dude import DBDude

WEIGHTS = {
    'financial_private': 1.0,
    'financial_public': 1.0,
    'environmental': 1.0,
    'political': 1.0
}

def fetch_next():
    dude = DBDude()
    category = choices(list(WEIGHTS.keys()), weights=WEIGHTS.values())[0]
    if category == 'financial_public':
        return choice(dude.select_all_financial_public())
    elif category == 'financial_private':
        return choice(dude.select_all_financial_private())
    elif category == 'environmental':
        return choice(dude.select_all_environmental())
    elif category == 'political':
        return choice(dude.select_all_political())
    else:
        print("Error: Choice not recognized")


if __name__ == '__main__':
    while(True):
        next_item = fetch_next()
        print(next_item)
        sleep(2)