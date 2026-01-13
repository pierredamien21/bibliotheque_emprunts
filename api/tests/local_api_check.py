import httpx
import sys
import time
import random

BASE_URL = "http://127.0.0.1:8000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def log(msg, status="INFO"):
    print(f"[{status}] {msg}")

def login():
    url = f"{BASE_URL}/auth/login"
    data = {"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(url, data=data) 
            if response.status_code == 200:
                token = response.json().get("access_token")
                log("Login successful", "SUCCESS")
                return token
            else:
                log(f"Login failed: {response.status_code} - {response.text}", "ERROR")
                return None
    except Exception as e:
        log(f"Login exception: {e}", "CRITICAL")
        return None

def get_current_user_id(client):
    res = client.get(f"{BASE_URL}/auth/me")
    if res.status_code == 200:
        me = res.json()
        return me.get('id')
    log(f"Failed to fetch /auth/me: {res.status_code}", "ERROR")
    return None

def test_categories(client):
    log("Testing Categories...")
    res = client.get(f"{BASE_URL}/categories/")
    if res.status_code == 200:
        cats = res.json()
        log(f"Fetched {len(cats)} categories", "SUCCESS")
        if len(cats) > 0:
            return cats[0]['id_categorie']
    
    new_cat = {"nom_categorie": f"Test Category {int(time.time())}", "description": "Temporary test category"}
    res = client.post(f"{BASE_URL}/categories/", json=new_cat)
    if res.status_code in [200, 201]:
        log("Category creation successful", "SUCCESS")
        return res.json()['id_categorie']
    return None

def test_authors(client):
    log("Testing Authors...")
    new_author = {"nom": f"Hugo_{int(time.time())}", "prenom": "Victor_Test", "nationalite": "Francaise"}
    res = client.post(f"{BASE_URL}/auteurs/", json=new_author)
    if res.status_code in [200, 201]:
         log("Author creation successful", "SUCCESS")
         return res.json()['id_auteur']
    return None

def test_books(client, cat_id):
    log("Testing Books...")
    if not cat_id:
        return None, None
    
    isbn = f"978-LOCAL-{int(time.time())}-{random.randint(100,999)}"
    new_book = {
        "titre": "Local Test Book",
        "isbn": isbn,
        "id_categorie": cat_id,
        "annee_publication": 2024,
        "description": "Test book for local debug",
        "langue": "Francais",
        "nombre_pages": 100,
        "editeur": "Test Ed"
    }
    
    res = client.post(f"{BASE_URL}/livres/", json=new_book)
    if res.status_code in [200, 201]:
        log("Book creation successful", "SUCCESS")
        return res.json()['id_livre'], None
    else:
        log(f"Book creation failed: {res.status_code} - {res.text}", "ERROR")
        return None, None

def main():
    token = login()
    if not token:
        sys.exit(1)
    
    with httpx.Client() as client:
        client.headers.update({"Authorization": f"Bearer {token}"})
        
        cat_id = test_categories(client)
        test_authors(client) # ensure works
        
        test_books(client, cat_id)

if __name__ == "__main__":
    main()
