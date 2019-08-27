import sys
from configparser import ConfigParser
from random import choices, choice
import time

import pygame

from database.db_dude import DBDude
from scroll_text import ScrollText

WEIGHTS = {
    'financial_private': 1.0,
    'financial_public': 1.0,
    'environmental': 1.0,
    'political': 1.0
}

white = (255, 255, 255)
green = (0, 255, 0)
blue = (0, 0, 255)
red = (255, 0, 0)

COLORS = {
    'financial_private': blue,
    'financial_public': blue,
    'environmental': red,
    'political': green
}


pygame.init()

class DataPresenter():
    def __init__(self, config_path):
        self.config = ConfigParser()
        self.config.read(config_path)

        self.dude = DBDude(self.config['general']['db_file'])

        self.sleep_time = self.config.getfloat('presenter', 'sleep_time')
        self.screen_width = self.config.getint('presenter', 'screen_width')
        self.screen_height = self.config.getint('presenter', 'screen_height')
        self.font = self.config['presenter']['font']
        self.font_size = self.config.getint('presenter', 'font_size')
        self.delta_y = self.config.getint('presenter', 'delta_y')
        self.margin_x = self.config.getint('presenter', 'margin_x')
        self.margin_y = self.config.getint('presenter', 'margin_y')

        self.line_length = self._determine_line_chars()
        self.scrolling_texts = []

    def fetch_next(self):
        category = choices(list(WEIGHTS.keys()), weights=WEIGHTS.values())[0]
        if category == 'financial_public':
            chosen = choice(self.dude.select_all_financial_public())
        elif category == 'financial_private':
            chosen = choice(self.dude.select_all_financial_private())
        elif category == 'environmental':
            chosen = choice(self.dude.select_all_environmental())
        elif category == 'political':
            chosen = choice(self.dude.select_all_political())
        else:
            print("Error: Choice not recognized")
            return None, None

        # Ensure that the new fetch isn't already being displayed
        if chosen.produce_id() in [text.data_id for text in self.scrolling_texts]:
            return self.fetch_next()
        else:
            return chosen, COLORS[category]

    def run(self):
        screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        font = pygame.font.SysFont(self.font, self.font_size)

        while True:
            # check for quit events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # TODO: Find a way for this to work also on a multi thread setup
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.delta_y = 0 if self.delta_y == 1 else 1

            screen.fill(0)

            # MAIN LOOP DESCRIPTION:
            #
            # Check that there is a scrolltext above the screen
            # if not add one
            # translate all items down
            # check if any have gone off screen
            # If so move to top of stack (find the one with min y and move above him)

            if not any(text.top_y < 0 for text in self.scrolling_texts):
                text_item, color = self.fetch_next()
                self.scrolling_texts.append(ScrollText(text_item.__str__(), text_item.produce_id(), self.line_length,
                                                       font, color, self.margin_x, self.margin_y))

            for text_scroll in self.scrolling_texts:
                text_scroll.translate(self.delta_y)
                text_scroll.render(screen)
                if text_scroll.top_y > self.screen_height:
                    offset = min([text.top_y for text in self.scrolling_texts])
                    text_scroll.reset(abs(offset), self.fetch_next())
            pygame.display.update()
            time.sleep(self.sleep_time)

    def _determine_line_chars(self):
        font = pygame.font.SysFont(self.font, self.font_size)
        char_length = 1
        while font.size("A"*char_length)[0] < (self.screen_width - 2 * self.margin_x):
            char_length += 1
        return char_length - 1


if __name__ == '__main__':
    presenter = DataPresenter('config.ini')
    presenter.run()
