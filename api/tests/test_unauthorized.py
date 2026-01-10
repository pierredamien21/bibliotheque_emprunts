
def test_unauthorized_access(client):
    # Try to access a protected endpoint without auth
    r = client.get("/emprunts/")
    assert r.status_code == 401
    assert r.json()["detail"] == "Not authenticated"
