import random

class Bot:

    def __init__(self,mind = "None"):
        self.mind = mind
        self.fold = int()
        self.bet = int()
        self.check = int()
        self.call = int()
        self.relaunch = int()
        self.all_in = int()
        self.money = int()
        self.define_spirit()

    def __repr__(self):
        return f"Mind : {self.mind} ; \
                 Fold : {self.fold} ; \
                 Bet : {self.bet} ; \
                 Check : {self.check} ; \
                 Call : {self.call} ; \
                 Relaunch : {self.relaunch}"
    
    def define_spirit(self): # "Folder","Coward","Payer","Follower","Risky","Rich"
        if self.mind == "None":
            self.fold = 10
            self.bet = 25
            self.check = 35
            self.call = 35
            self.relaunch = 25
            self.all_in = 2
            self.money = 4
        if self.mind == "Random":
            self.fold = random.randint(1,90)
            self.bet = random.randint(1,50)
            self.check = random.randint(1,75)
            self.call = random.randint(1,75)
            self.relaunch = random.randint(1,25)
            self.all_in = random.randint(1,10)
            self.money = random.randint(1,9)
        if self.mind == "Coward":
            self.fold = random.randint(1,100)
            self.bet = random.randint(1,50)
            self.check = random.randint(1,50)
            self.call = random.randint(1,50)
            self.relaunch = random.randint(1,50)
            self.all_in = random.randint(1,10)
            self.money = random.randint(1,3)
        if self.mind == "Payer":
            self.fold = random.randint(1,50)
            self.bet = random.randint(1,100)
            self.check = random.randint(1,50)
            self.call = random.randint(1,50)
            self.relaunch = random.randint(1,50)
            self.all_in = random.randint(1,50)
            self.money = random.randint(3,9)
        if self.mind == "Follower":
            self.fold = random.randint(1,50)
            self.bet = random.randint(1,50)
            self.check = random.randint(1,100)
            self.call = random.randint(1,100)
            self.relaunch = random.randint(1,50)
            self.all_in = random.randint(1,30)
            self.money = random.randint(2,7)
        if self.mind == "Risky":
            self.fold = random.randint(1,50)
            self.bet = random.randint(1,50)
            self.check = random.randint(1,50)
            self.call = random.randint(1,50)
            self.relaunch = random.randint(1,100)
            self.all_in = random.randint(1,100)
            self.money = random.randint(5,9)
        if self.mind == "Rich":
            self.fold = random.randint(1,50)
            self.bet = random.randint(1,100)
            self.check = random.randint(1,50)
            self.call = random.randint(1,50)
            self.relaunch = random.randint(1,100)
            self.all_in = random.randint(1,60)
            self.money = random.randint(1,9)

    def action(self,available_moves):
        move_dict = dict()
        if "Fold" in available_moves:
            move_dict["Fold"] = self.fold
        if "Bet" in available_moves:
            move_dict["Bet"] = self.bet
        if "Check" in available_moves:
            move_dict["Check"] = self.check
        if "Call" in available_moves:
            move_dict["Call"] = self.call
        if "Raise" in available_moves:
            move_dict["Raise"] = self.relaunch
        if "All-in" in available_moves:
            move_dict["All-in"] = self.all_in
        act,val = zip(*move_dict.items())
        return random.choices(act,weights=val)[0]

    def action_relaunch(self,money,bid):
        cut = money//9
        if cut==0:
            cut = 1
        if cut*self.money<=2*bid:
            relaunch = random.randint(2*bid+1,2*bid+cut)
        else:
            relaunch = random.randint(cut*self.money-1,cut*self.money)
            while relaunch==0:
                relaunch = random.randint(cut*self.money-1,cut*self.money)
        return relaunch

    def action_bet(self,money): #TODO régler le problème de la mise négative
        cut = money//9 #IF MONEY < 9 alors CUT = 0
        if cut==0:
            cut = 1
        bet = random.randint(cut*self.money-1,cut*self.money)
        while bet==0:
            bet = random.randint(cut*self.money-1,cut*self.money)
        return bet


