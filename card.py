"""
card.py
-------
Ce fichier définit le widget "Carte" : le petit rectangle qu'on tape pour
révéler un emoji, dans le jeu de Memory.

On part d'un Button Kivy (parce qu'un bouton gère déjà "je réagis quand
on tape dessus"), et on lui ajoute :
- un état (face cachée / face visible / déjà trouvée)
- une petite animation de "retournement" (on rétrécit en largeur, on change
  le texte affiché, puis on regrandit) pour que ça fasse un effet sympa,
  pas juste un texte qui apparaît d'un coup.
"""

from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.properties import BooleanProperty, StringProperty


HIDDEN_LABEL = "❓"


class Card(Button):
    # value = l'emoji caché derrière la carte (ex: "🐶")
    value = StringProperty("")
    # revealed = True si la carte est actuellement retournée (face visible)
    revealed = BooleanProperty(False)
    # matched = True si la paire a déjà été trouvée (la carte reste visible et désactivée)
    matched = BooleanProperty(False)

    def __init__(self, value, **kwargs):
        super().__init__(**kwargs)
        self.value = value
        self.text = HIDDEN_LABEL
        self.font_size = "28sp"
        self.background_normal = ""
        self.background_color = (0.20, 0.22, 0.30, 1)
        self.color = (1, 1, 1, 1)

    def flip_up(self, on_complete=None):
        """Anime le retournement de la carte pour montrer l'emoji."""
        if self.revealed or self.matched:
            return
        self.revealed = True

        def _switch_face(_anim, _widget):
            self.text = self.value
            self.background_color = (0.30, 0.55, 0.90, 1)

        anim = Animation(size_hint_x=0.02, duration=0.09)
        anim.bind(on_complete=_switch_face)
        anim += Animation(size_hint_x=self._base_size_hint_x, duration=0.09)
        if on_complete:
            anim.bind(on_complete=lambda *_: on_complete(self))
        self._base_size_hint_x = self.size_hint_x or 1
        anim.start(self)

    def flip_down(self):
        """Anime le retournement de la carte pour recacher l'emoji (mauvaise paire)."""
        if self.matched:
            return
        self.revealed = False

        def _switch_face(_anim, _widget):
            self.text = HIDDEN_LABEL
            self.background_color = (0.20, 0.22, 0.30, 1)

        base = self.size_hint_x or 1
        anim = Animation(size_hint_x=0.02, duration=0.09)
        anim.bind(on_complete=_switch_face)
        anim += Animation(size_hint_x=base, duration=0.09)
        anim.start(self)

    def set_matched(self):
        """La paire est trouvée : la carte reste face visible, avec une couleur de succès."""
        self.matched = True
        self.disabled = True
        self.text = self.value
        self.background_color = (0.25, 0.75, 0.45, 1)
