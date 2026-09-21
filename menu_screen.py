"""
menu_screen.py
--------------
Le tout premier écran que voit le joueur : le menu principal.
Il affiche le titre du jeu, le nombre de pièces actuelles, et des boutons
pour aller vers les autres écrans (Jouer, Survie, Boutique).
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from core.ui_kit import RoundedButton, PRIMARY, ACCENT, SUCCESS, DANGER, TEXT, TEXT_MUTED


class MenuScreen(Screen):
    def __init__(self, save_manager, **kwargs):
        super().__init__(**kwargs)
        self.save_manager = save_manager
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", padding=30, spacing=20)

        title = Label(
            text="[b]MEMORY[/b]\n[size=16]par toi[/size]",
            markup=True,
            font_size="44sp",
            color=TEXT,
            size_hint_y=0.35,
        )
        root.add_widget(title)

        self.coins_label = Label(
            text=f"🪙 {self.save_manager.coins}",
            font_size="20sp",
            color=ACCENT,
            size_hint_y=0.1,
        )
        root.add_widget(self.coins_label)

        btn_play = RoundedButton("🎮 Jouer", on_release=self._go_levels,
                                  bg_color=PRIMARY, size_hint_y=0.12)
        root.add_widget(btn_play)

        btn_survive = RoundedButton("⏱️ Mode Survie", on_release=self._go_survive,
                                     bg_color=DANGER, size_hint_y=0.12)
        root.add_widget(btn_survive)

        btn_shop = RoundedButton("🛒 Boutique", on_release=self._go_shop,
                                  bg_color=ACCENT, size_hint_y=0.12)
        root.add_widget(btn_shop)

        footer = Label(text="Fait avec Python + Kivy", font_size="12sp",
                        color=TEXT_MUTED, size_hint_y=0.08)
        root.add_widget(footer)

        self.add_widget(root)

    def on_pre_enter(self, *_args):
        # À chaque fois qu'on revient sur ce menu, on rafraîchit le nombre de pièces affiché
        self.coins_label.text = f"🪙 {self.save_manager.coins}"

    def _go_levels(self, *_args):
        self.manager.current = "level_select"

    def _go_survive(self, *_args):
        self.manager.current = "survival"

    def _go_shop(self, *_args):
        self.manager.current = "shop"
