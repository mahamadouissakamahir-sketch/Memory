"""
game_screen.py
--------------
L'écran où on joue vraiment une partie en mode Classique : la grille de
cartes, le chrono qui compte le temps écoulé, le compteur de coups, et
le popup de fin de niveau avec les étoiles gagnées.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.clock import Clock

from core.ui_kit import RoundedButton, PRIMARY, ACCENT, TEXT_MUTED, TEXT, SUCCESS
from core.game_data import get_level, stars_for_time, coins_for_result, THEMES, SHOP_HINTS
from core.board import build_deck, BoardController
from core.card import Card


class GameScreen(Screen):
    def __init__(self, save_manager, **kwargs):
        super().__init__(**kwargs)
        self.save_manager = save_manager
        self.level = None
        self.board = None
        self.elapsed = 0.0
        self._clock_event = None
        self._build_ui()

    # ---------------------------------------------------------------- UI --

    def _build_ui(self):
        self.root_layout = BoxLayout(orientation="vertical", padding=14, spacing=10)

        top_bar = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.quit_btn = RoundedButton("✕", on_release=self._quit, bg_color=TEXT_MUTED,
                                       size_hint_x=0.15)
        self.timer_label = Label(text="00:00", font_size="20sp", color=TEXT, size_hint_x=0.35)
        self.moves_label = Label(text="Coups: 0", font_size="16sp", color=TEXT_MUTED,
                                  size_hint_x=0.3)
        self.hint_btn = RoundedButton("💡", on_release=self._use_peek_hint, bg_color=ACCENT,
                                       size_hint_x=0.2)
        top_bar.add_widget(self.quit_btn)
        top_bar.add_widget(self.timer_label)
        top_bar.add_widget(self.moves_label)
        top_bar.add_widget(self.hint_btn)
        self.root_layout.add_widget(top_bar)

        self.board_grid = GridLayout(spacing=6)
        self.root_layout.add_widget(self.board_grid)

        self.add_widget(self.root_layout)

    # -------------------------------------------------------- Démarrage --

    def start_level(self, level_id):
        self.level = get_level(level_id)
        theme_id = self.save_manager.data.get("current_theme", "animaux")
        emoji_pool = THEMES.get(theme_id, THEMES["animaux"])["emojis"]

        pairs = (self.level["cols"] * self.level["rows"]) // 2
        deck = build_deck(pairs, emoji_pool)

        self.board_grid.clear_widgets()
        self.board_grid.cols = self.level["cols"]

        self.cards = []
        for value in deck:
            card = Card(value)
            card.bind(on_release=self._on_card_tap)
            self.board_grid.add_widget(card)
            self.cards.append(card)

        self.board = BoardController(
            total_pairs=pairs,
            on_match=self._on_match,
            on_mismatch=self._on_mismatch,
            on_complete=self._on_level_complete,
        )

        self.elapsed = 0.0
        self.moves_label.text = "Coups: 0"
        self.timer_label.text = "00:00"
        if self._clock_event:
            self._clock_event.cancel()
        self._clock_event = Clock.schedule_interval(self._tick, 1.0)

    def _tick(self, _dt):
        self.elapsed += 1
        minutes = int(self.elapsed) // 60
        seconds = int(self.elapsed) % 60
        self.timer_label.text = f"{minutes:02d}:{seconds:02d}"

    # ------------------------------------------------------------ Jeu --

    def _on_card_tap(self, card):
        self.board.on_card_selected(card)
        self.moves_label.text = f"Coups: {self.board.moves}"

    def _on_match(self, _card1, _card2):
        pass  # la carte se colore déjà toute seule (voir card.set_matched)

    def _on_mismatch(self, card1, card2):
        # On laisse les 2 cartes visibles une petite seconde pour que le joueur
        # mémorise, puis on les recache.
        def _hide(_dt):
            card1.flip_down()
            card2.flip_down()
            self.board.locked = False
        Clock.schedule_once(_hide, 0.7)

    def _on_level_complete(self):
        if self._clock_event:
            self._clock_event.cancel()
        stars = stars_for_time(self.level, self.elapsed)
        coins_earned = coins_for_result(self.level, stars)
        self.save_manager.set_level_result(self.level["id"], stars, self.elapsed)
        self.save_manager.add_coins(coins_earned)
        self._show_result_popup(stars, coins_earned)

    def _use_peek_hint(self, *_args):
        price = SHOP_HINTS["peek"]["price"]
        if not self.save_manager.spend_coins(price):
            self._show_message("Pas assez de pièces 🪙")
            return
        for card in self.cards:
            if not card.matched and not card.revealed:
                card.text = card.value
        def _hide_again(_dt):
            for card in self.cards:
                if not card.matched and not card.revealed:
                    card.text = "❓"
        Clock.schedule_once(_hide_again, 1.0)

    # ---------------------------------------------------------- Popups --

    def _show_result_popup(self, stars, coins_earned):
        content = BoxLayout(orientation="vertical", spacing=14, padding=20)
        content.add_widget(Label(text="⭐" * stars + "☆" * (3 - stars),
                                  font_size="34sp", color=ACCENT, size_hint_y=0.35))
        content.add_widget(Label(text=f"Niveau terminé en {int(self.elapsed)}s",
                                  font_size="16sp", color=TEXT, size_hint_y=0.2))
        content.add_widget(Label(text=f"+{coins_earned} 🪙", font_size="20sp",
                                  color=SUCCESS, size_hint_y=0.2))

        buttons = BoxLayout(size_hint_y=0.35, spacing=10)
        replay_btn = RoundedButton("🔁 Rejouer", bg_color=PRIMARY,
                                    on_release=lambda *_: self._replay(popup))
        back_btn = RoundedButton("Carte des niveaux", bg_color=TEXT_MUTED,
                                  on_release=lambda *_: self._back_to_levels(popup))
        buttons.add_widget(replay_btn)
        buttons.add_widget(back_btn)
        content.add_widget(buttons)

        popup = Popup(title="Bravo !", content=content, size_hint=(0.85, 0.6),
                       auto_dismiss=False)
        popup.open()

    def _show_message(self, text):
        content = BoxLayout(orientation="vertical", padding=20, spacing=10)
        content.add_widget(Label(text=text, color=TEXT))
        popup = Popup(title="Info", content=content, size_hint=(0.7, 0.3))
        popup.open()
        Clock.schedule_once(lambda *_: popup.dismiss(), 1.5)

    def _replay(self, popup):
        popup.dismiss()
        self.start_level(self.level["id"])

    def _back_to_levels(self, popup):
        popup.dismiss()
        self.manager.current = "level_select"

    def _quit(self, *_args):
        if self._clock_event:
            self._clock_event.cancel()
        self.manager.current = "level_select"
