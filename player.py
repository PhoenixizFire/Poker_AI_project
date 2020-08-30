class Player:

    def __init__(self,money):
        self.money = money
        self.hand = list()
        self.dealer = False
        self.small_blind = False
        self.big_blind = False

    def set_blind(self):
        pass

    def call(self):
        # Pay same as Big Blind (First turn or if someone already bet in further turns)
        pass

    def relaunch(self): #raise
        # Pay more than Big Blind (First turn or if someone already bet in further turns)
        pass

    def fold(self):
        # Down the hand without paying further (any turn)
        pass

    def bet(self):
        # Second turn
        pass

    def check(self):
        # Second turn and further only if nobody bet before you (wait for other players to play)
        pass