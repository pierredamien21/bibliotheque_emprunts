import sys
import os

# Ajoute le dossier actuel au path pour permettre les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, Base
from models.models import *  # Importe tous les modèles pour qu'ils soient enregistrés

def init_db():
    print("Création des tables dans la base de données...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Tables créées avec succès !")
    except Exception as e:
        print(f"Erreur lors de la création des tables : {e}")

if __name__ == "__main__":
    init_db()
