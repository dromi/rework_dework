import json
from datetime import datetime
import re

import requests
from bs4 import BeautifulSoup

from database.db_dude import DBDude
from database.environmental import Environmental

ENVIRONMENTAL_SRCS = 'sources/environmental.json'


def _first_lower(s):
    if len(s) == 0:
        return s
    else:
        return s[0].lower() + s[1:]


if __name__ == '__main__':
    dude = DBDude()
    dude.delete_all_environmental()
    print(dude.select_all_environmental())

    with open(ENVIRONMENTAL_SRCS) as file:
        environments = json.load(file)

    for env_name, env_url in environments.items():
        print("Fetching: ", env_name)
        env_response = requests.get(env_url)
        if env_response.status_code != 200:
            print("Bad response code")
            exit(0)

        env_html = BeautifulSoup(env_response.content, features="html.parser")
        big_counter = env_html.find('div', class_='big-counter')
        # Get pretty name
        h2_header = big_counter.find('h2')
        sub_title = _first_lower(h2_header.find_next_sibling('p').text.replace('\n', ''))
        pretty_name = h2_header.text.replace('\n', '') + " " + sub_title
        # Get increment and base_value
        script = big_counter.find('script')
        types = re.search('number_interval\((-?[\d\.e\-]+), (-?[\d\.e\-]+)', script.text)
        base_value, increment = types.groups()

        # create a new project
        dude.create_environmental(Environmental(env_name, pretty_name, base_value, increment, datetime.now()))
