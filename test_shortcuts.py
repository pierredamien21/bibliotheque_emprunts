import httpx

BASE_URL = "http://127.0.0.1:8000"

def verify_shortcuts():
    client = httpx.Client(timeout=10.0)
    
    # 1. Login Member
    print("Logging in as membre_demo...")
    res = client.post(f"{BASE_URL}/auth/login/member", data={"username": "membre_demo", "password": "password123"})
    if res.status_code != 200:
        print(f"Login failed: {res.text}")
        return
    
    token = res.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    
    # 2. Test Shortcuts
    endpoints = [
        "/emprunts/mes-emprunts",
        "/reservations/mes-reservations",
        "/sanctions/mes-sanctions"
    ]
    
    for ep in endpoints:
        print(f"Testing {ep}...")
        res = client.get(f"{BASE_URL}{ep}")
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            print(f"Success: Received {len(res.json())} items")
        else:
            print(f"Error: {res.text}")

if __name__ == "__main__":
    verify_shortcuts()
