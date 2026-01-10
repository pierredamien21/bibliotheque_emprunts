import pytest
from fastapi.testclient import TestClient

def test_crud_categorie(authorized_client):
    client = authorized_client
    
    # CREATE
    cat_data = {"nom_categorie": "Informatique", "description": "Livres sur la programmation"}
    response = client.post("/categories/", json=cat_data)
    assert response.status_code in [200, 201]
    data = response.json()
    cat_id = data["id_categorie"]
    assert data["nom_categorie"] == "Informatique"

    # READ (List)
    response = client.get("/categories/")
    assert response.status_code == 200
    assert any(c["id_categorie"] == cat_id for c in response.json())

    # READ (One)
    response = client.get(f"/categories/{cat_id}")
    assert response.status_code == 200
    assert response.json()["nom_categorie"] == "Informatique"

    # UPDATE
    update_data = {"nom_categorie": "Informatique & IA", "description": "Inclut l'IA"}
    response = client.put(f"/categories/{cat_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["nom_categorie"] == "Informatique & IA"

    # DELETE
    response = client.delete(f"/categories/{cat_id}")
    assert response.status_code == 200
    
    # Verify deletion
    response = client.get(f"/categories/{cat_id}")
    assert response.status_code == 404

def test_crud_auteur(authorized_client):
    client = authorized_client
    
    # CREATE
    auth_data = {"nom": "Hugo", "prenom": "Victor", "biographie": "Écrivain français"}
    response = client.post("/auteurs/", json=auth_data)
    assert response.status_code in [200, 201]
    data = response.json()
    auth_id = data["id_auteur"]
    assert data["nom"] == "Hugo"

    # READ
    response = client.get(f"/auteurs/{auth_id}")
    assert response.status_code == 200
    assert response.json()["prenom"] == "Victor"

    # UPDATE
    update_data = {"nom": "Hugo", "prenom": "Victor Marie"}
    response = client.put(f"/auteurs/{auth_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["prenom"] == "Victor Marie"

    # DELETE
    response = client.delete(f"/auteurs/{auth_id}")
    assert response.status_code == 200
    assert client.get(f"/auteurs/{auth_id}").status_code == 404

def test_crud_livre(authorized_client):
    client = authorized_client
    
    # Setup: Categorie needed
    cat_res = client.post("/categories/", json={"nom_categorie": "Test CRUD", "description": "desc"})
    cat_id = cat_res.json()["id_categorie"]

    # CREATE
    livre_data = {
        "titre": "Notre-Dame de Paris",
        "isbn": "1234567890",
        "id_categorie": cat_id
    }
    response = client.post("/livres/", json=livre_data)
    assert response.status_code in [200, 201]
    livre_id = response.json()["id_livre"]

    # READ
    response = client.get(f"/livres/{livre_id}")
    assert response.status_code == 200
    assert response.json()["titre"] == "Notre-Dame de Paris"

    # UPDATE
    update_data = {"titre": "Notre-Dame de Paris (Ed. Spéciale)", "id_categorie": cat_id}
    response = client.put(f"/livres/{livre_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["titre"] == "Notre-Dame de Paris (Ed. Spéciale)"

    # DELETE
    response = client.delete(f"/livres/{livre_id}")
    assert response.status_code == 200
    assert client.get(f"/livres/{livre_id}").status_code == 404
