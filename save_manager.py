"""
save_manager.py
----------------
Ce fichier s'occupe de TOUT ce qui doit être gardé en mémoire entre deux
lancements du jeu : les pièces, les thèmes débloqués, les étoiles gagnées
par niveau, le meilleur score en survie, etc.

On sauvegarde tout ça dans un simple fichier JSON sur le téléphone.
Un fichier JSON, c'est juste du texte organisé façon "dictionnaire Python"
(des clés et des valeurs) -> facile à lire et à écrire.
"""

import json
import os


def _default_data():
    """Retourne la structure de données de départ, pour un tout nouveau joueur."""
    return {
        "coins": 0,
        "unlocked_themes": ["animaux"],   # le thème Animaux est gratuit dès le début
        "current_theme": "animaux",
        "unlocked_modes": ["classique", "survie"],
        "survival_high_score": 0,
        # "levels" contiendra par exemple: {"1": {"stars": 3, "best_time": 12.4}, ...}
        "levels": {},
    }


class SaveManager:
    """
    Petite classe qui charge/sauvegarde la progression du joueur.

    On lui donne un chemin de fichier (save_path) où écrire le JSON.
    Elle garde les données en mémoire dans self.data, et on appelle
    self.save() à chaque fois qu'on veut écrire les changements sur le disque.
    """

    def __init__(self, save_path):
        self.save_path = save_path
        self.data = _default_data()
        self.load()

    def load(self):
        """Charge le fichier de sauvegarde s'il existe, sinon garde les valeurs par défaut."""
        if os.path.exists(self.save_path):
            try:
                with open(self.save_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                # On fusionne avec les valeurs par défaut, au cas où on ajoute
                # plus tard de nouvelles clés (ex: nouveau mode) : ça évite un crash
                # pour les joueurs qui avaient une sauvegarde plus ancienne.
                data = _default_data()
                data.update(loaded)
                self.data = data
            except (json.JSONDecodeError, OSError):
                # Fichier corrompu ou illisible -> on repart sur une sauvegarde neuve
                self.data = _default_data()

    def save(self):
        """Écrit l'état actuel (self.data) dans le fichier JSON."""
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
        with open(self.save_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    # ---------- Pièces (économie) ----------

    @property
    def coins(self):
        return self.data["coins"]

    def add_coins(self, amount):
        self.data["coins"] += amount
        self.save()

    def spend_coins(self, amount):
        """Essaie de dépenser des pièces. Retourne True si ça a marché, False si pas assez."""
        if self.data["coins"] >= amount:
            self.data["coins"] -= amount
            self.save()
            return True
        return False

    # ---------- Thèmes ----------

    def unlock_theme(self, theme_id):
        if theme_id not in self.data["unlocked_themes"]:
            self.data["unlocked_themes"].append(theme_id)
            self.save()

    def is_theme_unlocked(self, theme_id):
        return theme_id in self.data["unlocked_themes"]

    def set_current_theme(self, theme_id):
        self.data["current_theme"] = theme_id
        self.save()

    # ---------- Modes ----------

    def unlock_mode(self, mode_id):
        if mode_id not in self.data["unlocked_modes"]:
            self.data["unlocked_modes"].append(mode_id)
            self.save()

    def is_mode_unlocked(self, mode_id):
        return mode_id in self.data["unlocked_modes"]

    # ---------- Niveaux (mode classique) ----------

    def get_level_result(self, level_id):
        """Retourne {'stars': int, 'best_time': float|None} pour un niveau donné."""
        return self.data["levels"].get(str(level_id), {"stars": 0, "best_time": None})

    def is_level_unlocked(self, level_id):
        """Le niveau 1 est toujours débloqué. Les suivants demandent >=1 étoile au précédent."""
        if level_id <= 1:
            return True
        previous = self.get_level_result(level_id - 1)
        return previous["stars"] >= 1

    def set_level_result(self, level_id, stars, time_taken):
        """
        Enregistre le résultat d'un niveau. On ne garde que le MEILLEUR score
        (le plus d'étoiles, et à égalité le meilleur temps).
        """
        current = self.get_level_result(level_id)
        best_stars = max(current["stars"], stars)
        if current["best_time"] is None:
            best_time = time_taken
        else:
            best_time = min(current["best_time"], time_taken)
        self.data["levels"][str(level_id)] = {"stars": best_stars, "best_time": best_time}
        self.save()

    # ---------- Survie ----------

    def update_survival_score(self, score):
        """Met à jour le meilleur score de survie si le nouveau score est plus grand."""
        if score > self.data["survival_high_score"]:
            self.data["survival_high_score"] = score
            self.save()
            return True
        return False
