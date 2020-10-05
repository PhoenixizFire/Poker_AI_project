from board import Board
from cards import Deck
from player import Player
import random
import operator
from functools import reduce

## n_players between 2 to 10. 3 to 10 for now on
## if 2 players, Dealer is Small Blind
## small blind and big blind needs to put money before cards are distributed

class Game:

    def __init__(self,n_players,base_money,autoplay=False):
        print('Starting the game')
        print('The players come sit around the table')
        self.players = [Player(i+1,base_money) for i in range(n_players)]
        print('Setting up the board')
        self.board = Board(self.players)
        print('Shuffling the cards')
        self.deck = Deck()
        self.deck.big
        self.main(autoplay)
    
    def main(self,autoplay=False):
        turn = 0
        while len(self.players)>1:
            turn+=1
            while True:
                self.set_roles(turn)
                self.set_blinds(autoplay)
                self.set_cards()

                self.set_first_round(autoplay)
                self.the_flop()
                if len([x for x in self.players if x.active])==1:
                    self.the_turn()
                    self.the_river()
                    break
                else:
                    self.resume_active_players()

                self.set_second_round(autoplay)
                self.the_turn()
                if len([x for x in self.players if x.active])==1:
                    self.the_river()
                    break
                else:
                    self.resume_active_players()

                self.set_third_round(autoplay)
                self.the_river()
                if len([x for x in self.players if x.active])==1:
                    break
                else:
                    self.resume_active_players()

                self.set_fourth_round(autoplay)
                break
            self.distribute_pots()
            self.deck.reset()
            self.resume_active_players()
            break

    def pprint(func):
        def magic(self,phase):
            print("#### ==== ####")
            func(self,phase)
            print("#### ==== ####")
        return magic

    def burn_card(func):
        def burn(self):
            draw = random.choice(self.deck.content)
            print(f"{draw} gets burnt")
            self.deck.content.remove(draw)
            func(self)
        return burn


    def available_moves(self,phase):
        moves = list()
        moves.append("Fold") # EVERYTIME
        if phase==1 or self.board.current_bid>0:
            moves.append("Call") # ONLY IN PRE FLOP OR LATER IF THERE IS AN ACTIVE BET
            moves.append("Raise") # ONLY IN PRE FLOP OR LATER IF THERE IS AN ACTIVE BET
        if phase>1 and self.board.current_bid==0:
            moves.append("Bet") # ONLY AFTER PRE FLOP IF NO ACTIVE BET
            moves.append("Check") # ONLY AFTER PRE FLOP IF NO ACTIVE BET
        return moves

    def next_phase(self):
        active_players = list()
        betting_players = list()
        for i in self.players:
            if i.active==True:
                active_players.append(i)
                if i.all_in==False:
                    betting_players.append(i.current_bet)
        if len(active_players)==1: #IF ONLY ONE PLAYER LEFT => NEXT PHASE
            for i in active_players:
                if i.active:
                    print(f"Player {i.id} won the round.") #TODO Add the correct pot management with the winning management
            return True
        else: #IF MORE THAN ONE PLAYER LEFT
            if len(betting_players)==0: #IF NONE IS BETTING (EVERY ACTIVE PLAYER GOES ALL-IN)
                return True
            else:
                if sum(betting_players)==0:
                    return False
                else:
                    return betting_players[1:] == betting_players[:-1] #BOOLEAN IF ALL BETS FOR CURRENT PLAYERS ARE EQUAL (IF ALL-IN THEN NOT CHECKED)

    def play_moves(self,player,choice,phase):
        while choice not in self.available_moves(phase):
           choice = input(f"Player {player.id}, what do you want to do ? {self.available_moves(phase)}")
        if choice == "Fold":
            self.board.active_pot = player.fold(self.board.active_pot)
        elif choice == "Call":
            player.call(self.board.current_bid)
        elif choice == "Raise":
            self.board.current_bid = player.relaunch(self.board.current_bid)
        elif choice == "Bet":
            self.board.current_bid = player.bet()
        elif choice == "Check":
            player.check()

    def set_roles(self,turn):
        n_players = len(self.players)
        for i in self.players:
            i.dealer = False
            i.small_blind = False
            i.big_blind = False
        print("\033[31m"+"Players status reset"+"\033[0m")
        self.players[(turn-1)%n_players].dealer = True
        print(f"Player {((turn-1)%n_players)+1} is the dealer")
        self.players[turn%n_players].small_blind = True
        print(f"Player {(turn%n_players)+1} is the small blind")
        self.players[(turn+1)%n_players].big_blind = True
        print(f"Player {((turn+1)%n_players)+1} is the big blind")

    def set_blinds(self,autoplay=False):
        for i in self.players:
            if i.small_blind==True:
                if autoplay:
                    self.board.small_blind = i.set_blind(25)
                else:
                    self.board.small_blind = i.set_blind()
        print('Small blind set')
        for i in self.players:
            if i.big_blind==True:
                if autoplay:
                    self.board.big_blind = i.set_blind(50)
                else:
                    self.board.big_blind = i.set_blind()
        self.board.current_bid = self.board.big_blind
        print('Big blind set')

    def set_cards(self): # Distribution starts from small blind and goes on
        for i in self.players:
            i.hand = list()
        print('Distributing cards')
        for i in self.players+self.players:
            draw = random.choice(self.deck.content)
            i.hand.append(draw)
            self.deck.content.remove(draw)
        for i in self.players:
            print(i)

    def resume_active_players(self):
        for i in self.players:
            if i.active:
                print(i)

    @pprint
    def set_first_round(self,autoplay=False):
        n_players = len(self.players)
        for i in self.players:
            if i.big_blind:
                get_id = i.id
        play_order = [(get_id+i)%n_players+1 for i in range(n_players)]
        while_token = 0
        while not self.next_phase():
            active_id = play_order[while_token%n_players]
            for i in self.players:
                if i.id==active_id and i.active==True and i.all_in==False:
                    if autoplay:
                        choice = "Fold"
                    else:
                        choice = input(f"Player {i.id}, what do you want to do ? {self.available_moves(1)}")
                    self.play_moves(i,choice,1)
            while_token+=1
        for i in self.players:
            self.board.active_pot['value']+=i.current_bet
            i.current_bet=0
        self.board.current_bid=0

    @burn_card
    def the_flop(self): # Need to burn the first card from the deck before flopping
        print("### THE FLOP ###\r")
        for _ in range(3):
            draw = random.choice(self.deck.content)
            self.board.community_cards.append(draw)
            self.deck.content.remove(draw)
        print(self.board)

    @pprint
    def set_second_round(self,autoplay=False):
        n_players = len(self.players)
        for i in self.players:
            if i.small_blind:
                get_id = i.id
        play_order = [(get_id+i)%n_players+1 for i in range(n_players)]
        while_token = 0
        while not self.next_phase():
            active_id = play_order[while_token%n_players]
            for i in self.players:
                if i.id==active_id and i.active==True and i.all_in==False:
                    choice = input(f"Player {i.id}, what do you want to do ? {self.available_moves(2)}")
                    self.play_moves(i,choice,2)
            while_token+=1
        for i in self.players:
            self.board.active_pot['value']+=i.current_bet
            i.current_bet=0
            self.checked=False
        self.board.current_bid=0

    @burn_card
    def the_turn(self): #same as the flop but one card only # Need to burn the first card from the deck before flopping
        print("### THE TURN ###\r")
        draw = random.choice(self.deck.content)
        self.board.community_cards.append(draw)
        self.deck.content.remove(draw)
        print(self.board)

    @pprint
    def set_third_round(self,autoplay=False): #same as second
        n_players = len(self.players)
        for i in self.players:
            if i.small_blind:
                get_id = i.id
        play_order = [(get_id+i)%n_players+1 for i in range(n_players)]
        while_token = 0
        while not self.next_phase():
            active_id = play_order[while_token%n_players]
            for i in self.players:
                if i.id==active_id and i.active==True and i.all_in==False:
                    choice = input(f"Player {i.id}, what do you want to do ? {self.available_moves(3)}")
                    self.play_moves(i,choice,3)
            while_token+=1
        for i in self.players:
            self.board.active_pot['value']+=i.current_bet
            i.current_bet=0
            self.checked=False
        self.board.current_bid=0

    @burn_card
    def the_river(self): #same as the turn # Need to burn the first card from the deck before flopping
        print("### THE RIVER ###\r")
        draw = random.choice(self.deck.content)
        self.board.community_cards.append(draw)
        self.deck.content.remove(draw)
        print(self.board)

    @pprint
    def set_fourth_round(self,autoplay=False): #same as second and third
        n_players = len(self.players)
        for i in self.players:
            if i.small_blind:
                get_id = i.id
        play_order = [(get_id+i)%n_players+1 for i in range(n_players)]
        while_token = 0
        while not self.next_phase():
            active_id = play_order[while_token%n_players]
            for i in self.players:
                if i.id==active_id and i.active==True and i.all_in==False:
                    choice = input(f"Player {i.id}, what do you want to do ? {self.available_moves(4)}")
                    self.play_moves(i,choice,4)
            while_token+=1
        for i in self.players:
            self.board.active_pot['value']+=i.current_bet
            i.current_bet=0
            self.checked=False
        self.board.current_bid=0

    def distribute_pots(self):
        for i in self.board.pots:
            player_list = i['player_list']
            pot = i['value']
            win = self.showdown(player_list)
            if type(win)==list:
                pass
            else: # One winner
                win.money+=pot
                pot = 0

    def showdown(self,player_list): #everyone reveals their cards #TODO manage pots
        scores = dict()
        for p in player_list: #[x for x in self.players if x.active==True]:
            p.kickers = self.board.kicker_cards(p)
            scores[f"Player {p.id}"]=p.combo_score
            print(f"Player {p.id} has a score of {p.combo_score}")
        #print(scores)
        max_score = max(scores.items(),key=operator.itemgetter(1))[1]
        print(list(scores.values()))
        #print(list(scores.values()).count(max_score))
        if list(scores.values()).count(max_score)==1:
            for i in player_list:
                if i.combo_score==max_score:
                    print(f"Player {i.id} wins")
                    return i
        else:
            top_cards = dict()
            winners = [x for x,y in scores.items() if y==max_score]
            print(f"{winners} are tied for the win")

            if max_score==1:
                for p in player_list:
                    if p.combo_score==max_score:
                        top_cards[p]=self.board.highest_card(p)
                print(top_cards)
                max_card = max(top_cards.items(),key=operator.itemgetter(1))[1]
                print(f"Max card is : {max_card}")
                if list(top_cards.values()).count(max_card)>1:
                    cc=0
                    finalists = [x for x in player_list if x.combo_score==max_score and max_card.value==self.board.highest_card(x).value]
                    print(finalists)
                    kicker_cards = len(finalists[0].kickers)
                    while cc<kicker_cards:
                        final_battle=dict()
                        for p in finalists:
                            final_battle[p]=p.kickers[cc]
                        max_card = max(final_battle.items(),key=operator.itemgetter(1))[1]
                        if list(final_battle.values()).count(max_card)>1:
                            for p in finalists.copy():
                                if p.kickers[cc].value!=max_card.value:
                                    finalists.remove(p)
                            cc+=1
                        else:
                            winner = max(final_battle.items(),key=operator.itemgetter(1))[0]
                            print(f"Player {winner.id} wins")
                            return winner
                    if cc==kicker_cards:
                        print(f"It's a tie between {['Player '+str(x.id) for x in finalists]} for the win")
                        return finalists
                else:
                    winner = max(top_cards.items(),key=operator.itemgetter(1))[0]
                    print(f"Player {winner.id} wins")
                    return winner
            if max_score==2:
                for p in player_list:
                    if p.combo_score==max_score:
                        top_cards[p]=max(self.board.one_pair(p))
                print(top_cards)
                max_card = max(top_cards.items(),key=operator.itemgetter(1))[1]
                print(f"Max card is : {max_card}")
                if [x.value for x in list(top_cards.values())].count(max_card.value)>1:
                    cc=0
                    finalists = [x for x in player_list if x.combo_score==max_score and max_card.value in [i.value for i in self.board.one_pair(x)]]
                    print(finalists)
                    kicker_cards = len(finalists[0].kickers)
                    while cc<kicker_cards:
                        final_battle=dict()
                        for p in finalists:
                            final_battle[p]=p.kickers[cc]
                        max_card = max(final_battle.items(),key=operator.itemgetter(1))[1]
                        print(f"Max card is : {max_card}")
                        if [x.value for x in list(final_battle.values())].count(max_card.value)>1:
                            for p in finalists.copy():
                                if p.kickers[cc].value!=max_card.value:
                                    finalists.remove(p)
                            cc+=1
                        else:
                            winner = max(final_battle.items(),key=operator.itemgetter(1))[0]
                            print(f"Player {winner.id} wins")
                            return winner
                    if cc==kicker_cards:
                        print(f"It's a tie between {['Player '+str(x.id) for x in finalists]} for the win")
                        return finalists
                else:
                    winner = max(top_cards.items(),key=operator.itemgetter(1))[0]
                    print(f"Player {winner.id} wins")
                    return winner
            if max_score==3:
                for p in player_list:
                    if p.combo_score==max_score:
                        top_cards[p]=max(self.board.two_pair(p)[0])
                print(top_cards)
                max_card = max(top_cards.items(),key=operator.itemgetter(1))[1]
                print(f"Max card is : {max_card}")
                print([x.value for x in list(top_cards.values())].count(max_card.value))
                if [x.value for x in list(top_cards.values())].count(max_card.value)>1:
                    finalists = [x for x in player_list if x.combo_score==max_score and max_card.value in [i.value for i in self.board.two_pair(x)[0]]]
                    #print(finalists)
                    final_battle=dict()
                    for p in finalists:
                        final_battle[p]=max(self.board.two_pair(p)[1])
                    max_card = max(final_battle.items(),key=operator.itemgetter(1))[1]
                    print(f"Max card is : {max_card}")
                    print([x.value for x in list(final_battle.values())].count(max_card.value))
                    if list(final_battle.values()).count(max_card)>1:
                        print("Comparing the second pair")
                        for p in finalists.copy():
                            if final_battle[p].value!=max_card.value:
                                finalists.remove(p)
                    else:
                        winner = max(final_battle.items(),key=operator.itemgetter(1))[0]
                        print(f"Player {winner.id} wins")
                        return winner
                    if len(finalists)>1:
                        print("Comparing the last card")
                        final_battle=dict()
                        for p in finalists:
                            final_battle[p]=p.kickers[0]
                        print(final_battle)
                        max_card = max(final_battle.items(),key=operator.itemgetter(1))[1]
                        print(f"Max card is : {max_card}")
                        print([x.value for x in list(final_battle.values())].count(max_card.value))
                        if [x.value for x in list(final_battle.values())].count(max_card.value)>1:
                            print(f"It's a tie between {['Player '+str(x.id) for x in finalists]} for the win")
                            return finalists
                        del final_battle
                else:
                    winner = max(top_cards.items(),key=operator.itemgetter(1))[0]
                    print(f"Player {winner.id} wins")
                    return winner
            if max_score==4:
                for p in player_list:
                    if p.combo_score==max_score:
                        top_cards[p]=max(self.board.three_of_a_kind(p))
                print(top_cards)
                max_card = max(top_cards.items(),key=operator.itemgetter(1))[1]
                print(f"Max card is : {max_card}")
                if list(top_cards.values()).count(max_card)>1:
                    cc=0
                    finalists = [x for x in player_list if x.combo_score==max_score and max_card.value in [i.value for i in self.board.three_of_a_kind(x)]]
                    print(finalists)
                    kicker_cards = len(finalists[0].kickers)
                    while cc<kicker_cards:
                        final_battle=dict()
                        for p in finalists:
                            final_battle[p]=p.kickers[cc]
                        max_card = max(final_battle.items(),key=operator.itemgetter(1))[1]
                        if list(final_battle.values()).count(max_card)>1:
                            for p in finalists.copy():
                                if p.kickers[cc].value!=max_card.value:
                                    finalists.remove(p)
                            cc+=1
                        else:
                            winner = max(final_battle.items(),key=operator.itemgetter(1))[0]
                            print(f"Player {winner.id} wins")
                            return winner
                    if cc==kicker_cards:
                        print(f"It's a tie between {['Player '+str(x.id) for x in finalists]} for the win")
                        return finalists
                else:
                    winner = max(top_cards.items(),key=operator.itemgetter(1))[0]
                    print(f"Player {winner.id} wins")
                    return winner
            if max_score==5:
                for p in player_list:
                    if p.combo_score==max_score:
                        top_cards[p]=max(self.board.straight(p))
                print(top_cards)
                max_card = max(top_cards.items(),key=operator.itemgetter(1))[1]
                print(f"Max card is : {max_card}")
                print(list(top_cards.values()))
                if [x.value for x in list(top_cards.values())].count(max_card.value)>1:
                    cc=1
                    finalists = [x for x in player_list if x.combo_score==max_score and max_card.value in [i.value for i in self.board.straight(x)]]
                    print(finalists)
                    while cc<5:
                        print(f"finalists : {finalists}")
                        final_battle=dict()
                        for p in finalists:
                            final_battle[p]=self.board.straight(p)[cc]
                        print(final_battle)
                        max_card = max(final_battle.items(),key=operator.itemgetter(1))[1]
                        print(f"Max card is : {max_card}")
                        print([x.value for x in list(final_battle.values())].count(max_card.value))
                        if [x.value for x in list(final_battle.values())].count(max_card.value)>1:
                            for p in finalists.copy():
                                if p.hand[cc].value!=max_card.value:
                                    finalists.remove(p)
                            cc+=1
                        else:
                            winner = max(final_battle.items(),key=operator.itemgetter(1))[0]
                            print(f"Player {winner.id} wins")
                            return winner
                        del final_battle
                    if cc==kicker_cards:
                        print(f"It's a tie between {['Player '+str(x.id) for x in finalists]} for the win")
                        return finalists
                else:
                    winner = max(top_cards.items(),key=operator.itemgetter(1))[0]
                    print(f"Player {winner.id} wins")
                    return winner
            if max_score==6:
                for p in player_list:
                    if p.combo_score==max_score:
                        top_cards[p]=max(self.board.flush(p))
                print(top_cards)
                max_card = max(top_cards.items(),key=operator.itemgetter(1))[1]
                print(f"Max card is : {max_card}")
                if [x.value for x in list(top_cards.values())].count(max_card.value)>1:
                    cc=1
                    finalists = [x for x in player_list if x.combo_score==max_score and max_card.value in [i.value for i in self.board.flush(x)]]
                    #print(f"Finalists : {finalists}")
                    while cc<5:
                        final_battle=dict()
                        for p in finalists:
                            final_battle[p]=self.board.flush(p)[cc]
                        print(final_battle)
                        #print(final_battle.items())
                        max_card = max(final_battle.items(),key=operator.itemgetter(1))[1]
                        print(f"Max card is : {max_card}")
                        if [x.value for x in list(final_battle.values())].count(max_card.value)>1:
                            for p in finalists.copy():
                                if p.hand[cc].value!=max_card.value:
                                    finalists.remove(p)
                            cc+=1
                        else:
                            winner = max(final_battle.items(),key=operator.itemgetter(1))[0]
                            print(f"Player {winner.id} wins")
                            return winner
                        del final_battle
                    if cc==kicker_cards:
                        print(f"It's a tie between {['Player '+str(x.id) for x in finalists]} for the win")
                        return finalists
                else:
                    winner = max(top_cards.items(),key=operator.itemgetter(1))[0]
                    print(f"Player {winner.id} wins")
                    return winner
            if max_score==7:
                for p in player_list:
                    if p.combo_score==max_score:
                        top_cards[p]=max(self.board.full_house(p)[0])
                print(top_cards)
                max_card = max(top_cards.items(),key=operator.itemgetter(1))[1]
                print(f"Max card is : {max_card}")
                if list(top_cards.values()).count(max_card)>1:
                    finalists = [x for x in player_list if x.combo_score==max_score and max_card.value in [i.value for i in self.board.full_house(x)[0]]]
                    print(finalists)
                    final_battle=dict()
                    for p in finalists:
                        final_battle[p]=self.board.full_house(p)[1][0]
                    max_card = max(final_battle.items(),key=operator.itemgetter(1))[1]
                    print(f"Max card is : {max_card}")
                    if list(final_battle.values()).count(max_card)>1:
                        for p in finalists.copy():
                            if self.board.full_house(p)[1][0].value!=max_card.value:
                                finalists.remove(p)
                    else:
                        winner = max(final_battle.items(),key=operator.itemgetter(1))[0]
                        print(f"Player {winner.id} wins")
                        return winner
                    if list(final_battle.values()).count(max_card)>1:
                        print(f"It's a tie between {['Player '+str(x.id) for x in finalists]} for the win")
                        return finalists
                else:
                    winner = max(top_cards.items(),key=operator.itemgetter(1))[0]
                    print(f"Player {winner.id} wins")
                    return winner
            if max_score==8:
                for p in player_list:
                    if p.combo_score==max_score:
                        top_cards[p]=max(self.board.four_of_a_kind(p))
                print(top_cards)
                max_card = max(top_cards.items(),key=operator.itemgetter(1))[1]
                print(f"Max card is : {max_card}")
                if list(top_cards.values()).count(max_card)>1:
                    cc=0
                    finalists = [x for x in player_list if x.combo_score==max_score and max_card.value in [i.value for i in self.board.four_of_a_kind(x)]]
                    print(finalists)
                    kicker_cards = len(finalists[0].kickers)
                    while cc<kicker_cards:
                        final_battle=dict()
                        for p in finalists:
                            final_battle[p]=p.kickers[cc]
                        max_card = max(final_battle.items(),key=operator.itemgetter(1))[1]
                        if list(final_battle.values()).count(max_card)>1:
                            for p in finalists.copy():
                                if p.kickers[cc].value!=max_card.value:
                                    finalists.remove(p)
                            cc+=1
                        else:
                            winner = max(final_battle.items(),key=operator.itemgetter(1))[0]
                            print(f"Player {winner.id} wins")
                            return winner
                    if cc==kicker_cards:
                        print(f"It's a tie between {['Player '+str(x.id) for x in finalists]} for the win")
                        return finalists
                else:
                    winner = max(top_cards.items(),key=operator.itemgetter(1))[0]
                    print(f"Player {winner.id} wins")
                    return winner
            if max_score==9:
                for p in player_list:
                    if p.combo_score==max_score:
                        top_cards[p]=max(self.board.straight_flush(p))
                print(top_cards)
                winner = max(top_cards.items(),key=operator.itemgetter(1))[0]
                print(f"Player {winner.id} wins")
                return winner
            if max_score==10:
                for p in player_list:
                    if p.combo_score==max_score:
                        top_cards[p]=max(self.board.royal_flush(p))
                print(top_cards)
                winner= max(top_cards.items(),key=operator.itemgetter(1))[0]
                print(f"Player {winner.id} wins")
                return winner

        # FIVE CARD RULES ALWAYS ACT : For One_Pair, Two_Pair, Three_of_a_Kind, always the kickers up to 5 cards used.
        # In rare case of Four of a Kind in community cards, also take that into account
        # IF THE 5 CARDS ARE THE SAME : TIE = SPLIT THE POT

        #ONE PAIR (Detect two of the same value) Highest pair wins
        #TWO PAIR (Detect two of the same value twice) Highest value in pairs wins
        #THREE OF A KIND (Detect three of the same value) Highest three of a kind wins
        #STRAIGTH (Five cards with values that follows. E.G. 5,6,7,8,9) Highest card in straight wins
        #FLUSH (Five card with the same figure) Highest card in flush wins
        #FULL HOUSE (Pair + Three of a kind) Highest three of a kind, then highest pair
        #FOUR OF A KIND (Detect four of the same value) Highest four of a kind wins
        #STRAIGHT FLUSH (Five cards with values that follows + the same figure)
        #ROYAL FLUSH (10,J,Q,K,A of the same figure)
