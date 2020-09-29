from cards import Deck

class Board:

    def __init__(self):
        self.pot = 0
        self.small_blind = int()
        self.big_blind = int()
        self.current_bid = 0
        self.community_cards = list()
        self.side_pots = list()

    def __repr__(self):
        return f"\nCards :\n{self.community_cards} ; Pot : {self.pot}\n"

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

    def highest_card(self,player):
        max_value = 0
        for i in self.community_cards+player.cards:
            if i.value>max_value:
                high_card = i
        return high_card

    def one_pair(self,player):
        for i in self.community_cards+player.cards:
            for j in self.community_cards+player.cards:
                if i.value==j.value:
                    if i.figure==j.figure:
                        pass
                    else:
                        return [i,j]
        return None

    def two_pair(self,player):
        pass

    def three_of_a_kind(self,player):
        pass

    def straight(self,player):
        pass

    def flush(self,player):
        pass

    def full_house(self,player):
        pass

    def four_of_a_kind(self,player):
        pass

    def straight_flush(self,player):
        pass

    def royal_flush(self,player):
        pass