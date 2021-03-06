from board import Board
from cards import Deck
from player import Player
from bots import Bot
import random
import operator
import time
import colorama as cr
from functools import reduce
import mysql.connector
from datetime import datetime

## n_players between 2 to 10. 3 to 10 for now on
## if 2 players, Dealer is Small Blind
## small blind and big blind needs to put money before cards are distributed

def connect_sqldb():
    mydb = mysql.connector.connect(
        host = "localhost",
        user="root",
        password="admin",
        database="pokeraiproject"
    )
    return mydb

def log_sql(db:object(),table:str(),log:dict()):
    cursor = db.cursor()
    sql = f"INSERT INTO {table} ({','.join(str(x) for x in log.keys())}) VALUES ({','.join(chr(39)+str(x)+chr(39) for x in log.values())});"
    print("REQUETE SQL AVANT ENVOI : "+sql)
    cursor.execute(sql)
    db.commit()
    cursor.close()
    db.close()

class Game:

    def __init__(self,n_players,base_money,sb=25,bb=50,autoplay=False,simulation=False,training=False,AI=False):
        print('Starting the game')
        print('The players come sit around the table')
        if simulation==True:
            ## ["Folder","Coward","Payer","Follower","Risky","Rich"]
            self.players = [Player(i+1,base_money,bot=Bot("Random")) for i in range(n_players-1)]+[Player(n_players,base_money)]
        if training==True:
            base_money = 10000
            self.players = [Player(i+1,base_money,bot=Bot("Noob")) for i in range(n_players)]
        else:
            self.players = [Player(i+1,base_money) for i in range(n_players)]
        print('Setting up the board')
        self.board = Board(sb,bb,self.players)
        print('Shuffling the cards')
        self.deck = Deck()
        #self.deck.big
        self.all_in = False
        self.main(autoplay,simulation,training)
    
    def main(self,autoplay=False,simulation=False,training=False):
        if training:
            limit = 50
        else:
            limit = 3
        turn = 0
        while len([x for x in self.players if x.active==True])>1:
            turn+=1
            while True:
                self.game_id = datetime.now().strftime("%y%m%d%H%M%S")
                print(f"Game ID = {self.game_id}")
                self.set_roles(turn)
                init_logsql = dict()
                for x in self.players:
                    init_logsql[f'{x.id}'] = -x.money
                self.set_blinds() #TODO Fix the issue where players are going negative
                self.set_cards()

                self.set_first_round(autoplay,simulation,training)
                self.the_flop()
                if len([x for x in self.players if x.active])==1:
                    self.the_turn()
                    self.the_river()
                    break
                else:
                    self.resume_active_players()

                self.set_second_round(autoplay,simulation,training)
                self.the_turn()
                if len([x for x in self.players if x.active])==1:
                    self.the_river()
                    break
                else:
                    self.resume_active_players()

                self.set_third_round(autoplay,simulation,training)
                self.the_river()
                if len([x for x in self.players if x.active])==1:
                    break
                else:
                    self.resume_active_players()

                self.set_fourth_round(autoplay,simulation,training)
                break
            print("Avant distribute_pots()")
            print(f"Nombre de pots {len(self.board.pots)}")
            for x in self.distribute_pots():
                print(x)
            print("Après distribute_pots()")
            for x in self.players:
                init_logsql[f'{x.id}'] = init_logsql[f'{x.id}']+x.money
            print(f"init_logsql : {[(k,v) for k,v in init_logsql.items()]}")
            self._logdb(5,init_logsql)
            self.deck.reset()
            self.set_roles(turn)
            self.board.reset_board([x for x in self.players if x.active==True])
            #self.players[:] = [x for x in self.players if x.money!=0]
            for x in self.players:
                if x.money==0:
                    x.active=False
                    print(cr.Fore.YELLOW+f"{x.id} is out."+cr.Style.RESET_ALL)
            self.resume_active_players()
            if turn==limit:break
            time.sleep(1)

    def pprint(func):
        def magic(self,phase,opt,bonus):
            print("#### ==== ####")
            #print(f"{[(x.id,x.active,x.all_in,x.checked) for x in self.players]}")
            func(self,phase,opt,bonus)
            print("#### ==== ####\n")
        return magic

    def burn_card(func):
        def burn(self):
            draw = random.choice(self.deck.content)
            print(f"{draw} gets burnt")
            self.deck.content.remove(draw)
            func(self)
        return burn

    def _logdb(self,phase:int(),outcome):
        if outcome==None:
            table_action = f"Table{len(self.players)}Phase{phase}Action" #Table6Phase1Action
            print("Log_sql : "+table_action)
            #table_mise = f"Table{len(self.players)}Phase{phase}Mise"
        else:
            table_result = f"Table{len(self.players)}Result"
            print("Log_sql : "+table_result)
        request = dict() #TODO Dynamic request selection
        request["gameID"] = self.game_id
        if outcome==None:
            for x,y in enumerate(self.players):
                request[f"Player{x+1}Action"] = y.last_move
                request[f"Player{x+1}Bet"] = y.current_bet
                request[f"Player{x+1}Money"] = y.money
                request[f"Player{x+1}Status"] = y.active
                request[f"Player{x+1}Card1Value"] = y.hand[0].value
                request[f"Player{x+1}Card1Figure"] = y.hand[0].figure
                request[f"Player{x+1}Card2Value"] = y.hand[1].value
                request[f"Player{x+1}Card2Figure"] = y.hand[1].figure
        else:
            for x,y in enumerate(self.players):
                request[f"Player{x+1}Outcome"] = outcome[str(x+1)]
        if outcome==None:
            log_sql(connect_sqldb(),table_action,request)
        else:
            log_sql(connect_sqldb(),table_result,request)
        #log_sql(connect_sqldb(),table_mise,request)

    def available_moves(self,phase,player):
        moves = list()
        moves.append("Fold") # EVERYTIME
        if player.money+player.current_bet<=self.board.current_bid:
            moves.append("All-in")
        else:
            if phase==1 or self.board.current_bid>0:
                moves.append("Call") # ONLY IN PRE FLOP OR LATER IF THERE IS AN ACTIVE BET
                if player.money>2*self.board.current_bid: #CHECK IF PLAYER CAN PAY A REAL RAISE
                    moves.append("Raise") # ONLY IN PRE FLOP OR LATER IF THERE IS AN ACTIVE BET
                else:
                    moves.append("All-in")
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
            if x.current_bet>=self.board.current_bid:
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
            return choice
        elif choice == "Call":
            player.call(self.board.current_bid)
            return choice
        elif choice == "Raise":
            print("ALERT, THIS IS THE CURRENT HIGH BID : "+str(self.board.current_bid))
            self.board.current_bid = player.relaunch(self.board.current_bid)
            if player.all_in==True:
                self.all_in=True
                return "All-in"
            return choice+" at "+str(self.board.current_bid)
        elif choice == "Bet":
            self.board.current_bid = player.bet()
            if player.all_in==True:
                self.all_in=True
                return "All-in"
            return choice+" "+str(self.board.current_bid)
        elif choice == "Check":
            player.check()
            return choice
        elif choice == "All-in":
            self.all_in=True
            self.board.current_bid = player.tapis()
            return choice

    def set_roles(self,turn):
        list_players = [x for x in self.players if x.money>0]
        n_players = len(list_players)
        for i in self.players:
            if i.money>0:
                i.dealer = False
                i.small_blind = False
                i.big_blind = False
                i.active=True
                i.all_in=False
                i.checked=False
        print("\033[31m"+"Players status reset"+"\033[0m")
        list_players[(turn-1)%n_players].dealer = True
        print(f"Player {((turn-1)%n_players)+1} is the dealer")
        list_players[turn%n_players].small_blind = True
        print(f"Player {(turn%n_players)+1} is the small blind")
        list_players[(turn+1)%n_players].big_blind = True
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
    def set_first_round(self,autoplay=False,simulation=False,training=False):
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
                    if training:
                        choice = i.bot.action(self.available_moves(1,i))
                    else:
                        choice = input(f"Player {i.id}, what do you want to do ? {self.available_moves(1,i)}")
                    self.play_moves(i,choice,1)
                    i.last_move = choice
            while_token+=1
        #for i in self.players:
            #self.board.active_pot['value']+=i.current_bet
            #i.current_bet=0
        self._logdb(1,None)
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
    def set_second_round(self,autoplay=False,simulation=False,training=False):
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
                    if training:
                        choice = i.bot.action(self.available_moves(2,i))
                    else:
                        choice = input(f"Player {i.id}, what do you want to do ? {self.available_moves(2,i)}")
                    self.play_moves(i,choice,2)
                    i.last_move = choice
            while_token+=1
        for i in self.players:
            #self.board.active_pot['value']+=i.current_bet
            #i.current_bet=0
            i.checked=False
        self._logdb(2,None)
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
    def set_third_round(self,autoplay=False,simulation=False,training=False): #same as second
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
                    if training:
                        choice = i.bot.action(self.available_moves(3,i))
                    else:
                        choice = input(f"Player {i.id}, what do you want to do ? {self.available_moves(3,i)}")
                    self.play_moves(i,choice,3)
                    i.last_move = choice
            while_token+=1
        for i in self.players:
            #self.board.active_pot['value']+=i.current_bet
            #i.current_bet=0
            i.checked=False
        self._logdb(3,None)
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
    def set_fourth_round(self,autoplay=False,simulation=False,training=False): #same as second and third
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
                    if training:
                        choice = i.bot.action(self.available_moves(4,i))
                    else:
                        choice = input(f"Player {i.id}, what do you want to do ? {self.available_moves(4,i)}")
                    self.play_moves(i,choice,4)
                    i.last_move = choice
            while_token+=1
        self._logdb(4,None)
        self.manage_pots()
        self.board.current_bid=0

    def manage_pots(self):
        print(cr.Fore.RED+"MANAGING POTS"+cr.Fore.RESET)
        print(f"Nombre de pots {len(self.board.pots)}")
        print(f"Pot : {self.board.pots}")
        if self.all_in==True: # IF GAME DETECTED SOMEONE ALL-IN'D
            money_list = list() #LIST OF PLAYERS AND MONEY
            for i in self.players: # Exemple [0,0,50,100,300,500]
                if i.active:
                    money_list.append([i,i.current_bet]) # money_list[0] = (Player,Player.current_bet)
            if len(money_list)==1:
                pass
            else: # IF MORE THAN ONE PEOPLE ACTIVE
                sorted_money_list = sorted(money_list, key=lambda tup: tup[1]) # SORT THE LIST BY VALUE
                print(f"Current sorted money list : {[(x[0].id,x[1])for x in sorted_money_list]}")
                if sorted_money_list[-1][1]!=sorted_money_list[-2][1]: # Check the highest person in the value list, to regulate the highest all-in
                    difference = sorted_money_list[-1][1] - sorted_money_list[-2][1]
                    #money_list[-1][0].money+=difference
                    sorted_money_list[-1][0]._add_money(difference)
                    sorted_money_list[-1] = [sorted_money_list[-1][0],sorted_money_list[-1][1]-difference]

                """print("SORTED MONEY LIST #####################################")
                print(sorted_money_list):
                for tup in sorted_money_list: # THE ISSUE IS HERE : IT LOOPS FOR EVERY PLAYER IN LIST AND NOT EVERY DIFFERENCE #TODO MAKE A DIFFERENCE LIST AND MAKE THE POTS BASED ON THAT
                    print(tup)
                    if tup[1]!=0: #Si le joueur n'a pas 0 d'argent
                        self.board.active_pot['value'] += len([x for x in sorted_money_list if x[1]!=0])*tup[1] # Add value from the lowest player in the current_pot
                        for j in sorted_money_list: # pour chaque joueur
                            if j[1]!=0: #si sa monnaie est différente de 0
                                #j=(j[0],j[1]-tup[1]) # retire l'argent du tuple
                                j[1]-=tup[1]

                    if tup[1]==0:
                        print(f"Player {i.id} is 'tup[1]==0")
                    # une fois tous les joueurs passés
                    if len([x for x in self.players if x.active==True and x.money!=0])>1: # 0 or 1 ?
                        print("###############################    CREATING NEW POT")
                        self.board.new_pot([x for x in self.players if x.active==True and x.money!=0])
                        print(f"Nombre de pots : {len(self.board.pots)}")"""

                count_zeros_in_list = len([y for x,y in sorted_money_list if y==0])
                print(f"count_zeros_in_list = {count_zeros_in_list}")
                count_else_in_list = len([y for x,y in sorted_money_list if y!=0])
                print(f"count_else_in_list = {count_else_in_list}")
                debug = 0
                while count_else_in_list>0:
                    debug+=1
                    minimum = min([y for x,y in sorted_money_list if x!=0])
                    print(f"minimum = {minimum}")
                    self.board.active_pot['value'] += minimum*count_else_in_list
                    sorted_money_list = [[x,y-minimum] if y!=0 else [x,y] for x,y in sorted_money_list]
                    count_zeros_in_list = len([y for x,y in sorted_money_list if y==0])
                    print(f"count_zeros_in_list = {count_zeros_in_list}")
                    count_else_in_list = len([y for x,y in sorted_money_list if y!=0])
                    print(f"count_else_in_list = {count_else_in_list}")
                    if count_else_in_list>0:
                        print("###############################    CREATING NEW POT")
                        self.board.new_pot([x for x,y in sorted_money_list if x.active==True and y!=0])
                    if debug==3:break
                if (len([x for x in self.players if x.active==True and x.all_in==True])!=len([x for x in self.players if x.active==True])) and (len([x for x in self.players if x.active==True and x.all_in==True])>1):
                    self.board.new_pot([x for x in self.players if x.active==True and x.money!=0])
                for i in self.players:
                    i.current_bet=0
                    i.checked=False
        else: #IF NOT ALL-IN
            for i in self.players:
                self.board.active_pot['value']+=i.current_bet
                i.current_bet=0
                i.checked=False
        self.all_in=False

    def distribute_pots(self):
        print("Reach this ?")
        print(cr.Fore.MAGENTA+f"Number of pots : {len(self.board.pots)}"+cr.Style.RESET_ALL)
        print("Reach that !")
        for i in self.board.pots:
            winner_listup = list()
            player_list = i['player_list']
            pot = i['value']
            win,combo = self.showdown([x for x in player_list if x.active==True]) #unyield each showdown
            if type(win)==list:
                print("Splitting the pot")
                print(f"Splitting between : {win}")
                nwin = len(win)
                if pot%nwin==0:
                    split_pot = pot/nwin
                    for j in win:
                        j.money+=split_pot
                        winner_listup.append((j.id,split_pot))
                    i['value']=0
                else:
                    rest = pot%nwin
                    pot-=rest
                    split_pot = pot/nwin
                    for j in win:
                        j.money+=split_pot
                        if rest>0:
                            j.money+=1
                            rest-=1
                            winner_listup.append((j.id,split_pot+1))
                        else:
                            winner_listup.append((j.id,split_pot))
                    i['value']=0
            else: # One winner
                print("No split to do")
                win.money+=pot
                winner_listup.append((win.id,pot))
                pot=0
            yield [x.id for x in i['player_list']], winner_listup, combo               #PLAYER_LIST,WINNER(S),POT,COMBO

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
                    if max_score==1:combo = "a high card"
                    elif max_score==2:combo = "a pair"
                    elif max_score==3:combo = "two pairs"
                    elif max_score==4:combo = "a three of a kind"
                    elif max_score==5:combo = "a straight"
                    elif max_score==6:combo = "a flush"
                    elif max_score==7:combo = "a full house"
                    elif max_score==8:combo = "a four of a kind"
                    elif max_score==9:combo = "a straight flush"
                    elif max_score==10:combo = "a royal flush"
                    return i,combo
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
                            return winner,"a high card"
                    if cc==kicker_cards:
                        print(f"It's a tie between {['Player '+str(x.id) for x in finalists]} for the win")
                        return finalists,"a high card"
                else:
                    winner = max(top_cards.items(),key=operator.itemgetter(1))[0]
                    print(f"Player {winner.id} wins")
                    return winner,"a high card"
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
                            return winner,"a pair"
                    if cc==kicker_cards:
                        print(f"It's a tie between {['Player '+str(x.id) for x in finalists]} for the win")
                        return finalists,"a pair"
                else:
                    winner = max(top_cards.items(),key=operator.itemgetter(1))[0]
                    print(f"Player {winner.id} wins")
                    return winner,"a pair"
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
                        return winner,"twp pairs"
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
                            return finalists,"two pairs"
                        else:
                            winner = max(top_cards.items(),key=operator.itemgetter(1))[0]
                            print(f"Winner : {winner}")
                            return winner,"two pairs"
                else:
                    winner = max(top_cards.items(),key=operator.itemgetter(1))[0]
                    print(f"Player {winner.id} wins")
                    return winner,"two pairs"
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
                            return winner,"a three of a kind"
                    if cc==kicker_cards:
                        print(f"It's a tie between {['Player '+str(x.id) for x in finalists]} for the win")
                        return finalists,"a three of a kind"
                else:
                    winner = max(top_cards.items(),key=operator.itemgetter(1))[0]
                    print(f"Player {winner.id} wins")
                    return winner,"a three of a kind"
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
                            return winner,"a straight"
                        del final_battle
                    if cc==kicker_cards:
                        print(f"It's a tie between {['Player '+str(x.id) for x in finalists]} for the win")
                        return finalists,"a straight"
                else:
                    winner = max(top_cards.items(),key=operator.itemgetter(1))[0]
                    print(f"Player {winner.id} wins")
                    return winner,"a straight"
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
                            return winner,"a flush"
                        del final_battle
                    if cc==kicker_cards:
                        print(f"It's a tie between {['Player '+str(x.id) for x in finalists]} for the win")
                        return finalists,"a flush"
                else:
                    winner = max(top_cards.items(),key=operator.itemgetter(1))[0]
                    print(f"Player {winner.id} wins")
                    return winner,"a flush"
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
                        return winner,"a full house"
                    if list(final_battle.values()).count(max_card)>1:
                        print(f"It's a tie between {['Player '+str(x.id) for x in finalists]} for the win")
                        return finalists,"a full house"
                else:
                    winner = max(top_cards.items(),key=operator.itemgetter(1))[0]
                    print(f"Player {winner.id} wins")
                    return winner,"a full house"
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
                            return winner,"a four of a kind"
                    if cc==kicker_cards:
                        print(f"It's a tie between {['Player '+str(x.id) for x in finalists]} for the win")
                        return finalists,"a four of a kind"
                else:
                    winner = max(top_cards.items(),key=operator.itemgetter(1))[0]
                    print(f"Player {winner.id} wins")
                    return winner,"a four of a kind"
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
                return winner,"a straight flush"
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
                return winner,"a royal flush"

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
