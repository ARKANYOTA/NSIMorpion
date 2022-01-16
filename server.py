import random
import socket
import threading
import main
import sqlite3
from config import *


class SQL:
    def __init__(self):
        self.cur = None
        self.data = None

    def update_game(self, _, is_winner, winner, loser):
        self.data = sqlite3.connect('data.db')
        self.cur = self.data.cursor()
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS Result(pseudo TEXT PRIMARY KEY , score INTEGER, nombre_de_partie INTEGER)")

        for score, pseudo in [(is_winner, winner), (is_winner * -1, loser)]:
            nb_partie = 1
            self.cur.execute("SELECT pseudo FROM Result WHERE pseudo = ?", (pseudo,))
            if self.cur.fetchone() is None:
                self.cur.execute("INSERT INTO Result VALUES(?,?,?)", (pseudo, score, nb_partie))
            else:
                self.cur.execute("SELECT score FROM Result WHERE pseudo = ?", (pseudo,))
                db_score = self.cur.fetchone()[0]
                self.cur.execute("SELECT nombre_de_partie FROM Result WHERE pseudo = ?", (pseudo,))
                db_nb_partie = self.cur.fetchone()[0]
                self.cur.execute("UPDATE Result SET score = ?, nombre_de_partie = ? WHERE pseudo = ?",
                                 (db_score + score, db_nb_partie + nb_partie, pseudo))
        self.data.commit()
        self.cur.close()
        self.data.close()

    def get_data(self):
        self.data = sqlite3.connect('data.db')
        self.cur = self.data.cursor()
        self.cur.execute("SELECT * FROM Result ORDER BY score DESC LIMIT 5")
        bests_player = self.cur.fetchall()
        self.cur.execute("SELECT * FROM Result ORDER BY nombre_de_partie DESC LIMIT 5")
        bests_try_hard = self.cur.fetchall()
        self.cur.close()
        self.data.close()
        return bests_player + bests_try_hard


class Game:
    games = []
    playerNames = {0: -1, 1: 1}

    def __init__(self, name):
        self.name = name
        self.players = []
        self.again = []

        self.grid = main.Grid()
        self.playing = (-1) ** random.randint(0, 1)
        self.finished = False
        self.started = False

        Game.games.append(self)

    @staticmethod
    def get_game_by_name(name):
        for game in Game.games:
            if game.name == name:
                return game
        return None

    @staticmethod
    def get_game_by_player(player):
        for game in Game.games:
            if player in game.players:
                return game
        return None


class Server:
    header = 64
    format = 'utf-8'
    disc_message = "!DISCONNECT"
    sql = SQL()

    def __init__(self, host):
        self.port = port
        self.host = host
        self.adresse = (self.host, self.port)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.adresse)

    def handle_client(self, conn, adresse):
        if debug:
            print(f"[NEW CONNECTION] {adresse} connected.")

        connected = True
        while connected:
            msg_length = conn.recv(self.header).decode(self.format)
            if msg_length:
                msg_length = int(msg_length)
                msg = str(conn.recv(msg_length).decode(self.format))
                if debug:
                    print(f"[{adresse}] {msg}")
                if msg == self.disc_message:
                    connected = False
                elif msg == 'games':
                    s = 'games${'
                    for g in Game.games:
                        s += '"' + g.name + '":' + str(g.players) + ','
                    s += '}'
                    if debug:
                        print(s)
                    conn.send(s.encode(self.format))
                elif msg.startswith('create$'):
                    game, player = msg.replace('create$', '', 1).split('$')
                    if Game.get_game_by_name(game) is None:
                        Game(game).players.append(player)
                        conn.send(f"created${game}${player}".encode(self.format))
                    else:
                        conn.send(f"not_created${game}${player}".encode(self.format))
                elif msg.startswith('join$'):
                    game, player = msg.replace('join$', '', 1).split('$')
                    g = Game.get_game_by_name(game)
                    if g is not None:
                        if len(g.players) < 2 and player not in g.players:
                            g.players.append(player)
                            conn.send(f"joined${game}${player}".encode(self.format))

                            if len(g.players) >= 2:
                                g.started = True
                        else:
                            conn.send(f"not_joined${g}${player}".encode(self.format))
                    else:
                        conn.send(f'not_exist${game}${player}'.encode(self.format))
                elif msg.startswith('leave$'):
                    game, player = msg.replace('leave$', '', 1).split('$')
                    g: Game = Game.get_game_by_player(player)
                    if g is not None:
                        g.players.remove(player)
                        conn.send(f'left${game}${player}'.encode(self.format))
                        if g.started:
                            g.finished = False
                            g.started = False
                            g.again.clear()
                            g.grid.clear()
                            g.grid.last = [-1, -1]
                        else:
                            Game.games.remove(g)
                    else:
                        conn.send(f'not_exist${game}${player}'.encode(self.format))
                elif msg.startswith('play$'):
                    msg = msg.replace('play$', '', 1)
                    game, player, i, j = msg.split('$')
                    i, j = int(i), int(j)

                    g: Game = Game.get_game_by_name(game)
                    if g is not None:
                        if not g.finished and g.started and g.grid.get_value(i, j) == 0 and \
                                g.playing == Game.playerNames.get(g.players.index(player)):
                            g.grid.change_value(i, j, g.playing)
                            if g.grid.is_winner() == 1:
                                winner_player = g.players[main.MultiGame.playerNamesInv[g.grid.who_won()]]
                            else:
                                winner_player = 'None'
                            conn.send(
                                f"played${g.name}${player}${i}${j}${g.grid.is_winner()}${g.grid.is_full()}${winner_player}".
                                encode(self.format))

                            if g.grid.is_winner() or g.grid.is_full():
                                g.finished = True
                                if g.grid.who_won() != 0:
                                    winner = g.players[main.MultiGame.playerNamesInv[g.grid.who_won()]]
                                    loser = g.players[main.MultiGame.playerNamesInv[g.grid.who_won() * -1]]
                                    self.sql.update_game(g, 1, winner, loser)
                                else:
                                    joueur1, joueur2 = g.players
                                    self.sql.update_game(g, 0, joueur1, joueur2)
                            else:
                                g.playing *= -1
                        else:
                            conn.send(
                                f'not_played${g.name}${player}${i}${j}${g.grid.is_winner()}${g.grid.is_full()}'.encode(
                                    self.format))
                    else:
                        conn.send(f'not_exist${game}${player}'.encode(self.format))

                elif msg.startswith('again$'):
                    msg = msg.replace('again$', '', 1)
                    game, player = msg.split('$')
                    g: Game = Game.get_game_by_name(game)
                    if g is not None:
                        if player not in g.again:
                            g.again.append(player)

                        if len(g.again) == 2:
                            conn.send(f"restart${g.name}${player}".encode(self.format))
                            g.finished = False
                            g.started = True
                            g.again.clear()
                            g.grid.clear()
                        else:
                            conn.send(f"again${g.name}${player}".encode(self.format))
                    else:
                        conn.send(f'not_exist${game}${player}'.encode(self.format))
                elif msg.startswith('can_play$'):
                    game, player = msg.replace('can_play$', '', 1).split('$')
                    g: Game = Game.get_game_by_name(game)
                    if g.grid.is_winner() == 1:
                        winner_player = g.players[main.MultiGame.playerNamesInv[g.grid.who_won()]]
                    else:
                        winner_player = 'None'
                    if g is not None:
                        if not g.finished and g.started and g.playing == Game.playerNames.get(g.players.index(player)):
                            conn.send(f'can_play${game}${player}${g.grid.last[0]}${g.grid.last[1]}'.encode(self.format))
                        else:
                            conn.send(f'cant_play${game}${player}${g.grid.last[0]}${g.grid.last[1]}$'
                                      f'{g.grid.is_winner()}${g.grid.is_full()}${winner_player}'.encode(self.format))
                    else:
                        conn.send(f'not_exist{game}${player}'.encode(self.format))
                elif msg == 'getdata':
                    if debug:
                        print('getdata' + str(self.sql.get_data()))
                    conn.send(f"getdata${self.sql.get_data()}".encode(self.format))

                else:
                    conn.send(f"unknown${msg}".encode(self.format))
        conn.close()

    def start(self):
        self.server.listen()
        if debug:
            print(f"[LISTENING] Server is listening on {self.host}")
        while True:
            conn, adresse = self.server.accept()
            thread = threading.Thread(target=self.handle_client, args=(conn, adresse))
            thread.start()
            if debug:
                print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


debug = False
server = Server('0.0.0.0')
print("[STARTING] server is starting...")
server.start()
