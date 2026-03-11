# MUSIC-MOVE (HandiMusique)

Une application de musicothérapie basée sur les gestes utilisant la reconnaissance de posture et des zones audio interactives.

## Exigences d'Installation

**Terminal à utiliser :** cmd (ne fonctionne pas avec powershell)

**Configuration Python :**
- **Version :** Python 3.10 (installer avec : `winget install --id Python.Python.3.10 --source winget`)
- **Mise à jour Pip :** `python -m pip install --upgrade pip --disable-pip-version-check`

**Bibliothèques Requises :**
```bash
pip install opencv-python PyQt6 pygame numpy mediapipe==0.10.14
```

## Démarrage Rapide

1. **Premier Lancement**: L'application affiche un dialogue de connexion
2. **Créer un Profil**: Cliquez sur "Créer Profil" et entrez vos identifiants musicothérapeute
3. **Connexion**: Entrez votre nom d'utilisateur et votre mot de passe
4. **Gérer les Élèves**: Cliquez sur "📋 Gérer Profils" pour ajouter des profils d'élèves
5. **Créer des Configurations**: Concevez des zones musicales interactives pour les séances de thérapie
6. **Démarrer la Séance**: Cliquez sur "▶ Démarrer la séance" pour commencer

## Documentation

### Pour les Utilisateurs
- **[AUTHENTICATION_GUIDE.md](AUTHENTICATION_GUIDE.md)** - Guide complet du système de connexion et de profil
- **[PROFILE_LINKING_VISUAL_GUIDE.md](PROFILE_LINKING_VISUAL_GUIDE.md)** - Diagrammes visuels de la liaison des profils et configurations

### Pour les Développeurs
- **[PROFILE_LINKING_IMPLEMENTATION.md](PROFILE_LINKING_IMPLEMENTATION.md)** - Détails techniques de l'implémentation

## Fonctionnalités Clés

### Système d'Authentification
- Connexion musicothérapeute avec protection par mot de passe (hachage SHA256)
- Création de profil sécurisée avec validation
- Fonctionnalité facultative "Rester connecté"

### Gestion des Profils
- **Profils Musicothérapeute**: Accédez à toutes les séances et configurations des élèves
- **Profils Étudiants**: Espaces de séances de thérapie individuels avec configurations personnalisées
- **Liaison des Configurations**: Chaque configuration est strictement liée à un profil d'élève

### Agrégation des Configurations
Lors de la visualisation de votre profil musicothérapeute, le système automatiquement :
- Collecte toutes les configurations de tous vos élèves
- Les affiche dans une liste "Partitions Enregistrées" unifiée
- Vous permet d'examiner le travail des élèves dans votre caseload

Lors de la visualisation d'un profil d'élève spécifique :
- Seules les configurations de cet élève sont affichées
- Empêche le mélange accidentel des données de séance
- Assure la confidentialité et l'organisation

### Fonctionnalités Musicales et Gestuelles
- Suivi de posture en temps réel via MediaPipe
- "Zones chaudes" interactives pour la génération de son
- Support d'instruments MIDI (Piano, Guitare, Violon, etc.)
- Support de fichiers sons personnalisés
- Plusieurs modes de suivi corporel (mains, membres supérieurs, visage, corps complet)

## Architecture du Système

```
Connexion Musicothérapeute
    ↓
Accès au Profil Musicothérapeute (afficher tout le travail des élèves)
    ↓
    ├─ Passer à Élève 1 (afficher seulement les configs d'Élève 1)
    ├─ Passer à Élève 2 (afficher seulement les configs d'Élève 2)
    └─ Créer un nouveau profil d'élève
```

Toutes les configurations sont strictement liées aux profils des élèves et ne peuvent pas exister indépendamment.

## Structure du Projet

```
src/
├── core/
│   ├── user_manager.py          # Logique de profil et authentification
│   ├── audio.py                 # Gestion MIDI et audio
│   ├── engine.py                # Détection de posture MediaPipe
│   ├── models.py                # Définitions des carrés interactifs
│   └── __pycache__/
├── data/
│   ├── users.json               # Profils musicothérapeute et élève stockés
│   └── configs.json             # Configurations de séance stockées
├── ui/
│   ├── login_dialog.py          # Interface de connexion et création de profil
│   ├── student_management.py    # Interface de gestion des profils d'élèves
│   ├── main_window.py           # Fenêtre principale de l'application
│   ├── widgets.py               # Composants UI personnalisés
│   └── __pycache__/
└── main                         # Point d'entrée de l'application
```

## Structure des Données de Configuration

Les configurations sont strictement liées aux profils d'élèves :

```json
{
  "Nom de Séance": {
    "name": "Nom de Séance",
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
    "musicotherapist_id": "nom_utilisateur",
    "student_id": "id_eleve",
    "profile_type": "student"
  }
}
```

## Notes Importantes

- Chaque profil d'élève est définitivement lié au musicothérapeute qui l'a créé
- Les configurations ne peuvent pas exister sans être liées à un profil d'élève
- Le système maintient la compatibilité avec les formats de configuration plus anciens
- Tous les mots de passe sont hachés et ne sont jamais stockés en texte brut

## Dépannage

**Le dialogue de connexion n'apparaît pas ?**
- Assurez-vous que l'application a été démarrée depuis le bon répertoire
- Vérifiez que le dossier data/ a les permissions d'écriture

**Les configurations ne s'enregistrent pas ?**
- Vérifiez que le répertoire src/data/ existe et est accessible en écriture
- Vérifiez que vous êtes connecté en tant que musicothérapeute

**Erreurs MediaPipe ?**
- Assurez-vous que mediapipe==0.10.14 est installé (version exacte requise)
- Vérifiez que votre webcam est connectée et fonctionne
- Essayez de mettre à jour : `pip install --upgrade mediapipe==0.10.14`

## Améliorations Futures

- Synchronisation cloud des profils et configurations
- Modèles de configuration pour une configuration rapide
- Partage de configurations entre musicothérapeutes
- Analyse de séance et suivi des progrès
- Capacité d'enregistrement de séance vidéo

---

Pour des informations techniques détaillées, consultez les fichiers de documentation listé ci-dessus.

```
