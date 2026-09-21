"""
game_data.py
------------
Tout le "contenu" du jeu est défini ici : les niveaux (mode Classique),
les thèmes de cartes (les emojis utilisés), et les objets de la boutique.

C'est volontairement séparé du code des écrans : si un jour tu veux
ajouter un niveau ou un thème, tu modifies UNIQUEMENT ce fichier,
tu n'as pas besoin de toucher au reste du jeu.
"""

# ---------------------------------------------------------------------------
# THEMES : chaque thème est une liste d'emojis. Il en faut au moins autant
# que le plus grand niveau a de paires (ici le niveau le plus dur a 18 paires).
# ---------------------------------------------------------------------------

THEMES = {
    "animaux": {
        "name": "Animaux",
        "price": 0,  # gratuit, débloqué dès le départ
        "emojis": [
            "🐶", "🐱", "🐭", "🐹", "🦊", "🐻", "🐼", "🐨", "🐯", "🦁",
            "🐮", "🐷", "🐸", "🐵", "🐔", "🐧", "🐦", "🐤",
        ],
    },
    "fruits": {
        "name": "Fruits",
        "price": 150,
        "emojis": [
            "🍎", "🍐", "🍊", "🍋", "🍌", "🍉", "🍇", "🍓", "🫐", "🍒",
            "🍑", "🥭", "🍍", "🥥", "🥝", "🍅", "🥑", "🍈",
        ],
    },
    "drapeaux": {
        "name": "Drapeaux",
        "price": 250,
        "emojis": [
            "🇳🇪", "🇫🇷", "🇺🇸", "🇬🇧", "🇩🇪", "🇪🇸", "🇮🇹", "🇧🇷", "🇯🇵", "🇨🇳",
            "🇳🇬", "🇬🇭", "🇸🇳", "🇨🇮", "🇲🇦", "🇪🇬", "🇿🇦", "🇨🇦",
        ],
    },
    "espace": {
        "name": "Espace",
        "price": 400,
        "emojis": [
            "🚀", "🛸", "🌍", "🌕", "🌟", "☄️", "🪐", "👨‍🚀", "🌌", "⭐",
            "🌑", "🌠", "🛰️", "🌞", "🌙", "✨", "🔭", "👽",
        ],
    },
}

DEFAULT_THEME = "animaux"


# ---------------------------------------------------------------------------
# NIVEAUX (mode Classique) : au lieu d'écrire 200 niveaux à la main (ce qui
# serait illisible et impossible à maintenir), on les CALCULE à partir de
# leur numéro grâce à une formule. C'est ce qu'on appelle une génération
# "procédurale" : le contenu est produit par du code, pas tapé un par un.
#
# Logique choisie :
# - Niveaux 1 à 8  : la grille grandit petit à petit (comme un tutoriel),
#                    jusqu'à la plus grande taille jouable sur un écran
#                    de téléphone (6 colonnes x 6 lignes = 18 paires).
# - Niveaux 9 à 200 : la grille reste à cette taille max (pas question
#                    d'afficher une grille énorme illisible sur un petit
#                    écran), mais il faut aller de plus en plus VITE pour
#                    décrocher 3 étoiles -> la difficulté continue de monter
#                    sans jamais rendre le jeu injouable.
# ---------------------------------------------------------------------------

TOTAL_LEVELS = 200

# Les 8 premiers niveaux sont réglés "à la main" un par un, car c'est la
# partie tutoriel où chaque palier de taille de grille doit être testé
# précisément. Au-delà, la formule prend le relais.
_GRID_PROGRESSION = [
    (3, 2), (4, 2), (4, 3), (4, 4), (5, 4), (6, 4), (6, 5), (6, 6),
]
_PAR_TIMES_PROGRESSION = {
    1: (12, 20), 2: (18, 28), 3: (28, 42), 4: (38, 55),
    5: (50, 70), 6: (62, 85), 7: (78, 105), 8: (95, 130),
}

_MAX_GRID = _GRID_PROGRESSION[-1]     # (6, 6) : la taille max, réutilisée pour tous les niveaux 9+
_MIN_PAR_3 = 40   # en dessous de ce temps, on arrête de durcir : ça resterait jouable
_MIN_PAR_2 = 55
_DIFFICULTY_STEP_3 = 0.4   # le seuil "3 étoiles" perd 0.4s à chaque niveau après le 8
_DIFFICULTY_STEP_2 = 0.5


def get_level(level_id):
    """
    Calcule et retourne les infos d'un niveau (grille + seuils de temps),
    à partir de son simple numéro. Retourne None si le numéro est hors limites.
    """
    if level_id < 1 or level_id > TOTAL_LEVELS:
        return None

    if level_id <= len(_GRID_PROGRESSION):
        cols, rows = _GRID_PROGRESSION[level_id - 1]
        par_3, par_2 = _PAR_TIMES_PROGRESSION[level_id]
    else:
        cols, rows = _MAX_GRID
        levels_beyond = level_id - len(_GRID_PROGRESSION)
        base_par_3, base_par_2 = _PAR_TIMES_PROGRESSION[len(_GRID_PROGRESSION)]
        par_3 = max(_MIN_PAR_3, base_par_3 - levels_beyond * _DIFFICULTY_STEP_3)
        par_2 = max(_MIN_PAR_2, base_par_2 - levels_beyond * _DIFFICULTY_STEP_2)

    return {
        "id": level_id,
        "cols": cols,
        "rows": rows,
        "par_3_stars": par_3,
        "par_2_stars": par_2,
    }


def stars_for_time(level, time_taken):
    """Calcule le nombre d'étoiles (1 à 3) obtenu selon le temps mis à finir le niveau."""
    if time_taken <= level["par_3_stars"]:
        return 3
    if time_taken <= level["par_2_stars"]:
        return 2
    return 1


def coins_for_result(level, stars):
    """Combien de pièces on gagne selon la taille du niveau et le nombre d'étoiles."""
    pairs = level["cols"] * level["rows"] // 2
    # +5 pièces tous les 10 niveaux, pour que jouer un niveau 150 rapporte
    # un peu plus qu'un niveau 10, même si la grille a la même taille.
    progression_bonus = (level["id"] // 10) * 5
    base = pairs * 5 + progression_bonus
    if stars == 3:
        return int(base * 1.5)
    if stars == 2:
        return int(base * 1.2)
    return base


# ---------------------------------------------------------------------------
# BOUTIQUE : indices utilisables pendant une partie
# ---------------------------------------------------------------------------

SHOP_HINTS = {
    "peek": {
        "name": "Coup d'œil",
        "desc": "Montre toutes les cartes pendant 1 seconde",
        "price": 30,
    },
    "time_boost": {
        "name": "+10 secondes",
        "desc": "Ajoute 10 secondes au chrono en mode Survie",
        "price": 40,
    },
}

# ---------------------------------------------------------------------------
# BOUTIQUE : modes spéciaux à débloquer
# ---------------------------------------------------------------------------

SHOP_MODES = {
    "chrono_inverse": {
        "name": "Chrono Inversé",
        "desc": "Rejoue n'importe quel niveau débloqué contre la montre, et bats ton record",
        "price": 300,
    },
}
