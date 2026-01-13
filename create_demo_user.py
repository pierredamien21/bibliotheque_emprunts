import httpx
import sys

BASE_URL = "http://127.0.0.1:8000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def create_demo_user():
    # 1. Login Admin
    with httpx.Client(timeout=10.0) as client:
        res = client.post(f"{BASE_URL}/auth/login", data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD})
        if res.status_code != 200:
            print("Admin login failed")
            return
        token = res.json()["access_token"]
        
        # 2. Get/Create Type
        client.headers.update({"Authorization": f"Bearer {token}"})
        res = client.get(f"{BASE_URL}/types-membre/")
        type_id = 1
        if res.status_code == 200 and len(res.json()) > 0:
             type_id = res.json()[0]['id_type_membre']
        
        # 3. Create User
        data = {
            "numero_carte": "DEMO-001",
            "nom": "Demo",
            "prenom": "User",
            "email": "demo@example.com",
            "login": "membre_demo",
            "password": "password123",
            "id_type_membre": type_id,
            "statut_compte": "Actif"
        }
        # Try create
        res = client.post(f"{BASE_URL}/membres/", json=data)
        if res.status_code in [200, 201]:
            print("Created: membre_demo / password123")
        elif res.status_code == 400 and "existe déjà" in res.text:
             print("User already exists: membre_demo / password123")
        else:
            print(f"Failed: {res.text}")

if __name__ == "__main__":
    create_demo_user()
