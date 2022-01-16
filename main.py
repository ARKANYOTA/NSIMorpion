#!/usr/bin/env python
import os
import math
import random
import socket
import string
import sys
from config import *

# Permet de cacher le message pygame
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from pygame.locals import *
from GIFImage import GIFImage


class Sprite(Rect):
    pygame.font.init()
    FONT_30 = pygame.font.Font('./font/Roboto-Regular.ttf', 30)
    FONT_20 = pygame.font.Font('./font/Roboto-Regular.ttf', 20)
    current_theme_ext = 0

    def __init__(self, pos, size, image, name="null", collide=False):
        super().__init__(pos[0], pos[1], size[0], size[1])
        self.clicked = False
        self.image = image
        self.pos = pos
        self.name = name
        self.collide = collide

    def move(self, x: float, y: float):
        self.pos[0] = x
        self.pos[1] = y

    def isClicked(self):
        mouse = pygame.mouse
        m = mouse.get_pos()
        return self.collidepoint(m[0], m[1]) and (
                mouse.get_pressed()[0] or mouse.get_pressed()[1] or mouse.get_pressed()[2]) and mouse.get_focused()

    def isOver(self):
        mouse = pygame.mouse
        m = mouse.get_pos()
        return self.collidepoint(m[0], m[1]) and mouse.get_focused()

    @staticmethod
    def image(name, rotate=None, size=None) -> pygame.Surface:
        img = pygame.image.load("./images/" + name + ".png")
        if size is not None:
            img = pygame.transform.scale(img, size)
        if rotate is not None:
            img = pygame.transform.rotate(img, rotate)
        return img


class Button(Sprite):
    def __init__(self, pos: tuple, size: tuple, text: str = '', font: str = './font/Roboto-Regular.ttf',
                 name: str = "null",
                 collide: bool = False):
        super(Button, self).__init__(pos, size, GIFImage("./images/button.gif"), name, collide)
        self.image.get_frames()
        self.text = text
        self.font = font

    def afficher(self, screen):
        img = pygame.transform.scale(self.image.frames[self.image.cur][0], self.size)
        text_surface = pygame.font.Font(self.font, 50).render(self.text, False, (100, 100, 100))

        x_percent = img.get_size()[0] * 0.9 / text_surface.get_size()[0]
        text_surface = pygame.transform.scale(text_surface, (
            int(text_surface.get_size()[0] * x_percent), int(text_surface.get_size()[1] * x_percent)))

        if text_surface.get_size()[1] > img.get_size()[1]:
            y_percent = (img.get_size()[1] * 0.9) / text_surface.get_size()[1]
            text_surface = pygame.transform.scale(text_surface, (
                int(text_surface.get_size()[0] * y_percent), int(text_surface.get_size()[1] * y_percent)))

        screen.blit(
            pygame.transform.scale(self.image.frames[self.image.cur][0], (int(self.size[0]), int(self.size[1]))),
            (int(self.pos[0]), int(self.pos[1])))
        screen.blit(text_surface, (int(self.pos[0]) + int(self.size[0] - text_surface.get_size()[0]) // 2,
                                   int(self.pos[1]) + int(self.size[1] - text_surface.get_size()[1]) // 2))


class InputBox:
    inputs = []

    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = (0, 0, 0)
        self.color_active = (255, 0, 0)
        self.text = text
        self.font = Sprite.FONT_30
        self.txt_surface = self.font.render(text, True, self.color)
        self.txt_surface_active = self.font.render(text, True, self.color_active)
        self.active = False
        InputBox.inputs.append(self)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif len(self.text) < 12 and event.unicode != '$':
                    self.text += event.unicode
                self.txt_surface = self.font.render(self.text, True, self.color)
                self.txt_surface_active = self.font.render(self.text, True, self.color_active)

    def update(self):
        width = max(self.rect.w, self.txt_surface.get_width() + 30)
        self.rect.w = width

    def draw(self, screen):
        if self.active:
            screen.blit(self.txt_surface_active, (self.rect.x + 5, self.rect.y + 5))
        else:
            screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)


class Client:
    header = 64
    format = 'utf-8'
    disc_message = "!DISCONNECT"

    def __init__(self, host, port):
        self.port = port
        self.host = host
        self.adresse = (self.host, self.port)

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.adresse)

    def send(self, msg):
        message = msg.encode(self.format)
        msg_length = len(message)
        send_length = str(msg_length).encode(self.format)
        send_length += b' ' * (self.header - len(send_length))
        self.client.send(send_length)
        self.client.send(message)
        self.recv(self.client.recv(2048).decode(self.format))

    def recv(self, msg):
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
            game, player, i, j, winner, full, winner_player = msg.replace('played$', '', 1).split('$')
            i, j, winner, full = int(i), int(j), self.toBool(winner), self.toBool(full)
            winner_player = winner_player if winner_player != 'None' else None
            self.played(game, player, i, j, winner, full, winner_player=winner_player)
        elif msg.startswith('not_played$'):
            game, player, i, j, winner, full = msg.replace('not_played$', '', 1).split('$')
            i, j, winner, full = int(i), int(j), self.toBool(winner), self.toBool(full)
            self.not_played(game, player, i, j, winner, full)
        elif msg.startswith('again$'):
            game, player = msg.replace('again$', '', 1).split('$')
            self.again(game, player)
        elif msg.startswith('restart$'):
            game, player = msg.replace('restart$', '', 1).split('$')
            self.restart(game, player)
        elif msg.startswith('can_play$'):
            game, player, i, j = msg.replace('can_play$', '', 1).split('$')
            i, j = int(i), int(j)
            self.can_play(game, player, i, j)
        elif msg.startswith('cant_play$'):
            game, player, i, j, winner, full, winner_player = msg.replace('cant_play$', '', 1).split('$')
            i, j, winner, full = int(i), int(j), self.toBool(winner), self.toBool(full)
            winner_player = winner_player if winner_player != 'None' else None
            self.cant_play(game, player, i, j, winner, full, winner_player=winner_player)
        elif msg.startswith('not_exist$'):
            game, player = msg.replace('not_exist$', '', 1).split('$')
            self.not_exist(game, player)
        elif msg.startswith('unknown$'):
            msg = msg.replace('unknown$', '', 1).split('$')
            self.unknown(msg)
        elif msg.startswith('getdata$'):
            msg = msg.replace('getdata$', '', 1)
            Game.store_data(msg)

    @staticmethod
    def toBool(txt: str) -> bool:
        if txt.lower() == 'true':
            return True
        else:
            return False

    def close(self):
        self.send(self.disc_message)
        self.client.close()

    def games(self, msg):
        MultiGame.games.clear()
        games = eval(msg)
        for game in games.items():
            MultiGame(game[0], self).players = game[1]

    def joined(self, game, player):
        g: Game = Game.game
        g.whichMenu = 4
        g.game_name = game

    def not_joined(self, game, player):
        pass

    def created(self, game, player):
        g: Game = Game.game
        g.multi = MultiGame(game, self)
        g.whichMenu = 4
        self.creation = False

    def not_created(self, game, player):
        pass

    def played(self, game, player, i, j, winner, full, winner_player=None):
        game: Game = Game.game
        multi: MultiGame = MultiGame.getGameByName(game.game_name)

        if winner and winner_player == player:
            game.winner = 1

        game.won = winner
        game.full = full
        game.playing *= -1
        if multi is not None and game.pseudo in multi.players and multi.players.index(game.pseudo) == 1:
            img = 'circle' + list_theme[Sprite.current_theme_ext]
        else:
            img = 'cross' + list_theme[Sprite.current_theme_ext]
        if game.getSpriteByName(f'sp-{i}-{j}') is None:
            for sprite in game.sprites:
                if sprite.name == f'case-{i}-{j}':
                    game.sprites.append(
                        Sprite((sprite.pos[0] + int(sprite.size[0] * 0.1), sprite.pos[1] + int(sprite.size[1] * 0.1)),
                               (int(sprite.size[0] * 0.8), int(sprite.size[1] * 0.8)), Sprite.image(img),
                               name=f'sp-{i}-{j}'))
                    break

    def not_played(self, game, player, i, j, winner, full):
        pass

    def again(self, game, player):
        pass

    def restart(self, game, player):
        pass

    def can_play(self, game, player, i, j):
        game: Game = Game.game
        multi: MultiGame = MultiGame.getGameByName(game.game_name)

        if game.won or game.full:
            game.restart()

        game.won = False
        game.full = False
        game.playing = 1

        if multi is not None and game.pseudo in multi.players and multi.players.index(game.pseudo) == 0:
            img = 'circle' + list_theme[Sprite.current_theme_ext]
        else:
            img = 'cross' + list_theme[Sprite.current_theme_ext]
        if game.getSpriteByName(f'sp-{i}-{j}') is None:
            for sprite in game.sprites:
                if sprite.name == f'case-{i}-{j}':
                    game.sprites.append(
                        Sprite((sprite.pos[0] + int(sprite.size[0] * 0.1), sprite.pos[1] + int(sprite.size[1] * 0.1)),
                               (int(sprite.size[0] * 0.8), int(sprite.size[1] * 0.8)), Sprite.image(img),
                               name=f'sp-{i}-{j}'))
                    break

    def cant_play(self, game, player, i, j, winner, full, winner_player=None):
        game: Game = Game.game
        multi: MultiGame = MultiGame.getGameByName(game.game_name)

        if not (winner or full) and (game.won or game.full):
            game.restart()

        if winner and winner_player != player:
            game.winner = -1
        game.won = winner
        game.full = full
        game.playing = -1

        if multi is not None and game.pseudo in multi.players and multi.players.index(game.pseudo) == 0:
            img = 'circle' + list_theme[Sprite.current_theme_ext]
        else:
            img = 'cross' + list_theme[Sprite.current_theme_ext]

        if game.getSpriteByName(f'sp-{i}-{j}') is None:
            for sprite in game.sprites:
                if sprite.name == f'case-{i}-{j}':
                    game.sprites.append(
                        Sprite((sprite.pos[0] + int(sprite.size[0] * 0.1), sprite.pos[1] + int(sprite.size[1] * 0.1)),
                               (int(sprite.size[0] * 0.8), int(sprite.size[1] * 0.8)), Sprite.image(img),
                               name=f'sp-{i}-{j}'))
                    break

    def not_exist(self, game, player):
        pass

    def unknown(self, msg):
        pass


class MultiGame:
    games = []
    playerNames = {0: -1, 1: 1}
    playerNamesInv = {-1: 0, 1: 1}

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

    @staticmethod
    def get_data_list(client):
        client.send("getdata")


class Grid:
    def __init__(self):
        self.board = [[0 for _ in range(3)] for _ in range(3)]
        self.last = [-1, -1]

    def is_empty(self, i, j):
        return self.board[i][j] == 0

    def grid_is_empty(self):
        for i in range(3):
            for j in range(3):
                if self.board[i][j] != 0:
                    return False
        return True

    def get_value(self, i, j):
        return self.board[i][j]

    def change_value(self, i, j, value):
        self.last = [i, j]
        return self.board[i].__setitem__(j, value)

    def clear(self):
        self.board = [[0 for _ in range(3)] for _ in range(3)]

    def is_full(self):
        return self.board[0][0] != 0 and self.board[0][1] != 0 and self.board[0][2] != 0 and \
               self.board[1][0] != 0 and self.board[1][1] != 0 and self.board[1][2] != 0 and \
               self.board[2][0] != 0 and self.board[2][1] != 0 and self.board[2][2] != 0

    def is_winner(self):
        # Horizontal
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != 0:
                return True

        # Vertical
        for j in range(3):
            if self.board[0][j] == self.board[1][j] == self.board[2][j] != 0:
                return True

        # Diagonal
        return (self.board[0][0] == self.board[1][1] == self.board[2][2] or self.board[0][2] == self.board[1][1] ==
                self.board[2][0]) and self.board[1][1] != 0

    def who_won(self):
        # -1 = player 1, 0 = no one or not wining, 1 = player 2
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != 0:
                return self.board[i][0]

                # Vertical
        for j in range(3):
            if self.board[0][j] == self.board[1][j] == self.board[2][j] != 0:
                return self.board[0][j]

        # Diagonal
        if (self.board[0][0] == self.board[1][1] == self.board[2][2] or self.board[0][2] == self.board[1][1] ==
            self.board[2][0]) and self.board[1][1] != 0:
            return self.board[1][1]
        return 0

    def list_positions_empty(self):
        l = []
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == 0:
                    l.append((i, j))
        return l

    def copy(self):
        g = Grid()
        for i in range(3):
            for j in range(3):
                g.board[i][j] = self.board[i][j]
        return g


class Game:
    game = None
    stored_data = {}

    def __init__(self):
        Game.game = self
        pygame.init()
        pygame.font.init()

        self.client = None
        self.grid = Grid()
        self.playing = 1
        self.difficulty = 0
        self.finished = False
        self.clicked = True
        self.ai = False
        self.won = False

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((600, 600))
        pygame.display.set_caption("Le jeu des croix et des ronds")

        self.running = True
        self.sprites = []
        self.whichMenu = 0  # 0 = menu principal, 1 = Menu de selection, 2 = Menu de jeu
        self.oldMenu = -1
        self.ticks = 0

        self.game_name = ("Game" + make_pseudo_word(3))[:11]
        self.pseudo = make_pseudo_word(3)[:11]
        self.creation = False
        self.view_data = False
        self.started = False
        self.full = False
        self.winner = 0

        while self.running:
            self.ticks += 1
            self.screen.fill((255, 255, 255))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.client is not None:
                        multi: MultiGame = MultiGame.getGameByName(self.game_name)
                        if multi is not None:
                            multi.leave(self.pseudo)
                        self.client.close()
                    self.running = False
                for input in InputBox.inputs:
                    input.handle_event(event)

            if self.whichMenu != self.oldMenu:  # Menu de Jeu
                self.changeMenu()
                self.oldMenu = self.whichMenu

            if self.whichMenu == 0:
                self.mainMenu()
            elif self.whichMenu == 1:
                self.aiMenu()
            elif self.whichMenu == 2:
                self.versusMenu()
            elif self.whichMenu == 3:
                self.multiMenu()
            elif self.whichMenu == 4:
                self.multiGameMenu()

            for input in InputBox.inputs:
                input.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(30)
        pygame.quit()

    def changeMenu(self):
        self.sprites.clear()
        InputBox.inputs.clear()
        self.creation = False

        if self.whichMenu == 0:
            InputBox(150, 500, 200, 50, self.pseudo)
            # Afficher les boutons du menu principal
            self.sprites.append(Button((100, 200), (150, 75), "Jouer", name="boutton-jouer"))
            self.sprites.append(Button((300, 200), (150, 75), "1v1", name="boutton-1v1"))
            self.sprites.append(Button((100, 300), (150, 75), "Multi", name="boutton-multi"))
            self.sprites.append(Button((300, 300), (150, 75), "Quitter", name="boutton-quitter"))
            self.sprites.append(Sprite((100, 0), (400, 200), Sprite.image("Title"), "title"))
            self.sprites.append(Sprite((100, 400), (80, 80), Sprite.image("fleche"), "fleche-gauche"))
            self.sprites.append(Sprite((400, 400), (80, 80), Sprite.image("fleche", rotate=180), "fleche-droite"))
            self.sprites.append(Sprite((200, 400), (80, 80), Sprite.image('circle' + list_theme[Sprite.current_theme_ext]), "circle"))
            self.sprites.append(Sprite((300, 400), (80, 80), Sprite.image('cross' + list_theme[Sprite.current_theme_ext]), "cross"))
        elif self.whichMenu == 1:
            # Jouer contre IA
            self.sprites.append(Button((80, 150), (200, 100), 'Facile', name='button-easy'))
            self.sprites.append(Button((320, 150), (200, 100), 'Normale', name='button-normal'))
            self.sprites.append(Button((200, 270), (200, 100), 'Difficile', name='button-hard'))
            self.sprites.append(Sprite((int(self.screen.get_size()[0] * 0.9), 5), (50, 50),
                                       Sprite.image('home'), 'button-return'))
        elif self.whichMenu == 2:
            # Menu de jeu
            for i in range(3):
                for j in range(3):
                    size_of_case = 100
                    taille_a_gauche = (pygame.display.get_surface().get_size()[0] - 3 * size_of_case) // 2
                    self.sprites.append(
                        Sprite((taille_a_gauche + i * size_of_case, 200 + j * size_of_case),
                               (size_of_case, size_of_case), Sprite.image("case"),
                               "case-" + str(i) + "-" + str(j))
                    )
            self.sprites.append(Sprite((int(self.screen.get_size()[0] * 0.9), 5), (50, 50),
                                       Sprite.image('home'), 'button-return'))
        elif self.whichMenu == 3:
            try:
                self.client = Client(local if is_local else public, port)
                self.sprites.append(
                    Button(((self.screen.get_size()[0] - 400) / 2, int(self.screen.get_size()[1] * 0.9) - 130),
                           (400, 100), 'Créez une partie', name='button-create'))
                self.sprites.append(
                    Button(((self.screen.get_size()[0] - 220) / 2, int(self.screen.get_size()[1] * 0.9 - 10)),
                           (400 * 0.5, 100 * 0.5), 'Données', name='button-data'))
                self.sprites.append(Sprite((int(self.screen.get_size()[0] * 0.9), 5), (50, 50),
                                           Sprite.image('home'), 'button-return'))
                self.updateGames()
            except OSError:
                self.whichMenu = 0
                self.changeMenu()
                print("Nous n'arrivons pas à nous connecter au serveur")
        elif self.whichMenu == 4:
            # Menu de jeu multi
            for i in range(3):
                for j in range(3):
                    size_of_case = 100
                    taille_a_gauche = (pygame.display.get_surface().get_size()[0] - 3 * size_of_case) // 2
                    self.sprites.append(
                        Sprite((taille_a_gauche + i * size_of_case, 200 + j * size_of_case),
                               (size_of_case, size_of_case), Sprite.image("case"),
                               "case-" + str(i) + "-" + str(j))
                    )
            self.sprites.append(Sprite((int(self.screen.get_size()[0] * 0.9), 5), (50, 50),
                                       Sprite.image('home'), 'button-return'))

    def restart(self):
        self.grid.clear()
        self.finished = False
        self.won = False
        self.full = False
        self.playing = (-1) ** random.randint(0, 1)

        to_clear = []
        for sprite in self.sprites:
            if sprite.name == 'button-restart' or sprite.name == 'temp':
                to_clear.append(sprite)

        for sprite in to_clear:
            self.sprites.remove(sprite)

    def mainMenu(self):
        text_surface = Sprite.FONT_30
        txt = text_surface.render("Pseudo", False, (0, 0, 0))
        self.screen.blit(txt, (20, 500))
        if len(InputBox.inputs) >= 1:
            self.pseudo = InputBox.inputs[0].text

        for sprite in self.sprites:
            sprite.clicked = sprite.isClicked() or sprite.clicked
            if not sprite.isClicked() and sprite.clicked:
                sprite.clicked = False
                if sprite.name == "boutton-quitter":
                    self.running = False
                if sprite.name == "boutton-jouer":
                    self.whichMenu = 1
                if sprite.name == "boutton-1v1":
                    self.playing = (-1) ** random.randint(0, 1)
                    self.whichMenu = 2
                if sprite.name == "boutton-multi":
                    self.whichMenu = 3
                if sprite.name[:6] == "fleche":
                    if sprite.name == "fleche-gauche":
                        Sprite.current_theme_ext = (Sprite.current_theme_ext - 1) % len(list_theme)
                    if sprite.name == "fleche-droite":
                        Sprite.current_theme_ext = (Sprite.current_theme_ext + 1) % len(list_theme)
                    self.sprites.remove(self.getSpriteByName('circle'))
                    self.sprites.remove(self.getSpriteByName('cross'))
                    self.sprites.append(
                        Sprite((300, 400), (80, 80),
                               Sprite.image('cross' + list_theme[Sprite.current_theme_ext]), "circle")
                    )
                    self.sprites.append(
                        Sprite((200, 400), (80, 80),
                               Sprite.image('circle' + list_theme[Sprite.current_theme_ext]), "cross")
                    )

            # Il faudrait move ce truc autre part, car il se répète sur tout les Game Main
            if isinstance(sprite.image, GIFImage):
                if sprite.isOver():
                    sprite.image.next_frame()
                elif sprite.image.cur >= 1:
                    sprite.image.prev_frame()

                if isinstance(sprite, Button):
                    sprite.afficher(self.screen)
            else:
                self.screen.blit(pygame.transform.scale(sprite.image, sprite.size), sprite.pos)

    def versusMenu(self):
        for sprite in self.sprites:
            if sprite.name == 'button-restart':
                if sprite.isOver():
                    sprite.image.next_frame()
                elif sprite.image.cur >= 1:
                    sprite.image.prev_frame()

            if self.ai and self.playing == -1 and not (self.grid.is_winner() or self.grid.is_full()):
                if self.difficulty == 0:
                    self.play_easy()
                elif self.difficulty == 1:
                    self.play_normal()
                elif self.difficulty == 2:
                    self.play_hard()

                if self.grid.is_winner() or self.grid.is_full():
                    self.sprites.append(Button((230, 120), (150, 75), 'Rejouer', name='button-restart'))
                    self.won = self.grid.is_winner()
                    self.finished = True

            if sprite.isClicked() and (not self.ai or self.playing == 1):
                sprite.clicked = False
                if sprite.name == 'button-restart':
                    self.restart()
                elif sprite.name == 'button-return':
                    self.finished = False
                    self.won = False
                    self.ai = False
                    self.whichMenu = 0
                    self.grid.clear()
                elif 'case-' in sprite.name and not self.finished:
                    t = sprite.name.replace('case-', '').split('-')
                    i, j = int(t[0]), int(t[1])
                    if self.grid.is_empty(i, j):
                        if self.playing == 1:
                            img = 'circle' + list_theme[Sprite.current_theme_ext]
                        else:
                            img = 'cross' + list_theme[Sprite.current_theme_ext]
                        self.sprites.append(
                            Sprite(
                                (sprite.pos[0] + int(sprite.size[0] * 0.1), sprite.pos[1] + int(sprite.size[1] * 0.1)),
                                (int(sprite.size[0] * 0.8), int(sprite.size[1] * 0.8)), Sprite.image(img), name='temp'))

                        self.grid.change_value(i, j, self.playing)
                        if self.grid.is_winner() or self.grid.is_full():
                            self.sprites.append(Button((230, 120), (150, 75), 'Rejouer', name='button-restart'))
                            self.won = self.grid.is_winner()
                            self.finished = True
                        else:
                            self.playing *= -1

            if isinstance(sprite.image, pygame.Surface):
                self.screen.blit(pygame.transform.scale(sprite.image, sprite.size), sprite.pos)
            else:
                sprite.afficher(self.screen)

        if self.playing == 1:
            player = 1
            img = Sprite.image('circle' + list_theme[Sprite.current_theme_ext], size=(30, 30))
        else:
            player = 2
            img = Sprite.image('cross' + list_theme[Sprite.current_theme_ext], size=(30, 30))

        if self.won:
            who_won = self.grid.who_won()  # -1 0 ou 1

            # txt = 'Joueur ' + str(who_won) + ' a gagné !'
            txt = 'Le joueur ' + ["Égalité", "rond", "croix"][who_won] + ' a gagné !'
            text_surface = Sprite.FONT_20
            for i in range(len(txt)):
                self.screen.blit(text_surface.render(txt[i], False, (0, 0, 0)),
                                 (130 + (15 * i), int(50 + (5 * math.sin((self.ticks // 2) + (i * 5))))))
        elif self.finished:
            text_surface = Sprite.FONT_30
            self.screen.blit(text_surface.render("Il n'y a eu aucun gagnants !", False, (0, 0, 0)), (120, 60))
        else:
            text_surface = Sprite.FONT_20
            self.screen.blit(text_surface.render("C'est au tour du joueur " + str(player), False, (0, 0, 0)), (50, 20))
            self.screen.blit(img, (300, 20))

    def aiMenu(self):
        text_surface = Sprite.FONT_30
        txt = text_surface.render("Choisissez la difficulté de l'IA", False, (0, 0, 0))
        self.screen.blit(txt, (90, 80))

        for sprite in self.sprites:
            if isinstance(sprite.image, pygame.Surface):
                self.screen.blit(pygame.transform.scale(sprite.image, sprite.size), sprite.pos)
            else:
                if sprite.isOver():
                    sprite.image.next_frame()
                elif sprite.image.cur != 0:
                    sprite.image.prev_frame()
                sprite.afficher(self.screen)

            sprite.clicked = sprite.isClicked() or sprite.clicked
            if not sprite.isClicked() and sprite.clicked:
                sprite.clicked = False
                if sprite.name == 'button-return':
                    self.whichMenu = 0
                elif sprite.name == 'button-easy':
                    self.playing = (-1) ** random.randint(0, 1)
                    self.difficulty = 0
                    self.whichMenu = 2
                    self.ai = True
                elif sprite.name == 'button-normal':
                    self.playing = (-1) ** random.randint(0, 1)
                    self.difficulty = 1
                    self.whichMenu = 2
                    self.ai = True
                elif sprite.name == 'button-hard':
                    self.playing = (-1) ** random.randint(0, 1)
                    self.difficulty = 2
                    self.whichMenu = 2
                    self.ai = True

    def multiMenu(self):
        text_surface = Sprite.FONT_30
        txt = text_surface.render("Rejoignez une partie ou créez-en une", False, (0, 0, 0))
        self.screen.blit(txt, (10, 20))

        if self.ticks % 40 == 0 and not self.creation:
            self.updateGames()

        for sprite in self.sprites:
            if isinstance(sprite.image, pygame.Surface):
                self.screen.blit(pygame.transform.scale(sprite.image, sprite.size), sprite.pos)
            else:
                if sprite.isOver():
                    sprite.image.next_frame()
                elif sprite.image.cur != 0:
                    sprite.image.prev_frame()
                sprite.afficher(self.screen)

            sprite.clicked = sprite.isClicked() or sprite.clicked
            if not sprite.isClicked() and sprite.clicked:
                sprite.clicked = False
                if sprite.name == 'button-return' and not self.creation and not self.view_data:
                    self.whichMenu = 0
                    self.client.close()
                elif sprite.name.startswith('button-join-') and not self.creation and not self.view_data:
                    game = sprite.name.replace('button-join-', '', 1)
                    MultiGame.join(self.pseudo, game, self.client)
                elif sprite.name == 'button-create' and not self.creation and not self.view_data:
                    self.creation = True
                    self.sprites.append(Sprite((50, 50), (500, 500), Sprite.image('create-bg'), 'create-bg'))
                    self.sprites.append(Sprite((470, 78), (50, 50), Sprite.image('close'), name='create-close'))
                    self.sprites.append(Button((210, 400), (180, 90), 'Créer la partie', name='button-creation'))
                    InputBox(205, 200, 200, 50, self.game_name)
                elif sprite.name == 'button-creation' and self.creation and not self.view_data:
                    MultiGame.create(self.pseudo, self.game_name, self.client)
                elif sprite.name == 'button-data' and not self.view_data and not self.creation:
                    self.view_data = True
                    self.sprites.append(Sprite((50, 50), (500, 500), Sprite.image('create-bg'), 'create-bg'))
                    self.sprites.append(Sprite((470, 78), (50, 50), Sprite.image('close'), name='create-close'))
                    MultiGame.get_data_list(self.client)
                elif sprite.name == 'create-close' and self.creation:
                    InputBox.inputs.clear()
                    self.sprites.remove(self.getSpriteByName('create-bg'))
                    self.sprites.remove(self.getSpriteByName('create-close'))
                    self.sprites.remove(self.getSpriteByName('button-creation'))
                    self.creation = False
                elif sprite.name == 'create-close' and self.view_data:
                    self.sprites.remove(self.getSpriteByName('create-bg'))
                    self.sprites.remove(self.getSpriteByName('create-close'))
                    self.view_data = False

        if self.creation:
            self.game_name = InputBox.inputs[0].text
            txt = text_surface.render("Entrez le nom de votre partie", False, (0, 0, 0))
            self.screen.blit(txt, (95, 150))
        if self.view_data:
            txt = text_surface.render("Player/Score/Parties/Ratio", False, (0, 0, 0))
            self.screen.blit(txt, (110, 80))
            txt = text_surface.render("Meilleurs Joueurs:", False, (0, 0, 0))
            self.screen.blit(txt, (95, 110))
            txt = text_surface.render("Joueurs les plus accros:", False, (0, 0, 0))
            self.screen.blit(txt, (95, 110 + 30 * 7))
            score_colors = [(255, 215, 0), (192, 192, 192), (106, 82, 17), (0, 0, 0), (0, 0, 0)]
            for knd, k in enumerate((Game.stored_data[:5], Game.stored_data[5:])):
                for ind, i in enumerate(k):
                    txt = text_surface.render(i[0], False, score_colors[ind])
                    self.screen.blit(txt, (130, 140 + ind * 30 + 30 * 7 * knd))
                    txt = text_surface.render(str(i[1]), False, score_colors[ind])
                    self.screen.blit(txt, (130 + 140, 140 + ind * 30 + 30 * 7 * knd))
                    txt = text_surface.render(str(i[2]), False, score_colors[ind])
                    self.screen.blit(txt, (130 + 220, 140 + ind * 30 + 30 * 7 * knd))
                    txt = text_surface.render(f'{round(i[1] / i[2] * 100)}%', False, score_colors[ind])
                    self.screen.blit(txt, (130 + 300, 140 + ind * 30 + 30 * 7 * knd))

    def multiGameMenu(self):
        multi: MultiGame = MultiGame.getGameByName(self.game_name)
        if multi is not None:
            if self.ticks % 10 == 0:
                multi.can_play(self.pseudo)
                if not self.started or len(multi.players) < 2:
                    MultiGame.getGamesList(self.client)
                if len(multi.players) < 2:
                    for sprite in self.sprites:
                        if 'sp-' in sprite.name:
                            self.sprites.remove(sprite)
            multi = MultiGame.getGameByName(self.game_name)

        for sprite in self.sprites:
            if sprite.name == 'button-restart' or sprite.name == 'button-again':
                if sprite.isOver():
                    sprite.image.next_frame()
                elif sprite.image.cur >= 1:
                    sprite.image.prev_frame()

            if sprite.isClicked():
                sprite.clicked = False
                if sprite.name == 'button-restart':
                    multi.again(self.pseudo)
                elif sprite.name == 'button-return':
                    self.finished = False
                    self.won = False
                    self.ai = False
                    self.whichMenu = 0
                    if self.client is not None:
                        multi: MultiGame = MultiGame.getGameByName(self.game_name)
                        if multi is not None:
                            multi.leave(self.pseudo)
                        self.client.close()
                elif 'case-' in sprite.name and not self.finished and self.playing == 1:
                    i, j = sprite.name.replace('case-', '').split('-')
                    multi.play(self.pseudo, i, j)
                elif sprite.name == 'button-again':
                    multi.again(self.pseudo)

            if isinstance(sprite.image, pygame.Surface):
                self.screen.blit(pygame.transform.scale(sprite.image, sprite.size), sprite.pos)
            else:
                sprite.afficher(self.screen)

        if len(multi.players) == 2:
            if self.playing == 1:
                txt = "C'est à vous de jouer"
            else:
                txt = "C'est à l'adversaire de jouer"

            if self.pseudo in multi.players and multi.players.index(self.pseudo) == 1:
                img = Sprite.image('circle' + list_theme[Sprite.current_theme_ext], size=(30, 30))
            else:
                img = Sprite.image('cross' + list_theme[Sprite.current_theme_ext], size=(30, 30))

            if self.won:
                if self.winner == 1:
                    txt = 'Vous avez gagné !'
                else:
                    txt = 'Vous avez perdu !'

                text_surface = Sprite.FONT_30
                for i in range(len(txt)):
                    self.screen.blit(text_surface.render(txt[i], False, (0, 0, 0)),
                                     (180 + (15 * i), int(50 + (5 * math.sin((self.ticks // 2) + (i * 5))))))
            elif self.full:
                text_surface = Sprite.FONT_30
                self.screen.blit(text_surface.render("Il n'y a eu aucun gagnants !", False, (0, 0, 0)), (120, 60))
            else:
                text_surface = Sprite.FONT_20
                self.screen.blit(text_surface.render(txt, False, (0, 0, 0)), (50, 20))
                self.screen.blit(img, (300, 20))
        else:
            text_surface = Sprite.FONT_20
            self.screen.blit(text_surface.render("En attente d'un adversaire", False, (0, 0, 0)), (50, 20))
        multi: MultiGame = MultiGame.getGameByName(self.game_name)
        if multi is not None and self.pseudo in multi.players and len(multi.players) == 2:
            text_surface = Sprite.FONT_20
            if multi.players.index(self.pseudo) == 0:
                self.screen.blit(text_surface.render(f"Adversaire: {multi.players[1]}", False, (0, 0, 0)), (50, 75))
            else:
                self.screen.blit(text_surface.render(f"Adversaire: {multi.players[0]}", False, (0, 0, 0)), (50, 75))

    def updateGames(self):
        MultiGame.getGamesList(self.client)

        remove = []
        for sprite in self.sprites:
            if sprite.name.startswith('button-join-'):
                game: MultiGame = MultiGame.getGameByName(sprite.name.replace('button-join-', '', 1))
                if game is None or len(game.players) == 2:
                    remove.append(sprite)

        for sprite in remove:
            self.sprites.remove(sprite)
        remove.clear()

        i = self.countCurrentGames()
        for game in MultiGame.games:
            if len(game.players) == 1 and self.getSpriteByName(f'button-join-{game.name}') is None:
                self.sprites.insert(len(self.sprites) - 1, Button((50 + 170 * (i % 3), 100 + 85 * (i // 3)), (150, 75),
                                                                  game.name, name=f'button-join-{game.name}'))
                i += 1

    def countCurrentGames(self):
        count = 0
        for sprite in self.sprites:
            if sprite.name.startswith('button-join-'):
                count += 1
        return count

    def getSpriteByName(self, name):
        for sprite in self.sprites:
            if sprite.name == name:
                return sprite
        return None

    def play_easy(self):
        self.playing *= -1

        empty_positions = self.grid.list_positions_empty()
        i, j = random.choice(empty_positions)

        self.grid.change_value(i, j, -1)
        sprite = None
        for s in self.sprites:
            if s.name == 'case-' + str(i) + '-' + str(j):
                sprite = s
                break

        self.sprites.append(
            Sprite((sprite.pos[0] + int(sprite.size[0] * 0.1), sprite.pos[1] + int(sprite.size[1] * 0.1)),
                   (int(sprite.size[0] * 0.8), int(sprite.size[1] * 0.8)),
                   Sprite.image('cross' + list_theme[Sprite.current_theme_ext]), name='temp'))

    def play_normal(self):
        self.playing *= -1

        l = self.grid.list_positions_empty()
        i, j = random.choice(l)

        # On vérifie en premier si on peut bloquer puis si on peut gagner (On = le bot) car si la 2e action est vrai
        # elle écrasera la premiere
        for d in [1, -1]:
            for a in range(3):
                for b in range(3):
                    if self.grid.get_value(a, b) == 0:
                        self.grid.change_value(a, b, d)
                        if self.grid.is_winner():
                            i, j = a, b
                        self.grid.change_value(a, b, 0)

        self.grid.change_value(i, j, -1)
        sprite = None
        for s in self.sprites:
            if s.name == 'case-' + str(i) + '-' + str(j):
                sprite = s
                break

        self.sprites.append(
            Sprite((sprite.pos[0] + int(sprite.size[0] * 0.1), sprite.pos[1] + int(sprite.size[1] * 0.1)),
                   (int(sprite.size[0] * 0.8), int(sprite.size[1] * 0.8)),
                   Sprite.image('cross' + list_theme[Sprite.current_theme_ext]), name='temp'))

        return None, None

    def hard_choose_pos(self):
        if self.grid.grid_is_empty():
            return 0, 0

        for d in [-1, 1]:
            for a in range(3):
                for b in range(3):
                    if self.grid.get_value(a, b) == 0:
                        self.grid.change_value(a, b, d)
                        if self.grid.is_winner():
                            return a, b
                        self.grid.change_value(a, b, 0)

        if self.grid.get_value(1, 1) == 0:
            return 1, 1
        best_position = [-1, -1, -1000]
        for i, j in self.grid.list_positions_empty():
            new_grid = self.grid.copy()
            new_grid.change_value(i, j, -1)
            if new_grid.is_winner():
                return i, j
            points = 0
            for i2, j2 in new_grid.list_positions_empty():
                new_new_grid = new_grid.copy()
                new_new_grid.change_value(i2, j2, 1)
                if new_new_grid.is_winner():
                    points -= 1
                elif new_new_grid.is_full():
                    pass
                for i3, j3 in new_new_grid.list_positions_empty():
                    new_new_new_grid = new_new_grid.copy()
                    new_new_new_grid.change_value(i3, j3, -1)
                    if new_new_new_grid.is_winner():
                        points += 1
            if points > best_position[2]:
                best_position = [i, j, points]
        return best_position[0], best_position[1]

    def play_hard(self):
        self.playing *= -1
        i, j = self.hard_choose_pos()
        self.grid.change_value(i, j, -1)
        sprite = None
        for s in self.sprites:
            if s.name == 'case-' + str(i) + '-' + str(j):
                sprite = s
                break

        self.sprites.append(
            Sprite((sprite.pos[0] + int(sprite.size[0] * 0.1), sprite.pos[1] + int(sprite.size[1] * 0.1)),
                   (int(sprite.size[0] * 0.8), int(sprite.size[1] * 0.8)),
                   Sprite.image('cross' + list_theme[Sprite.current_theme_ext]), name='temp'))

        return None, None

    @staticmethod
    def store_data(msg):
        Game.stored_data = eval(msg)


# https://www.it-swarm-fr.com/fr/python/generateur-de-mot-de-passe-aleatoire-simple-de-haute-qualite/940086298/
def make_pseudo_word(syllables=5, add_number=False):
    """Create decent memorable passwords.
    Alternate random consonants & vowels
    """
    rnd = random.SystemRandom()
    s = string.ascii_lowercase
    vowels = "aeiou"
    consonants = ''.join([x for x in s if x not in vowels])
    pwd = ''.join([rnd.choice(consonants) + rnd.choice(vowels)
                   for _ in range(syllables)]).title()
    if add_number:
        pwd += str(rnd.choice(range(10)))
    return pwd


if __name__ == '__main__':
    if "--t" in sys.argv:  # Pour pouvoir faire python3 main.py --t pour lancer la version terminal
        import default

        default.main()
    else:
        game = Game()
