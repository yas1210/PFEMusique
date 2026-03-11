from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QComboBox, QCalendarWidget, QWidget,
    QFormLayout, QMessageBox
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from datetime import datetime


class StudentManagementDialog(QDialog):
    """Dialogue de gestion des profils étudiants."""

    profile_changed = pyqtSignal(str, str)  # profile_type, profile_id

    def __init__(self, user_manager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.setWindowTitle("Gestion des Profils Étudiants")
        self.setFixedSize(500, 450)
        self.setModal(True)
        self.init_ui()
        self.refresh_student_list()

    def init_ui(self):
        """Initialiser l'interface utilisateur."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # Titre
        title = QLabel("Profils Étudiants")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Profil actuel
        current_label = QLabel("Profil Actuel :")
        current_label.setStyleSheet("font-weight: bold;")
        self.current_profile_label = QLabel()
        self.current_profile_label.setStyleSheet("color: #2E7D32; padding: 5px;")
        layout.addWidget(current_label)
        layout.addWidget(self.current_profile_label)
        self.update_current_profile_label()

        # Bouton pour passer au profil général
        self.switch_general_btn = QPushButton("Utiliser le Profil Musicothérapeute")
        self.switch_general_btn.clicked.connect(self.switch_to_general)
        layout.addWidget(self.switch_general_btn)

        # Séparateur
        sep_label = QLabel("Ou sélectionner un élève :")
        sep_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(sep_label)

        # Student list
        self.student_list = QListWidget()
        self.student_list.itemClicked.connect(self.on_student_selected)
        layout.addWidget(self.student_list)

        # Boutons pour gérer les élèves
        button_layout = QHBoxLayout()

        self.add_student_btn = QPushButton("Ajouter Élève")
        self.add_student_btn.clicked.connect(self.open_add_student_dialog)
        button_layout.addWidget(self.add_student_btn)

        self.edit_student_btn = QPushButton("Éditer")
        self.edit_student_btn.clicked.connect(self.edit_selected_student)
        self.edit_student_btn.setEnabled(False)
        button_layout.addWidget(self.edit_student_btn)

        self.delete_student_btn = QPushButton("Supprimer")
        self.delete_student_btn.clicked.connect(self.delete_selected_student)
        self.delete_student_btn.setEnabled(False)
        button_layout.addWidget(self.delete_student_btn)

        layout.addLayout(button_layout)

        # Bouton fermer
        close_btn = QPushButton("Fermer")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def refresh_student_list(self):
        """Rafraîchir l'affichage de la liste des élèves."""
        self.student_list.clear()
        students = self.user_manager.get_current_musicotherapist_students()

        for student_id, student_data in students:
            first_name = student_data.get("first_name", "")
            last_name = student_data.get("last_name", "")
            dob = student_data.get("date_of_birth", "")
            
            display_text = f"{first_name} {last_name}"
            if dob:
                display_text += f" (DDN: {dob})"
            
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, student_id)
            self.student_list.addItem(item)

    def on_student_selected(self, item):
        """Handle student selection."""
        self.edit_student_btn.setEnabled(True)
        self.delete_student_btn.setEnabled(True)
        
        student_id = item.data(Qt.ItemDataRole.UserRole)
        success, _ = self.user_manager.switch_to_student_profile(student_id)
        
        if success:
            self.update_current_profile_label()
            self.profile_changed.emit("student", student_id)

    def switch_to_general(self):
        """Switch to general musicotherapist profile."""
        success, _ = self.user_manager.switch_to_musicotherapist_profile()
        
        if success:
            self.student_list.clearSelection()
            self.edit_student_btn.setEnabled(False)
            self.delete_student_btn.setEnabled(False)
            self.update_current_profile_label()
            self.profile_changed.emit("musicotherapist", "")

    def open_add_student_dialog(self):
        """Open dialog to add a new student."""
        dialog = AddStudentDialog(self.user_manager, self)
        dialog.student_added.connect(self.on_student_added)
        dialog.exec()

    def on_student_added(self):
        """Handle when a student is added."""
        self.refresh_student_list()

    def edit_selected_student(self):
        """Edit the selected student."""
        current_item = self.student_list.currentItem()
        if not current_item:
            return
        
        student_id = current_item.data(Qt.ItemDataRole.UserRole)
        students = dict(self.user_manager.get_current_musicotherapist_students())
        
        if student_id not in students:
            return
        
        student_data = students[student_id]
        
        dialog = EditStudentDialog(student_data, self)
        if dialog.exec():
            first_name, last_name, dob = dialog.get_data()
            # For now, we'll just show a message that editing isn't fully implemented
            # In a full implementation, you'd update the user_manager
            QMessageBox.information(self, "Edit Student", 
                                   "Student profile edit functionality can be extended later")

    def delete_selected_student(self):
        """Delete the selected student."""
        current_item = self.student_list.currentItem()
        if not current_item:
            return
        
        student_id = current_item.data(Qt.ItemDataRole.UserRole)
        display_text = current_item.text()
        
        reply = QMessageBox.question(
            self,
            "Delete Student",
            f"Are you sure you want to delete '{display_text}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.user_manager.delete_student_profile(student_id)
            if success:
                self.refresh_student_list()
                self.switch_to_general()  # Switch back to general profile
            else:
                QMessageBox.warning(self, "Error", message)

    def update_current_profile_label(self):
        """Mettre à jour l'étiquette du profil actuel."""
        profile_name = self.user_manager.get_current_profile_name()
        profile_type = self.user_manager.current_profile_type
        
        if profile_type == "musicotherapist":
            label = f"Musicothérapeute : {profile_name}"
        elif profile_type == "student":
            label = f"Élève : {profile_name}"
        else:
            label = "Aucun profil sélectionné"
        
        self.current_profile_label.setText(label)


class AddStudentDialog(QDialog):
    """Dialogue pour ajouter un nouvel élève."""

    student_added = pyqtSignal()

    def __init__(self, user_manager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.setWindowTitle("Ajouter Profil Élève")
        self.setFixedSize(400, 350)
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        """Initialiser l'interface utilisateur."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # Formulaire
        form_layout = QFormLayout()

        # Prénom
        self.first_name_input = QLineEdit()
        self.first_name_input.setPlaceholderText("Prénom de l'élève")
        form_layout.addRow("Prénom :", self.first_name_input)

        # Nom
        self.last_name_input = QLineEdit()
        self.last_name_input.setPlaceholderText("Nom de l'élève")
        form_layout.addRow("Nom :", self.last_name_input)

        # Date de naissance avec calendrier
        dob_label = QLabel("Date de Naissance :")
        dob_layout = QHBoxLayout()
        
        self.dob_input = QLineEdit()
        self.dob_input.setPlaceholderText("YYYY-MM-DD")
        self.dob_input.setReadOnly(True)
        dob_layout.addWidget(self.dob_input)

        self.calendar_btn = QPushButton("📅 Sélectionner Date")
        self.calendar_btn.clicked.connect(self.open_calendar)
        dob_layout.addWidget(self.calendar_btn)

        form_layout.addRow(dob_label, dob_layout)

        layout.addLayout(form_layout)

        # Message d'erreur
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setWordWrap(True)
        layout.addWidget(self.error_label)

        # Boutons
        button_layout = QHBoxLayout()

        add_btn = QPushButton("Ajouter Élève")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #2E7D32;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        """)
        add_btn.clicked.connect(self.add_student)
        button_layout.addWidget(add_btn)

        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addSpacing(10)
        layout.addLayout(button_layout)
        layout.addStretch()

    def open_calendar(self):
        """Open a calendar dialog to select date of birth."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Date of Birth")
        dialog.setFixedSize(400, 350)
        
        layout = QVBoxLayout(dialog)
        
        calendar = QCalendarWidget()
        calendar.setSelectedDate(QDate.currentDate())
        layout.addWidget(calendar)
        
        button_layout = QHBoxLayout()
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(lambda: self.on_date_selected(calendar.selectedDate(), dialog))
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        dialog.exec()

    def on_date_selected(self, date, dialog):
        """Handle date selection from calendar."""
        self.dob_input.setText(date.toString("yyyy-MM-dd"))
        dialog.accept()

    def add_student(self):
        """Add the student profile."""
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        dob = self.dob_input.text().strip()

        if not all([first_name, last_name, dob]):
            self.error_label.setText("Tous les champs sont obligatoires")
            return

        # Valider le format de la date
        try:
            datetime.strptime(dob, "%Y-%m-%d")
        except ValueError:
            self.error_label.setText("Format de date invalide. Utilisez YYYY-MM-DD")
            return

        success, message = self.user_manager.create_student_profile(
            first_name, last_name, dob
        )

        if success:
            self.error_label.setText("")
            self.student_added.emit()
            self.accept()
        else:
            self.error_label.setText(message)


class EditStudentDialog(QDialog):
    """Dialogue pour éditer un profil d'élève."""

    def __init__(self, student_data, parent=None):
        super().__init__(parent)
        self.student_data = student_data
        self.setWindowTitle("Éditer Profil Élève")
        self.setFixedSize(400, 300)
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        """Initialiser l'interface utilisateur."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # Formulaire
        form_layout = QFormLayout()

        # Prénom
        self.first_name_input = QLineEdit()
        self.first_name_input.setText(self.student_data.get("first_name", ""))
        form_layout.addRow("Prénom :", self.first_name_input)

        # Nom
        self.last_name_input = QLineEdit()
        self.last_name_input.setText(self.student_data.get("last_name", ""))
        form_layout.addRow("Nom :", self.last_name_input)

        # Date de naissance
        self.dob_input = QLineEdit()
        self.dob_input.setText(self.student_data.get("date_of_birth", ""))
        form_layout.addRow("Date de Naissance :", self.dob_input)

        layout.addLayout(form_layout)

        # Boutons
        button_layout = QHBoxLayout()

        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        layout.addStretch()

    def get_data(self):
        """Get the edited data."""
        return (
            self.first_name_input.text(),
            self.last_name_input.text(),
            self.dob_input.text()
        )
