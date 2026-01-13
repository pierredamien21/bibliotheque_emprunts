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
            return response.json().get("access_token")
    return None

def create_and_login_member(admin_token):
    with httpx.Client(timeout=10.0) as client:
        client.headers.update({"Authorization": f"Bearer {admin_token}"})
        
        # Ensure TypeMembre exists
        res = client.get(f"{BASE_URL}/types-membre/")
        type_id = 1
        if res.status_code == 200 and len(res.json()) > 0:
             type_id = res.json()[0]['id_type_membre']
        else:
             res = client.post(f"{BASE_URL}/types-membre/", json={"nom_type": "Standard", "duree_max_emprunt": 14, "nb_max_emprunt": 5})
             if res.status_code == 200:
                 type_id = res.json()['id_type_membre']

        ts = int(time.time())
        login = f"chatuser_{ts}"
        pwd = "password123"
        data = {
            "numero_carte": f"CHAT-{ts}",
            "nom": "Chatter",
            "prenom": "Box",
            "email": f"chat_{ts}@example.com",
            "login": login,
            "password": pwd,
            "id_type_membre": type_id,
            "statut_compte": "Actif"
        }
        res = client.post(f"{BASE_URL}/membres/", json=data)
        if res.status_code not in [200, 201]:
            log(f"Create member failed: {res.text}", "ERROR")
            return None, None

    # Login
    url = f"{BASE_URL}/auth/login/member"
    data = {"username": login, "password": pwd}
    with httpx.Client(timeout=10.0) as client:
        response = client.post(url, data=data) 
        if response.status_code == 200:
            return response.json().get("access_token"), login
        else:
            log(f"Member login failed: {response.text}", "ERROR")
            return None, None

def test_chat(admin_token, member_token):
    log("--- Testing Chat ---")
    msg_id = None
    
    # 1. Member sends message
    with httpx.Client(timeout=10.0) as client:
        client.headers.update({"Authorization": f"Bearer {member_token}"})
        res = client.post(f"{BASE_URL}/messages/", json={"contenu": "Help me!"})
        if res.status_code == 200:
            msg_id = res.json()['id_message']
            log("Member sent message", "SUCCESS")
        else:
            log(f"Member send message failed: {res.status_code}", "ERROR")
            return

    # 2. Admin replies
    with httpx.Client(timeout=10.0) as client:
        client.headers.update({"Authorization": f"Bearer {admin_token}"})
        res = client.patch(f"{BASE_URL}/messages/{msg_id}/repondre", json={"reponse": "Here is help."})
        if res.status_code == 200:
            log("Admin replied", "SUCCESS")
        else:
            log(f"Admin reply failed: {res.status_code} - {res.text}", "ERROR")

    # 3. Member checks reply
    with httpx.Client(timeout=10.0) as client:
        client.headers.update({"Authorization": f"Bearer {member_token}"})
        res = client.get(f"{BASE_URL}/messages/")
        if res.status_code == 200:
            msgs = res.json()
            my_msg = next((m for m in msgs if m['id_message'] == msg_id), None)
            if my_msg and my_msg['reponse'] == "Here is help." and my_msg['statut'] == "Repondu":
                log("Member received reply verification", "SUCCESS")
            else:
                log(f"Member verification failed or reply mismatch: {my_msg}", "ERROR")

def test_recommendations(admin_token, member_token):
    log("--- Testing Recommendations ---")
    
    # 1. Member Reco
    with httpx.Client(timeout=10.0) as client:
        client.headers.update({"Authorization": f"Bearer {member_token}"})
        res = client.get(f"{BASE_URL}/livres/recommandations")
        if res.status_code == 200:
            recos = res.json()
            log(f"Member Recommendation OK (Count: {len(recos)})", "SUCCESS")
        else:
             log(f"Member Recommendation Failed: {res.status_code}", "ERROR")

    # 2. Staff Reco
    with httpx.Client(timeout=10.0) as client:
        client.headers.update({"Authorization": f"Bearer {admin_token}"})
        res = client.get(f"{BASE_URL}/livres/recommandations")
        if res.status_code == 200:
            recos = res.json()
            log(f"Staff Recommendation OK (Count: {len(recos)})", "SUCCESS")
        else:
             log(f"Staff Recommendation Failed: {res.status_code}", "ERROR")

def main():
    admin_token = login_admin()
    if not admin_token:
        log("Admin login failed", "CRITICAL")
        sys.exit(1)

    member_token, member_login = create_and_login_member(admin_token)
    if not member_token:
        sys.exit(1)

    test_chat(admin_token, member_token)
    test_recommendations(admin_token, member_token)

if __name__ == "__main__":
    main()
