from board import Board
from cards import Deck
from player import Player
import random

## n_players between 2 to 10. 3 to 10 for now on
## if 2 players, Dealer is Small Blind
## small blind and big blind needs to put money before cards are distributed

class Game:

    def __init__(self,n_players,base_money):
        print('Starting the game')
        print('Creating the board')
        self.board = Board()
        print('Shuffling the cards')
        self.deck = Deck()
        print('Filling players pockets')
        self.players = [Player(i+1,base_money) for i in range(n_players)]
        self.main()
    
    def main(self):
        turn = 0
        while len(self.players)>1:
            turn+=1
            self.set_roles(turn)
            self.set_blinds()
            self.set_cards()
            ### GAME
            self.set_first_round()
            ### GAME
            self.deck.reset()
            break

    def available_moves(self,phase):
        moves = list()
        moves.append("Fold") # EVERYTIME
        moves.append("Call") # ONLY IN PRE FLOP OR LATER IF THERE IS AN ACTIVE BET
        moves.append("Raise") # ONLY IN PRE FLOP OR LATER IF THERE IS AN ACTIVE BET
        moves.append("Bet") # ONLY AFTER PRE FLOP IF NO ACTIVE BET
        moves.append("Check") # ONLY AFTER PRE FLOP IF NO ACTIVE BET
        return moves

    def play_moves(self,player,choice):
        if choice == "Fold":
            player.fold()
        elif choice == "Call":
            player.call()
        elif choice == "Raise":
            player.relaunch()
        elif choice == "Bet":
            player.bet()
        elif choice == "Check":
            player.check()

    def set_roles(self,turn):
        n_players = len(self.players)
        for i in self.players:
            i.dealer = False
            i.small_blind = False
            i.big_blind = False
        print("Players status reset")
        self.players[(turn-1)%n_players].dealer = True
        print(f"Player {((turn-1)%n_players)+1} is the dealer")
        self.players[turn%n_players].small_blind = True
        print(f"Player {(turn%n_players)+1} is the small blind")
        self.players[(turn+1)%n_players].big_blind = True
        print(f"Player {((turn+1)%n_players)+1} is the dealer")

    def set_blinds(self):
        for i in self.players:
            if i.small_blind==True:
                self.board.small_blind = i.set_blind()
        print('Small blind set')
        for i in self.players:
            if i.big_blind==True:
                self.board.big_blind = i.set_blind()
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

    def set_first_round(self):
        n_players = len(self.players)
        for i in self.players:
            if i.big_blind:
                get_id = i.id
        play_order = [(get_id+i)%n_players+1 for i in range(n_players)]
        ## print(f"{play_order}")
        for i in play_order:
            for j in self.players:
                if j.id==i:
                    ## PLAY
                    choice = input(f"Player {i}, what do you want to do ? {self.available_moves(1)}")
                    self.play_moves(j,choice)

    def the_flop(self): # Need to burn the first card from the deck before flopping
        for _ in range(3):
            draw = random.choice(self.deck.content)
            self.board.community_cards.append(draw)
            self.deck.content.remove(draw)

    def set_second_round(self):
        pass

    def the_turn(self): #same as the flop but one card only # Need to burn the first card from the deck before flopping
        draw = random.choice(self.deck.content)
        self.board.community_cards.append(draw)
        self.deck.content.remove(draw)

    def set_third_round(self): #same as second
        pass

    def the_river(self): #same as the turn # Need to burn the first card from the deck before flopping
        draw = random.choice(self.deck.content)
        self.board.community_cards.append(draw)
        self.deck.content.remove(draw)

    def set_fourth_round(self): #same as second and third
        pass

    def showdown(self): #everyone reveals their cards
        pass
        #ONE PAIR (Detect two of the same value) Highest pair wins
        #TWO PAIR (Detect two of the same value twice) Highest value in pairs wins
        #THREE OF A KIND (Detect three of the same value) Highest three of a kind wins
        #STRAIGTH (Five cards with values that follows. E.G. 5,6,7,8,9) Highest card in straight wins
        #FLUSH (Five card with the same figure) Highest card in flush wins
        #FULL HOUSE (Pair + Three of a kind) Highest three of a kind, then highest pair
        #FOUR OF A KIND (Detect four of the same value) Highest four of a kind wins
        #STRAIGHT FLUSH (Five cards with values that follows + the same figure)
        #ROYAL FLUSH (10,J,Q,K,A of the same figure)
