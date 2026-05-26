PROJET MUSIC-MOVE 


lMUSIC-MOVE est une application permettant la pratique musicale sans contact. Cette application permettra à l’élève de produire des sons ou des notes de musique en réalisant des gestes dans des zones interactives, définies dans la partie configuration de l’application. En effet, le système doit pouvoir être paramétré par une musicothérapeute, afin de s’adapter au profil moteur du musicien afin de configurer correctement l’interface et mener à bien la session.

Elle permet de produire de la musique par le mouvement du corps, grâce à une détection en temps réel (MediaPipe: framework open source développé par Google).


CONCEPT DU PROJET


MUSIC-MOVE est un outil conçu pour rendre la pratique musicale accessible aux personnes en situation de handicap ou ayant des limitations motrices. L’application permet à un musicothérapeute de configurer une séance personnalisée afin d’adapter l’interface aux capacités de l’élève. Chaque mouvement détecté dans certaines zones de l’écran déclenche un son ou une note de musique.


OBJECTIFS DE L'APPLICATION


Favoriser l’expression musicale par le mouvement
Adapter l’interface aux capacités motrices de chaque utilisateur
Proposer un outil intuitif pour la musicothérapie
Permettre un suivi personnalisé des élèves
Offrir une expérience interactive 



FONCTIONNALITES PRINCIPALES

- Configuration de la session

Sélectionner la partie du corps utilisée par l’élève pour générer du son
Ajouter une ou plusieurs zones interactives et les placer librement sur l’interface
Choisir la couleur de chaque zone interactive
Sélectionner un instrument de musique
Associer une note de musique et son octave à chaque zone
Supprimer une ou plusieurs zones interactives



- Visualisation de la configuration


Déplacer les zones interactives créées
Redimensionner les zones interactives


- Lancement de la session


Démarrer la session via un bouton dédié
Passage en mode “caméra” avec affichage des zones interactives
Masquage automatique de la barre de configuration


- Modification de la configuration

Retour au mode configuration via un bouton dédié
Modification des paramètres des zones :
couleur
position
taille
son / note associée


- Interaction musicale 


Déplacement d’une partie du corps dans une zone interactive pour déclencher un son
Possibilité de jouer un accord avec une partie du corps
Génération sonore en temps réel selon la position du corps


FONCTIONNALITES OPTIONNELLES 

- Enregistrement et gestion des configurations


Connexion et déconnexion à une session utilisateur
Création et gestion de profils élèves
Enregistrement d’une configuration associée à un élève
Chargement et récupération de configurations existantes


- Chargement de sons personnalisés


Import de fichiers audio dans l’application
Association d’un son personnalisé à une zone interactive


- Modification avancée des zones interactives


Modification des paramètres d’une zone existante
Réutilisation et adaptation de configurations précédentes


- Suivi de l’évolution de l’élève


Monitoring de la durée des sessions
Analyse de l’évolution des capacités motrices (degrés de liberté des mouvements)



ARCHITECTURE DU PROJET 

src/
├── core/
│   ├── user_manager.py      # Gestion des utilisateurs
│   ├── audio.py             # Gestion du son / MIDI
│   ├── engine.py            # Détection MediaPipe
│   ├── models.py            # Zones interactives
│
├── data/
│   ├── users.json           # Profils utilisateurs
│   ├── configs.json         # Configurations des séances
│
├── ui/
│   ├── login_dialog.py         # Interface connexion / création de compte
│   ├── student_management.py   # Interface gestion des élèves
│   ├── main_window.py          # Interface de paramétrage des zones interactives 
│   ├── widgets.py              # Composants UI
│
└── main.py                     # Lancement de l'application


INSTALLATION

Python 3.10
Terminal recommandé : CMD (Windows)

Installation Python
winget install --id Python.Python.3.10 --source winget

Mise à jour pip
python -m pip install --upgrade pip --disable-pip-version-check

Installation des dépendances
pip install opencv-python PyQt6 pygame numpy mediapipe==0.10.14

Lancement de l'application
python main.py


UTILISATION

Ouvrir l’application
Créer ou se connecter à un profil musicothérapeute
Gérer les profils élèves
Créer une configuration musicale :
Ajouter des zones interactives
Choisir notes, instruments et couleurs
Lancer la séance 
Interagir avec les zones via les mouvements du corps
Revenir en mode configuration si nécessaire


STRUCTURE DES DONNEES

Exemple de configuration :

{
  "Nom de séance": {
    "name": "Nom de séance",
    "data": [
      {
        "x": 100,
        "y": 150,
        "w": 200,
        "h": 100,
        "note": 60,
        "color": [255, 100, 50],
        "instrument": "Piano",
        "program": 0,
        "custom_sound": null
      }
    ],
    "musicotherapist_id": "user123",
    "student_id": "student456",
    "profile_type": "student"
  }
}

NB: 
Chaque profil d'élève est définitivement lié au musicothérapeute qui l'a créé
Les configurations ne peuvent pas exister sans être liées à un profil d'élève
Le système maintient la compatibilité avec les formats de configuration plus anciens
Tous les mots de passe sont hachés et ne sont jamais stockés en texte brut


AMELIORATIONS FUTURES

Synchronisation cloud
Analyse des performances des élèves
Enregistrement vidéo des séances
Partage de configurations
Templates de séances
IA d’adaptation automatique des zones


TECHNOLOGIES UTILISEES 

Python

PyQt6 : Interface graphique
OpenCV : Vision par ordinateur
pygame : Audio
MIDI : Communication musicale
NumPy : Calculs

MediaPipe : Détection de posture

AUTEURS

Projet réalisé par Anthony SALIBA, Yasmine ELJRAIDI, Constance GUTIERREZ, Hamado NIKIEMA, élèves TIS5, dans le cadre de notre projet de Fin d'étude. 