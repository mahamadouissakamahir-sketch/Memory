# 🃏 Memory — ton jeu de cartes

Un jeu de Memory complet, fait 100% en Python avec Kivy/KivyMD :
- Mode **Classique** avec **200 niveaux**, générés automatiquement (pas de niveaux tapés à la main un par un)
- **⭐ Système d'étoiles** (1 à 3) selon ton temps sur chaque niveau
- Mode **Survie** : un chrono qui descend, +3s par paire trouvée, -2s par erreur
- **💰 Économie** : tu gagnes des pièces en jouant, tu les dépenses dans la boutique
- **🎨 4 thèmes de cartes** à débloquer (Animaux, Fruits, Drapeaux, Espace)
- **💡 Indices** achetables (voir les cartes, temps bonus)
- **🔓 Mode spécial** débloquable (Chrono Inversé)

---

## 📁 Comment le projet est organisé

```
memory_game/
├── main.py                     → démarre l'application
├── buildozer.spec              → la "recette" pour transformer le code en APK
├── core/
│   ├── save_manager.py         → sauvegarde (pièces, étoiles, thèmes...)
│   ├── game_data.py            → LA LISTE des niveaux, thèmes, objets boutique
│   ├── board.py                → logique du plateau (mélange, comparaison de paires)
│   ├── card.py                 → le widget "carte" avec son animation
│   └── ui_kit.py                → couleurs et boutons stylés réutilisés partout
├── screens/
│   ├── menu_screen.py          → écran d'accueil
│   ├── level_select_screen.py  → carte des niveaux
│   ├── game_screen.py          → écran de jeu (mode Classique)
│   ├── survival_screen.py      → écran de jeu (mode Survie)
│   └── shop_screen.py          → boutique
└── .github/workflows/build.yml → dit à GitHub "compile ça en APK"
```

**Pour ajouter un niveau ou un thème plus tard**, tu n'as besoin de modifier
QUE `core/game_data.py` — tout le reste du jeu s'adapte automatiquement.

---

## 🚀 Obtenir le fichier .apk depuis ton téléphone (aucun ordinateur nécessaire)

Je ne peux pas générer le .apk moi-même (ça demande le SDK Android, plusieurs
Go de fichiers, que je n'ai pas ici). Par contre, **GitHub Actions** va le
faire gratuitement à ta place, dans le cloud. Voici toutes les étapes, en
détail.

### Étape 1 — Crée un compte GitHub

1. Ouvre ton navigateur (Chrome par exemple) et va sur **github.com**
2. Touche **Sign up** (S'inscrire), remplis email / mot de passe / nom d'utilisateur
3. Confirme ton compte via l'email qu'ils t'envoient

> GitHub, c'est juste un site qui stocke du code en ligne, gratuitement.

### Étape 2 — Crée un nouveau "repository" (dépôt = dossier de projet)

1. En haut à droite, touche le **+** puis **New repository**
2. Donne-lui un nom, par exemple `memory-game`
3. Laisse-le en **Public**
4. Touche **Create repository**

### Étape 3 — Crée chaque fichier du projet

C'est l'étape la plus longue, mais chaque action est simple et se répète.
Pour CHAQUE fichier listé dans "Comment le projet est organisé" ci-dessus :

1. Dans ton repository, touche **Add file** → **Create new file**
2. Dans le champ du nom de fichier, tape le **chemin complet**, par exemple :
   `core/save_manager.py`
   → Écrire `core/` avant le nom crée automatiquement le dossier `core`,
   tu n'as rien d'autre à faire pour créer les dossiers !
3. Colle le contenu du fichier (récupéré depuis l'archive que je t'ai donnée
   — ouvre-la avec ton gestionnaire de fichiers, ouvre chaque fichier `.py`
   avec une appli "éditeur de texte" pour voir/copier son contenu)
4. Descends tout en bas, touche **Commit changes...** puis confirme

Répète ça pour les **13 fichiers** :
`main.py`, `buildozer.spec`,
`core/__init__.py`, `core/save_manager.py`, `core/game_data.py`,
`core/board.py`, `core/card.py`, `core/ui_kit.py`,
`screens/__init__.py`, `screens/menu_screen.py`, `screens/level_select_screen.py`,
`screens/game_screen.py`, `screens/survival_screen.py`, `screens/shop_screen.py`,
et enfin `.github/workflows/build.yml`.

> 💡 Astuce : les fichiers `__init__.py` sont **vides**, tu n'as même pas
> besoin de coller de contenu, juste créer le fichier avec ce nom et valider.

### Étape 4 — Laisse GitHub compiler l'APK tout seul

Dès que tu as ajouté `.github/workflows/build.yml`, GitHub lance
**automatiquement** la compilation (c'est ce fichier qui lui dit quoi faire).

1. En haut de ton repository, touche l'onglet **Actions**
2. Tu vois une ligne avec un petit rond orange 🟠 (= en cours) — touche dessus
3. Attends... ça prend environ **10 à 20 minutes** la première fois (le temps
   que GitHub télécharge tout l'outillage Android). Tu peux fermer et revenir
   plus tard, ça continue de tourner sur leurs serveurs.
4. Quand le rond devient vert ✅, c'est terminé !
5. Sur cette même page, tout en bas, section **Artifacts**, touche
   **memory-apk** pour télécharger un fichier `.zip`

Si le rond devient rouge ❌ : touche dessus pour voir les logs (le journal
de ce qui s'est passé) et repère la ligne qui commence par "Error" — tu
peux me la copier-coller, je t'aiderai à corriger.

### Étape 5 — Installe le jeu sur ton téléphone

1. Ouvre le fichier `.zip` téléchargé (ton gestionnaire de fichiers sait
   l'ouvrir, ou installe l'appli gratuite **ZArchiver** si besoin)
2. Extrais-en le fichier `.apk`
3. Touche le fichier `.apk` pour l'installer
4. Android va probablement te dire "Source inconnue bloquée" → touche
   **Paramètres**, puis autorise l'installation depuis cette appli
   (Chrome ou ton gestionnaire de fichiers) — c'est normal, ça arrive
   pour toute app qui ne vient pas du Play Store
5. Installe, ouvre, et joue à ton jeu ! 🎉

---

## 🔁 Pour mettre à jour le jeu plus tard

Tu n'as pas besoin de tout refaire :

1. Va sur ton fichier sur GitHub (ex: `core/game_data.py`)
2. Touche le **crayon ✏️** en haut à droite pour l'éditer directement dans
   le navigateur
3. Modifie, puis **Commit changes**
4. GitHub relance automatiquement la compilation → un nouvel APK t'attend
   dans l'onglet Actions quelques minutes après

---

## 🔢 Comment fonctionnent les 200 niveaux

Au lieu d'écrire 200 lignes à la main (illisible et impossible à ajuster),
`core/game_data.py` CALCULE chaque niveau à partir de son numéro :
- Niveaux 1 à 8 : la grille grandit petit à petit (tutoriel), réglée à la main
- Niveaux 9 à 200 : la grille reste à sa taille max (6x6, la plus grande
  jouable sur un écran de téléphone), mais il faut aller de plus en plus
  vite pour décrocher 3 étoiles

Pour changer le nombre total de niveaux, modifie juste la ligne
`TOTAL_LEVELS = 200` dans `core/game_data.py`.

## 🛠️ Idées pour la suite

- Ajouter d'autres niveaux dans `LEVELS` (fichier `core/game_data.py`)
- Ajouter un nouveau thème dans `THEMES` (il faut au moins 18 emojis)
- Implémenter complètement le mode "Chrono Inversé" une fois débloqué
- Ajouter une icône personnalisée (`icon.filename` dans `buildozer.spec`)
- Ajouter des sons (un petit "ding" quand on trouve une paire)

Dis-moi quand tu veux qu'on avance sur l'une de ces idées !
