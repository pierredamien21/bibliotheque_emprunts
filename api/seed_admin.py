import sys
import os

# Add the current directory to sys.path to allow imports from api
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models.models import Bibliothecaire
from security import hash_password

def seed_admin():
    db = SessionLocal()
    try:
        # Check if an admin already exists
        admin_exists = db.query(Bibliothecaire).filter(Bibliothecaire.login == "admin").first()
        if admin_exists:
            print("L'administrateur 'admin' existe déjà.")
            return

        # Create default admin
        new_admin = Bibliothecaire(
            matricule="ADMIN-001",
            nom="ADMIN",
            prenom="System",
            email="admin@bibliotheque.com",
            login="admin",
            mot_de_passe_hash=hash_password("admin123"),
            role="Admin"
        )
        
        db.add(new_admin)
        db.commit()
        print("Premier administrateur créé avec succès !")
        print("Login : admin")
        print("Mot de passe : admin123")
        print("IMPORTANT : Changez ce mot de passe dès votre première connexion.")
        
    except Exception as e:
        print(f"Erreur lors de la création de l'admin : {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin()
