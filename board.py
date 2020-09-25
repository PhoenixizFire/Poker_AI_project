from cards import Deck

class Board:

    def __init__(self):
        self.pot = 0
        self.small_blind = int()
        self.big_blind = int()
        self.current_bid = 0
        self.community_cards = list()
        self.side_pots = list()

    @property
    def current_bid(self):
        return self._current_bid

    @current_bid.setter
    def current_bid(self,value):
        self._current_bid = value

    @property
    def side_pots(self):
        return self._side_pots

    @side_pots.setter
    def side_pots(self,situation): #???
        pass #Schéma : List of {"players":list(),"value":int()} for each side pot