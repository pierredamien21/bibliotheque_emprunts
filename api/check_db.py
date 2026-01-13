import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import SessionLocal
from models.models import Bibliothecaire

def check_users():
    db = SessionLocal()
    try:
        users = db.query(Bibliothecaire).all()
        print(f"Nombre de bibliothécaires trouvé : {len(users)}")
        for u in users:
            print(f"- {u.login} ({u.role})")
    finally:
        db.close()

if __name__ == "__main__":
    check_users()
