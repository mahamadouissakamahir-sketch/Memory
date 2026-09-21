"""
board.py
--------
Ce fichier contient la logique du "plateau de jeu" (le tableau de cartes),
indépendamment de l'affichage. Le but : le mode Classique ET le mode Survie
utilisent tous les deux cette même logique, au lieu de la réécrire deux fois.

Comment ça marche, en simple :
1. On demande un "deck" (paquet) de cartes mélangées avec build_deck()
2. Chaque fois que le joueur tape sur une carte, on appelle on_card_selected()
3. Cette classe se souvient de la carte précédemment retournée
   - si aucune carte n'était retournée avant -> elle retient celle-ci et attend
   - si une carte était déjà retournée -> elle compare les deux valeurs
     -> pareil = paire trouvée (on appelle le callback on_match)
     -> différent = mauvaise pioche (on appelle le callback on_mismatch)
"""

import random


def build_deck(pairs_count, emoji_pool):
    """
    Crée une liste de valeurs mélangées, avec chaque emoji présent exactement
    2 fois (une paire), pour un total de pairs_count * 2 cartes.
    """
    chosen = emoji_pool[:pairs_count]
    deck = chosen * 2
    random.shuffle(deck)
    return deck


class BoardController:
    """
    Suit l'état d'une partie de Memory : quelle carte est actuellement
    retournée en attente de sa paire, combien de paires ont été trouvées,
    combien de coups ont été joués.
    """

    def __init__(self, total_pairs, on_match, on_mismatch, on_complete):
        self.total_pairs = total_pairs
        self.found_pairs = 0
        self.moves = 0
        self._waiting_card = None  # la première carte retournée, en attente de sa paire
        self.on_match = on_match          # appelé avec (card1, card2) si paire trouvée
        self.on_mismatch = on_mismatch    # appelé avec (card1, card2) si mauvaise paire
        self.on_complete = on_complete    # appelé sans argument quand toutes les paires sont faites
        self.locked = False  # True pendant qu'on affiche le résultat d'une paire (anti double-clic)

    def on_card_selected(self, card):
        """À appeler quand le joueur tape sur une carte non retournée."""
        if self.locked or card.revealed or card.matched:
            return

        card.flip_up()

        if self._waiting_card is None:
            # Première carte de la paire : on attend juste la deuxième
            self._waiting_card = card
            return

        # Deuxième carte : on compare
        self.moves += 1
        first = self._waiting_card
        self._waiting_card = None
        self.locked = True

        if first.value == card.value:
            first.set_matched()
            card.set_matched()
            self.found_pairs += 1
            self.locked = False
            if self.on_match:
                self.on_match(first, card)
            if self.found_pairs >= self.total_pairs and self.on_complete:
                self.on_complete()
        else:
            if self.on_mismatch:
                self.on_mismatch(first, card)
