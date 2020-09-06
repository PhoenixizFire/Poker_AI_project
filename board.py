from cards import Deck

class Board:

    def __init__(self):
        self.pot = 0
        self.small_blind = int()
        self.big_blind = int()
        self.current_bid = 0
        self.community_cards = list()

    @property
    def current_bid(self,value):
        self._current_bid = value

    @current_bid.getter
    def current_bid(self):
        return self._current_bid