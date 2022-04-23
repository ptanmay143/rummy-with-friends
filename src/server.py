import logging
import random
import socket
import struct
import threading
from tkinter import StringVar, Tk, messagebox
from tkinter.constants import DISABLED
from tkinter.ttk import Button, Entry, Frame, Label

logging.basicConfig(level=logging.DEBUG)

SUIT = ["H", "C", "S", "D"]
RANK = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K"]


class App(Tk):
    def __init__(self):
        super().__init__()

        self.game_server = GameServer(self)

        self.draw_ui()
        self.position_ui()

    def draw_ui(self):
        self.title("Rummy With Friends")
        self.server_div = Frame(self)
        self.n_players_input_str = StringVar()
        self.n_players_label = Label(self.server_div, text="No. of players: ")
        self.n_players_input = Entry(
            self.server_div, textvariable=self.n_players_input_str, width=20
        )
        self.status_button = Button(
            self.server_div, text="Start", command=self.game_server.run
        )

    def position_ui(self):
        self.server_div.grid(row=0, column=0, padx=10, pady=10)
        self.n_players_label.grid(row=0, column=0)
        self.n_players_input.grid(row=0, column=1)
        self.status_button.grid(row=0, column=2, padx=5)


class GameServer:
    def __init__(self, app):
        self.app = app

    def run(self, n_players=2):
        try:
            self.n_players = int(
                self.app.n_players_input_str.get()) or n_players
            self.player_count = 0
            self.players = {}

            self.address = "0.0.0.0"
            self.port = 65432
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self.address, int(self.port)))
            self.server.listen(5)

            self.app.status_button.config(text="Started", state=DISABLED)
            self.app.n_players_input.config(state=DISABLED)

            listen_t = threading.Thread(target=self.listen)
            listen_t.start()

        except:
            messagebox.showerror(title="Game Error",
                                 message="Cannot start game.")

    def listen(self):
        while True:
            client, address = self.server.accept()
            threaded_player = Player(self)
            threaded_player.run(id=self.player_count, client=client)
            self.players[self.player_count] = threaded_player
            self.player_count += 1
            logging.debug("Connected to " + address[0] + ":" + str(address[1]))

            if self.player_count == self.n_players:
                self.check_ready_t = threading.Thread(target=self.check_ready)
                self.check_ready_t.start()

    def check_ready(self):
        while True:
            all_ready = True
            for p_id in self.players.keys():
                player = self.players[p_id]
                all_ready = all_ready and player.is_ready
            if all_ready == True:
                self.start_game()
                break

    def start_game(self, n_cards=10):
        self.stock_deck = [(r + s) for s in SUIT for r in RANK]
        random.shuffle(self.stock_deck)

        for _ in range(n_cards):
            for player in self.players.values():
                card = self.stock_deck.pop()
                player.stash_deck.append(card)
                data = "@STASH " + card
                player.sendall(data)
                logging.debug("Sent " + card + " to stash")

        discard_top = self.stock_deck.pop()
        self.discard_deck = [discard_top]
        data = "@DISCARD " + discard_top
        for player in self.players.values():
            player.sendall(data)
            logging.debug("Sent " + card + " to discard")

        first_player = self.players[0]
        first_player.is_drawing = True
        data = "@DRAWING"
        first_player.sendall(data)


class Player:
    def __init__(self, game_server):
        self.game_server = game_server

    def run(self, id, client):
        self.id = id
        self.client = client
        self.stash_deck = []
        self.is_ready = False
        self.is_drawing = False
        self.is_dropping = False

        data = "@ID " + str(self.id)
        self.sendall(data)

        listen_t = threading.Thread(target=self.listen)
        listen_t.start()

    def listen(self):
        while True:
            reply = self.recv_msg()
            if not reply:
                break
            else:
                self.handle_command(reply)
        self.client.close()
        self.game_server.players[self.id] = None

    def recv_msg(self):
        raw_msglen = self.recvall(4)
        if not raw_msglen:
            return None
        msglen = struct.unpack(">I", raw_msglen)[0]
        reply = self.recvall(msglen).decode()
        logging.debug("FROM CLIENT --> " + str(reply))
        return reply

    def recvall(self, n):
        data = bytearray()
        while len(data) < n:
            packet = self.client.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data

    def sendall(self, data):
        self.client.sendall(struct.pack(">I", len(data)) + data.encode())
        logging.debug("TO CLIENT {} --> ".format(self.id) + str(data))

    def handle_command(self, command):
        if "@READY" in command:
            self.is_ready = True
        elif "@DRAW" in command:
            cmd = command.split()
            deck = cmd[1]
            if deck == "STOCK":
                self.draw_stock()
            elif deck == "DISCARD":
                self.draw_discard()
            self.is_drawing = False
            self.is_dropping = True
            data = "@DROPPING"
            self.sendall(data)
        elif "@DROP" in command:
            cmd = command.split(" ")
            card = cmd[1]
            self.drop(card)
            self.is_drawing = False
            self.is_dropping = False
            data = "@IDLE"
            self.sendall(data)

            n_players = len(self.game_server.players)
            if self.id + 1 >= n_players:
                next_id = 0
            else:
                next_id = self.id + 1
            next_player = self.game_server.players[next_id]
            next_player.is_drawing = True
            data = "@DRAWING"
            next_player.sendall(data)

        elif "@END" in command:
            self.end()

    def draw_stock(self):
        card = self.game_server.stock_deck.pop()
        if len(self.game_server.stock_deck) == 0:
            self.game_server.stock_deck = self.game_server.discard_deck[:-1].reverse(
            )
            self.game_server.discard_deck = [self.game_server.discard_deck[-1]]
        logging.debug("Stash Before --> " + str(self.stash_deck))
        logging.debug("Drawing Stock --> " + str(card))
        self.stash_deck.append(card)
        logging.debug("Stash After --> " + str(self.stash_deck))
        data = "@STASH " + card
        self.sendall(data)
        data = "@STOCK " + card
        self.sendall(data)

    def draw_discard(self):
        card = self.game_server.discard_deck.pop()
        logging.debug("Stash Before --> " + str(self.stash_deck))
        logging.debug("Drawing Discard --> " + str(card))
        self.stash_deck.append(card)
        logging.debug("Stash After --> " + str(self.stash_deck))
        data = "@STASH " + card
        self.sendall(data)
        if len(self.game_server.discard_deck) > 0:
            top = self.game_server.discard_deck[-1]
            data = "@DISCARD " + top
            for player in self.game_server.players.values():
                player.sendall(data)

    def drop(self, card):
        logging.debug("Stash Before --> " + str(self.stash_deck))
        logging.debug("Dropping --> " + str(card))
        idx = self.stash_deck.index(card)
        del self.stash_deck[idx]
        logging.debug("Stash After --> " + str(self.stash_deck))
        self.game_server.discard_deck.append(card)
        discard_top = self.game_server.discard_deck[-1]
        data = "@DISCARD " + discard_top
        for player in self.game_server.players.values():
            player.sendall(data)

    def end(self):
        # set this player as winner
        # send lose signal to rest players
        # close game and app gracefully
        data = "@END"
        for player in self.game_server.players.values():
            if not player == self:
                player.sendall(data)


if __name__ == "__main__":
    app = App()
    app.mainloop()
