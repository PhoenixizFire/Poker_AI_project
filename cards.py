import random
import colorama as cr

class Card:

    def __init__(self,value,figure):
        self.value = value
        self.figure = figure
        self.short = self.name()

    """def __repr__(self):
        if self.value==1:
            return f"{self.figure} Ace"
        elif self.value==11:
            return f"Jack of {self.figure}"
        elif self.value==12:
            return f"Queen of {self.figure}"
        elif self.value==13:
            return f"King of {self.figure}"
        else:
            return f"{self.value} of {self.figure}"""

    def __repr__(self):
        return cr.Back.WHITE+self.short+cr.Style.RESET_ALL

    def __gt__(self,b):
        return self.value>b.value

    def __lt__(self,b):
        return self.value<b.value

    def name(self):
        value,figure = int(),str()
        if self.value==14:
            value = "A"
        elif self.value==11:
            value = "J"
        elif self.value==12:
            value = "Q"
        elif self.value==13:
            value = "K"
        else:
            value = str(self.value)
        if self.figure=="Hearts":
            figure = cr.Fore.RED+"♥"+cr.Style.RESET_ALL
        elif self.figure=="Spades":
            figure = cr.Fore.BLACK+"♠"+cr.Style.RESET_ALL
        elif self.figure=="Clubs":
            figure = cr.Fore.BLACK+"♣"+cr.Style.RESET_ALL
        elif self.figure=="Diamonds":
            figure = cr.Fore.RED+"♦"+cr.Style.RESET_ALL
        return f"{cr.Fore.BLACK}{value}{figure}{cr.Style.RESET_ALL}"


class Deck:

    def __init__(self):
        self.content = list()
        self.create_deck()
        self.shuffle()
        self.big = self.intro_cards()

    def create_deck(self):
        print("Adding cards to the deck")
        for value in range(1,14):
            for figure in ['Hearts','Spades','Clubs','Diamonds']:
                self.content.append(Card(value+1,figure))

    def shuffle(self):
        print("Shuffling deck")
        random.shuffle(self.content)

    def reset(self):
        print("Resetting the deck")
        self.__init__()

    def __repr__(self):
        return str(self.content)
        

    def intro_cards(self):
        print(f"""{cr.Back.WHITE}{cr.Fore.RED}
A           A\r
♥           ♥\r
             \r
             \r
      ♥      \r
             \r
             \r
♥           ♥\r
A           A\r
{cr.Style.RESET_ALL}""")
        return "Big"