import random
import socket
import threading
import main


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
    def getGameByName(name):
        for game in Game.games:
            if game.name == name:
                return game
        return None

    @staticmethod
    def getGameByPlayer(player):
        for game in Game.games:
            if player in game.players:
                return game
        return None


class Server:
    header = 64
    format = 'utf-8'
    disc_message = "!DISCONNECT"

    def __init__(self, host, port):
        self.port = port
        self.host = host
        self.addr = (self.host, self.port)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.addr)

    def handle_client(self, conn, addr):
        if debug:
            print(f"[NEW CONNECTION] {addr} connected.")

        connected = True
        while connected:
            msg_length = conn.recv(self.header).decode(self.format)
            if msg_length:
                msg_length = int(msg_length)
                msg = str(conn.recv(msg_length).decode(self.format))
                if debug:
                    print(f"[{addr}] {msg}")
                if msg == self.disc_message:
                    connected = False
                elif msg == 'games':
                    s = 'games${'
                    for g in Game.games:
                        s += '"' + g.name + '":' + str(g.players) + ','
                    s += '}'
                    print(s)
                    conn.send(s.encode(self.format))
                elif msg.startswith('create$'):
                    game, player = msg.replace('create$', '', 1).split('$')
                    if Game.getGameByName(game) is None:
                        Game(game).players.append(player)
                        conn.send(f"created${game}${player}".encode(self.format))
                    else:
                        conn.send(f"not_created${game}${player}".encode(self.format))
                elif msg.startswith('join$'):
                    game, player = msg.replace('join$', '', 1).split('$')
                    g = Game.getGameByName(game)
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
                    g: Game = Game.getGameByPlayer(player)
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

                    g: Game = Game.getGameByName(game)
                    if g is not None:
                        if not g.finished and g.started and g.grid.get_value(i, j) == 0 and \
                                g.playing == Game.playerNames.get(g.players.index(player)):
                            g.grid.change_value(i, j, g.playing)
                            conn.send(f"played${g.name}${player}${i}${j}${g.grid.is_winner()}${g.grid.is_full()}".
                                      encode(self.format))

                            if g.grid.is_winner() or g.grid.is_full():
                                g.finished = True
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
                    g: Game = Game.getGameByName(game)
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
                    g: Game = Game.getGameByName(game)
                    if g is not None:
                        if not g.finished and g.started and g.playing == Game.playerNames.get(g.players.index(player)):
                            conn.send(f'can_play${game}${player}${g.grid.last[0]}${g.grid.last[1]}'.encode(self.format))
                        else:
                            conn.send(f'cant_play${game}${player}${g.grid.last[0]}${g.grid.last[1]}$'
                                      f'{g.grid.is_winner()}${g.grid.is_full()}'.encode(self.format))
                    else:
                        conn.send(f'not_exist{game}${player}'.encode(self.format))
                else:
                    conn.send(f"unknown${msg}".encode(self.format))
        conn.close()

    def start(self):
        self.server.listen()
        if debug:
            print(f"[LISTENING] Server is listening on {self.host}")
        while True:
            conn, addr = self.server.accept()
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()
            if debug:
                print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

debug = False
server = Server('0.0.0.0', 5050)
print("[STARTING] server is starting...")
server.start()
