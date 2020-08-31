import random

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
        return self.short

    def name(self):
        value,figure = int(),str()
        if self.value==1:
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
            figure = "♥"
        elif self.figure=="Spades":
            figure = "♠"
        elif self.figure=="Clubs":
            figure = "♣"
        elif self.figure=="Diamonds":
            figure = "♦"
        return f"{value}{figure}"


class Deck:

    def __init__(self):
        self.content = list()
        self.create_deck()
        self.shuffle()

    def create_deck(self):
        print("Adding cards to the deck")
        for value in range(13):
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