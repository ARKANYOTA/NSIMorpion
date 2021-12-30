import socket


class Client:
    header = 64
    format = 'utf-8'
    disc_message = "!DISCONNECT"

    def __init__(self, host, port):
        self.port = port
        self.host = host
        self.addr = (self.host, self.port)

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.addr)

    def send(self, msg):
        message = msg.encode(self.format)
        msg_length = len(message)
        send_length = str(msg_length).encode(self.format)
        send_length += b' ' * (self.header - len(send_length))
        self.client.send(send_length)
        self.client.send(message)
        self.recv(self.client.recv(2048).decode(self.format))

    def recv(self, msg):
        print(msg)
        if msg.startswith('games$'):
            self.games(msg.replace('games$', '', 1))
        elif msg.startswith('joined$'):
            game, player = msg.replace('joined$', '', 1).split('$')
            self.joined(game, player)
        elif msg.startswith('not_joined$'):
            game, player = msg.replace('not_joined$', '', 1).split('$')
            self.not_joined(game, player)
        elif msg.startswith('created$'):
            game, player = msg.replace('created$', '', 1).split('$')
            self.created(game, player)
        elif msg.startswith('not_created$'):
            game, player = msg.replace('not_created$', '', 1).split('$')
            self.not_created(game, player)
        elif msg.startswith('played$'):
            game, player, i, j, winner, full = msg.replace('played$', '', 1).split('$')
            i, j, winner, full = int(i), int(j), bool(winner), bool(full)
            self.played(game, player, i, j)
        elif msg.startswith('not_played$'):
            game, player, i, j, winner, full = msg.replace('not_played$', '', 1).split('$')
            i, j, winner, full = int(i), int(j), bool(winner), bool(full)
            self.not_played(game, player, i, j)
        elif msg.startswith('again$'):
            game, player = msg.replace('again$', '', 1).split('$')
            self.again(game, player)
        elif msg.startswith('restart$'):
            game, player = msg.replace('restart$', '', 1).split('$')
            self.restart(game, player)
        elif msg.startswith('can_play$'):
            game, player, winner, full = msg.replace('can_play$', '', 1).split('$')
            self.can_play(game, player, winner, full)
        elif msg.startswith('cant_play$'):
            game, player, winner, full = msg.replace('cant_play$', '', 1).split('$')
            self.cant_play(game, player, winner, full)
        elif msg.startswith('not_exist$'):
            game, player = msg.replace('not_exist$', '', 1).split('$')
            self.not_exist(game, player)
        elif msg.startswith('unknown$'):
            msg = msg.replace('unknown$', '', 1).split('$')
            self.unknown(msg)

    def close(self):
        self.send(self.disc_message)
        self.client.close()

    def games(self, msg):
        MultiGame.games.clear()
        games = eval(msg)
        for game in games.items():
            MultiGame(game[0], self).players = game[1]

    def joined(self, game, player):
        pass

    def not_joined(self, game, player):
        pass

    def created(self, game, player):
        pass

    def not_created(self, game, player):
        pass

    def played(self, game, player, i, j, winner, full):
        pass

    def not_played(self, game, player, i, j, winner, full):
        pass

    def again(self, game, player):
        pass

    def restart(self, game, player):
        pass

    def can_play(self, game, player, winner, full):
        pass

    def cant_play(self, game, player, winner, full):
        pass

    def not_exist(self, game, player):
        pass

    def unknown(self, msg):
        pass


class MultiGame:
    games = []
    playerNames = {0: -1, 1: 1}

    def __init__(self, name, client):
        self.players = []
        self.name = name
        self.client = client
        self.games.append(self)

    def __str__(self):
        return f'name: {self.name}, players: {str(self.players)}'

    def leave(self, player):
        self.players.remove(player)
        self.client.send(f'leave${self.name}${player}')

    def play(self, player, i, j):
        self.client.send(f'play${self.name}${player}${str(i)}${str(j)}')

    def again(self, player):
        self.client.send(f'again${self.name}${player}')

    def can_play(self, player):
        self.client.send(f'can_play${self.name}${player}')

    @staticmethod
    def getGamesList(client):
        client.send("games")

    @staticmethod
    def getGameByName(name):
        for game in MultiGame.games:
            if game.name == name:
                return game
        return None

    @staticmethod
    def getGameByPlayer(player):
        for game in MultiGame.games:
            if player in game.players:
                return game
        return None

    @staticmethod
    def join(player, game, client):
        g = MultiGame.getGameByName(game)
        if g is not None and len(g.players) < 2:
            client.send(f"join${game}${player}")

    @staticmethod
    def create(player, game, client):
        g = MultiGame.getGameByName(game)
        if g is None:
            client.send(f"create${game}${player}")


running = True
local = '192.168.56.1'
public = '91.165.38.233'
host, port = local, 5050
client = Client(host, port)
player = input('Entrez votre pseudo:  ')
while running:
    cmd = input('Commande:  ').lower()
    if cmd == 'quit':
        running = False
    elif cmd == 'games':
        MultiGame.getGamesList(client)
        for game in MultiGame.games:
            print(str(game))
    elif cmd == 'create':
        game = input('Entrez le nom de votre partie:  ')
        MultiGame.create(player, game, client)
    elif cmd == 'join':
        game: str = input('Entrez le nom de la partie:  ')
        MultiGame.join(player, game, client)
    elif cmd == 'leave':
        game = MultiGame.getGameByPlayer(player)
        if game is not None:
            game.leave(player)
    elif cmd == 'play':
        game: MultiGame = MultiGame.getGameByPlayer(player)
        if game is not None:
            game.play(player, int(input('Entrez le nombre i:  ')), int(input('Entrez le nombre j:  ')))
    elif cmd == 'can_play':
        game: MultiGame = MultiGame.getGameByPlayer(player)
        if game is not None:
            game.can_play(player)
client.close()

