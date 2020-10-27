# Useful link to determine coordinates over an oval/ellipse : https://math.stackexchange.com/questions/22064/calculating-a-point-that-lies-on-an-ellipse-given-an-angle
# How to scroll a widget based on platform : https://stackoverflow.com/questions/17355902/tkinter-binding-mousewheel-to-scrollbar
# How to determine platform : https://stackoverflow.com/questions/1854/python-what-os-am-i-running-on
# Wait for event : https://stackoverflow.com/questions/44790449/making-tkinter-wait-untill-button-is-pressed

import tkinter as tk
from datetime import datetime
from tkinter.scrolledtext import ScrolledText
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
import os,sys,platform

WIDTH = 1440
HEIGHT = 810

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
        if platform.system()==("Windows" or "Darwin"):
            self.settings_panel.bind_all("<MouseWheel>",self._on_mousewheel)
        elif platform.system()=="Linux":
            self.settings_panel.bind_all("<Button-4>",self._on_mousewheel)
            self.settings_panel.bind_all("<Button-5>",self._on_mousewheel)

        self.settings_money = tk.Entry(self.settings_panel,textvariable=self.var_money,width=10,font=(None,13))
        self.settings_money.grid(row=2,column=2,padx=10,pady=20)

        self.settings_simulation = tk.Checkbutton(self.settings_panel,text='Simulation',width=10,font=(None,13),variable=self.var_simulation)
        self.settings_simulation.grid(row=2,column=3,padx=10,pady=20)

        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.mainloop()

    #def __del__(self):
        #self.root.destroy()
    #    self._update_key = False
    #    self.after(500,self.update_display())

    def _on_closing(self):
        self.root.destroy()

    def _pause(self):
        if self._update_key == True:
            self._update_key = False
            self.pause_button.config(text='PLAY')
            self.pause_button.grid_forget()
            self.pause_button.grid(row=0,column=0)
        else:
            self._update_key = True
            self.update_display()
            self.pause_button.config(text='PAUSE')
            self.pause_button.grid_forget()
            self.pause_button.grid(row=0,column=0)

    def _on_mousewheel(self,event):
        if self.settings_panel.winfo_ismapped()==True:
            if platform.system()==('Windows' or 'Linux'):
                if event.delta == -120:
                    self.settings_player.invoke('buttondown')
                if event.delta == 120:
                    self.settings_player.invoke('buttonup')
            if platform.system()==('Darwin'):
                if event.delta == -1:
                    self.settings_player.invoke('buttondown')
                if event.delta == 1:
                    self.settings_player.invoke('buttonup')

    def _log_message(self,message,log_screen=True):
        datestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        with open('log.txt','a+') as f:
            f.write(str(datestamp)+" : "+message+'\n')
        if log_screen:
            self.historic.config(state='normal')
            self.historic.insert('insert',message+'\n')
            self.historic.config(state='disabled')
            self.historic.see('end')

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
        try:
            if self._update_key==True:
                for i in self.players:
                    if i.active==False:
                        self.background.itemconfig(i.player_active,fill='#888888')
                    else:
                        self.background.itemconfig(i.player_active,fill='white')
                    if i.money==0 and i.all_in==False:
                        self.background.itemconfig(i.player_active,fill='#555555')
                    self.background.itemconfig(i.player_hand,text=f"{i.hand}")
                    self.background.itemconfig(i.player_money,text=f"{i.money} $")
                    self.background.itemconfig(i.player_bet,text=f"{i.current_bet}")
                    if i.all_in==True:
                        self.background.itemconfig(i.player_action,text='All-in')
                    else:
                        self.background.itemconfig(i.player_action,text=f'{i.last_move}')
                    if i.dealer==False and i.small_blind==False and i.big_blind==False:
                        self.background.itemconfig(i.player_button,fill='',width=0)
                        self.background.itemconfig(i.player_button_name,text=f"")
                    else:
                        if i.dealer==True:
                            self.background.itemconfig(i.player_button,fill='white',width=1)
                            self.background.itemconfig(i.player_button_name,text=f"DE",font=(None,10,'bold'),fill='red')
                        if i.small_blind==True:
                            self.background.itemconfig(i.player_button,fill='white',width=1)
                            self.background.itemconfig(i.player_button_name,text=f"SB",font=(None,10,'bold'),fill='black')
                        if i.big_blind==True:
                            self.background.itemconfig(i.player_button,fill='white',width=1)
                            self.background.itemconfig(i.player_button_name,text=f"BB",font=(None,10,'bold'),fill='black')

                try:
                    for i in self.pot_table:
                        i.grid_forget()
                except:
                    self._log_message('Impossible de pot_table.grid_forget()',False)

                self.pot_table = list()
                if len(self.board.pots)>0:
                    for i in range(len(self.board.pots)):
                        slot = tk.Entry(self.pots,textvariable=tk.StringVar(value=[x.id for x in self.board.pots[i]['player_list']]))
                        slot.grid(row=0,column=i)
                        slot2 = tk.Entry(self.pots,textvariable=tk.StringVar(value=self.board.pots[i]['value']))
                        slot2.grid(row=1,column=i)
                        self.pot_table.append(slot)
                        self.pot_table.append(slot2)

                self.background.itemconfig(self.community_cards,text=f"{self.board.community_cards}")
                self.background.itemconfig(self.pot, text=f"Current bid : {self.board.current_bid}\n{[x.id for x in self.board.active_pot['player_list']]}\n{self.board.active_pot['value']}")
                self.root.after(500,self.update_display)

        except:
            print("Fenêtre introuvable")

    def reset_actions(self):
        for i in self.players:
            i.reset_move()

    def main(self,simulation=False):
        self.pause_button = tk.Button(self.game_menu,text='PAUSE',command=self._pause)
        self.pause_button.grid(row=0,column=0)

        self._continue_flag = tk.BooleanVar(value=False)
        autoplay=False
        turn=0
        while len([x for x in self.players if x.active==True])>1:
            turn+=1
            while True:
                self.update_display()
                self.init_button.grid_forget()
                self.cards_button.grid_forget()

                self.root.after(500,lambda : Game.set_roles(self,turn))
                self.root.after(1000,lambda : Game.set_blinds(self))
                self.root.after(1500,lambda : Game.set_cards(self))
                
                self.root.after(1500,self.background.itemconfig(self.current_step,text='Pre-Flop'))
                self.root.after(2000,lambda : self.set_first_round(autoplay,simulation))
                self.root.wait_variable(self._continue_flag)
                #self._update_key = True
                #self.update_display()
                self._continue_flag.set(False)
                self.root.after(2500,lambda : self.reset_actions())
                self.root.after(3000,lambda : Game.the_flop(self))
                
                self.root.after(3000,self.background.itemconfig(self.current_step,text='Flop'))
                self.root.after(3500,lambda : self.set_second_round(autoplay,simulation))
                self.root.wait_variable(self._continue_flag)
                #self._update_key = True
                #self.update_display()
                self._continue_flag.set(False)
                self.root.after(2500,lambda : self.reset_actions())
                self.root.after(3000,lambda : Game.the_turn(self))

                self.root.after(3000,self.background.itemconfig(self.current_step,text='Turn'))
                self.root.after(3500,lambda : self.set_third_round(autoplay,simulation))
                self.root.wait_variable(self._continue_flag)
                #self._update_key = True
                #self.update_display()
                self._continue_flag.set(False)
                self.root.after(2500,lambda : self.reset_actions())
                self.root.after(3000,lambda : Game.the_river(self))

                self.root.after(3000,self.background.itemconfig(self.current_step,text='River'))
                self.root.after(3500,lambda : self.set_fourth_round(autoplay,simulation))
                self.root.wait_variable(self._continue_flag)
                #self._update_key = True
                #self.update_display()
                self._continue_flag.set(False)
                break
            for i in self.players:
                i.checked=False
            self._log_message("### RESULTS ###")
            for output in self.distribute_pots():
                if len(output[1])==1:
                    self._log_message(f"In the pot containing players :\n    {output[0]},\nPlayer {output[1][0][0]} wins {output[1][0][1]} with {output[2]}")
                else:
                    for winner,money in output[1]:
                        self._log_message(f"In the pot containing players :\n    {output[0]},\nPlayer {winner} is tied on {output[2]} and wins {money}")
                self._log_message("")
            self.deck.reset()
            self.set_roles(turn)
            self.board.reset_board([x for x in self.players if x.active==True])
            for x in self.players:
                if x.money==0:
                    x.active=False
                x.last_move=""
            if turn==5:
                self._update_key = False
                break
        
    def init_game(self,n_players,base_money,sb=25,bb=50,simulation=False):
        self._update_key=True
        if simulation==True:
            self.players = [Player(i+1,base_money,bot=Bot("Random")) for i in range(n_players-1)]+[Player(n_players,base_money)]
        else:
            self.players = [Player(i+1,base_money) for i in range(n_players)]
        self.board = Board(sb,bb,self.players)
        self.deck = Deck()
        self.all_in = False
        
        self.game_menu = tk.Frame(self.root,bg='#3545B0') #bg same as self.background
        self.game_menu.rowconfigure(0,weight=15)
        self.game_menu.columnconfigure(0,weight=15)

        self.button_panel = tk.Frame(self.game_menu,bg='#3C4163')
        self.button_panel.grid(row=0,column=1)
        self.button_panel.rowconfigure(0,weight=1)

        self.init_button = tk.Button(self.button_panel,text='Play',command=lambda : self.main(simulation))
        self.init_button.grid(row=0,column=0,padx=10,pady=10)

        self.cards_button = tk.Button(self.button_panel,text='Give cards',command=self.set_cards)
        self.cards_button.grid(row=0,column=1,padx=10,pady=10)

        self.background = tk.Canvas(self.game_menu,width=WIDTH,height=HEIGHT,bd=0, highlightthickness=0, relief='ridge',bg='#3545B0') #bg='#4459E3'
        self.background.grid(row=1,column=1,padx=0,pady=0)

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
            x.player_name   = self.background.create_text(     coord_x,              coord_y,                                                            text=f'{x.id}')
            x.player_money  = self.background.create_text(     coord_x,              coord_y+HEIGHT/18*0.5,                                              text=f"{x.money} $")
            x.player_hand   = self.background.create_text(     coord_x,              coord_y+HEIGHT/18*1.5,                                              text=f"{x.hand}")
            x.player_button = self.background.create_oval(     coord_x-WIDTH/32*1.25,coord_y+HEIGHT/18*0.75,coord_x-WIDTH/32*0.75,coord_y+HEIGHT/18*1.25,fill='',width=0)
            x.player_button_name = self.background.create_text(coord_x-WIDTH/32*1,   coord_y+HEIGHT/18*1,                                                text='')
            x.player_action = self.background.create_text(     coord_x,              coord_y-HEIGHT/18*1.5,                                              text=f'{x.last_move}',fill='YELLOW',font=(None,10,'bold'))
            x.player_bet    = self.background.create_text(     bet_x,                bet_y,                                                              text=f"{x.current_bet}")

        self.community_board = self.background.create_rectangle(WIDTH/32*14,HEIGHT/18*6.5,WIDTH/32*18,HEIGHT/18*8, fill='#FFFFFF')
        self.current_step    = self.background.create_text(     WIDTH/32*16,HEIGHT/18*6,                           text="",fill='#31DEDE',font=(None,15,'bold'))
        self.community_cards = self.background.create_text(     WIDTH/32*16,HEIGHT/18*9,                           text=f"{self.board.community_cards}")
        self.pot             = self.background.create_text(     WIDTH/32*16,HEIGHT/18*7.25,                        text=f"{[x.id for x in self.board.active_pot['player_list']]}\n{self.board.active_pot['value']}")

        self.below_background = tk.Frame(self.game_menu)
        self.below_background.grid(row=2,column=1,sticky='s',padx=10,pady=20)

        self.pots = tk.Canvas(self.below_background,width=WIDTH/2,height=HEIGHT/18,bd=0,highlightthickness=0,relief='ridge',bg='#85503C')
        #for i in self.board.pots:
        #    self.pots.create_text(WIDTH/2,HEIGHT/2,text=f"{i['player_list']}\n{i['value']}")
        self.pots.grid()

        self.left_background = tk.Frame(self.game_menu,bg='BLACK',width=WIDTH/32*8,height=HEIGHT/18*12)
        self.left_background.grid_propagate(0)
        self.left_background.grid(row=1,column=0,sticky='w',padx=10,pady=20)
        
        self.historic = tk.Text(self.left_background,fg='#00FF00',bg='BLACK',height=int(math.floor((HEIGHT/18*12)/16)),bd=0,relief='ridge',highlightthickness=0,width=int(WIDTH/32*8))
        self.historic.config(state='disabled')
        self._log_message('Creating the board',False)
        self._log_message(f'Settings : Players = {n_players} ; Money = {base_money} ; Simulation = {simulation}',False)
        self.historic.grid(row=1,column=0,sticky='n')

    def set_first_round(self,autoplay=False,simulation=False):
        self._log_message("### PRE-FLOP ###")
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
                            i.last_move = i.bot.action(self.available_moves(1,i))
                        else:
                            self._chosen_action = tk.StringVar()
                            self._chosen_action.set('')
                            self._move_list = list()
                            for e,m in enumerate(self.available_moves(1,i)):
                                __button = tk.Button(self.button_panel,text=m,command=lambda m=m : self._move_choice(i,m))
                                self._move_list.append(__button)
                                self._move_list[e].grid(row=0,column=e,padx=10,pady=10)
                            self.settings_panel.wait_variable(self._chosen_action)
                            #self.update_display()
                    else:
                        self._chosen_action = tk.StringVar()
                        self._chosen_action.set('')
                        self._move_list = list()
                        for e,m in enumerate(self.available_moves(1,i)):
                            __button = tk.Button(self.button_panel,text=m,command=lambda m=m : self._move_choice(i,m))
                            self._move_list.append(__button)
                            self._move_list[e].grid(row=0,column=e,padx=10,pady=10)
                        self.settings_panel.wait_variable(self._chosen_action)
                        #self.update_display()
                    choice = i.last_move
                    output = self.play_moves(i,choice,1)
                    self._log_message(f"Player {i.id} did : {output}")
            while_token+=1
        self.manage_pots()
        self.board.current_bid=0
        self._continue_flag.set(True)
        #self._update_key = False

    def set_second_round(self,autoplay=False,simulation=False):
        self._log_message("### THE FLOP ###")
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
                            i.last_move = i.bot.action(self.available_moves(2,i))
                        else:
                            self._chosen_action = tk.StringVar()
                            self._chosen_action.set('')
                            self._move_list = list()
                            for e,m in enumerate(self.available_moves(2,i)):
                                __button = tk.Button(self.button_panel,text=m,command=lambda m=m : self._move_choice(i,m))
                                self._move_list.append(__button)
                                self._move_list[e].grid(row=0,column=e,padx=10,pady=10)
                            self.settings_panel.wait_variable(self._chosen_action)
                            #self.update_display()
                    else:
                        self._chosen_action = tk.StringVar()
                        self._chosen_action.set('')
                        self._move_list = list()
                        for e,m in enumerate(self.available_moves(2,i)):
                            __button = tk.Button(self.button_panel,text=m,command=lambda m=m : self._move_choice(i,m))
                            self._move_list.append(__button)
                            self._move_list[e].grid(row=0,column=e,padx=10,pady=10)
                        self.settings_panel.wait_variable(self._chosen_action)
                        #self.update_display()
                    choice = i.last_move
                    output = self.play_moves(i,choice,2)
                    self._log_message(f"Player {i.id} did : {output}")
            while_token+=1
        for i in self.players:
            i.checked=False
        self.manage_pots()
        self.board.current_bid=0
        self._continue_flag.set(True)
        #self._update_key = False

    def set_third_round(self,autoplay=False,simulation=False): #same as second
        self._log_message("### THE TURN ###")
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
                            i.last_move = i.bot.action(self.available_moves(3,i))
                        else:
                            self._chosen_action = tk.StringVar()
                            self._chosen_action.set('')
                            self._move_list = list()
                            for e,m in enumerate(self.available_moves(3,i)):
                                __button = tk.Button(self.button_panel,text=m,command=lambda m=m : self._move_choice(i,m))
                                self._move_list.append(__button)
                                self._move_list[e].grid(row=0,column=e,padx=10,pady=10)
                            self.settings_panel.wait_variable(self._chosen_action)
                            #self.update_display()
                    else:
                        self._chosen_action = tk.StringVar()
                        self._chosen_action.set('')
                        self._move_list = list()
                        for e,m in enumerate(self.available_moves(3,i)):
                            __button = tk.Button(self.button_panel,text=m,command=lambda m=m : self._move_choice(i,m))
                            self._move_list.append(__button)
                            self._move_list[e].grid(row=0,column=e,padx=10,pady=10)
                        self.settings_panel.wait_variable(self._chosen_action)
                        #self.update_display()
                    choice = i.last_move
                    output = self.play_moves(i,choice,3)
                    self._log_message(f"Player {i.id} did : {output}")
            while_token+=1
        for i in self.players:
            i.checked=False
        self.manage_pots()
        self.board.current_bid=0
        self._continue_flag.set(True)
        #self._update_key = False

    def set_fourth_round(self,autoplay=False,simulation=False): #same as second and third
        self._log_message("### THE RIVER ###")
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
                            i.last_move = i.bot.action(self.available_moves(4,i))
                        else:
                            self._chosen_action = tk.StringVar()
                            self._chosen_action.set('')
                            self._move_list = list()
                            for e,m in enumerate(self.available_moves(4,i)):
                                __button = tk.Button(self.button_panel,text=m,command=lambda m=m : self._move_choice(i,m))
                                self._move_list.append(__button)
                                self._move_list[e].grid(row=0,column=e,padx=10,pady=10)
                            self.settings_panel.wait_variable(self._chosen_action)
                            #self.update_display()
                    else:
                        self._chosen_action = tk.StringVar()
                        self._chosen_action.set('')
                        self._move_list = list()
                        for e,m in enumerate(self.available_moves(4,i)):
                            __button = tk.Button(self.button_panel,text=m,command=lambda m=m : self._move_choice(i,m))
                            self._move_list.append(__button)
                            self._move_list[e].grid(row=0,column=e,padx=10,pady=10)
                        self.settings_panel.wait_variable(self._chosen_action)
                        #self.update_display()
                    choice = i.last_move
                    output = self.play_moves(i,choice,4)
                    self._log_message(f"Player {i.id} did : {output}")
            while_token+=1
        self.manage_pots()
        self.board.current_bid=0
        self._continue_flag.set(True)
        
    def setup_game_menu(self):
        try:
            if self.var_money.get()>0:
                self.init_game(self.var_players.get(),self.var_money.get(),simulation=True)
            else:
                _ = 42/0
        except:
            self.init_game(self.var_players.get(),1500,simulation=True)
        self.main_menu.grid_forget()
        self.game_menu.grid(sticky="nsew")
        self.root.geometry(f"{int(WIDTH)}x{int(HEIGHT)}")

    def _move_choice(self,player,action):
        print("BUTTON PRESSED : "+action)
        player.last_move = action
        self._chosen_action.set(action)
        for i in self._move_list:
            i.grid_forget()

if __name__=='__main__':
    VisualGame()