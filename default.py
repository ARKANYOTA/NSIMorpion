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
        return (self.board[0][0].symbole == self.board[1][1].symbole == self.board[2][2].symbole or
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
