"""
level_select_screen.py
-----------------------
La "carte des niveaux". Avec 200 niveaux, on ne peut pas juste tout
afficher d'un coup dans une longue liste qui scrolle : créer 200 boutons
en même temps ralentirait le jeu, surtout sur un téléphone d'entrée de
gamme. La solution : une "pagination" -> on affiche 20 niveaux à la fois,
avec des boutons "◀" / "▶" pour naviguer. Même principe qu'une liste de
résultats Google découpée en pages.

Astuce de performance : on crée les 20 boutons UNE SEULE FOIS au démarrage,
et on se contente ensuite de changer leur texte/couleur/action à chaque
changement de page, plutôt que de les détruire et recréer à chaque fois.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout

from core.ui_kit import RoundedButton, PRIMARY, TEXT_MUTED, TEXT, ACCENT
from core.game_data import TOTAL_LEVELS

PAGE_SIZE = 20


class LevelSelectScreen(Screen):
    def __init__(self, save_manager, **kwargs):
        super().__init__(**kwargs)
        self.save_manager = save_manager
        self.current_page = 0
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", padding=20, spacing=10)

        header = BoxLayout(size_hint_y=None, height=50, spacing=8)
        back_btn = RoundedButton("← Retour", on_release=self._go_back, bg_color=TEXT_MUTED,
                                  size_hint_x=0.4)
        continue_btn = RoundedButton("▶ Continuer", on_release=self._jump_to_current,
                                      bg_color=ACCENT, size_hint_x=0.6)
        header.add_widget(back_btn)
        header.add_widget(continue_btn)
        root.add_widget(header)

        self.title_label = Label(text="Choisis un niveau", font_size="20sp",
                                  color=TEXT, size_hint_y=None, height=36, bold=True)
        root.add_widget(self.title_label)

        # Grille FIXE de 20 cases (4 colonnes x 5 lignes), réutilisée pour
        # chaque page : on ne recrée jamais ces boutons, on change juste
        # ce qu'ils affichent. Beaucoup plus léger pour le téléphone.
        self.grid = GridLayout(cols=4, spacing=8, size_hint_y=0.75)
        self._level_buttons = []
        for _ in range(PAGE_SIZE):
            btn = RoundedButton("", bg_color=PRIMARY)
            self.grid.add_widget(btn)
            self._level_buttons.append(btn)
        root.add_widget(self.grid)

        nav_bar = BoxLayout(size_hint_y=None, height=50, spacing=10)
        prev_btn = RoundedButton("◀", on_release=self._prev_page, bg_color=TEXT_MUTED,
                                  size_hint_x=0.25)
        self.page_label = Label(text="", font_size="16sp", color=TEXT_MUTED, size_hint_x=0.5)
        next_btn = RoundedButton("▶", on_release=self._next_page, bg_color=TEXT_MUTED,
                                  size_hint_x=0.25)
        nav_bar.add_widget(prev_btn)
        nav_bar.add_widget(self.page_label)
        nav_bar.add_widget(next_btn)
        root.add_widget(nav_bar)

        self.add_widget(root)

    def on_pre_enter(self, *_args):
        self._refresh_page()

    # ------------------------------------------------------------ Pages --

    @property
    def total_pages(self):
        return (TOTAL_LEVELS + PAGE_SIZE - 1) // PAGE_SIZE

    def _refresh_page(self):
        start_id = self.current_page * PAGE_SIZE + 1
        self.page_label.text = f"Page {self.current_page + 1} / {self.total_pages}"

        for i, btn in enumerate(self._level_buttons):
            level_id = start_id + i

            if level_id > TOTAL_LEVELS:
                # Case vide (dernière page pas complètement remplie)
                btn.set_text("")
                btn.set_disabled(True)
                btn.set_on_release(None)
                continue

            unlocked = self.save_manager.is_level_unlocked(level_id)
            result = self.save_manager.get_level_result(level_id)

            if unlocked:
                stars = "⭐" * result["stars"] + "·" * (3 - result["stars"])
                btn.set_text(f"{level_id}\n{stars}")
                btn.set_disabled(False)
                btn.set_on_release(self._make_starter(level_id))
            else:
                btn.set_text(f"{level_id}\n🔒")
                btn.set_disabled(True)
                btn.set_on_release(None)

    def _make_starter(self, level_id):
        def _start(*_args):
            game_screen = self.manager.get_screen("game")
            game_screen.start_level(level_id)
            self.manager.current = "game"
        return _start

    def _prev_page(self, *_args):
        if self.current_page > 0:
            self.current_page -= 1
            self._refresh_page()

    def _next_page(self, *_args):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self._refresh_page()

    def _jump_to_current(self, *_args):
        """Va directement à la page contenant le premier niveau pas encore terminé."""
        target = TOTAL_LEVELS
        for level_id in range(1, TOTAL_LEVELS + 1):
            if not self.save_manager.is_level_unlocked(level_id):
                target = max(1, level_id - 1)
                break
            if self.save_manager.get_level_result(level_id)["stars"] == 0:
                target = level_id
                break
        self.current_page = (target - 1) // PAGE_SIZE
        self._refresh_page()

    def _go_back(self, *_args):
        self.manager.current = "menu"
