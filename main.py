
import math
import random

import pygame
from pygame.locals import *
from GIFImage import GIFImage


'''
Mail Prof: CoulombNSI@gmail.com

Check List:
    - Créer une nouvelle classe qui va gérer tous les affichages et demandes (input()). Il
    est important qu’un objet soit responsable d’effectuer des tâches qui le concerne
    uniquement. L’affichage et les demandes d’informations se feront par
    l'intermédiaire d’une autre classe qu’il sera inutile d’instancier. Les méthodes de
    cette classe seront alors statiques (rechercher sur le web ce que cela signifie).
    - Faire une interface graphique avec l’outil de votre choix. Vous pouvez utiliser les
    bibliothèques pygame ou tkinter.
    - Avoir la possibilité de jouer contre l’ordinateur. A vous de choisir les stratégies de
    jeu de l’ordinateur.
    - Gérer les joueurs dans une base de données (comme vu en TP) et pouvoir noter les
    scores et tenir à jour un tableau de joueurs ayant les meilleurs résultats au jeu.
    - Pouvoir changer la taille de la grille et les conditions de victoires (lignes plus
    longues ou schéma en particulier)
'''

class Sprite(Rect):
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
    def image(name, rotate=None, size=None):
        img = pygame.image.load("./images/" + name + ".png")
        if size is not None:
            img = pygame.transform.scale(img, size)
        if rotate is not None:
            img = pygame.transform.rotate(img, rotate)
        return img


class Button(Sprite):
    def __init__(self, pos: tuple, size: tuple, text: str = '', font: str = 'Comic Sans MS', name: str = "null",
                 collide: bool = False):
        super(Button, self).__init__(pos, size, GIFImage("./images/button.gif"), name, collide)
        self.image.get_frames()
        self.text = text
        self.font = font

    def afficher(self, screen):
        img = pygame.transform.scale(self.image.frames[self.image.cur][0], self.size)
        text_surface = pygame.font.SysFont(self.font, 50).render(self.text, False, (100, 100, 100))

        x_percent = (img.get_size()[0] * 0.9) / text_surface.get_size()[0]
        text_surface = pygame.transform.scale(text_surface, (
            (text_surface.get_size()[0] * x_percent), (text_surface.get_size()[1] * x_percent)))

        if text_surface.get_size()[1] > img.get_size()[1]:
            y_percent = (img.get_size()[1] * 0.9) / text_surface.get_size()[1]
            text_surface = pygame.transform.scale(text_surface, (
                (text_surface.get_size()[0] * y_percent), (text_surface.get_size()[1] * y_percent)))

        screen.blit(pygame.transform.scale(self.image.frames[self.image.cur][0], self.size), self.pos)
        screen.blit(text_surface, (self.pos[0] + (self.size[0] - text_surface.get_size()[0]) // 2,
                                   self.pos[1] + (self.size[1] - text_surface.get_size()[1]) // 2))


class Grid:
    def __init__(self):
        self.board = [[0 for _ in range(3)] for _ in range(3)]

    def is_empty(self, i, j):
        return self.board[i][j] == 0

    def get_value(self, i, j):
        return self.board[i][j]

    def change_value(self, i, j, value):
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


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()

        self.grid = Grid()
        self.playing = 1
        self.finished = False
        self.clicked = True
        self.won = False

        self.screen = pygame.display.set_mode((600, 600))
        pygame.display.set_caption("Le jeu des croix et des ronds")
        self.running = True
        self.sprites = []
        self.whichMenu = 0  # 0 = menu principal, 1 = Menu de selection, 2 = Menu de jeu
        self.oldMenu = -1
        self.ticks = 0

        while self.running:
            self.ticks += 1
            self.screen.fill((255, 255, 255))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            if self.whichMenu != self.oldMenu:  # Menu de Jeu
                self.changeMenu()
                self.oldMenu = self.whichMenu

            if self.whichMenu == 0:
                self.mainMenu()
            if self.whichMenu == 2:
                self.main1v1()

            pygame.display.update()
            pygame.display.flip()
        pygame.quit()

    def changeMenu(self):
        self.sprites.clear()
        if self.whichMenu == 0:
            # Afficher les bouttons du menu principal
            self.sprites.append(Button((100, 200), (150, 75), "Jouer", "Comic Sans MS", "boutton-jouer"))
            self.sprites.append(Button((300, 200), (150, 75), "1v1", "Comic Sans MS", "boutton-1v1"))
            self.sprites.append(Button((100, 300), (150, 75), "Multi", "Comic Sans MS", "boutton-multi"))
            self.sprites.append(Button((300, 300), (150, 75), "Quitter", "Comic Sans MS", "boutton-quitter"))
            self.sprites.append(Sprite((100, 0), (400, 200), Sprite.image("Title"), "title"))
        elif self.whichMenu == 1:
            # Jouer contre IA
            pass
        elif self.whichMenu == 2:
            # 1v1 Local
            for i in range(3):
                for j in range(3):
                    size_of_case = 100
                    taille_a_gauche = (pygame.display.get_surface().get_size()[0] - 3 * size_of_case) // 2
                    self.sprites.append(
                        Sprite((taille_a_gauche + i * size_of_case, 200 + j * size_of_case),
                               (size_of_case, size_of_case), Sprite.image("case"),
                               "case-" + str(i) + "-" + str(j))
                    )
            self.sprites.append(Sprite((self.screen.get_size()[0] * 0.9, 5), (50, 50),
                                       Sprite.image('home'), 'button-return'))
        elif self.whichMenu == 3:
            pass
        elif self.whichMenu == 4:
            pass

    def restart(self):
        self.grid.clear()
        self.finished = False
        self.playing = -1 ** random.randint(0, 2)

        to_clear = []
        for sprite in self.sprites:
            if sprite.name == 'button-restart' or sprite.name == 'temp':
                to_clear.append(sprite)

        for sprite in to_clear:
            self.sprites.remove(sprite)

    def mainMenu(self):
        for sprite in self.sprites:
            sprite.clicked = sprite.isClicked() or sprite.clicked
            if not sprite.isClicked() and sprite.clicked:
                sprite.clicked = False
                if sprite.name == "boutton-quitter":
                    self.running = False
                if sprite.name == "boutton-jouer":
                    self.whichMenu = 1
                if sprite.name == "boutton-1v1":
                    self.whichMenu = 2

            # Faudrait move ce truc autre part car il se repette sur tout les Game Main
            if isinstance(sprite.image, GIFImage):
                if self.ticks % 10 == 0:
                    if sprite.isOver():
                        sprite.image.next_frame()
                    elif sprite.image.cur >= 1:
                        sprite.image.prev_frame()

                if isinstance(sprite, Button):
                    sprite.afficher(self.screen)
            else:
                self.screen.blit(pygame.transform.scale(sprite.image, sprite.size), sprite.pos)

    def main1v1(self):
        for sprite in self.sprites:
            if sprite.name == 'button-restart':
                if self.ticks % 10 == 0:
                    if sprite.isOver():
                        sprite.image.next_frame()
                    elif sprite.image.cur >= 1:
                        sprite.image.prev_frame()

            if sprite.isClicked():
                if sprite.name == 'button-restart':
                    self.restart()
                elif sprite.name == 'button-return':
                    self.finished = False
                    self.whichMenu = 0
                    self.playing = 1
                    self.grid.clear()
                elif 'case-' in sprite.name and not self.finished:
                    t = sprite.name.replace('case-', '').split('-')
                    i, j = int(t[0]), int(t[1])
                    if self.grid.is_empty(i, j):
                        if self.playing == 1:
                            img = 'circle'
                        else:
                            img = 'cross'
                        self.sprites.append(
                            Sprite((sprite.pos[0] + (sprite.size[0] * 0.1), sprite.pos[1] + (sprite.size[1] * 0.1)),
                                   (sprite.size[0] * 0.8, sprite.size[1] * 0.8), Sprite.image(img), name='temp'))

                        self.grid.change_value(i, j, self.playing)
                        if self.grid.is_winner() or self.grid.is_full():
                            self.sprites.append(Button((220, 120), (150, 75), 'Rejouer', name='button-restart'))
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
            img = Sprite.image('circle', size=(30, 30))
        else:
            player = 2
            img = Sprite.image('cross', size=(30, 30))

        if self.won:
            txt = 'Joueur ' + str(player) + ' a gagné !'
            text_surface = pygame.font.SysFont("Comic Sans MS", 20)
            for i in range(len(txt)):
                self.screen.blit(text_surface.render(txt[i], False, (0, 0, 0)),
                                 (180 + (15 * i), 50 + (5 * math.sin((self.ticks // 8) + (i * 5)))))
        elif self.finished:
            text_surface = pygame.font.SysFont("Comic Sans MS", 30)
            self.screen.blit(text_surface.render("Il n'y a eu aucun gagnants !", False, (0, 0, 0)), (120, 60))
        else:
            text_surface = pygame.font.SysFont("Comic Sans MS", 20)
            self.screen.blit(text_surface.render("C'est au tour du joueur " + str(player), False, (0, 0, 0)), (50, 20))
            self.screen.blit(img, (300, 20))


if __name__ == '__main__':
    game = Game()
