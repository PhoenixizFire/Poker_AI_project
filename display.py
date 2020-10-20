import tkinter as tk
from game import Game
from player import Player
from bots import Bot
from board import Board
from cards import Deck
import random
import colorama as cr
from PIL import Image,ImageTk
import webbrowser

WIDTH = 1200
HEIGHT = 675

class VisualGame:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Poker")
        self.root.geometry(f"{int(WIDTH*.66)}x{int(HEIGHT*.66)}")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.background_image = Image.open("images/Blue.jpg")
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        self.background_label = tk.Label(self.root,image=self.background_photo)
        self.background_label.place(x=0,y=0,relwidth=1,relheight=1)

        self.main_menu = tk.Frame(self.root)
        self.main_menu.grid()

        self.game_title = tk.Label(self.main_menu,text="Poker AI Project",font=(None,75))
        self.game_title.grid(row=0,padx=10,pady=10,columnspan=3)

        self.play_button = tk.Button(self.main_menu, text='Play',command=self.setup_game_menu, width=10,height=2,font=(None,15))
        self.play_button.grid(row=1,column=0,padx=5,pady=20)

        self.settings_button = tk.Button(self.main_menu,text='Settings',command=self.open_settings_menu,width=10,height=2,font=(None,15))
        self.settings_button.grid(row=1,column=1,padx=5,pady=20)

        self.credits_button = tk.Button(self.main_menu, text='GitHub', command=self.show_credits,width=10,height=2,font=(None,15))
        self.credits_button.grid(row=1,column=2,padx=5,pady=20)

        self.settings_panel = tk.Frame(self.main_menu)

        self.settings_player = tk.Spinbox(self.settings_panel,from_=2,to_=10,increment=1,textvariable=tk.DoubleVar(value=6))
        self.settings_player.grid(row=0,column=0,padx=10,pady=20)

        self.settings_money = tk.Entry(self.settings_panel,textvariable=tk.DoubleVar(value=1500))
        self.settings_money.grid(row=0,column=1,padx=10,pady=20)

        self.settings_simulation = tk.Checkbutton(self.settings_panel,text='Simulation',variable=tk.IntVar(value=1))
        self.settings_simulation.grid(row=0,column=2,padx=10,pady=10)

        self.root.mainloop()

    def open_settings_menu(self):
        if self.settings_panel.winfo_ismapped()==True:
            self.settings_panel.grid_forget()
        else:
            self.settings_panel.grid(row=2,columnspan=3,padx=10,pady=20)

    def show_credits(self):
        webbrowser.open('http://github.com/PhoenixizFire')

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
        self.background.itemconfig(self.player2_hand,text=f"{self.players[1].hand}")
        self.background.itemconfig(self.player3_hand,text=f"{self.players[2].hand}")
        self.background.itemconfig(self.player4_hand,text=f"{self.players[3].hand}")
        self.background.itemconfig(self.player5_hand,text=f"{self.players[4].hand}")
        self.background.itemconfig(self.player6_hand,text=f"{self.players[5].hand}")
        self.background.itemconfig(self.community_cards,text=f"{self.board.community_cards}")

        self.init_button.grid_forget()
        self.background.grid_forget()
        self.background.grid(padx=0,pady=0)

    def init_game(self,n_players,base_money,sb=25,bb=50,simulation=False):
        print('Starting the game')
        print('The players come sit around the table')
        if simulation==True:
            self.players = [Player(i+1,base_money,bot=Bot("Random")) for i in range(n_players-1)]+[Player(n_players,base_money)]
        else:
            self.players = [Player(i+1,base_money) for i in range(n_players)]
        print('Setting up the board')
        self.board = Board(sb,bb,self.players)
        print('Shuffling the cards')
        self.deck = Deck()
        self.deck.big
        self.all_in = False
        
        self.game_menu = tk.Frame(self.root,bg='#4459E3')
        self.game_menu.rowconfigure(0,weight=10)
        self.game_menu.columnconfigure(0,weight=10)

        self.init_button = tk.Button(self.game_menu,text='Play',command=self.set_cards)
        self.init_button.grid()

        self.background = tk.Canvas(self.game_menu,width=WIDTH,height=HEIGHT,bg='#4459E3',bd=0, highlightthickness=0, relief='ridge')
        self.background.grid(padx=0,pady=0)

        self.background.create_oval(WIDTH/32*6,HEIGHT/18*5.3,WIDTH/32*26,HEIGHT/18*12.8,fill='#333333')
        self.background.create_oval(WIDTH/32*6.5,HEIGHT/18*5.7,WIDTH/32*25.5,HEIGHT/18*12.3,fill='#80522F')
        self.background.create_oval(WIDTH/32*7.5,HEIGHT/18*6.6,WIDTH/32*24.5,HEIGHT/18*11.4,fill='#2D9F01')

        self.player1_active = self.background.create_rectangle(WIDTH/32*3, HEIGHT/18*8, WIDTH/32*5,  HEIGHT/18*10,fill='#FFFFFF',)
        self.player1_name   = self.background.create_text(     WIDTH/32*4, HEIGHT/18*9,                           text=self.players[0].id)
        self.player1_money  = self.background.create_text(     WIDTH/32*4, HEIGHT/18*9.5,                         text=f"{self.players[0].money} $")
        self.player1_hand   = self.background.create_text(     WIDTH/32*4, HEIGHT/18*10.5,                        text=f"{self.players[0].hand}")
        self.player2_active = self.background.create_rectangle(WIDTH/32*10,HEIGHT/18*3, WIDTH/32*12, HEIGHT/18*5, fill='#FFFFFF')
        self.player2_name   = self.background.create_text(     WIDTH/32*11,HEIGHT/18*4,                           text=self.players[1].id)
        self.player2_money  = self.background.create_text(     WIDTH/32*11,HEIGHT/18*4.5,                         text=f"{self.players[1].money} $")
        self.player2_hand   = self.background.create_text(     WIDTH/32*11,HEIGHT/18*5.5,                         text=f"{self.players[1].hand}")
        self.player3_active = self.background.create_rectangle(WIDTH/32*21,HEIGHT/18*3, WIDTH/32*23, HEIGHT/18*5, fill='#FFFFFF')
        self.player3_name   = self.background.create_text(     WIDTH/32*22,HEIGHT/18*4,                           text=self.players[2].id)
        self.player3_money  = self.background.create_text(     WIDTH/32*22,HEIGHT/18*4.5,                         text=f"{self.players[2].money} $")
        self.player3_hand   = self.background.create_text(     WIDTH/32*22,HEIGHT/18*5.5,                         text=f"{self.players[2].hand}")
        self.player4_active = self.background.create_rectangle(WIDTH/32*27,HEIGHT/18*8, WIDTH/32*29, HEIGHT/18*10,fill='#FFFFFF')
        self.player4_name   = self.background.create_text(     WIDTH/32*28,HEIGHT/18*9,                           text=self.players[3].id)
        self.player4_money  = self.background.create_text(     WIDTH/32*28,HEIGHT/18*9.5,                         text=f"{self.players[3].money} $")
        self.player4_hand   = self.background.create_text(     WIDTH/32*28,HEIGHT/18*10.5,                         text=f"{self.players[3].hand}")
        self.player5_active = self.background.create_rectangle(WIDTH/32*21,HEIGHT/18*13,WIDTH/32*23, HEIGHT/18*15,fill='#FFFFFF')
        self.player5_name   = self.background.create_text(     WIDTH/32*22,HEIGHT/18*14,                          text=self.players[4].id)
        self.player5_money  = self.background.create_text(     WIDTH/32*22,HEIGHT/18*14.5,                        text=f"{self.players[4].money} $")
        self.player5_hand   = self.background.create_text(     WIDTH/32*22,HEIGHT/18*15.5,                        text=f"{self.players[4].hand}")
        self.player6_active = self.background.create_rectangle(WIDTH/32*10,HEIGHT/18*13,WIDTH/32*12, HEIGHT/18*15,fill='#FFFFFF')
        self.player6_name   = self.background.create_text(     WIDTH/32*11,HEIGHT/18*14,                          text=self.players[5].id)
        self.player6_money  = self.background.create_text(     WIDTH/32*11,HEIGHT/18*14.5,                        text=f"{self.players[5].money} $")
        self.player6_hand   = self.background.create_text(     WIDTH/32*11,HEIGHT/18*15.5,                        text=f"{self.players[5].hand}")

        self.community_board = self.background.create_rectangle(WIDTH/32*14,HEIGHT/18*6.5,WIDTH/32*18,HEIGHT/18*8,fill='#FFFFFF')
        self.community_cards = self.background.create_text(     WIDTH/32*16,HEIGHT/18*9,                         text=f"{self.board.community_cards}")

    def setup_game_menu(self):
        self.init_game(6,1500,simulation=True)
        self.main_menu.grid_forget()
        self.game_menu.grid(sticky="nsew")
        self.root.geometry(f"{int(WIDTH)}x{int(HEIGHT)}")

if __name__=='__main__':
    VisualGame()