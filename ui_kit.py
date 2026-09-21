"""
ui_kit.py
---------
Petite "boîte à outils" visuelle utilisée par tous les écrans, pour que
le jeu ait un style cohérent (mêmes couleurs, mêmes boutons) sans copier-
coller le même code partout.
"""

from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window

# Palette de couleurs (format RGBA, valeurs de 0 à 1)
BG_DARK = (0.08, 0.09, 0.13, 1)
SURFACE = (0.14, 0.16, 0.22, 1)
PRIMARY = (0.36, 0.55, 0.95, 1)
PRIMARY_DARK = (0.27, 0.42, 0.80, 1)
ACCENT = (0.95, 0.75, 0.20, 1)      # couleur "or" pour les pièces / étoiles
SUCCESS = (0.30, 0.78, 0.48, 1)
DANGER = (0.90, 0.35, 0.35, 1)
TEXT = (0.95, 0.96, 0.98, 1)
TEXT_MUTED = (0.65, 0.68, 0.75, 1)

Window.clearcolor = BG_DARK


class RoundedButton(BoxLayout):
    """
    Un bouton avec des coins arrondis et une couleur de fond personnalisée.
    Kivy ne propose pas ça nativement avec un simple Button (les Button
    standards sont rectangulaires avec un thème système), donc on dessine
    nous-mêmes un rectangle arrondi derrière un Label cliquable.
    """

    def __init__(self, text, on_release=None, bg_color=PRIMARY, text_color=TEXT,
                 font_size="18sp", **kwargs):
        super().__init__(**kwargs)
        self._bg_color = bg_color
        self._btn = Button(
            text=text,
            font_size=font_size,
            color=text_color,
            background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0),  # on masque le fond par défaut de Kivy
        )
        self._on_release_callback = None
        if on_release:
            self.set_on_release(on_release)
        self.add_widget(self._btn)

        with self.canvas.before:
            Color(*bg_color)
            self._rect = RoundedRectangle(radius=[14], pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *_args):
        self._rect.pos = self.pos
        self._rect.size = self.size

    def set_text(self, text):
        self._btn.text = text

    def set_on_release(self, callback):
        """
        Change le callback appelé quand on tape sur le bouton, en retirant
        proprement l'ancien d'abord. Utile quand on RÉUTILISE le même bouton
        pour représenter des choses différentes au fil du temps (ex: la
        pagination des niveaux, où le bouton n°3 de la grille représente
        le niveau 43 sur une page puis le niveau 63 sur la page suivante).
        Passer callback=None désactive juste le bouton sans lui donner d'action.
        """
        if self._on_release_callback is not None:
            self._btn.unbind(on_release=self._on_release_callback)
        self._on_release_callback = callback
        if callback is not None:
            self._btn.bind(on_release=callback)

    def set_disabled(self, disabled):
        self._btn.disabled = disabled
        with self.canvas.before:
            self.canvas.before.clear()
            Color(*(TEXT_MUTED if disabled else self._bg_color))
            self._rect = RoundedRectangle(radius=[14], pos=self.pos, size=self.size)


def section_title(text, size="22sp"):
    return Label(text=text, font_size=size, color=TEXT, bold=True, size_hint_y=None, height=48)


def muted_label(text, size="14sp"):
    return Label(text=text, font_size=size, color=TEXT_MUTED, size_hint_y=None, height=30)
