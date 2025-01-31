from cards import Card


class User:
    def __init__(self, name: str) -> None:
        self.id = 0
        self.name: str = name
        self.score: int = 0
        self.cards: list[Card] = []
