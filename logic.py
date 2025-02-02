from random import shuffle

from flask_socketio import emit

from cards import *
from user import User


class Game:
    """Object to save the state of the current game"""

    discard_pile = []
    draw_pile = []
    all_cards = []
    draw_number = 0
    users: dict[str, User] = {}

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

    def reset(self):
        """Resets the game for a new round"""
        for user in self.users.values():
            user.cards.clear()
        self.discard_pile.clear()
        self.draw_pile.clear()
        self.draw_number = 0
        self.draw_pile = list(self.all_cards)
        shuffle(self.draw_pile)


game = Game()


def update_leaderboard():
    sorted_users = sorted(game.users.values(), key=lambda user: user.score, reverse=True)
    leaderboard = {user.name: user.score for user in sorted_users}
    emit("update_leaderboard", leaderboard, broadcast=True)


def trigger_won(user_id):
    """Handles updating the leaderboard and informing the clients about a winning user"""
    # TODO: Different scores for player counts > 2
    game.users[user_id].score += 1
    update_leaderboard()
    emit("player_won", {"winner": user_id}, broadcast=True)


def trigger_game_over():
    game.reset()
    reset_draw()
    emit("game_over", broadcast=True)


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
    emit("set_user", {"user_id": user_id, "name": game.users[user_id].name}, broadcast=True)


def set_next_user(user_id):
    """Continues to the next user"""
    # TODO: Write proper implementation, this one's just for testing
    set_user(list(game.users.keys())[(list(game.users.keys()).index(user_id) + 1) % 2])


def get_card(id):
    """Gets a card by id"""
    return game.all_cards[game.all_cards.index(id)]


def draw_card(user_id):
    """Handles the drawing of cards, including refreshing the draw_pile"""
    # TODO: Check if draw_pile needs to be refilled
    drawn_card = game.draw_pile.pop()
    game.users[user_id].cards.append(drawn_card)
    emit("receive_card", {"id": drawn_card.id}, to=user_id)


def can_play_card(user_id, id):
    """Returns True if a card can be played else False"""
    # TODO: Check if card can be played
    card = game.users[user_id].cards[game.users[user_id].cards.index(id)]
    return True


def play_card(user_id, id):
    """Handles playing a card"""
    card = game.users[user_id].cards.pop(game.users[user_id].cards.index(id))
    game.discard_pile.append(card)
    # TODO: Handle action cards and stuff
    if card.card_type == CardType.PlusFour:
        increase_draw(4)
    if len(game.users[user_id].cards) <= 0:
        trigger_won(user_id)
        trigger_game_over()
    set_next_user(user_id)
