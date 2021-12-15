'''
Mail Prof: CoulombNSI@gmail.com

TODO:
- Normal
- Socket
- SQL
-
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
            if self.board[0][i].symbole == self.board[1][i].symbole == self.board[2][i].symbole and self.board[0][i].symbole is not None:
                return True

        # Diagonal
        return (self.board[0][0].symbole == self.board[1][1].symbole == self.board[2][2].symbole or \
               self.board[0][2].symbole == self.board[1][1].symbole == self.board[2][0].symbole) and self.board[1][1].symbole is not None

    def __str__(self):
        txt = "\n-------\n"
        for i in self.board:
            txt += "|"
            for j in i:
                if j.symbole is None:
                    txt += " |"
                else:
                    txt += j.symbole+ "|"
            txt += "\n-------\n"
        return txt


class Jeu:
    def __init__(self, joueur1, joueur2):
        self.joueurs = [joueur1, joueur2]
        self.grille = Grille()
        self.quiJoue = False  # False est equivalant à 0
        self.compteur = 0

    def joueur(self):
        return self.joueurs[self.quiJoue]

    def changerJoueur(self):
        self.quiJoue = not self.quiJoue

    def tourSuivant(self):
        boucleQuelleCase = True
        while boucleQuelleCase:
            print(str(self.grille))
            currentCase = input(str(self.joueurs[self.quiJoue])+": Quelle case jouer? entre [0;8] : ")
            if currentCase.isdigit():
                currentCase = int(currentCase)
                if 0 <= currentCase <= 8:
                    if self.grille.estVide(currentCase):
                        self.grille.changerValeur(currentCase, self.joueur().symbole)
                        self.changerJoueur()
                        self.compteur += 1
                        boucleQuelleCase = False
                    else:
                        print("Cette case est déjà prise!")
                else:
                    print("Cette case n'existe pas!")
            else:
                print("Veuillez entrer un chiffre entre [0;8] !")

    def jouer(self):
        while not self.grille.isGagnant():
            self.tourSuivant()

        print(str(self.grille))
        self.quiJoue = not self.quiJoue
        print(f"{str(self.joueur())} a gagné!")

def image(name, rotate=0, size=(32, 32)):
    return pygame.transform.rotate(pygame.transform.scale(pygame.image.load("./images/" + name + ".png"), size), rotate)

def changeMenu(menu, sprites):
    # menu:  0= Menu principal, 1=Selection de partie(Multi), 2=Selection de partie(Local), 3=
    if menu == 0:
        # Afficher les bouttons du menu principal
        sprites.append(Sprite((50, 50), (1000, 1000), image("buttonJouer"), "jouer"))
        pass
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
    screen.fill((255, 255, 255))
    running = True
    sprites = []
    witchMenu = 0  # 0 = menu principal, 1 = Menu de selection, 2 = Menu de jeu
    oldMenu = -1
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if witchMenu != oldMenu:  # Menu de Jeu
            changeMenu(witchMenu, sprites)
            oldMenu = witchMenu

        for sprite in sprites:
            screen.blit(sprite.image, sprite.pos)

        pygame.display.update()
    pygame.quit()


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
        return self.topleft[0] <= pygame.mouse.get_pos()[0] <= self.bottomright[0] and self.topleft[1] <= pygame.mouse.get_pos()[1] <= self.bottomright[1]



if __name__ == '__main__':
    main_pygame()
























