import httpx

BASE_URL = "http://127.0.0.1:8000"

def test_logins():
    client = httpx.Client(timeout=10.0)
    
    # 1. Staff Login (Admin)
    print("Testing Staff Login (admin/admin123)...")
    res = client.post(f"{BASE_URL}/auth/login", data={"username": "admin", "password": "admin123"})
    print(f"Status: {res.status_code}")
    if res.status_code != 200:
        print(f"Error: {res.text}")
        
    # 2. Member Login (membre_demo)
    print("\nTesting Member Login (membre_demo/password123) at /auth/login/member...")
    res = client.post(f"{BASE_URL}/auth/login/member", data={"username": "membre_demo", "password": "password123"})
    print(f"Status: {res.status_code}")
    if res.status_code != 200:
        print(f"Error: {res.text}")

    # 3. Mismatch test: Member at Staff endpoint
    print("\nTesting Mismatch: Member at Staff endpoint...")
    res = client.post(f"{BASE_URL}/auth/login", data={"username": "membre_demo", "password": "password123"})
    print(f"Status: {res.status_code} (Expected 401)")

if __name__ == "__main__":
    test_logins()
