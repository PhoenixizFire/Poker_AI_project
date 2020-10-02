import operator
from functools import reduce
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
        for i in self.community_cards+player.hand:
            if i.value>max_value:
                high_card = i
                max_value = i.value
        return high_card

    def one_pair(self,player):
        cards = self.community_cards+player.hand
        for i in cards:
            for j in [x for x in cards if x!=i]:
                if i.value==j.value:
                    return [i,j]
        return None

    def two_pair(self,player):
        pairing = list()
        cards = self.community_cards+player.hand
        for i in cards:
            for j in [x for x in cards if x!=i]:
                if i.value==j.value:
                    pairing.append([i,j])
                    cards.remove(i)
                    cards.remove(j)
        if len(pairing)==2:
            if pairing[0][0].value>pairing[1][0].value:
                return [pairing[0],pairing[1]]
            else:
                return [pairing[1],pairing[0]]
        elif len(pairing)>2:
            #print("More than 2 pairs detected, what to do ?")
            #print(f"Issue there : {pairing}")
            if pairing[0][0].value>pairing[1][0].value:
                if pairing[1][0].value>pairing[2][0].value:
                    return [pairing[0],pairing[1]]
                else:
                    if pairing[0][0].value>pairing[2][0].value:
                        return [pairing[0],pairing[2]]
                    else:
                        return [pairing[2],pairing[0]]
            else:
                if pairing[0][0].value>pairing[2][0].value:
                    return [pairing[1],pairing[0]]
                else:
                    if pairing[1][0].value>pairing[2][0].value:
                        return [pairing[1],pairing[2]]
                    else:
                        return [pairing[2],pairing[1]]
        else:
            return None

    def three_of_a_kind(self,player):
        cards = self.community_cards+player.hand
        for i in cards:
            for j in [x for x in cards if i!=x]:
                if i.value==j.value:
                    for k in [x for x in cards if (i!=x and j!=x)]:
                        if j.value==k.value:
                            return [i,j,k]
        return None


    def straight(self,player):
        cards = self.community_cards+player.hand
        for i in cards:
            for j in [x for x in cards if i!=x]:
                if i.value+1==j.value:
                    for k in [x for x in cards if (i!=x and j!=x)]:
                        if j.value+1==k.value:
                            for l in [x for x in cards if (i!=x and j!=x and k!=x)]:
                                if k.value+1==l.value:
                                    for m in [x for x in cards if (i!=x and j!=x and k!=x and l!=x)]:
                                        if l.value+1==m.value:
                                            return [m,l,k,j,i]
        return None

    def flush(self,player):
        cards = self.community_cards+player.hand
        for i in cards:
            for j in [x for x in cards if i!=x]:
                if i.figure==j.figure:
                    for k in [x for x in cards if (i!=x and j!=x)]:
                        if j.figure==k.figure:
                            for l in [x for x in cards if (i!=x and j!=x and k!=x)]:
                                if k.figure==l.figure:
                                    for m in [x for x in cards if (i!=x and j!=x and k!=x and l!=x)]:
                                        if l.figure==m.figure:
                                            return sorted([i,j,k,l,m],key=lambda x: x.value,reverse=True)
        return None

    def full_house(self,player): #TODO Avoid conflicts
        cards = self.community_cards+player.hand
        pair,three = None,None
        for i in cards:
            for j in [x for x in cards if i!=x]:
                if i.value==j.value:
                    for k in [x for x in cards if (i!=x and j!=x)]:
                        if j.value==k.value:
                            three = [i,j,k]
        if three==None:
            return None
        cards = [x for x in cards if not x in three]
        for l in cards:
            for m in [x for x in cards if l!=x]:
                if l.value==m.value:
                    pair = [l,m]
        #pair = self.one_pair(player)
        #three = self.three_of_a_kind(player)
        if pair != None and three!=None:
            if pair[0].value != three[0].value:
                return [three,pair]
        return None

    def four_of_a_kind(self,player):
        cards = self.community_cards+player.hand
        for i in cards:
            for j in [x for x in cards if i!=x]:
                if i.value==j.value:
                    for k in [x for x in cards if (i!=x and j!=x)]:
                        if j.value==k.value:
                            for l in [x for x in cards if (i!=x and j!=x and k!=x)]:
                                if k.value==l.value:
                                    return [i,j,k,l]
        return None

    def straight_flush(self,player):
        straight = self.straight(player)
        if straight!=None:
            if straight[0].figure==straight[1].figure==straight[2].figure==straight[3].figure==straight[4].figure:
                return straight
        return None

    def royal_flush(self,player):
        flush = self.straight_flush(player)
        if flush!=None:
            if flush[0].value==10:
                return flush
        return None

    def highest_combo(self,player):
        royal_flush = self.royal_flush(player)
        if royal_flush!=None:
            print(f"Player {player.id} has a Royal Flush : {royal_flush}")
            return 10
        straight_flush = self.straight_flush(player)
        if straight_flush!=None:
            print(f"Player {player.id} has a Straight Flush : {straight_flush}")
            return 9
        four = self.four_of_a_kind(player)
        if four!=None:
            print(f"Player {player.id} has a Four of a Kind : {four}")
            return 8
        full = self.full_house(player)
        if full!=None:
            print(f"Player {player.id} has a Full House : {full}")
            return 7
        flush = self.flush(player)
        if flush!=None:
            print(f"Player {player.id} has a Flush : {flush}")
            return 6
        straight = self.straight(player)
        if straight!=None:
            print(f"Player {player.id} has a Straight : {straight}")
            return 5
        three = self.three_of_a_kind(player)
        if three!=None:
            print(f"Player {player.id} has a Three of a Kind : {three}")
            return 4
        two_pair = self.two_pair(player)
        if two_pair!=None:
            print(f"Player {player.id} has Two Pairs : {two_pair}")
            return 3
        pair = self.one_pair(player)
        if pair!=None:
            print(f"Player {player.id} has a Pair : {pair}")
            return 2
        highest_card = self.highest_card(player)
        print(f"Player {player.id} highest card is : {highest_card}")
        return 1

    def kicker_cards(self,player):
        player.combo_score = self.highest_combo(player)
        cards = player.hand + self.community_cards
        kickers = list()
        if player.combo_score==1: #One best card
            card = self.highest_card(player)
            kickers = [x for x in cards if (x.value,x.figure)!=(card.value,card.figure)]
            kickers = sorted(kickers, key=lambda x: x.value,reverse=True)
            kickers = kickers[:4]
            print(f"{[card,]+kickers}")
            return kickers
        if player.combo_score==2: #Two best cards
            pair = self.one_pair(player)
            kickers = [x for x in cards if x not in pair]
            kickers = sorted(kickers, key=lambda x: x.value,reverse=True)
            kickers = kickers[:3]
            print(pair+kickers)
            return kickers                        
        if player.combo_score==4: #Three best cards
            three = self.three_of_a_kind(player)
            kickers = [x for x in cards if x not in three]
            kickers = sorted(kickers, key=lambda x : x.value,reverse=True)
            kickers = kickers[:2]
            print(three+kickers)
            return kickers
        if player.combo_score in [3,8]: #Four best cards
            if player.combo_score==3:
                hand = reduce(operator.add,self.two_pair(player))
                kickers = [x for x in cards if x not in hand]
            if player.combo_score==8:
                hand = self.four_of_a_kind(player)
                kickers = [x for x in cards if x not in hand]
            kickers = sorted(kickers,key=lambda x:x.value)
            kickers = kickers[:1]
            print(hand+kickers)
            return kickers
        if player.combo_score in [5,6,7,9,10]: #Five best cards
            pass