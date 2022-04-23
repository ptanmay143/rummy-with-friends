import logging
import socket
import struct
import threading
from itertools import permutations
from tkinter import PhotoImage, StringVar, Tk, messagebox
from tkinter.constants import DISABLED, NORMAL
from tkinter.ttk import Button, Entry, Frame, Label, Radiobutton

logging.basicConfig(level=logging.DEBUG)

SUIT = ["H", "C", "S", "D"]
RANK = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K"]


class App(Tk):
    def __init__(self):
        super().__init__()

        self.game_client = GameClient(self)

        self.draw_ui()
        self.position_ui()

    def draw_ui(self):
        self.title("Rummy With Friends")

        # server connection
        self.server_connection_div = Frame(self)
        self.address_input_str = StringVar()
        self.address_label = Label(
            self.server_connection_div, text="Server Address: ", name="address_label"
        )
        self.address_input = Entry(
            self.server_connection_div, textvariable=self.address_input_str, width=20
        )
        self.status_button = Button(
            self.server_connection_div, text="Connect", command=self.game_client.run
        )

        # cards
        self.blank_card = PhotoImage(file="assets/cards_special/gray_back.png")

        self.card_images = {}
        for s in SUIT:
            for r in RANK:
                card_str = r + s
                card_path = "assets/cards/" + card_str + ".png"
                card_image = PhotoImage(file=card_path)
                self.card_images[card_str] = card_image

        # player stash
        self.stash_div = Frame(self)

        self.stash_card_idx_sel = StringVar()
        self.stash_card_rbtn_0 = Radiobutton(
            self.stash_div, image=self.blank_card, variable=self.stash_card_idx_sel,
        )

        self.stash_card_rbtn_1 = Radiobutton(
            self.stash_div, image=self.blank_card, variable=self.stash_card_idx_sel,
        )

        self.stash_card_rbtn_2 = Radiobutton(
            self.stash_div, image=self.blank_card, variable=self.stash_card_idx_sel,
        )

        self.stash_card_rbtn_3 = Radiobutton(
            self.stash_div, image=self.blank_card, variable=self.stash_card_idx_sel,
        )

        self.stash_card_rbtn_4 = Radiobutton(
            self.stash_div, image=self.blank_card, variable=self.stash_card_idx_sel,
        )

        self.stash_card_rbtn_5 = Radiobutton(
            self.stash_div, image=self.blank_card, variable=self.stash_card_idx_sel,
        )

        self.stash_card_rbtn_6 = Radiobutton(
            self.stash_div, image=self.blank_card, variable=self.stash_card_idx_sel,
        )

        self.stash_card_rbtn_7 = Radiobutton(
            self.stash_div, image=self.blank_card, variable=self.stash_card_idx_sel,
        )

        self.stash_card_rbtn_8 = Radiobutton(
            self.stash_div, image=self.blank_card, variable=self.stash_card_idx_sel,
        )

        self.stash_card_rbtn_9 = Radiobutton(
            self.stash_div, image=self.blank_card, variable=self.stash_card_idx_sel,
        )

        self.stash_card_rbtn_list = [
            self.stash_card_rbtn_0,
            self.stash_card_rbtn_1,
            self.stash_card_rbtn_2,
            self.stash_card_rbtn_3,
            self.stash_card_rbtn_4,
            self.stash_card_rbtn_5,
            self.stash_card_rbtn_6,
            self.stash_card_rbtn_7,
            self.stash_card_rbtn_8,
            self.stash_card_rbtn_9,
        ]

        # game deck
        self.deck_div = Frame(self)
        self.deck_sel = StringVar(value="DISCARD")

        self.stock_deck_rbtn = Radiobutton(
            self.deck_div, image=self.blank_card, variable=self.deck_sel, value="STOCK"
        )

        self.discard_deck_rbtn = Radiobutton(
            self.deck_div,
            image=self.blank_card,
            variable=self.deck_sel,
            value="DISCARD",
        )

        # player moves
        self.moves_div = Frame(self)
        self.draw_btn = Button(
            self.moves_div, text="Draw", command=self.game_client.draw
        )
        self.drop_btn = Button(
            self.moves_div, text="Drop", command=self.game_client.drop
        )
        self.end_btn = Button(self.moves_div, text="End",
                              command=self.game_client.end)

    def position_ui(self):
        self.server_connection_div.grid(row=0, column=0, padx=10, pady=10)
        self.address_label.grid(row=0, column=0)
        self.address_input.grid(row=0, column=1, padx=5)
        self.status_button.grid(row=0, column=3, padx=5)

        self.stash_div.grid(row=1, column=0, padx=10, pady=10)
        i = 0
        for row in range(2):
            for column in range(5):
                stash_card_rbtn = self.stash_card_rbtn_list[i]
                stash_card_rbtn.grid(row=row, column=column)
                i += 1
        for child in self.stash_div.winfo_children():
            child.configure(state=DISABLED)

        self.deck_div.grid(row=2, column=0, padx=10, pady=10)
        self.stock_deck_rbtn.grid(row=0, column=1)
        self.discard_deck_rbtn.grid(row=0, column=2)
        for child in self.deck_div.winfo_children():
            child.configure(state=DISABLED)

        self.moves_div.grid(row=3, column=0, padx=10, pady=10)
        self.draw_btn.grid(row=0, column=1, padx=5)
        self.drop_btn.grid(row=0, column=2, padx=5)
        self.end_btn.grid(row=0, column=3, padx=5)
        self.draw_btn.config(state=DISABLED)
        self.drop_btn.config(state=DISABLED)
        self.end_btn.config(state=DISABLED)


class GameClient(threading.Thread):
    def __init__(self, app):
        super().__init__()
        self.app = app

    def run(self):
        try:
            self.stash_deck = []
            self.stock_top = None
            self.discard_top = None
            self.is_ready = False
            self.is_drawing = False
            self.is_dropping = False
            self.is_winner = False
            self.deadwood = 0

            self.address = self.app.address_input_str.get()
            self.port = 65432
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.connect((self.address, int(self.port)))

            self.app.status_button.config(text="Ready", command=self.ready)
            self.app.address_input.config(state=DISABLED)

            listen_t = threading.Thread(target=self.listen)
            listen_t.start()

        except:
            messagebox.showerror(
                title="Connection Error",
                message="Cannot connect to "
                + self.address
                + ":"
                + str(self.port)
                + ".",
            )

    def listen(self):
        while True:
            reply = self.recv_msg()
            if not reply:
                break
            else:
                self.handle_command(reply)
        self.server.close()

    def recv_msg(self):
        raw_msglen = self.recvall(4)
        if not raw_msglen:
            return None
        msglen = struct.unpack(">I", raw_msglen)[0]
        reply = self.recvall(msglen).decode()
        logging.debug("FROM SERVER --> " + str(reply))
        return reply

    def recvall(self, n):
        data = bytearray()
        while len(data) < n:
            packet = self.server.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data

    def sendall(self, data):
        self.server.sendall(struct.pack(">I", len(data)) + data.encode())
        logging.debug("TO SERVER --> " + str(data))

    def handle_command(self, command):
        if "@ID " in command:
            cmd = command.split(" ")
            self.id = cmd[1]
            logging.debug("Got client ID as " + str(self.id))
        elif "@STASH" in command:
            cmd = command.split(" ")
            card = cmd[1][:2]
            self.stash_deck.append(card)
            logging.debug("Added " + str(card) + " to the stash deck")
            if len(self.stash_deck) == 10:
                for i in range(10):
                    stash_card_rbtn = self.app.stash_card_rbtn_list[i]
                    card = self.stash_deck[i]
                    card_image = self.app.card_images[card]
                    stash_card_rbtn.config(image=card_image, value=card)
        elif "@STOCK" in command:
            cmd = command.split(" ")
            card = cmd[1][:2]
            self.stock_top = card
            if self.stock_top == None:
                self.app.stock_deck_rbtn.config(image=self.app.blank_card)
            else:
                card = self.stock_top
                card_image = self.app.card_images[card]
                self.app.stock_deck_rbtn.config(image=card_image)
            logging.debug("Set " + str(card) + " as the stock top")
        elif "@DISCARD" in command:
            cmd = command.split(" ")
            card = cmd[1][:2]
            self.discard_top = card
            if self.discard_top == None:
                self.app.discard_deck_rbtn.config(image=self.app.blank_card)
            else:
                card = self.discard_top
                card_image = self.app.card_images[card]
                self.app.discard_deck_rbtn.config(image=card_image)
            logging.debug("Set " + str(card) + " as the discard top")
        elif "@DRAWING" in command:
            self.is_dropping = False
            self.is_drawing = True
            self.drawing()
        elif "@DROPPING" in command:
            self.is_dropping = True
            self.is_drawing = False
            self.dropping()
        elif "@IDLE" in command:
            self.is_drawing = False
            self.is_dropping = False
        elif "@END" in command:
            self.end()

    def ready(self):
        data = "@READY;"
        self.sendall(data)
        self.app.status_button.config(text="Connected", state=DISABLED)

    def drawing(self):
        for child in self.app.stash_div.winfo_children():
            child.configure(state=DISABLED)
        self.app.drop_btn.config(state=DISABLED)

        for child in self.app.deck_div.winfo_children():
            child.configure(state=NORMAL)
        self.app.draw_btn.config(state=NORMAL)

    def dropping(self):
        for child in self.app.deck_div.winfo_children():
            child.configure(state=DISABLED)
        self.app.draw_btn.config(state=DISABLED)

        for child in self.app.stash_div.winfo_children():
            child.configure(state=NORMAL)
        self.app.drop_btn.config(state=NORMAL)

    def idle(self):
        for child in self.app.deck_div.winfo_children():
            child.configure(state=DISABLED)
        self.app.draw_btn.config(state=DISABLED)

        for child in self.app.stash_div.winfo_children():
            child.configure(state=DISABLED)
        self.app.drop_btn.config(state=DISABLED)

    def draw(self):
        deck = self.app.deck_sel.get()
        data = "@DRAW " + deck
        self.sendall(data)
        self.is_drawing = False

    def drop(self):
        card = self.app.stash_card_idx_sel.get()
        if card is not None:
            logging.debug("Stash Before --> " + str(self.stash_deck))
            logging.debug("Dropping --> " + str(card))
            self.stash_deck.remove(card)
            logging.debug("Stash After --> " + str(self.stash_deck))
            data = "@DROP " + card
            self.sendall(data)
            if len(self.stash_deck) == 10:
                for i in range(10):
                    stash_card_rbtn = self.app.stash_card_rbtn_list[i]
                    card = self.stash_deck[i]
                    stash_card_rbtn.config(
                        image=self.app.card_images[card], value=card)
            logging.debug("Stash {}".format(self.stash_deck))
            self.stock_top = None
            self.app.stock_deck_rbtn.config(image=self.app.blank_card)
            self.is_dropping = False
            self.idle()
            self.calculate_deadwood()

    def end(self):
        if self.is_winner:
            data = "@END"
            self.sendall(data)
            messagebox.showinfo("Congratulations!", "You won!")
        else:
            messagebox.showinfo("Game Over", "You lost!")

    def calculate_deadwood(self):
        self.deadwood = 0
        cmb_3 = list(permutations(self.stash_deck, 3))
        melds = self.get_melds(cmb_3)
        if melds is not None:
            self.deadwood_deck = self.stash_deck.copy()
            for meld in melds:
                for card in meld:
                    if card in self.deadwood_deck:
                        self.deadwood_deck.remove(card)

            for card in self.deadwood_deck:
                self.deadwood += self.calculate_rank(card)
            logging.debug("DEADWOOD --> " + str(self.deadwood))

            if len(self.deadwood_deck) < 2 and self.deadwood < 14:
                self.app.end_btn.config(state=NORMAL)
                self.is_winner = True
            else:
                self.app.end_btn.config(state=DISABLED)
                self.is_winner = False

    def get_melds(self, cmbs):
        melds = []

        while len(cmbs) > 0:
            curr_cmb = cmbs.pop()
            if self.is_meld(curr_cmb):
                melds.append(curr_cmb)
                to_remove_cmbs = set()
                for card in curr_cmb:
                    for cmb in cmbs:
                        if card in cmb:
                            to_remove_cmbs.add(cmb)
                cmbs = list(set(cmbs).difference(to_remove_cmbs))

        if len(melds) == 0:
            return None
        else:
            return melds

    def is_meld(self, cmb):
        meld_rank = cmb[0][0]
        meld_suit = cmb[0][1]

        is_rank_meld = False
        for card in cmb:
            rank = card[0]
            suit = card[1]
            if rank != meld_rank:
                is_rank_meld = False
                break
            else:
                is_rank_meld = True
        if is_rank_meld:
            return is_rank_meld

        is_suit_meld = False
        for idx in range(len(cmb)):
            card = cmb[idx]
            rank = card[0]
            suit = card[1]
            if suit != meld_suit:
                is_suit_meld = False
                break
            else:
                if idx == 0:
                    continue
                else:
                    prev_card = cmb[idx - 1]
                    if self.calculate_rank(card) == self.calculate_rank(prev_card) + 1:
                        is_suit_meld = True
                    else:
                        is_suit_meld = False
                        break
        if is_suit_meld:
            return is_suit_meld

        return False

    def calculate_rank(self, card):
        rank = card[0]
        if rank == "A":
            return 1
        elif rank == "T":
            return 10
        elif rank == "K":
            return 13
        elif rank == "Q":
            return 12
        elif rank == "J":
            return 11
        else:
            return int(rank)


if __name__ == "__main__":
    app = App()
    app.mainloop()
