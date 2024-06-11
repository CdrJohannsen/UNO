from enum import Enum


class CardColor(Enum):
    Red = "#FF5555"
    Green = "#55AA55"
    Blue = "#5555FF"
    Yellow = "#FFAA00"
    Black = "#000000"


class CardType(Enum):
    Zero = 0
    One = 1
    Two = 2
    Three = 3
    Four = 4
    Five = 5
    Six = 6
    Seven = 7
    Eight = 8
    Nine = 9
    Skip = 10
    Reverse = 11
    PlusTwo = 12
    ColorChange = 13
    PlusFour = 14


card_id = 0


class Card:
    def __init__(self, color, card_type, special = False) -> None:
        self.color = color
        self.card_type = card_type
        self.is_special = special
        global card_id
        self.id = card_id
        card_id += 1

    def get_image(self):
        return f"card_{self.card_type.value}.png"

    def get_data(self):
        return f"{self.color.value}-{self.card_type.value}"

    def get_description(self):
        return f"{self.color.name}-{self.card_type.name}"

    def __eq__(self, __value) -> bool:
        return __value == self.id
