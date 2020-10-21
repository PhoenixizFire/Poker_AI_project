# Useful link to determine coordinates over an oval/ellipse : https://math.stackexchange.com/questions/22064/calculating-a-point-that-lies-on-an-ellipse-given-an-angle

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
import math
import time

WIDTH = 1600
HEIGHT = 900

class VisualGame(Game):

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Poker AI Project")
        self.root.iconbitmap('images/chips.ico')
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

        self.settings_panel = tk.Frame(self.root)

        self.var_players = tk.IntVar(value=6)
        self.var_money = tk.IntVar(value=1500)
        self.var_simulation = tk.IntVar(value=1)

        self.settings_back = tk.Button(self.settings_panel, text='<',command=self.open_settings_menu,width=3,height=1,font=(None,10,'bold'))
        self.settings_back.grid(row=0,column=0,padx=10,pady=10,sticky='nw')

        self.settings_label = tk.Label(self.settings_panel, text='Settings',font=(None,50))
        self.settings_label.grid(row=0,column=1,columnspan=3,padx=10,pady=20)

        self.settings_player = tk.Spinbox(self.settings_panel,from_=2,to_=10,increment=1,textvariable=self.var_players,width=10,font=(None,13))
        self.settings_player.grid(row=2,column=1,padx=10,pady=20)

        self.settings_money = tk.Entry(self.settings_panel,textvariable=self.var_money,width=10,font=(None,13))
        self.settings_money.grid(row=2,column=2,padx=10,pady=20)

        self.settings_simulation = tk.Checkbutton(self.settings_panel,text='Simulation',width=10,font=(None,13),variable=self.var_simulation)
        self.settings_simulation.grid(row=2,column=3,padx=10,pady=20)

        self.root.mainloop()

    def open_settings_menu(self):
        if self.settings_panel.winfo_ismapped()==True:
            self.settings_panel.grid_forget()
            self.main_menu.grid()
        else:
            self.main_menu.grid_forget()
            self.settings_panel.grid()

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
            self.background.itemconfig(i.player_hand,text=f"{i.hand}")

        Game.the_flop(self)
        self.background.itemconfig(self.community_cards,text=f"{self.board.community_cards}")
        self.button_panel.grid_forget()
        self.background.grid_forget()
        self.background.grid(padx=0,pady=0)

    def update_display(self):
        for i in self.players:
            self.background.itemconfig(i.player_hand,text=f"{i.hand}")
            self.background.itemconfig(i.player_money,text=f"{i.money}")
            self.background.itemconfig(i.player_bet,text=f"{i.current_bet}")
            if i.dealer==False and i.small_blind==False and i.big_blind==False:
                self.background.itemconfig(i.player_button,fill='',width=0)
                self.background.itemconfig(i.player_button_name,text=f"")
            else:
                if i.dealer==True:
                    self.background.itemconfig(i.player_button,fill='white',width=1)
                    self.background.itemconfig(i.player_button_name,text=f"DE",font=(None,10,'bold'),fill='red')
                if i.small_blind==True:
                    self.background.itemconfig(i.player_button,fill='white',width=1)
                    self.background.itemconfig(i.player_button_name,text=f"SB",font=(None,10,'bold'))
                if i.big_blind==True:
                    self.background.itemconfig(i.player_button,fill='white',width=1)
                    self.background.itemconfig(i.player_button_name,text=f"BB",font=(None,10,'bold'))

        self.background.itemconfig(self.community_cards,text=f"{self.board.community_cards}")

    def main(self,simulation=False):
        turn=1
        Game.set_roles(self,turn)
        self.update_display()
        Game.set_blinds(self)
        self.update_display()
        Game.set_cards(self)
        self.update_display()

        #Game.set_first_round(self,autoplay,simulation)
        Game.the_flop(self)
        self.update_display()

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
        self.all_in = False
        
        self.game_menu = tk.Frame(self.root,bg='#4459E3') #bg same as self.background
        self.game_menu.rowconfigure(0,weight=10)
        self.game_menu.columnconfigure(0,weight=10)

        self.button_panel = tk.Frame(self.game_menu)
        self.button_panel.grid()

        self.init_button = tk.Button(self.button_panel,text='Play',command=self.main)
        self.init_button.grid(row=0,column=0,padx=10,pady=10)

        self.cards_button = tk.Button(self.button_panel,text='Give cards',command=self.set_cards)
        self.cards_button.grid(row=0,column=1,padx=10,pady=10)

        self.background = tk.Canvas(self.game_menu,width=WIDTH,height=HEIGHT,bd=0, highlightthickness=0, relief='ridge',bg='#4459E3') #bg='#4459E3'
        self.background.grid(padx=0,pady=0)

        self.background.create_oval(WIDTH/32*6,HEIGHT/18*5.3,WIDTH/32*26,HEIGHT/18*12.8,fill='#333333')
        self.background.create_oval(WIDTH/32*6.5,HEIGHT/18*5.7,WIDTH/32*25.5,HEIGHT/18*12.3,fill='#80522F')
        self.background.create_oval(WIDTH/32*7.5,HEIGHT/18*6.6,WIDTH/32*24.5,HEIGHT/18*11.4,fill='#2D9F01')

        angle = 360/n_players
        for i,x in enumerate(self.players):
            coord_x = ((((WIDTH/32*26)-(WIDTH/32*6))/2)+WIDTH/32*2)*math.cos(math.radians(i*angle))+WIDTH/2
            coord_y = ((((HEIGHT/18*12.8)-(HEIGHT/18*5.3))/2)+HEIGHT/18*2)*math.sin(math.radians(i*angle))+HEIGHT/2
            bet_x = ((((WIDTH/32*26)-(WIDTH/32*6))/2)-WIDTH/32*2)*math.cos(math.radians(i*angle))+WIDTH/2
            bet_y = ((((HEIGHT/18*12.8)-(HEIGHT/18*5.3))/2)-HEIGHT/18*2)*math.sin(math.radians(i*angle))+HEIGHT/2

            x.player_active = self.background.create_rectangle(coord_x - WIDTH/32*1, coord_y - HEIGHT/18*1, coord_x + WIDTH/32*1, coord_y + HEIGHT/18*1, fill='#FFFFFF',)
            x.player_name   = self.background.create_text(     coord_x,              coord_y,                                                            text=x.id)
            x.player_money  = self.background.create_text(     coord_x,              coord_y+HEIGHT/18*0.5,                                              text=f"{x.money} $")
            x.player_hand   = self.background.create_text(     coord_x,              coord_y+HEIGHT/18*1.5,                                              text=f"{x.hand}")
            x.player_button = self.background.create_oval(     coord_x-WIDTH/32*1.25,coord_y+HEIGHT/18*0.75,coord_x-WIDTH/32*0.75,coord_y+HEIGHT/18*1.25,fill='',width=0)
            x.player_button_name = self.background.create_text(coord_x-WIDTH/32*1,   coord_y+HEIGHT/18*1,                                                text='')
            x.player_action = self.background.create_text(     coord_x,              coord_y-HEIGHT/18*1.5,                                              text='BET',fill='YELLOW',font=(None,10,'bold'))
            x.player_bet    = self.background.create_text(     bet_x,                bet_y,                                                              text=f"{x.current_bet}")

        self.community_board = self.background.create_rectangle(WIDTH/32*14,HEIGHT/18*6.5,WIDTH/32*18,HEIGHT/18*8, fill='#FFFFFF')
        self.community_cards = self.background.create_text(     WIDTH/32*16,HEIGHT/18*9,                           text=f"{self.board.community_cards}")
        self.pot             = self.background.create_text(     WIDTH/32*16,HEIGHT/18*7.25,                        text=f"{[x.id for x in self.board.active_pot['player_list']]}\n{self.board.active_pot['value']}")

    def setup_game_menu(self):
        try:
            if self.var_money.get()>0:
                self.init_game(self.var_players.get(),self.var_money.get(),simulation=True)
            else:
                CRASH = 42/0
        except:
            self.init_game(self.var_players.get(),1500,simulation=True)
        self.main_menu.grid_forget()
        self.game_menu.grid(sticky="nsew")
        self.root.geometry(f"{int(WIDTH)}x{int(HEIGHT)}")

if __name__=='__main__':
    VisualGame()