from random import shuffle

from flask_socketio import emit

from cards import *


class Game:
    """Object to save the state of the current game"""
    cards = {}
    discard_pile = []
    draw_pile = []
    all_cards = []
    draw_number = 0
    users = {}

    def __init__(self) -> None:
        for color in list(CardColor._member_map_.values())[:-1]:
            for c_type in list(CardType._member_map_.values())[:-2]:
                self.all_cards.append(Card(color, c_type))
                if not c_type == CardType.Zero:
                    self.all_cards.append(Card(color, c_type))
        for i in range(4):
            self.all_cards.append(Card(CardColor.Black, CardType.ColorChange))
        for i in range(4):
            self.all_cards.append(Card(CardColor.Black, CardType.PlusFour))
        self.draw_pile = list(self.all_cards)
        shuffle(self.draw_pile)


game = Game()


def reset_draw():
    """Reset the number of cards that need to be drawn
    Use this function instead of directly modifying draw_number"""
    game.draw_number = 0
    emit("draw_update", {"number": game.draw_number}, broadcast=True)


def increase_draw(n):
    """Increased the number of cards that need to be drawn by n
    Use this function instead of directly modifying draw_number"""
    game.draw_number += n
    emit("draw_update", {"number": game.draw_number}, broadcast=True)


def set_user(user_id):
    """Informs the clients about the new user"""
    emit("set_user", {"user_id": user_id, "name": game.users[user_id]}, broadcast=True)

def set_next_user(user_id):
    """Continues to the next user"""
    # TODO: Write proper implementation, this one's just for testing
    set_user(list(game.users.keys())[(list(game.users.keys()).index(user_id)+1)%2])


def get_card(id):
    """Gets a card by id"""
    return game.all_cards[game.all_cards.index(id)]


def draw_card(user_id):
    """Handles the drawing of cards, including refreshing the draw_pile"""
    # TODO: Check if draw_pile needs to be refilled
    drawn_card = game.draw_pile.pop()
    game.cards[user_id].append(drawn_card)
    emit("receive_card", {"id": drawn_card.id})


def can_play_card(user_id, id):
    """Returns True if a card can be played else False"""
    # TODO: Check if card can be played
    return True


def play_card(user_id, id):
    """Handles playing a card"""
    card = game.cards[user_id].pop(game.cards[user_id].index(id))
    game.discard_pile.append(card)
    # TODO: Handle action cards and stuff
    if card.card_type == CardType.PlusFour:
        increase_draw(4)
    set_next_user(user_id)
