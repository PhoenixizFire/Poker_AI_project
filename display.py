import tkinter as tk
from game import Game
from player import Player
from bots import Bot
from board import Board
from cards import Deck
import random
import colorama as cr

WIDTH = 1200
HEIGHT = 675

class VisualGame(Game):

    def __init__(self,n_players,base_money,simulation=False,sb=25,bb=50):
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

        self.root = tk.Tk()
        self.root.title = "Poker"

        self.play_button = tk.Button(self.root,text='Play',command=self.set_cards)
        self.play_button.pack()

        self.background = tk.Canvas(self.root,width=WIDTH,height=HEIGHT,bg='#2D9F01')
        self.background.pack()

        self.background.create_oval(WIDTH/32*5.5,HEIGHT/18*5,WIDTH/32*26.5,HEIGHT/18*13,fill='#80522F')

        self.background.create_rectangle(WIDTH/32*3, HEIGHT/18*8, WIDTH/32*5,  HEIGHT/18*10,fill='#FFFFFF',)
        self.background.create_text(     WIDTH/32*4, HEIGHT/18*9,                           text=self.players[0].id)
        self.background.create_text(     WIDTH/32*4, HEIGHT/18*9.5,                         text=f"{self.players[0].money} $")
        self.player1_hand = self.background.create_text(     WIDTH/32*4, HEIGHT/18*10.5,                        text=f"{self.players[0].hand}")
        self.background.create_rectangle(WIDTH/32*10,HEIGHT/18*3, WIDTH/32*12, HEIGHT/18*5, fill='#FFFFFF')
        self.background.create_text(     WIDTH/32*11,HEIGHT/18*4,                           text=self.players[1])
        self.background.create_text(     WIDTH/32*11,HEIGHT/18*4.5,                         text="8000 $")
        self.background.create_rectangle(WIDTH/32*21,HEIGHT/18*3, WIDTH/32*23, HEIGHT/18*5, fill='#FFFFFF')
        self.background.create_text(     WIDTH/32*22,HEIGHT/18*4,                           text=self.players[2])
        self.background.create_text(     WIDTH/32*22,HEIGHT/18*4.5,                         text="8000 $")
        self.background.create_rectangle(WIDTH/32*27,HEIGHT/18*8, WIDTH/32*29, HEIGHT/18*10,fill='#FFFFFF')
        self.background.create_text(     WIDTH/32*28,HEIGHT/18*9,                           text=self.players[3])
        self.background.create_text(     WIDTH/32*28,HEIGHT/18*9.5,                         text="8000 $")
        self.background.create_rectangle(WIDTH/32*21,HEIGHT/18*13,WIDTH/32*23, HEIGHT/18*15,fill='#FFFFFF')
        self.background.create_text(     WIDTH/32*22,HEIGHT/18*14,                          text=self.players[4])
        self.background.create_text(     WIDTH/32*22,HEIGHT/18*14.5,                        text="8000 $")
        self.background.create_rectangle(WIDTH/32*10,HEIGHT/18*13,WIDTH/32*12, HEIGHT/18*15,fill='#FFFFFF')
        self.background.create_text(     WIDTH/32*11,HEIGHT/18*14,                          text=self.players[5])
        self.background.create_text(     WIDTH/32*11,HEIGHT/18*14.5,                        text="8000 $")

        self.root.mainloop()

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
        self.background.itemconfig(self.player1_hand,text=f"{self.players[0].hand}")

if __name__=='__main__':
    VisualGame(6,1500,simulation=True)