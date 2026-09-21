"""
survival_screen.py
-------------------
Le mode Survie : un chrono qui commence à 60 secondes et qui DESCEND.
- Trouver une paire -> +3 secondes
- Se tromper -> -2 secondes
- Le chrono arrive à 0 -> partie finie, on affiche le score (nombre de
  paires trouvées au total) et on compare au record.

Dès qu'une grille est complètement terminée, une nouvelle grille apparaît
tout de suite (mélangée à nouveau) : la partie continue tant qu'il reste
du temps, donc en théorie ça peut durer très longtemps si le joueur est bon !
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.clock import Clock

from core.ui_kit import RoundedButton, PRIMARY, ACCENT, DANGER, TEXT_MUTED, TEXT, SUCCESS
from core.game_data import THEMES, SHOP_HINTS
from core.board import build_deck, BoardController
from core.card import Card

START_TIME = 60
TIME_BONUS_ON_MATCH = 3
TIME_PENALTY_ON_MISS = 2
GRID_COLS = 5
GRID_ROWS = 4  # 10 paires par grille


class SurvivalScreen(Screen):
    def __init__(self, save_manager, **kwargs):
        super().__init__(**kwargs)
        self.save_manager = save_manager
        self.time_left = START_TIME
        self.total_pairs_found = 0
        self.board = None
        self._clock_event = None
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", padding=14, spacing=10)

        top_bar = BoxLayout(size_hint_y=None, height=50, spacing=10)
        quit_btn = RoundedButton("✕", on_release=self._quit, bg_color=TEXT_MUTED,
                                  size_hint_x=0.15)
        self.timer_label = Label(text="⏱️ 60", font_size="22sp", color=DANGER, size_hint_x=0.35)
        self.score_label = Label(text="Paires: 0", font_size="16sp", color=TEXT_MUTED,
                                  size_hint_x=0.3)
        self.hint_btn = RoundedButton("💡+10s", on_release=self._use_time_hint, bg_color=ACCENT,
                                       size_hint_x=0.2)
        top_bar.add_widget(quit_btn)
        top_bar.add_widget(self.timer_label)
        top_bar.add_widget(self.score_label)
        top_bar.add_widget(self.hint_btn)
        root.add_widget(top_bar)

        self.board_grid = GridLayout(cols=GRID_COLS, spacing=6)
        root.add_widget(self.board_grid)

        self.add_widget(root)

    def on_pre_enter(self, *_args):
        self._start_run()

    def _start_run(self):
        self.time_left = START_TIME
        self.total_pairs_found = 0
        self.timer_label.text = f"⏱️ {self.time_left}"
        self.score_label.text = "Paires: 0"
        self._new_grid()
        if self._clock_event:
            self._clock_event.cancel()
        self._clock_event = Clock.schedule_interval(self._tick, 1.0)

    def _new_grid(self):
        theme_id = self.save_manager.data.get("current_theme", "animaux")
        emoji_pool = THEMES.get(theme_id, THEMES["animaux"])["emojis"]
        pairs = (GRID_COLS * GRID_ROWS) // 2
        deck = build_deck(pairs, emoji_pool)

        self.board_grid.clear_widgets()
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
            on_complete=self._on_grid_complete,
        )

    def _tick(self, _dt):
        self.time_left -= 1
        self.timer_label.text = f"⏱️ {max(self.time_left, 0)}"
        if self.time_left <= 0:
            self._end_run()

    def _on_card_tap(self, card):
        if self.time_left <= 0:
            return
        self.board.on_card_selected(card)

    def _on_match(self, _card1, _card2):
        self.time_left += TIME_BONUS_ON_MATCH
        self.total_pairs_found += 1
        self.timer_label.text = f"⏱️ {self.time_left}"
        self.score_label.text = f"Paires: {self.total_pairs_found}"

    def _on_mismatch(self, card1, card2):
        self.time_left = max(0, self.time_left - TIME_PENALTY_ON_MISS)
        self.timer_label.text = f"⏱️ {self.time_left}"

        def _hide(_dt):
            card1.flip_down()
            card2.flip_down()
            self.board.locked = False
            if self.time_left <= 0:
                self._end_run()
        Clock.schedule_once(_hide, 0.7)

    def _on_grid_complete(self):
        if self.time_left > 0:
            Clock.schedule_once(lambda *_: self._new_grid(), 0.3)

    def _use_time_hint(self, *_args):
        price = SHOP_HINTS["time_boost"]["price"]
        if not self.save_manager.spend_coins(price):
            self._show_message("Pas assez de pièces 🪙")
            return
        self.time_left += 10
        self.timer_label.text = f"⏱️ {self.time_left}"

    def _end_run(self):
        if self._clock_event:
            self._clock_event.cancel()
        is_new_record = self.save_manager.update_survival_score(self.total_pairs_found)
        self._show_result_popup(is_new_record)

    def _show_result_popup(self, is_new_record):
        content = BoxLayout(orientation="vertical", spacing=14, padding=20)
        title = "🏆 Nouveau record !" if is_new_record else "Temps écoulé"
        content.add_widget(Label(text=title, font_size="22sp", color=ACCENT, size_hint_y=0.25))
        content.add_widget(Label(text=f"Paires trouvées : {self.total_pairs_found}",
                                  font_size="18sp", color=TEXT, size_hint_y=0.25))
        content.add_widget(Label(text=f"Record : {self.save_manager.data['survival_high_score']}",
                                  font_size="14sp", color=TEXT_MUTED, size_hint_y=0.2))

        buttons = BoxLayout(size_hint_y=0.3, spacing=10)
        retry_btn = RoundedButton("🔁 Rejouer", bg_color=PRIMARY,
                                   on_release=lambda *_: self._retry(popup))
        back_btn = RoundedButton("Menu", bg_color=TEXT_MUTED,
                                  on_release=lambda *_: self._back_to_menu(popup))
        buttons.add_widget(retry_btn)
        buttons.add_widget(back_btn)
        content.add_widget(buttons)

        popup = Popup(title="Fin de partie", content=content, size_hint=(0.85, 0.6),
                       auto_dismiss=False)
        popup.open()

    def _show_message(self, text):
        content = BoxLayout(orientation="vertical", padding=20, spacing=10)
        content.add_widget(Label(text=text, color=TEXT))
        popup = Popup(title="Info", content=content, size_hint=(0.7, 0.3))
        popup.open()
        Clock.schedule_once(lambda *_: popup.dismiss(), 1.5)

    def _retry(self, popup):
        popup.dismiss()
        self._start_run()

    def _back_to_menu(self, popup):
        popup.dismiss()
        self.manager.current = "menu"

    def _quit(self, *_args):
        if self._clock_event:
            self._clock_event.cancel()
        self.manager.current = "menu"
