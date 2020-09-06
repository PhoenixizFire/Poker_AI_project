class Player:

    def __init__(self,idty,money):
        self.id = idty
        self.money = money
        self.hand = list()
        self.dealer = False
        self.small_blind = False
        self.big_blind = False
        self.current_bet = int()
        self.active = True

    @property
    def dealer(self):
        return self._dealer

    @dealer.setter
    def dealer(self,boolean):
        self._dealer = boolean
    
    @property
    def small_blind(self):
        return self._small_blind

    @small_blind.setter
    def small_blind(self,boolean):
        self._small_blind = boolean

    @property
    def big_blind(self):
        return self._big_blind

    @big_blind.setter
    def big_blind(self,boolean):
        self._big_blind = boolean

    def __repr__(self):
        return f"Player {self.id} :\n{self.hand} ; Current money : {self.money} $ ; Bet : {self.current_bet}"

    def set_blind(self):
        if self.small_blind==True:
            arg = "small"
        elif self.big_blind==True:
            arg = "big"
        bet = input(f"Setting {arg} blind. How much do you pay player {self.id} ? ")
        bet = int(bet)
        self.money-=bet
        self.current_bet+=bet
        return bet

    def call(self):
        # Pay same as Big Blind (First turn or if someone already bet in further turns)
        pass

    def relaunch(self): #raise
        # Pay more than Big Blind (First turn or if someone already bet in further turns)
        pass

    def fold(self):
        # Down the hand without paying further (any turn)
        self.active = False

    def bet(self):
        # Second turn
        pass

    def check(self):
        # Second turn and further only if nobody bet before you (wait for other players to play)
        pass