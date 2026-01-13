import httpx
import sys
import time
import random

BASE_URL = "http://127.0.0.1:8000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def log(msg, status="INFO"):
    print(f"[{status}] {msg}")

def login_admin():
    url = f"{BASE_URL}/auth/login"
    data = {"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
    with httpx.Client(timeout=10.0) as client:
        response = client.post(url, data=data) 
        if response.status_code == 200:
            token = response.json().get("access_token")
            return token
    return None

def create_test_member(admin_token):
    # 1. Need TypeMembre
    with httpx.Client(timeout=10.0) as client:
        client.headers.update({"Authorization": f"Bearer {admin_token}"})
        # Check types
        res = client.get(f"{BASE_URL}/types-membre/")
        type_id = 1
        if res.status_code == 200 and len(res.json()) > 0:
             type_id = res.json()[0]['id_type_membre']
        else:
             # Create type
             res = client.post(f"{BASE_URL}/types-membre/", json={"nom_type": "Standard", "duree_max_emprunt": 14, "nb_max_emprunt": 5})
             type_id = res.json()['id_type_membre']

        # 2. Create Member
        ts = int(time.time())
        email = f"user_{ts}@example.com"
        login = f"user_{ts}"
        pwd = "password123"
        data = {
            "numero_carte": f"CART-{ts}",
            "nom": "Doe",
            "prenom": "John",
            "email": email,
            "login": login,
            "password": pwd,
            "id_type_membre": type_id,
            "statut_compte": "Actif"
        }
        res = client.post(f"{BASE_URL}/membres/", json=data)
        if res.status_code in [200, 201]:
            log(f"Created member {login}", "SUCCESS")
            return login, pwd, email
        else:
            log(f"Failed to create member: {res.text}", "ERROR")
            return None, None, None

def login_member(login, password):
    url = f"{BASE_URL}/auth/login/member"
    data = {"username": login, "password": password}
    with httpx.Client(timeout=10.0) as client:
        response = client.post(url, data=data) 
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            log(f"Member login failed: {response.status_code} - {response.text}", "ERROR")
            return None

def test_member_actions(token):
    with httpx.Client(timeout=10.0) as client:
        client.headers.update({"Authorization": f"Bearer {token}"})
        
        # 1. Get Me
        res = client.get(f"{BASE_URL}/auth/me")
        if res.status_code == 200:
            log("Member /me check OK", "SUCCESS")
            # log(res.json())
        else:
             log(f"Member /me failed: {res.status_code}", "ERROR")

        # 2. List Books
        res = client.get(f"{BASE_URL}/livres/")
        if res.status_code == 200:
            books = res.json()
            log(f"Listed {len(books)} books", "SUCCESS")
            if len(books) > 0:
                book_id = books[0]['id_livre']
                
                # 3. Reserve Book
                res_data = {"id_livre": book_id, "priorite": 1}
                res = client.post(f"{BASE_URL}/reservations/", json=res_data)
                if res.status_code in [200, 201]:
                    log("Reservation successful", "SUCCESS")
                else:
                    log(f"Reservation failed: {res.status_code} - {res.text}", "ERROR")
        else:
            log("Failed to list books", "ERROR")

def main():
    admin_token = login_admin()
    if not admin_token:
        log("Admin login failed", "CRITICAL")
        sys.exit(1)
        
    login, pwd, email = create_test_member(admin_token)
    if not login:
        sys.exit(1)
        
    member_token = login_member(login, pwd)
    if not member_token:
        sys.exit(1)
        
    test_member_actions(member_token)

if __name__ == "__main__":
    main()
