

from tempfile import TemporaryDirectory

from src.core.user_manager import UserManager


def test_create_musicotherapist():
    with TemporaryDirectory() as temp_dir:
        manager = UserManager(temp_dir)

        success, message = manager.create_musicotherapist_profile(
            username="admin",
            password="1234",
            full_name="Admin Test"
        )

        assert success is True
        assert "succès" in message.lower()

        assert "admin" in manager.users
        assert manager.users["admin"]["type"] == "musicotherapist"

## Test de la création d'un musicothérapeute avec un nom d'utilisateur déjà existant
def test_create_duplicate_musicotherapist():
    with TemporaryDirectory() as temp_dir:
        manager = UserManager(temp_dir)

        manager.create_musicotherapist_profile(
            "admin",
            "1234",
            "Admin Test"
        )

        success, message = manager.create_musicotherapist_profile(
            "admin",
            "5678",
            "Autre Admin"
        )

        assert success is False
        assert "existe déjà" in message
## Test 3 : mot de passe trop court
def test_create_musicotherapist_short_password():
    with TemporaryDirectory() as temp_dir:
        manager = UserManager(temp_dir)

        success, message = manager.create_musicotherapist_profile(
            "admin",
            "123",
            "Admin Test"
        )

        assert success is False
        assert "4 caractères" in message
## Test 4 : authentification réussie
def test_authenticate_musicotherapist_success():
    with TemporaryDirectory() as temp_dir:
        manager = UserManager(temp_dir)

        manager.create_musicotherapist_profile(
            "admin",
            "1234",
            "Admin Test"
        )

        success, message = manager.authenticate_musicotherapist(
            "admin",
            "1234"
        )

        assert success is True
        assert manager.current_user == "admin"
        assert manager.current_profile_type == "musicotherapist"
## Test 5 : mot de passe incorrect
def test_authenticate_musicotherapist_wrong_password():
    with TemporaryDirectory() as temp_dir:
        manager = UserManager(temp_dir)

        manager.create_musicotherapist_profile(
            "admin",
            "1234",
            "Admin Test"
        )

        success, message = manager.authenticate_musicotherapist(
            "admin",
            "0000"
        )

        assert success is False
        assert "incorrect" in message.lower()
##Test 6 : Création d'un élève
def test_create_student_profile():
    with TemporaryDirectory() as temp_dir:
        manager = UserManager(temp_dir)

        manager.create_musicotherapist_profile(
            "admin",
            "1234",
            "Admin Test"
        )

        manager.authenticate_musicotherapist(
            "admin",
            "1234"
        )

        success, message = manager.create_student_profile(
            "Ali",
            "Diallo",
            "2010-01-01"
        )

        assert success is True

        students = manager.get_current_musicotherapist_students()

        assert len(students) == 1
        assert students[0][1]["first_name"] == "Ali"        
## Test 7 : Récupération des élèves
def test_get_current_musicotherapist_students():
    with TemporaryDirectory() as temp_dir:
        manager = UserManager(temp_dir)

        manager.create_musicotherapist_profile(
            "admin",
            "1234",
            "Admin Test"
        )

        manager.authenticate_musicotherapist(
            "admin",
            "1234"
        )

        manager.create_student_profile(
            "Ali",
            "Diallo",
            "2010-01-01"
        )

        students = manager.get_current_musicotherapist_students()

        assert len(students) == 1
## Test 8 : Changement vers un profil élève
def test_switch_to_student_profile():
    with TemporaryDirectory() as temp_dir:
        manager = UserManager(temp_dir)

        manager.create_musicotherapist_profile(
            "admin",
            "1234",
            "Admin Test"
        )

        manager.authenticate_musicotherapist(
            "admin",
            "1234"
        )

        manager.create_student_profile(
            "Ali",
            "Diallo",
            "2010-01-01"
        )

        success, message = manager.switch_to_student_profile(
            "ali_diallo"
        )

        assert success is True
        assert manager.current_profile_type == "student"
## Test 9 : Création d'un élève sans connexion
def test_create_student_without_login():
    with TemporaryDirectory() as temp_dir:
        manager = UserManager(temp_dir)

        success, message = manager.create_student_profile(
            "Ali",
            "Diallo",
            "2010-01-01"
        )

        assert success is False
        assert "connecté" in message