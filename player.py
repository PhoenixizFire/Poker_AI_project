class Player:

    def __init__(self,idty,money,bot=None):
        self.id = idty #Identité du joueur
        self.money = money #Argent du joueur
        self.hand = list() #Cartes en main du joueur
        self.dealer = False # Est-il le dealer sur la manche ?
        self.small_blind = False # Est-il small blind sur la manche ?
        self.big_blind = False # Est-il big blind sur la manche ?
        self.current_bet = int() # Combien a-t-il de jetons devant lui pour ce tour ?
        self.last_move = str()
        self.active = True # Le joueur est-il toujours actif ou s'est-il couché ?
        self.all_in = False # Le joueur a-t-il fait tapis ?
        self.checked = False # Le joueur a-t-il check ? 
        self.combo_score = 0
        self.kickers = list()
        self.bot = bot

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

    @property
    def money(self):
        return self._money

    @money.setter
    def money(self,value):
        self._money = value

    def __repr__(self):
        if self.bot==None:
            return f"\nPlayer {self.id} :\n{self.hand} ; Current money : {self.money} $ ; Bet : {self.current_bet}\n"
        else:
            return f"\n[BOT]({self.bot.mind}) Player {self.id} :\n{self.hand} ; Current money : {self.money} $ ; Bet : {self.current_bet}\n"            

    def __del__(self):
        print(f"Deleting player {self.id}")

    def _add_money(self,value):
        self.money+=value

    def set_blind(self,auto=0):
        if auto==0:
            bet = "bet"
        else:
            bet = str(auto)
        if self.small_blind==True:
            arg = "small"
            self.last_move = 'Blind'
        elif self.big_blind==True:
            arg = "big"
            self.last_move = 'Blind'
        while not bet.isdecimal():
            bet = input(f"Setting {arg} blind. How much do you pay, player {self.id} ? ")
        bet = int(bet)
        if bet>self.money:
            bet = self.money
        self.money-=bet
        self.current_bet+=bet
        if self.money==0:
            self.all_in=True
        return bet

    def call(self,bid):
        # Pay same as Big Blind (First turn or if someone already bet in further turns)
        difference = bid - self.current_bet
        self.checked = False
        self.money-=difference
        self.current_bet+=difference
        print(f"Player {self.id} calls : {self.current_bet}")
        print(self)

    def relaunch(self,bid,qty="qty"): #raise
        # Pay more than Big Blind (First turn or if someone already bet in further turns)
        self.checked = False
        print(f"ALERT : {self.money}")
        if self.bot!=None:
            qty = self.bot.action_relaunch(self.money,bid)
            while qty+self.current_bet<bid or qty>self.money:
                print(qty)
                qty = self.bot.action_relaunch(self.money,bid)
            qty = str(qty)
            print(f"Player {self.id} raised to {qty}")
        while not qty.isdecimal():
            qty = input(f"How much do you want to raise to, player {self.id} ? ")
        qty = int(qty)
        difference = qty-self.current_bet
        if difference>self.money:
            difference=self.money
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
        print(f"Player {self.id} folds")
        return active_pot

    def bet(self,bet="bet"):
        # Second turn and further
        self.checked = False
        if self.bot!=None:
            bet = self.bot.action_bet(self.money)
            bet = str(bet)
            print(f"Player {self.id} bets {bet}")
        while not bet.isdecimal():
            bet = input(f"How much do you wanna bet, player {self.id} ? ")
        bet = int(bet)
        if bet>self.money:
            bet=self.money
        self.money-=bet
        self.current_bet+=bet
        print(self)
        if self.money==0:
            self.all_in=True
        return self.current_bet

    def check(self):
        self.checked = True
        # Second turn and further only if nobody bet before you (wait for other players to play)
        print(f"Player {self.id} folds")
        print(self)

    def tapis(self):
        self.checked = False
        self.current_bet+=self.money
        self.money = 0
        self.all_in = True
        print(f"Player {self.id} goes all-in : {self.current_bet}")
        return self.current_bet

    def reset_move(self):
        self.last_move = ''