import pygame


class ScrollText:
    def __init__(self, text_item: any, data_id: str, line_length: int, font: pygame.font.Font, color: tuple,
                 margin_x: int, margin_y: int):
        self.text_item = text_item
        self.data_id = data_id
        self.line_length = line_length
        self.font = font
        self.color = color
        self.margin_x = margin_x
        self.margin_y = margin_y

        self.text_lines = self._split_string()
        self.text_objects = [self.font.render(t, True, self.color) for t in self.text_lines]
        self.height = (len(self.text_objects) * self.text_objects[0].get_size()[1]) + self.margin_y
        self.top_y = 0 - self.height

    def _split_string(self):
        words = self.text_item.__str__().split()
        lines = []
        current_line = []
        while len(words) > 0:
            section_len = sum([len(s) for s in current_line]) + len(current_line) - 1
            if (section_len + len(words[0]) + 1 <= self.line_length) or (len(words[0]) > self.line_length):
                current_line.append(words[0])
                words.pop(0)
            else:
                lines.append(' '.join(current_line))
                current_line = []
        if len(current_line) > 0:
            lines.append(' '.join(current_line))
        return lines

    def translate(self, delta_y: int):
        self.top_y += delta_y

    def render(self, screen: pygame.Surface):
        self.text_lines = self._split_string()
        self.text_objects = [self.font.render(t, True, self.color) for t in self.text_lines]
        line_height = self.text_objects[0].get_size()[1]
        for i, text in enumerate(self.text_objects):
            screen.blit(text, (self.margin_x, i * line_height + self.top_y))

    def reset(self, offset: int, text_item, color):
        self.text_item = text_item
        self.data_id = text_item.produce_id()
        self.color = color
        self.text_lines = self._split_string()
        self.text_objects = [self.font.render(t, True, self.color) for t in self.text_lines]
        self.height = (len(self.text_objects) * self.text_objects[0].get_size()[1]) + self.margin_y
        self.top_y = 0 - self.height - offset
