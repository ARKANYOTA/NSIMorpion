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


TODO:
- Interface
- Socket
- SQL
'''

import pygame
from pygame.locals import *
from GIFImage import GIFImage


class Player:
    def __init__(self, name, symbole):
        self.name = name
        self.symbole = symbole

    def __str__(self):
        return f"{self.name} ({self.symbole})"


class Case:
    def __init__(self, pos):
        self.pos = pos
        self.symbole = None

    def __str__(self):
        print(self.symbole)


class Grille:
    def __init__(self):
        self.board = [[Case(0), Case(1), Case(2)], [Case(3), Case(4), Case(5)], [Case(6), Case(7), Case(8)]]

    def estVide(self, pos):
        return self.board[pos // 3][pos % 3].symbole is None

    def changerValeur(self, pos, symbole):
        self.board[pos // 3][pos % 3].symbole = symbole

    def isGagnant(self):
        # Horizontal
        for i in range(3):
            if self.board[i][0].symbole == self.board[i][1].symbole == self.board[i][2].symbole and self.board[i][
                0].symbole is not None:
                return True
        # Vertical
        for i in range(3):
            if self.board[0][i].symbole == self.board[1][i].symbole == self.board[2][i].symbole and self.board[0][
                i].symbole is not None:
                return True

        # Diagonal
        return (self.board[0][0].symbole == self.board[1][1].symbole == self.board[2][2].symbole or \
                self.board[0][2].symbole == self.board[1][1].symbole == self.board[2][0].symbole) and self.board[1][
                   1].symbole is not None

    def __str__(self):
        txt = "\n-------\n"
        for i in self.board:
            txt += "|"
            for j in i:
                if j.symbole is None:
                    txt += " |"
                else:
                    txt += j.symbole + "|"
            txt += "\n-------\n"
        return txt


class Jeu:
    def __init__(self, joueur1, joueur2):
        self.joueurs = [joueur1, joueur2]
        self.grille = Grille()
        self.quiJoue = False  # False est equivalant à 0
        self.compteur = 0
        self.coupsJouer = []

    def joueur(self):
        return self.joueurs[self.quiJoue]

    def changerJoueur(self):
        self.quiJoue = not self.quiJoue

    def tourSuivant(self):
        boucleQuelleCase = True
        while boucleQuelleCase:
            print(str(self.grille))
            currentCase = input(str(self.joueurs[self.quiJoue]) + ": Quelle case jouer? entre [0;8] : ")
            if currentCase.isdigit():
                currentCase = int(currentCase)
                if 0 <= currentCase <= 8:
                    if self.grille.estVide(currentCase):
                        self.grille.changerValeur(currentCase, self.joueur().symbole)
                        self.changerJoueur()
                        self.compteur += 1
                        self.coupsJouer.append(currentCase)
                        boucleQuelleCase = False
                    else:
                        print("Cette case est déjà prise!")
                else:
                    print("Cette case n'existe pas!")
            elif currentCase == "r":  # Revenir en arrière
                if len(self.coupsJouer) != 0:
                    self.grille.changerValeur(self.coupsJouer[-1], None)
                    self.changerJoueur()
                    self.compteur -= 1
                    self.coupsJouer.pop()
                    boucleQuelleCase = False
                else:
                    print('Aucun coup a annuler')
            else:
                print("Veuillez entrer un chiffre entre [0;8] !")

    def jouer(self):
        while not (self.grille.isGagnant() or self.compteur == 9):
            self.tourSuivant()

        print(str(self.grille))
        if self.grille.isGagnant():
            self.quiJoue = not self.quiJoue
            print(f"{str(self.joueur())} a gagné!")
            return None
        print(f"égalité: Personne a gagner")


class Sprite(Rect):
    def __init__(self, pos, size, image, name="null", collide=False):
        super().__init__(pos[0], pos[1], size[0], size[1])
        self.image = image
        self.pos = pos
        self.name = name
        self.collide = collide

    def move(self, x: float, y: float) -> Rect:
        self.pos[0] = x
        self.pos[1] = y

    def isClicked(self):
        mouse = pygame.mouse
        m = mouse.get_pos()
        return self.collidepoint(m[0], m[1]) and mouse.get_pressed()[0] and mouse.get_focused()

    def isOver(self):
        mouse = pygame.mouse
        m = mouse.get_pos()
        return self.collidepoint(m[0], m[1]) and mouse.get_focused()


class Button(Sprite):
    def __init__(self, pos: tuple, size: tuple, text: str = '', font: str = 'Comic Sans MS', name: str = "null",
                 collide: bool = False):
        super(Button, self).__init__(pos, size, GIFImage("./images/button.gif"), name, collide)
        self.text = text
        self.font = font


def image(name, rotate=None, size=None):
    img = pygame.image.load("./images/" + name + ".png")
    if size != None:
        img = pygame.transform.scale(img, size)
    if rotate != None:
        img = pygame.transform.rotate(img, rotate)
    return img


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()

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
            self.sprites.append(Sprite((100, 0), (400, 200), image("Title"), "title"))
        elif self.whichMenu == 1:
            # Jouer contre IA
            pass
        elif self.whichMenu == 2:
            print(pygame.display.get_surface().get_size())

            # 1v1 Local
            for i in range(3):
                for j in range(3):
                    size_of_case = 100
                    taille_a_gauche = (pygame.display.get_surface().get_size()[0]-3*size_of_case)//2
                    self.sprites.append(
                        Sprite((taille_a_gauche + i * size_of_case, 200 + j * size_of_case),
                        (size_of_case, size_of_case), image("case"),
                        "case-" + str(i) + "-" + str(j))
                    )
                    
        elif self.whichMenu == 3:
            pass
        elif self.whichMenu == 4:
            pass

    def mainMenu(self):
        for sprite in self.sprites:
            if sprite.isClicked():
                if sprite.name == "boutton-quitter":
                    self.running = False
                if sprite.name == "boutton-jouer":
                    self.whichMenu = 1
                if sprite.name == "boutton-1v1":
                    self.whichMenu = 2

            # Faudrait move ce truc autre part car il se repette sur tout les Game Main
            if isinstance(sprite.image, GIFImage):
                if sprite.image.frames == None or sprite.image.frames == []:
                    sprite.image.get_frames()

                if self.ticks % 10 == 0:
                    if sprite.isOver():
                        sprite.image.next_frame()
                    elif sprite.image.cur >= 1:
                        sprite.image.prev_frame()

                if isinstance(sprite, Button):
                    textsurface = pygame.font.SysFont(sprite.font, int(90 / len(sprite.text))).render(sprite.text,
                                                                                                      False,
                                                                                                      (220, 220, 220))
                    y = 3
                    if sprite.text == "1v1":
                        y = -7
                    if sprite.text == "Quitter":
                        y = 6
                    sprite.image.frames[sprite.image.cur][0].blit(textsurface, (
                        (sprite.size[0] - textsurface.get_size()[0]) // 16, y))
                self.screen.blit(pygame.transform.scale(sprite.image.frames[sprite.image.cur][0], sprite.size),
                                 sprite.pos)
            else:
                self.screen.blit(pygame.transform.scale(sprite.image, sprite.size), sprite.pos)

    def main1v1(self):
        for sprite in self.sprites:
            if sprite.isClicked():
                for i in range(3):
                    for j in range(3):
                        if sprite.name == "case-" + str(i) + "-" + str(j):
                            sprite.image = image("casecroix")

            if isinstance(sprite.image, GIFImage):
                if sprite.image.frames == None or sprite.image.frames == []:
                    sprite.image.get_frames()

                if self.ticks % 10 == 0:
                    if sprite.isOver():
                        sprite.image.next_frame()
                    elif sprite.image.cur >= 1:
                        sprite.image.prev_frame()

                if isinstance(sprite, Button):
                    textsurface = pygame.font.SysFont(sprite.font, int(90 / len(sprite.text))).render(sprite.text,
                                                                                                      False,
                                                                                                      (220, 220, 220))
                    y = 3
                    if sprite.text == "1v1":
                        y = -7
                    if sprite.text == "Quitter":
                        y = 6
                    sprite.image.frames[sprite.image.cur][0].blit(textsurface, (
                        (sprite.size[0] - textsurface.get_size()[0]) // 16, y))
                self.screen.blit(pygame.transform.scale(sprite.image.frames[sprite.image.cur][0], sprite.size),
                                 sprite.pos)
            else:
                self.screen.blit(pygame.transform.scale(sprite.image, sprite.size), sprite.pos)


def main():
    while True:
        joueur1 = Player(input("Joueur 1: Quel est ton nom? : "), "X")
        joueur2 = Player(input("Joueur 2: Quel est ton nom? : "), "O")
        jeu = Jeu(joueur1, joueur2)
        jeu.jouer()
        rep = input("Voulez-vous rejouer? [y/n] : ")
        while not (rep == 'y' or rep == 'n'):
            rep = input("Voulez-vous rejouer? [y/n] : ")
        if rep == "y":
            continue
        else:
            break


if __name__ == '__main__':
    game = Game()
