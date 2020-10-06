class Player:

    def __init__(self,idty,money):
        self.id = idty #Identité du joueur
        self.money = money #Argent du joueur
        self.hand = list() #Cartes en main du joueur
        self.dealer = False # Est-il le dealer sur la manche ?
        self.small_blind = False # Est-il small blind sur la manche ?
        self.big_blind = False # Est-il big blind sur la manche ?
        self.current_bet = int() # Combien a-t-il de jetons devant lui pour ce tour ?
        self.active = True # Le joueur est-il toujours actif ou s'est-il couché ?
        self.all_in = False # Le joueur a-t-il fait tapis ?
        self.checked = False # Le joueur a-t-il check ? 
        self.combo_score = 0
        self.kickers = list()

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
        return f"\nPlayer {self.id} :\n{self.hand} ; Current money : {self.money} $ ; Bet : {self.current_bet}\n"

    def __del__(self):
        print(f"Deleting player {self.id}")
        del self

    def set_blind(self,auto=0):
        if auto==0:
            bet = "bet"
        else:
            bet = str(auto)
        if self.small_blind==True:
            arg = "small"
        elif self.big_blind==True:
            arg = "big"
        while not bet.isdecimal():
            bet = input(f"Setting {arg} blind. How much do you pay, player {self.id} ? ")
        bet = int(bet)
        self.money-=bet
        self.current_bet+=bet
        return bet

    def call(self,bid):
        # Pay same as Big Blind (First turn or if someone already bet in further turns)
        difference = bid - self.current_bet
        self.money-=difference
        self.current_bet+=difference
        print(self)

    def relaunch(self,bid): #raise
        # Pay more than Big Blind (First turn or if someone already bet in further turns)
        qty = "qty"
        while not qty.isdecimal():
            qty = input(f"How much do you want to raise to, player {self.id} ? ")
        qty = int(qty)
        difference = qty-self.current_bet
        self.money-=difference
        self.current_bet+=difference
        print(self)
        if self.money==0:
            self.all_in=True
        return self.current_bet

    def fold(self,pot):
        # Down the hand without paying further (any turn)
        active_pot = pot['value']
        self.active = False
        active_pot += self.current_bet
        self.current_bet = 0
        return active_pot

    def bet(self):
        # Second turn and further
        bet = "bet"
        while not bet.isdecimal():
            bet = input(f"How much do you wanna bet, player {self.id} ? ")
        bet = int(bet)
        self.money-=bet
        self.current_bet+=bet
        print(self)
        return self.current_bet

    def check(self):
        # Second turn and further only if nobody bet before you (wait for other players to play)
        print(self)

    def tapis(self):
        self.current_bet+=self.money
        self.money = 0
        print("Self.all_in=False")
        self.all_in = True
        print("Self.all_in=True")
        return self.current_bet