import sys
import os

# Add the current directory to sys.path to allow imports from api
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models.models import TypeMembre

def seed_types():
    db = SessionLocal()
    try:
        types = [
            {"nom_type": "Étudiant", "duree_max_emprunt": 14, "nb_max_emprunt": 5},
            {"nom_type": "Standard", "duree_max_emprunt": 21, "nb_max_emprunt": 3},
            {"nom_type": "Professionnel", "duree_max_emprunt": 30, "nb_max_emprunt": 10},
        ]
        
        for t_data in types:
            exists = db.query(TypeMembre).filter(TypeMembre.nom_type == t_data["nom_type"]).first()
            if not exists:
                new_type = TypeMembre(**t_data)
                db.add(new_type)
                print(f"Type '{t_data['nom_type']}' créé.")
            else:
                print(f"Type '{t_data['nom_type']}' existe déjà.")
        
        db.commit()
        print("\nInitialisation des types de membres terminée !")
        
    except Exception as e:
        print(f"Erreur : {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_types()
