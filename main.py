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
            if self.board[i][0].symbole == self.board[i][1].symbole == self.board[i][2].symbole and self.board[i][0].symbole is not None:
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
                    self.compteur -=1
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


class Affichage:
    @classmethod
    def affGrille(cls, grille):
        print(str(grille))



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



def image(name, rotate=None, size=None):
    img = pygame.image.load("./images/" + name + ".png")
    if size != None:
        img = pygame.transform.scale(img, size)
    if rotate != None:
        img = pygame.transform.rotate(img, rotate)
    return img


def changeMenu(menu, sprites):
    sprites.clear()
    if menu == 0:
        # Afficher les bouttons du menu principal
        sprites.append(Sprite((100, 200), (200, 100), image("buttonJouer"), "boutton-jouer"))
        sprites.append(Sprite((300, 200), (200, 100), image("buttonLan"), "boutton-lan"))
        sprites.append(Sprite((100, 300), (200, 100), image("buttonMulti"), "boutton-multi"))
        sprites.append(Sprite((300, 300), (200, 100), image("buttonQuitter"), "boutton-quitter"))
        sprites.append(Sprite((100, 0), (400, 200), image("Title"), "title"))
    elif menu == 1:
        # Afficher la selection de partie (multi)
        pass
    elif menu == 2:
        # Afficher la selection de partie (local)
        pass
    elif menu == 3:
        # Afficher le menu config IA
        pass
    elif menu == 4:
        # Afficher le jeu
        pass


def main():
    while True:
        joueur1 = Player(input("Joueur 1: Quel est ton nom? : "), "X")
        joueur2 = Player(input("Joueur 2: Quel est ton nom? : "), "O")
        jeu = Jeu(joueur1, joueur2)
        jeu.jouer()
        if input("Voulez-vous rejouer? [y/n] : ") == "y":
            continue
        else:
            break


def main_pygame():
    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    pygame.display.set_caption("PyGame")
    running = True
    sprites = []
    witchMenu = 0  # 0 = menu principal, 1 = Menu de selection, 2 = Menu de jeu
    oldMenu = -1
    while running:
        screen.fill((255, 255, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if witchMenu != oldMenu:  # Menu de Jeu
            changeMenu(witchMenu, sprites)
            oldMenu = witchMenu

        for sprite in sprites:
            if "boutton" in sprite.name:
                if sprite.isOver():
                    sprite.size = (210, 105)
                else:
                    sprite.size = (200, 100)

                if sprite.isClicked():
                    if sprite.name == "boutton-quitter":
                        running = False
                    if sprite.name == "boutton-jouer":
                        witchMenu = 1

            screen.blit(pygame.transform.scale(sprite.image, sprite.size), sprite.pos)

        pygame.display.update()
        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main_pygame()
