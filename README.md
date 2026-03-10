# DESCRIPTION DE MUSICMOOVE : une application sans contact pour la pratique musicale. Cette application permettra à l’élève de produire des sons ou des notes de musique par le mouvement, grâce à des zones interactives définies dans la partie configuration de l’application.En effet, le système doit pouvoir être paramétré par une musicothérapeute ou un professionnel accompagnant, afin de s’adapter au profil moteur du musicien afin de configurer correctement l’interface et mener à bien la session.


# BUT DU PROJET : Le projet vise donc à proposer un outil accessible, adaptable et intuitif permettant de favoriser l’expression musicale et de soutenir la participation à une activité artistique tout en personnalisant l’expérience selon les capacités de l’élève.

# FONCTIONNALITES : L'application MUSICMOOVE comporte plusieurs fonctionnalités. 

1) Configurer la session de musique -> 

a) Sélectionner la partie du corps qui peut être utilisée par l'élève musicien
b) Ajouter une ou plusieurs zones interactives et pouvoir les placer librement
c) Choisir la couleur de la zone interactive
d) Sélectionner un instrument de musique /à faire/
e) Sélectionner la note de musique jouée et son octave
f) Supprimer une ou des zone(s) interactive(s)

2) Visualiser sa configuration -> 

a) Déplacer la ou les zones interactives créées
b) Redimensionner la ou les zones créées

3) Lancer la session de musique -> 

a) En appuyant sur le bouton Démarrer, la session se lance et l'affichage laisse place au retour caméra avec les zones interactives sans la partie de configuration

4) Modification de paramètres ->

a) En appuyant sur le bouton Configuration de la partie musique de l’application, il est possible de revenir au mode configuration et changer des paramètres comme une couleur de zone intéractive, sa position, son dimensionnement ou encore le son émis par cette zone.

5) Jouer de la musique -> 

a) Déplacer la partie/les parties de son corps au niveau des zones interactives pour produire un son

6) Enregistrement de la configuration -> 

a) Enregistrer une configuration associée à un élève

# Installation : Commandes à executer pour pouvoir lancer le projet correctement / A REVOIR /

**Terminal à utiliser :** cmd (ça ne marche pas avec powershell)
**Vérifier que vous avez pip à jour :** (python -m pip install --upgrade pip --disable-pip-version-check)
**Version de python à utiliser :** 3.10 (installable en copiant cette commande dans un terminal: winget install --id Python.Python.3.10 --source winget)
**Version de mediapipe à utiliser :** 0.10.14 (pip install mediapipe==0.10.14)
**Librairies à installer :** opencv-python, PyQt6, pygame et numpy (pip install opencv-python PyQt6 pygame numpy)

# UTILISATION :

1) Ouvrir l’application.
2) L’application se lance avec à droite la barre de configuration et au centre la visualisation avec le retour caméra où apparaitront les zones interactives 
3) La/le musicothérapeute peut sélectionner une partie du corps sur le pannel configuration afin d'activer le bon mode de détection par MediaPipe
4) La/le musicothérapeute peut configurer une zone interactive en choisissant sa couleur, l’instrument et la note de musique en cliquant sur les boutons : Couleur, Note, Octave et Ajouter Carré
4) La/le musicothérapeute peut placer la zone interactive à un endroit sur l’écran et le déplacer et/ou le redimensionner en sélectionnant un des 4 points verts sur le carré. Pour le déplacer il suffit de le drag-and-drop, et pour supprimer la zone on peut cliquer sur la croix rouge
5) La/le musicothérapeute peut sélectionner plusieurs instruments de musique sur la zone de visualisation. C'est la forme des zones interactives qui varient selon l'instrument sélectionné. Tout comme la couleur des zones change selon la note jouée.
6) La/le musicothérapeute peut appuyer sur le bouton Démarrer : La fenêtre de configuration disparaît et le retour caméra s'agrandit avec les formes ajoutées pendant la configuration. 
7) Quand l'élève vient poser la partie du corps dans la forme configurée, le PC émet le son correspondant à la forme et à la couleur en question. 
8) La/le musicothérapeute peut appuyer sur le bouton Configuration : la fenêtre de configuration apparaît de nouveau. Maintenant, on peut réaliser des modifications en déplaçant les formes, en les ajoutant ou en les supprimant.

// A COMPLETER AVEC FONCTIONNALITES OPTIONNELLES 

# STRUCTURE DU PROJET 

PFEMUSIQUE
> src
    > core
        > audio.py
        > engine.py
        > models.py

    > data
        > configs.json

    > tests
        > test_main_window.py

    > ui
        > main_window.py
        > widgets.py

    > main

# LIBRAIRIES UTILISEES 

PyQt6: bibliothèque permettant de créer des interfaces graphiques 

OpenCV: bibliothèque spécialisée dans le traitement d’images et la vision par ordinateur

MIDI: protocole de communication utilisé en musique pour transmettre des informations musicales

MEDIAPIPE : bibliothèque permettant de détecter les positions des différentes parties du corps

