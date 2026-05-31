import json
import os
import hashlib
from typing import Dict, List, Optional, Tuple


class UserManager:
    """Gère les profils musicothérapeute et étudiant avec stockage persistant."""

    def __init__(self, data_dir: str):
        """Initialiser le gestionnaire d'utilisateurs.
        
        Args:
            data_dir: Répertoire où les données utilisateur seront stockées
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.users_file = os.path.join(data_dir, "users.json")
        self.users = {}
        self.current_user = None
        self.current_profile_type = None  # "musicotherapist" or "student"
        self.current_student_id = None
        
        self.load_users()

    def load_users(self):
        """Charger les utilisateurs depuis le disque."""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, "r", encoding="utf-8") as f:
                    self.users = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.users = {}
        else:
            self.users = {}

    def save_users(self):
        """Sauvegarder les utilisateurs sur le disque."""
        with open(self.users_file, "w", encoding="utf-8") as f:
            json.dump(self.users, f, indent=4, ensure_ascii=False)

    def _hash_password(self, password: str) -> str:
        """Hasher un mot de passe en utilisant SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def create_musicotherapist_profile(self, username: str, password: str, 
                                      full_name: str = "") -> Tuple[bool, str]:
        """Créer un nouveau profil musicothérapeute.
        
        Args:
            username: Nom d'utilisateur pour la connexion
            password: Mot de passe (sera haché)
            full_name: Nom complet du musicothérapeute
            
        Returns:
            Tuple de (succès: bool, message: str)
        """
        if username in self.users:
            return False, "Le nom d'utilisateur existe déjà"
        
        if len(password) < 4:
            return False, "Le mot de passe doit contenir au moins 4 caractères"
        
        self.users[username] = {
            "type": "musicotherapist",
            "password": self._hash_password(password),
            "full_name": full_name,
            "students": {},
            "created_at": self._get_timestamp()
        }
        
        self.save_users()
        return True, "Profil créé avec succès"

    def authenticate_musicotherapist(self, username: str, password: str) -> Tuple[bool, str]:
        """Authentifier un musicothérapeute.
        
        Args:
            username: Nom d'utilisateur
            password: Mot de passe (texte brut)
            
        Returns:
            Tuple de (succès: bool, message: str)
        """
        if username not in self.users:
            return False, "Nom d'utilisateur introuvable"
        
        user = self.users[username]
        if user.get("type") != "musicotherapist":
            return False, "Type d'utilisateur invalide"
        
        if user.get("password") != self._hash_password(password):
            return False, "Mot de passe incorrect"
        
        self.current_user = username
        self.current_profile_type = "musicotherapist"
        self.current_student_id = None
        
        return True, "Connexion réussie"

    def create_student_profile(self, first_name: str, last_name: str, 
                              date_of_birth: str) -> Tuple[bool, str]:
        """Créer un profil d'élève sous le musicothérapeute actuel.
        
        Args:
            first_name: Prénom de l'élève
            last_name: Nom de l'élève
            date_of_birth: Date de naissance (format: YYYY-MM-DD)
            
        Returns:
            Tuple de (succès: bool, message: str)
        """
        if not self.current_user:
            return False, "Aucun musicothérapeute connecté"
        
        if self.current_user not in self.users:
            return False, "Utilisateur actuel introuvable"
        
        user = self.users[self.current_user]
        if user.get("type") != "musicotherapist":
            return False, "Seuls les musicothérapeutes peuvent créer des profils d'élève"
        
        student_id = self._generate_student_id(first_name, last_name)
        
        if student_id in user.get("students", {}):
            return False, "Un profil d'élève avec ce nom existe déjà"
        
        if "students" not in user:
            user["students"] = {}
        
        user["students"][student_id] = {
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": date_of_birth,
            "musicotherapist_id": self.current_user,
            "created_at": self._get_timestamp()
        }
        
        self.save_users()
        return True, f"Profil d'élève créé : {first_name} {last_name}"

    def get_current_musicotherapist_students(self) -> List[Tuple[str, Dict]]:
        """Obtenir tous les élèves du musicothérapeute actuel.
        
        Returns:
            Liste de tuples (student_id, student_data)
        """
        if not self.current_user or self.current_user not in self.users:
            return []
        
        user = self.users[self.current_user]
        students = user.get("students", {})
        
        return list(students.items())

    def switch_to_student_profile(self, student_id: str) -> Tuple[bool, str]:
        """Passer à un profil d'élève.
        
        Args:
            student_id: ID de l'élève
            
        Returns:
            Tuple de (succès: bool, message: str)
        """
        if not self.current_user or self.current_user not in self.users:
            return False, "Aucun musicothérapeute connecté"
        
        user = self.users[self.current_user]
        students = user.get("students", {})
        
        if student_id not in students:
            return False, "Élève introuvable"
        
        self.current_profile_type = "student"
        self.current_student_id = student_id
        
        return True, "Changement vers le profil d'élève réussi"

    def switch_to_musicotherapist_profile(self) -> Tuple[bool, str]:
        """Passer au profil musicothérapeute.
        
        Returns:
            Tuple de (succès: bool, message: str)
        """
        if not self.current_user:
            return False, "Aucun utilisateur connecté"
        
        self.current_profile_type = "musicotherapist"
        self.current_student_id = None
        
        return True, "Changement vers le profil musicothérapeute réussi"

    def logout(self):
        """Déconnecter l'utilisateur actuel."""
        self.current_user = None
        self.current_profile_type = None
        self.current_student_id = None

    def get_current_profile_name(self) -> str:
        """Get the display name of the current profile."""
        if not self.current_user:
            return ""
        
        if self.current_profile_type == "musicotherapist":
            user = self.users.get(self.current_user, {})
            return user.get("full_name", self.current_user)
        elif self.current_profile_type == "student" and self.current_student_id:
            user = self.users.get(self.current_user, {})
            student = user.get("students", {}).get(self.current_student_id, {})
            return f"{student.get('first_name', '')} {student.get('last_name', '')}"
        
        return ""

    @staticmethod
    def _generate_student_id(first_name: str, last_name: str) -> str:
        """Generate a unique student ID based on name."""
        return f"{first_name.lower()}_{last_name.lower()}".replace(" ", "_")

    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp as ISO format string."""
        from datetime import datetime
        return datetime.now().isoformat()

    def delete_student_profile(self, student_id: str) -> Tuple[bool, str]:
        """Supprimer un profil d'élève.
        
        Args:
            student_id: ID de l'élève
            
        Returns:
            Tuple de (succès: bool, message: str)
        """
        if not self.current_user or self.current_user not in self.users:
            return False, "Aucun musicothérapeute connecté"
        
        user = self.users[self.current_user]
        students = user.get("students", {})
        
        if student_id not in students:
            return False, "Élève introuvable"
        
        del students[student_id]
        
        # Si nous regardions cet élève, revenir au musicothérapeute
        if self.current_student_id == student_id:
            self.switch_to_musicotherapist_profile()
        
        self.save_users()
        return True, "Profil d'élève supprimé"

    def get_all_musicotherapists(self) -> List[str]:
        """Obtenir la liste de tous les noms d'utilisateur musicothérapeute."""
        return [username for username, user_data in self.users.items() 
                if user_data.get("type") == "musicotherapist"]
