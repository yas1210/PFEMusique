from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QCheckBox, QFrame, QWidget, QFormLayout
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, pyqtSignal


class LoginDialog(QDialog):
    """Dialogue de connexion pour les musicothérapeutes."""

    login_successful = pyqtSignal()  # Émis lors d'une connexion réussie

    def __init__(self, user_manager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.setWindowTitle("MUSIC-MOVE - Connexion")
        self.setFixedSize(500, 420)
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        """Initialiser l'interface utilisateur."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(25, 20, 25, 20)

        # Titre
        title = QLabel("MUSIC-MOVE")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Application de Musicothérapie")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_font = QFont()
        subtitle_font.setPointSize(10)
        subtitle.setFont(subtitle_font)
        layout.addWidget(subtitle)

        # Séparateur
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(separator)

        # Formulaire
        form_layout = QFormLayout()
        form_layout.setSpacing(8)
        form_layout.setContentsMargins(0, 0, 0, 0)

        # Nom d'utilisateur
        username_label = QLabel("Nom d'utilisateur :")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Entrez votre nom d'utilisateur")
        self.username_input.setMinimumHeight(35)
        form_layout.addRow(username_label, self.username_input)

        # Mot de passe
        password_label = QLabel("Mot de passe :")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Entrez votre mot de passe")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(35)
        form_layout.addRow(password_label, self.password_input)

        layout.addLayout(form_layout)

        # Case à cocher pour rester connecté
        self.stay_logged_in = QCheckBox("Rester connecté sur cet ordinateur")
        self.stay_logged_in.setStyleSheet("margin: 5px 0px;")
        layout.addWidget(self.stay_logged_in)

        # Étiquette message d'erreur
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: red; margin: 5px 0px;")
        self.error_label.setWordWrap(True)
        self.error_label.setMinimumHeight(30)
        layout.addWidget(self.error_label)

        # Mise en page des boutons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.login_btn = QPushButton("Connexion")
        self.login_btn.setFixedHeight(38)
        self.login_btn.setMinimumWidth(120)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #2E7D32;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                font-size: 13px;
                border: none;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
            QPushButton:pressed {
                background-color: #1B5E20;
            }
        """)
        self.login_btn.clicked.connect(self.essayer_connexion)
        buttons_layout.addWidget(self.login_btn)

        # Lien créer profil
        create_profile_link = QLabel('<a href="#">Créer un profil</a>')
        create_profile_link.setStyleSheet("color: #2E7D32; margin-left: 10px;")
        create_profile_link.linkActivated.connect(self.ouvrir_dialogue_creer_profil)

        buttons_layout.addWidget(create_profile_link)
        buttons_layout.addStretch()

        layout.addLayout(buttons_layout)
        layout.addStretch()

        # Connecter la touche Entrée à la connexion
        self.password_input.returnPressed.connect(self.essayer_connexion)

    def essayer_connexion(self):
        """Essayer de se connecter avec les identifiants saisis."""
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            self.error_label.setText("Veuillez entrer le nom d'utilisateur et le mot de passe")
            return

        success, message = self.user_manager.authenticate_musicotherapist(username, password)

        if success:
            self.error_label.setText("")
            
            # TODO: Stocker la préférence "rester connecté" si nécessaire
            if self.stay_logged_in.isChecked():
                # Pourrait implémenter la connexion persistante ici
                pass
            
            self.login_successful.emit()
            self.accept()
        else:
            self.error_label.setText(message)

    def ouvrir_dialogue_creer_profil(self):
        """Ouvrir le dialogue de création de profil."""
        dialog = CreateProfileDialog(self.user_manager, self)
        dialog.profile_created.connect(self.sur_profil_cree)
        dialog.exec()

    def sur_profil_cree(self):
        """Gérer la création réussie d'un profil."""
        self.error_label.setText("Profil créé ! Veuillez vous connecter.")
        self.error_label.setStyleSheet("color: green;")
        self.username_input.clear()
        self.password_input.clear()


class CreateProfileDialog(QDialog):
    """Dialogue pour créer un nouveau profil de musicothérapeute."""

    profile_created = pyqtSignal()  # Émis lors de la création d'un profil

    def __init__(self, user_manager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.setWindowTitle("Créer Profil Musicothérapeute")
        self.setFixedSize(500, 480)
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        """Initialiser l'interface utilisateur."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(25, 20, 25, 20)

        # Titre
        title = QLabel("Créer un Nouveau Profil")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Formulaire
        form_layout = QFormLayout()
        form_layout.setSpacing(8)
        form_layout.setContentsMargins(0, 0, 0, 0)

        # Nom complet
        name_label = QLabel("Nom complet :")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Votre nom complet")
        self.name_input.setMinimumHeight(35)
        form_layout.addRow(name_label, self.name_input)

        # Nom d'utilisateur
        username_label = QLabel("Nom d'utilisateur :")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Choisissez un nom d'utilisateur")
        self.username_input.setMinimumHeight(35)
        form_layout.addRow(username_label, self.username_input)

        # Mot de passe
        password_label = QLabel("Mot de passe :")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Au moins 4 caractères")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(35)
        form_layout.addRow(password_label, self.password_input)

        # Confirmer mot de passe
        confirm_label = QLabel("Confirmer mot de passe :")
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Confirmez votre mot de passe")
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.setMinimumHeight(35)
        form_layout.addRow(confirm_label, self.confirm_input)

        layout.addLayout(form_layout)

        # Étiquette message d'erreur
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: red; margin: 5px 0px;")
        self.error_label.setWordWrap(True)
        self.error_label.setMinimumHeight(30)
        layout.addWidget(self.error_label)

        # Boutons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.create_btn = QPushButton("Créer Profil")
        self.create_btn.setFixedHeight(38)
        self.create_btn.setMinimumWidth(120)
        self.create_btn.setStyleSheet("""
            QPushButton {
                background-color: #2E7D32;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                font-size: 13px;
                border: none;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
            QPushButton:pressed {
                background-color: #1B5E20;
            }
        """)
        self.create_btn.clicked.connect(self.creer_profil)
        buttons_layout.addWidget(self.create_btn)

        cancel_btn = QPushButton("Annuler")
        cancel_btn.setFixedHeight(38)
        cancel_btn.setMinimumWidth(120)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #888;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                font-size: 13px;
                border: none;
            }
            QPushButton:hover {
                background-color: #999;
            }
            QPushButton:pressed {
                background-color: #666;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        buttons_layout.addStretch()

        layout.addLayout(buttons_layout)
        layout.addStretch()

    def creer_profil(self):
        """Créer un nouveau profil."""
        full_name = self.name_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_input.text()

        if not all([full_name, username, password, confirm_password]):
            self.error_label.setText("Tous les champs sont requis")
            return

        if password != confirm_password:
            self.error_label.setText("Les mots de passe ne correspondent pas")
            return

        success, message = self.user_manager.create_musicotherapist_profile(
            username, password, full_name
        )

        if success:
            self.error_label.setText("")
            self.profile_created.emit()
            self.accept()
        else:
            self.error_label.setText(message)
