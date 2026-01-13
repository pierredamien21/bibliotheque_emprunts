from dotenv import load_dotenv
import os
import sys

# Add the current directory to sys.path to allow imports from api
sys.path.append(os.path.join(os.getcwd(), "api"))

from database import SessionLocal
from models.models import Bibliothecaire
from security import hash_password

def reset_admin():
    load_dotenv()
    db = SessionLocal()
    try:
        admin = db.query(Bibliothecaire).filter(Bibliothecaire.login == "admin").first()
        if not admin:
            print("Admin non trouvé. Création en cours...")
            admin = Bibliothecaire(
                matricule="ADMIN-001",
                nom="ADMIN",
                prenom="System",
                email="admin@bibliotheque.com",
                login="admin",
                role="Admin"
            )
            db.add(admin)
        
        admin.mot_de_passe_hash = hash_password("admin123")
        db.commit()
        print("Mot de passe de l'administrateur 'admin' réinitialisé à : admin123")
        print("URL DB utilisée :", os.getenv("DATABASE_URL").split("@")[-1])
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin()
