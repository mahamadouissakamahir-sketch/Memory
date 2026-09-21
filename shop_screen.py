"""
shop_screen.py
---------------
La boutique : le joueur y dépense les pièces gagnées en jouant.
Trois catégories :
1. Thèmes de cartes (change le visuel des emojis dans toutes les parties)
2. Indices (achetés à l'unité, utilisés pendant une partie)
3. Modes spéciaux (débloqués une fois pour toutes)
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout

from core.ui_kit import RoundedButton, PRIMARY, ACCENT, SUCCESS, TEXT_MUTED, TEXT
from core.game_data import THEMES, SHOP_HINTS, SHOP_MODES


class ShopScreen(Screen):
    def __init__(self, save_manager, **kwargs):
        super().__init__(**kwargs)
        self.save_manager = save_manager
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", padding=20, spacing=10)

        header = BoxLayout(size_hint_y=None, height=50)
        back_btn = RoundedButton("← Retour", on_release=self._go_back, bg_color=TEXT_MUTED,
                                  size_hint_x=0.5)
        self.coins_label = Label(text="🪙 0", font_size="18sp", color=ACCENT)
        header.add_widget(back_btn)
        header.add_widget(self.coins_label)
        root.add_widget(header)

        scroll = ScrollView()
        self.content_grid = GridLayout(cols=1, spacing=14, size_hint_y=None, padding=(0, 10))
        self.content_grid.bind(minimum_height=self.content_grid.setter("height"))
        scroll.add_widget(self.content_grid)
        root.add_widget(scroll)

        self.add_widget(root)

    def on_pre_enter(self, *_args):
        self._refresh()

    def _refresh(self):
        self.coins_label.text = f"🪙 {self.save_manager.coins}"
        self.content_grid.clear_widgets()

        self.content_grid.add_widget(Label(text="🎨 Thèmes de cartes", font_size="18sp",
                                            color=TEXT, bold=True, size_hint_y=None, height=36))
        for theme_id, theme in THEMES.items():
            self.content_grid.add_widget(self._build_theme_row(theme_id, theme))

        self.content_grid.add_widget(Label(text="💡 Indices", font_size="18sp",
                                            color=TEXT, bold=True, size_hint_y=None, height=36))
        for hint_id, hint in SHOP_HINTS.items():
            self.content_grid.add_widget(self._build_info_row(hint["name"], hint["desc"],
                                                                hint["price"]))

        self.content_grid.add_widget(Label(text="🔓 Modes spéciaux", font_size="18sp",
                                            color=TEXT, bold=True, size_hint_y=None, height=36))
        for mode_id, mode in SHOP_MODES.items():
            self.content_grid.add_widget(self._build_mode_row(mode_id, mode))

    def _build_theme_row(self, theme_id, theme):
        row = BoxLayout(size_hint_y=None, height=64, spacing=10)
        is_unlocked = self.save_manager.is_theme_unlocked(theme_id)
        is_active = self.save_manager.data.get("current_theme") == theme_id
        preview = " ".join(theme["emojis"][:4])
        label = Label(text=f"{theme['name']}\n{preview}", color=TEXT, font_size="14sp")
        row.add_widget(label)

        if is_active:
            btn = RoundedButton("✓ Actif", bg_color=SUCCESS, size_hint_x=0.35)
            btn.set_disabled(True)
        elif is_unlocked:
            btn = RoundedButton("Choisir", bg_color=PRIMARY, size_hint_x=0.35,
                                 on_release=self._make_theme_selector(theme_id))
        else:
            btn = RoundedButton(f"🪙 {theme['price']}", bg_color=ACCENT, size_hint_x=0.35,
                                 on_release=self._make_theme_buyer(theme_id, theme["price"]))
        row.add_widget(btn)
        return row

    def _build_info_row(self, name, desc, price):
        row = BoxLayout(size_hint_y=None, height=64, spacing=10)
        label = Label(text=f"{name}\n{desc}", color=TEXT_MUTED, font_size="12sp")
        row.add_widget(label)
        tag = Label(text=f"🪙 {price}\n(utilisable en jeu)", color=ACCENT, font_size="12sp",
                    size_hint_x=0.4)
        row.add_widget(tag)
        return row

    def _build_mode_row(self, mode_id, mode):
        row = BoxLayout(size_hint_y=None, height=64, spacing=10)
        is_unlocked = self.save_manager.is_mode_unlocked(mode_id)
        label = Label(text=f"{mode['name']}\n{mode['desc']}", color=TEXT, font_size="12sp")
        row.add_widget(label)
        if is_unlocked:
            btn = RoundedButton("✓ Débloqué", bg_color=SUCCESS, size_hint_x=0.35)
            btn.set_disabled(True)
        else:
            btn = RoundedButton(f"🪙 {mode['price']}", bg_color=ACCENT, size_hint_x=0.35,
                                 on_release=self._make_mode_buyer(mode_id, mode["price"]))
        row.add_widget(btn)
        return row

    def _make_theme_selector(self, theme_id):
        def _select(*_args):
            self.save_manager.set_current_theme(theme_id)
            self._refresh()
        return _select

    def _make_theme_buyer(self, theme_id, price):
        def _buy(*_args):
            if self.save_manager.spend_coins(price):
                self.save_manager.unlock_theme(theme_id)
                self.save_manager.set_current_theme(theme_id)
            self._refresh()
        return _buy

    def _make_mode_buyer(self, mode_id, price):
        def _buy(*_args):
            if self.save_manager.spend_coins(price):
                self.save_manager.unlock_mode(mode_id)
            self._refresh()
        return _buy

    def _go_back(self, *_args):
        self.manager.current = "menu"
