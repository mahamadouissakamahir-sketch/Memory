[app]

# --- Informations de base sur l'app ---
title = Memory
package.name = memorygame
package.domain = org.claudeetmoi

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

version = 1.0

# --- Dépendances Python nécessaires pour que l'app tourne ---
requirements = python3,kivy

# --- Orientation et affichage ---
orientation = portrait
fullscreen = 0

# --- Icône (facultatif, tu pourras en ajouter une plus tard) ---
# icon.filename = %(source.dir)s/icon.png

# --- Permissions Android nécessaires ---
# Aucune permission spéciale : le jeu sauvegarde uniquement dans son propre
# dossier privé (user_data_dir), pas besoin d'accéder au stockage du téléphone.
android.permissions =

# --- Version minimale et cible d'Android ---
android.api = 33
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
