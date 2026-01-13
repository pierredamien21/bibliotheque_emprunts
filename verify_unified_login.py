import httpx

BASE_URL = "http://127.0.0.1:8000"

def test_unified():
    client = httpx.Client(timeout=10.0)
    
    # 1. Staff Login
    print("Testing Unified Login (Staff: admin)...")
    res = client.post(f"{BASE_URL}/auth/login/unified", data={"username": "admin", "password": "admin123"})
    print(f"Status: {res.status_code}")
    if res.status_code == 200:
        print(f"Role: {res.json()['role']}")
    
    # 2. Member Login
    print("\nTesting Unified Login (Member: membre_demo)...")
    res = client.post(f"{BASE_URL}/auth/login/unified", data={"username": "membre_demo", "password": "password123"})
    print(f"Status: {res.status_code}")
    if res.status_code == 200:
        print(f"Role: {res.json()['role']}")

if __name__ == "__main__":
    test_unified()
