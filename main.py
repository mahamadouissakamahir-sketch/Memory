"""
main.py
-------
Le point de départ de l'application. C'est CE fichier que Kivy/Buildozer
lance en premier. Il crée l'application, prépare la sauvegarde, et
enregistre tous les écrans (menu, niveaux, jeu, survie, boutique) dans
un ScreenManager (un gestionnaire qui affiche un écran à la fois et
permet de naviguer entre eux).
"""

import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition

from core.save_manager import SaveManager
from screens.menu_screen import MenuScreen
from screens.level_select_screen import LevelSelectScreen
from screens.game_screen import GameScreen
from screens.survival_screen import SurvivalScreen
from screens.shop_screen import ShopScreen


class MemoryApp(App):
    def build(self):
        # user_data_dir = un dossier propre à l'app, fourni automatiquement par Kivy,
        # qui existe aussi bien sur PC que sur Android. C'est là qu'on range la sauvegarde.
        save_path = os.path.join(self.user_data_dir, "save.json")
        self.save_manager = SaveManager(save_path)

        sm = ScreenManager(transition=FadeTransition(duration=0.15))
        sm.add_widget(MenuScreen(self.save_manager, name="menu"))
        sm.add_widget(LevelSelectScreen(self.save_manager, name="level_select"))
        sm.add_widget(GameScreen(self.save_manager, name="game"))
        sm.add_widget(SurvivalScreen(self.save_manager, name="survival"))
        sm.add_widget(ShopScreen(self.save_manager, name="shop"))
        sm.current = "menu"
        return sm


if __name__ == "__main__":
    MemoryApp().run()
