from cards import Deck

class Board:

    def __init__(self):
        self.pot = int()
        self.small_blind = int()
        self.big_blind = int()
        self.current_bid = int()
        self.community_cards = list()