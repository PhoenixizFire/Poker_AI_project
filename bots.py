import random

class Bot:

    def __init__(self,mind = "None"):
        self.mind = mind
        self.fold = int()
        self.bet = int()
        self.check = int()
        self.call = int()
        self.relaunch = int()
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
        if self.mind == "Random":
            self.fold = random.randint(1,100)
            self.bet = random.randint(1,100)
            self.check = random.randint(1,100)
            self.call = random.randint(1,100)
            self.relaunch = random.randint(1,100)
            self.money = random.randint(1,9)
        if self.mind == "Coward":
            self.fold = random.randint(50,100)
            self.bet = random.randint(1,50)
            self.check = random.randint(1,50)
            self.call = random.randint(1,50)
            self.relaunch = random.randint(1,50)
            self.money = random.randint(1,3)
        if self.mind == "Payer":
            self.fold = random.randint(1,50)
            self.bet = random.randint(50,100)
            self.check = random.randint(1,50)
            self.call = random.randint(1,50)
            self.relaunch = random.randint(1,50)
            self.money = random.randint(3,9)
        if self.mind == "Follower":
            self.fold = random.randint(1,50)
            self.bet = random.randint(1,50)
            self.check = random.randint(1,100)
            self.call = random.randint(1,100)
            self.relaunch = random.randint(1,50)
            self.money = random.randint(2,7)
        if self.mind == "Risky":
            self.fold = random.randint(1,50)
            self.bet = random.randint(1,50)
            self.check = random.randint(1,50)
            self.call = random.randint(1,50)
            self.relaunch = random.randint(1,100)
            self.money = random.randint(5,9)
        if self.mind == "Rich":
            self.fold = random.randint(1,50)
            self.bet = random.randint(1,100)
            self.check = random.randint(1,50)
            self.call = random.randint(1,50)
            self.relaunch = random.randint(1,100)
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
        act,val = zip(*move_dict.items())
        return random.choices(act,weights=val)[0]

    def action_relaunch(self,money):
        pass

    def action_bet(self,money):
        pass


