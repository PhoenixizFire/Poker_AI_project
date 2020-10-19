from board import Board
from cards import Deck
from player import Player
from bots import Bot
import random
import operator
import colorama as cr
from functools import reduce

## n_players between 2 to 10. 3 to 10 for now on
## if 2 players, Dealer is Small Blind
## small blind and big blind needs to put money before cards are distributed

class Game:

    def __init__(self,n_players,base_money,sb=25,bb=50,autoplay=False,simulation=False,training=False,AI=False):
        print('Starting the game')
        print('The players come sit around the table')
        if simulation==True:
            ## ["Folder","Coward","Payer","Follower","Risky","Rich"]
            self.players = [Player(i+1,base_money,bot=Bot("Random")) for i in range(n_players-1)]+[Player(n_players,base_money)]
        else:
            self.players = [Player(i+1,base_money) for i in range(n_players)]
        print('Setting up the board')
        self.board = Board(sb,bb,self.players)
        print('Shuffling the cards')
        self.deck = Deck()
        self.deck.big
        self.all_in = False
        self.main(autoplay,simulation)
    
    def main(self,autoplay=False,simulation=False):
        turn = 0
        while len(self.players)>1:
            turn+=1
            while True:
                self.set_roles(turn)
                self.set_blinds() #TODO Fix the issue where players are going negative
                self.set_cards()

                self.set_first_round(autoplay,simulation)
                self.the_flop()
                if len([x for x in self.players if x.active])==1:
                    self.the_turn()
                    self.the_river()
                    break
                else:
                    self.resume_active_players()

                self.set_second_round(autoplay,simulation)
                self.the_turn()
                if len([x for x in self.players if x.active])==1:
                    self.the_river()
                    break
                else:
                    self.resume_active_players()

                self.set_third_round(autoplay,simulation)
                self.the_river()
                if len([x for x in self.players if x.active])==1:
                    break
                else:
                    self.resume_active_players()

                self.set_fourth_round(autoplay,simulation)
                break
            self.distribute_pots()
            self.deck.reset()
            self.set_roles(turn)
            self.board.reset_board([x for x in self.players if x.active==True])
            #self.players[:] = [x for x in self.players if x.money!=0]
            for x in self.players:
                if x.money==0:
                    x.active=False
                    print(cr.Fore.YELLOW+f"{x.id} is out."+cr.Style.RESET_ALL)
            self.resume_active_players()
            if turn==3:break

    def pprint(func):
        def magic(self,phase,opt):
            print("#### ==== ####")
            #print(f"{[(x.id,x.active,x.all_in,x.checked) for x in self.players]}")
            func(self,phase,opt)
            print("#### ==== ####\n")
        return magic

    def burn_card(func):
        def burn(self):
            draw = random.choice(self.deck.content)
            print(f"{draw} gets burnt")
            self.deck.content.remove(draw)
            func(self)
        return burn

    def available_moves(self,phase,player):
        moves = list()
        moves.append("Fold") # EVERYTIME
        if player.money+player.current_bet<=self.board.current_bid:
            moves.append("All-in")
        else:
            if phase==1 or self.board.current_bid>0:
                moves.append("Call") # ONLY IN PRE FLOP OR LATER IF THERE IS AN ACTIVE BET
                moves.append("Raise") # ONLY IN PRE FLOP OR LATER IF THERE IS AN ACTIVE BET
            if phase>1 and self.board.current_bid==0:
                moves.append("Bet") # ONLY AFTER PRE FLOP IF NO ACTIVE BET
                moves.append("Check") # ONLY AFTER PRE FLOP IF NO ACTIVE BET
        return moves

    def next_phase(self): #TODO Fix the issue where when there are all-ins, others continue to play
        print(f"Actives : {[x.id for x in self.players if x.active==True]}")
        active_players = list()
        betting_players = list()
        for i in self.players:
            if i.active==True:
                active_players.append(i)
                if i.all_in==False:
                    betting_players.append(i.current_bet)
        check_list = [x.checked for x in self.players if x.active==True and x.all_in==False]
        count_max_value = 0
        for x in [x for x in self.players if x.active==True and x.all_in==False]:
            if x.current_bet==self.board.current_bid:
                count_max_value+=1
        if count_max_value!=len([x for x in self.players if x.active==True and x.all_in==False]):
            return False
        if len(active_players)==1: #IF ONLY ONE PLAYER LEFT => NEXT PHASE
            for i in active_players:
                if i.active:
                    print(f"Player {i.id} won the round.") #TODO Add the correct pot management with the winning management
            return True
        elif sum(check_list)==len(check_list):
            return True
        else: #IF MORE THAN ONE PLAYER LEFT
            if len(betting_players)==0: #IF NONE IS BETTING (EVERY ACTIVE PLAYER GOES ALL-IN)
                return True
            else:
                if sum(betting_players)==0:
                    return False
                else:
                    if len(betting_players)==1:
                        if betting_players[0]!=self.board.current_bid:
                            return False
                    return betting_players[1:] == betting_players[:-1] #BOOLEAN IF ALL BETS FOR CURRENT PLAYERS ARE EQUAL (IF ALL-IN THEN NOT CHECKED)

    def play_moves(self,player,choice,phase):
        while choice not in self.available_moves(phase,player):
           choice = input(f"Player {player.id}, what do you want to do ? {self.available_moves(phase,player)}")
        if choice == "Fold":
            self.board.active_pot = player.fold(self.board.active_pot)
        elif choice == "Call":
            player.call(self.board.current_bid)
        elif choice == "Raise":
            self.board.current_bid = player.relaunch(self.board.current_bid)
            if player.all_in==True:
                self.all_in=True
        elif choice == "Bet":
            self.board.current_bid = player.bet()
        elif choice == "Check":
            player.check()
        elif choice == "All-in":
            self.all_in=True
            player.tapis()

    def set_roles(self,turn):
        n_players = len(self.players)
        for i in self.players:
            if i.money>0:
                i.dealer = False
                i.small_blind = False
                i.big_blind = False
                i.active=True
                i.all_in=False
                i.checked=False
        print("\033[31m"+"Players status reset"+"\033[0m")
        self.players[(turn-1)%n_players].dealer = True
        print(f"Player {((turn-1)%n_players)+1} is the dealer")
        self.players[turn%n_players].small_blind = True
        print(f"Player {(turn%n_players)+1} is the small blind")
        self.players[(turn+1)%n_players].big_blind = True
        print(f"Player {((turn+1)%n_players)+1} is the big blind")

    def set_blinds(self):
        for i in self.players:
            if i.small_blind==True:
                self.board.small_blind = i.set_blind(25)
        print(f'Small blind set at {self.board.small_blind}')
        for i in self.players:
            if i.big_blind==True:
                self.board.big_blind = i.set_blind(50)
        self.board.current_bid = self.board.big_blind
        print(f'Big blind set at {self.board.big_blind}')

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
    def set_first_round(self,autoplay=False,simulation=False):
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
                    if simulation:
                        if i.bot!=None:
                            choice = i.bot.action(self.available_moves(1,i))
                            print(f"Player {i.id} did : {choice}")
                        else:
                            choice = input(f"Player {i.id}, what do you want to do ? {self.available_moves(1,i)}")
                    else:
                        choice = input(f"Player {i.id}, what do you want to do ? {self.available_moves(1,i)}")
                    self.play_moves(i,choice,1)
            while_token+=1
        #for i in self.players:
            #self.board.active_pot['value']+=i.current_bet
            #i.current_bet=0
        self.manage_pots()
        self.board.current_bid=0

    @burn_card
    def the_flop(self): # Need to burn the first card from the deck before flopping
        print(cr.Fore.CYAN+"### THE FLOP ###\r"+cr.Style.RESET_ALL)
        for _ in range(3):
            draw = random.choice(self.deck.content)
            self.board.community_cards.append(draw)
            self.deck.content.remove(draw)
        print(self.board)

    @pprint
    def set_second_round(self,autoplay=False,simulation=False):
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
                    if simulation:
                        if i.bot!=None:
                            choice = i.bot.action(self.available_moves(2,i))
                            print(f"Player {i.id} did : {choice}")
                        else:
                            choice = input(f"Player {i.id}, what do you want to do ? {self.available_moves(2,i)}")
                    else:
                        choice = input(f"Player {i.id}, what do you want to do ? {self.available_moves(2,i)}")
                    self.play_moves(i,choice,2)
            while_token+=1
        for i in self.players:
            #self.board.active_pot['value']+=i.current_bet
            #i.current_bet=0
            i.checked=False
        self.manage_pots()
        self.board.current_bid=0

    @burn_card
    def the_turn(self): #same as the flop but one card only # Need to burn the first card from the deck before flopping
        print(cr.Fore.BLUE+"### THE TURN ###\r"+cr.Style.RESET_ALL)
        draw = random.choice(self.deck.content)
        self.board.community_cards.append(draw)
        self.deck.content.remove(draw)
        print(self.board)

    @pprint
    def set_third_round(self,autoplay=False,simulation=False): #same as second
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
                    if simulation:
                        if i.bot!=None:
                            choice = i.bot.action(self.available_moves(3,i))
                            print(f"Player {i.id} did : {choice}")
                        else:
                            choice = input(f"Player {i.id}, what do you want to do ? {self.available_moves(3,i)}")
                    else:
                        choice = input(f"Player {i.id}, what do you want to do ? {self.available_moves(3,i)}")
                    self.play_moves(i,choice,3)
            while_token+=1
        for i in self.players:
            #self.board.active_pot['value']+=i.current_bet
            #i.current_bet=0
            i.checked=False
        self.manage_pots()
        self.board.current_bid=0

    @burn_card
    def the_river(self): #same as the turn # Need to burn the first card from the deck before flopping
        print(cr.Fore.MAGENTA+"### THE RIVER ###\r"+cr.Style.RESET_ALL)
        draw = random.choice(self.deck.content)
        self.board.community_cards.append(draw)
        self.deck.content.remove(draw)
        print(self.board)

    @pprint
    def set_fourth_round(self,autoplay=False,simulation=False): #same as second and third
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
                    if simulation:
                        if i.bot!=None:
                            choice = i.bot.action(self.available_moves(4,i))
                            print(f"Player {i.id} did : {choice}")
                        else:
                            choice = input(f"Player {i.id}, what do you want to do ? {self.available_moves(4,i)}")
                    else:
                        choice = input(f"Player {i.id}, what do you want to do ? {self.available_moves(4,i)}")
                    self.play_moves(i,choice,4)
            while_token+=1
        self.manage_pots()
        self.board.current_bid=0

    def manage_pots(self):
        if self.all_in==True: # IF GAME DETECTED SOMEONE ALL-IN'D
            money_list = list() #LIST OF PLAYERS AND MONEY
            for i in self.players: # Exemple [0,0,50,100,300,500]
                if i.active:
                    money_list.append((i,i.money)) # money_list[0] = (Player,Player.money)
            if len(money_list)==1:
                pass
            else: # IF MORE THAN ONE PEOPLE ACTIVE
                money_list = sorted(money_list, key=lambda tup: tup[1]) # SORT THE LIST BY VALUE
                print(f"{money_list}")
                if money_list[-1][1]!=money_list[-2][1]:
                    difference = money_list[-1][1] - money_list[-2][1]
                    money_list[-1][0].money+=difference
                    money_list[-1] = (money_list[-1][0],money_list[-1][1]-difference)
                for i in money_list:
                    if i[1]!=0:
                        self.board.active_pot['value']+=len([x[1] for x in money_list if x[1]!=0])*i[1]
                        for j in money_list:
                            if j[1]!=0:
                                j=(j[0],j[1]-i[1])
                        self.board.new_pot([x[0] for x in money_list if x[1]!=0])
                    if i[1]==0:
                        print(cr.Fore.YELLOW+f"{i}"+cr.Style.RESET_ALL)
        else: #IF NOT ALL-IN
            for i in self.players:
                self.board.active_pot['value']+=i.current_bet
                i.current_bet=0
                i.checked=False
        self.all_in=False

    def distribute_pots(self):
        print(cr.Fore.MAGENTA+f"Number of pots : {len(self.board.pots)}"+cr.Style.RESET_ALL)
        for i in self.board.pots:
            #print(f"{i}")
            player_list = i['player_list']
            #print(f"{player_list}")
            pot = i['value']
            win = self.showdown([x for x in player_list if x.active==True])
            if type(win)==list:
                print("Splitting the pot")
                nwin = len(win)
                if pot%nwin==0:
                    split_pot = pot/nwin
                    for j in win:
                        j.money+=split_pot
                    i['value']=0
                else:
                    rest = pot%nwin
                    split_pot = pot
                    pot-=rest
                    for j in win:
                        j.money+=split_pot
                        if rest>0:
                            j.money+=1
                            rest-=1
                    i['value']=0
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
                        else:
                            winner = max(top_cards.items(),key=operator.itemgetter(1))[0]
                            print(f"Winner : {winner}")
                            return winner
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
                if self.board.straight_flush(Player("Dummy",0))==sorted(self.board.community_cards,key=lambda x: x.value,reverse=True):
                    winner = player_list
                else:
                    for p in player_list:
                        if p.combo_score==max_score:
                            top_cards[p]=max(self.board.straight_flush(p))
                    print(top_cards)
                    winner = max(top_cards.items(),key=operator.itemgetter(1))[0]
                    print(f"Player {winner.id} wins")
                return winner
            if max_score==10:
                if self.board.royal_flush(Player("Dummy",0))==sorted(self.board.community_cards,key=lambda x: x.value,reverse=True):
                    winner = player_list
                else:
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
