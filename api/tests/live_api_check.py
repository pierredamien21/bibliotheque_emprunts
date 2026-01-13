import httpx
import sys
import time
import random

BASE_URL = "https://bibliotheque-emprunts.onrender.com"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def log(msg, status="INFO"):
    print(f"[{status}] {msg}")

def login():
    url = f"{BASE_URL}/auth/login"
    data = {"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
    try:
        with httpx.Client() as client:
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
        # API returns "id" for staff and members, not "id_bibliotecaire"
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
    else:
        log(f"Failed to fetch categories: {res.status_code}", "ERROR")
    
    # Try to create one just in case
    new_cat = {"nom_categorie": f"Test Category {int(time.time())}", "description": "Temporary test category"}
    res = client.post(f"{BASE_URL}/categories/", json=new_cat)
    if res.status_code in [200, 201]:
        log("Category creation successful", "SUCCESS")
        return res.json()['id_categorie']
    elif res.status_code == 400:
         log("Category might already exist, falling back to fetch", "INFO")
         res = client.get(f"{BASE_URL}/categories/")
         return res.json()[0]['id_categorie'] if res.json() else None
    else:
        log(f"Category creation failed: {res.status_code} - {res.text}", "ERROR")
    return None

def test_authors(client):
    log("Testing Authors...")
    res = client.get(f"{BASE_URL}/auteurs/")
    if res.status_code == 200:
        log(f"Fetched {len(res.json())} authors", "SUCCESS")
    else:
        log(f"Failed to fetch authors: {res.status_code}", "ERROR")
        return None

    new_author = {"nom": f"Hugo_{int(time.time())}", "prenom": "Victor_Test", "nationalite": "Francaise"}
    res = client.post(f"{BASE_URL}/auteurs/", json=new_author)
    if res.status_code in [200, 201]:
         log("Author creation successful", "SUCCESS")
         return res.json()['id_auteur']
    elif res.status_code == 400:
        log("Author probably exists", "INFO")
        res = client.get(f"{BASE_URL}/auteurs/")
        return res.json()[0]['id_auteur'] if res.json() else None
    else:
         log(f"Author creation failed: {res.status_code} - {res.text}", "ERROR")
    return None

def test_books(client, cat_id):
    log("Testing Books...")
    if not cat_id:
        log("Skipping book test due to missing category", "WARNING")
        return None, None
    
    isbn = f"978-LIVE-{int(time.time())}-{random.randint(100,999)}"
    new_book = {
        "titre": "Live Test Book",
        "isbn": isbn,
        "id_categorie": cat_id,
        "annee_publication": 2024,
        "description": "Test book for live debug",
        "langue": "Francais",
        "nombre_pages": 100,
        "editeur": "Test Ed"
    }
    
    res = client.post(f"{BASE_URL}/livres/", json=new_book)
    book_id = None
    if res.status_code in [200, 201]:
        log("Book creation successful", "SUCCESS")
        book_id = res.json()['id_livre']
    else:
        log(f"Book creation failed: {res.status_code} - {res.text}", "ERROR")
        return None, None

    # Add copy
    if book_id:
        # Need unique barcode? Schema Exemplaire doesn't say, but model says unique code_barre
        code_barre = f"CB-{int(time.time())}-{random.randint(100,999)}"
        # Check api/schemas/exemplaire.py ... it likely needs code_barre if not default?
        # Model: code_barre nullable=False.
        # Check Schema... I haven't checked ExemplaireCreate Schema.
        # Let's assume it needs it.
        # But for now try without, if fail, add it.
        res = client.post(f"{BASE_URL}/exemplaires/", json={"id_livre": book_id, "etat": "Neuf"})
        
        if res.status_code == 422: # Validation Error
             # Maybe missing code_barre
             log("Exemplaire creation 422, trying with code_barre", "INFO")
             res = client.post(f"{BASE_URL}/exemplaires/", json={"id_livre": book_id, "etat": "Neuf", "code_barre": code_barre})
        
        if res.status_code in [200, 201]:
             log("Copy added", "SUCCESS")
             copy_obj = res.json()
             return book_id, copy_obj.get('id_exemplaire')
        else:
             log(f"Copy addition failed: {res.status_code} - {res.text}", "ERROR")
    
    return None, None

def test_members(client):
    log("Testing Members...")
    # FIXED URL: /types-membre/
    res = client.get(f"{BASE_URL}/types-membre/")
    type_id = None
    if res.status_code == 200 and len(res.json()) > 0:
        first = res.json()[0]
        type_id = first.get('id_type_membre')
        log(f"Found TypeMembre ID: {type_id}", "INFO")
    else:
        log(f"No member types found or failed: {res.status_code}", "ERROR")
        return None

    email = f"test_live_{int(time.time())}_{random.randint(100,999)}@example.com"
    new_member = {
        "nom": "Tester",
        "prenom": "Live",
        "email": email,
        "telephone": "123456789",
        "adresse": "Test Address",
        "id_type_membre": type_id,
        "numero_carte": f"CART-{int(time.time())}-{random.randint(100,999)}",
        "statut_compte": "Actif",
        "login": f"user{int(time.time())}_{random.randint(100,999)}",
        "password": "password123"
    }
    
    res = client.post(f"{BASE_URL}/membres/", json=new_member)
    if res.status_code in [200, 201]:
        log(f"Member creation successful ({email})", "SUCCESS")
        return res.json()['id_membre']
    else:
        log(f"Member creation failed: {res.status_code} - {res.text}", "ERROR")
        return None

def test_loan_flow(client, member_id, copy_id, staff_id):
    log("Testing Loan Flow...")
    if not member_id or not copy_id or not staff_id:
        log(f"Skipping loan test due to missing dependencies details: m={member_id}, c={copy_id}, s={staff_id}", "WARNING")
        return

    # 1. Check if copy is available?
    # It should be if created newly.

    # 2. Borrow
    loan_data = {
        "id_membre": member_id,
        "id_exemplaire": copy_id,
        "id_bibliotecaire": staff_id,
        "statut": "En cours"
    }
    res = client.post(f"{BASE_URL}/emprunts/", json=loan_data)
    if res.status_code in [200, 201]:
        log("Loan created successfully", "SUCCESS")
        loan = res.json()
        loan_id = loan['id_emprunt']
        
        # 3. Return
        log("Testing Return...")
        res = client.put(f"{BASE_URL}/emprunts/{loan_id}/retour")
        if res.status_code == 200:
             log("Return processed successfully", "SUCCESS")
             log(f"Result: {res.json()}", "INFO")
        else:
             log(f"Return failed: {res.status_code} - {res.text}", "ERROR")

    else:
        log(f"Loan creation failed: {res.status_code} - {res.text}", "ERROR")

def main():
    token = login()
    if not token:
        sys.exit(1)
    
    with httpx.Client() as client:
        client.headers.update({"Authorization": f"Bearer {token}"})
        
        staff_id = get_current_user_id(client)
        log(f"Current Staff ID: {staff_id}", "INFO")

        cat_id = test_categories(client)
        
        # Note: Authors not needed for book creation based on previous analysis, 
        # but good to test they trigger correctly.
        author_id = test_authors(client)
        
        book_id, copy_id = test_books(client, cat_id)
        
        member_id = test_members(client)
        
        test_loan_flow(client, member_id, copy_id, staff_id)

if __name__ == "__main__":
    main()
