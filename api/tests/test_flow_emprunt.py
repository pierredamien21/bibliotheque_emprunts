from datetime import date

def test_emprunt_flow(authorized_client):
    client = authorized_client
    # 1. Create essential metadata (TypeMembre, Categorie)
    
    # 1.1 Create TypeMembre
    type_membre_data = {
        "nom_type": "Étudiant",
        "duree_max_emprunt": 14,
        "nb_max_emprunt": 3
    }
    r = client.post("/types-membre/", json=type_membre_data)
    # Fallback checking
    if r.status_code == 404:
        r = client.post("/type_membre/", json=type_membre_data)

    assert r.status_code in [200, 201], f"TypeMembre creation failed: {r.text}"
    id_type_membre = r.json()["id_type_membre"]

    # 1.2 Create Categorie
    cat_data = {"nom_categorie": "Science Fiction", "description": "Sci-Fi Books"}
    r = client.post("/categories/", json=cat_data)
    assert r.status_code in [200, 201], f"Categorie creation failed: {r.text}"
    id_cat = r.json()["id_categorie"]

    # 2. Create Bibliothecaire (for handling emprunt)
    bib_data = {
        "matricule": "BIB-001",
        "nom": "Admin",
        "prenom": "Super",
        "email": "admin@biblio.com",
        "login": "admin",
        "mot_de_passe": "secret",
        "role": "Admin"
    }
    r = client.post("/bibliothecaires/", json=bib_data)
    assert r.status_code in [200, 201], f"Bibliothecaire creation failed: {r.text}"
    id_bib = r.json()["id_bibliotecaire"]

    # 3. Create Membre
    membre_data = {
        "numero_carte": "CARD-001",
        "nom": "Doe",
        "prenom": "John",
        "email": "john.doe@example.com",
        "password": "password123",
        "statut_compte": "Actif",
        "id_type_membre": id_type_membre
    }
    r = client.post("/membres/", json=membre_data)
    assert r.status_code in [200, 201], f"Membre creation failed: {r.text}"
    id_membre = r.json()["id_membre"]

    # 4. Create Livre
    livre_data = {
        "titre": "Dune",
        "isbn": "978-0441172719",
        "id_categorie": id_cat
    }
    r = client.post("/livres/", json=livre_data)
    assert r.status_code in [200, 201], f"Livre creation failed: {r.text}"
    id_livre = r.json()["id_livre"]

    # 5. Create Exemplaire
    ex_data = {
        "code_barre": "BAR-001",
        "etat": "Disponible",
        "statut_logique": "Actif",
        "id_livre": id_livre
    }
    r = client.post("/exemplaires/", json=ex_data)
    assert r.status_code in [200, 201], f"Exemplaire creation failed: {r.text}"
    id_exemplaire = r.json()["id_exemplaire"]

    # 6. Emprunter
    emprunt_data = {
        "id_membre": id_membre,
        "id_exemplaire": id_exemplaire,
        "id_bibliotecaire": id_bib,
        "statut": "En cours",
        "renouvellement_count": 0
    }
    r = client.post("/emprunts/", json=emprunt_data)
    assert r.status_code in [200, 201], f"Emprunt creation failed: {r.text}"
    emprunt_json = r.json()
    assert emprunt_json["statut"] == "En cours"
    assert emprunt_json["date_retour_prevue"] is not None
    id_emprunt = emprunt_json["id_emprunt"]

    # 7. Verify Exemplaire status changed to "Emprunte"
    r = client.get(f"/exemplaires/{id_exemplaire}")
    assert r.status_code == 200
    assert r.json()["etat"] == "Emprunte", "L'exemplaire devrait être marqué comme Emprunte"

    # 8. Try to borrow the same copy again -> Should Fail
    r = client.post("/emprunts/", json=emprunt_data)
    assert r.status_code == 400
    assert "disponible" in r.text

    # 9. Returning the book
    r = client.put(f"/emprunts/{id_emprunt}/retour")
    assert r.status_code == 200

    # 10. Verify Emprunt is terminated
    r = client.get(f"/emprunts/{id_emprunt}")
    assert r.json()["statut"] == "Termine"
    assert r.json()["date_retour_effective"] == str(date.today())

    # 11. Verify Exemplaire is available again
    r = client.get(f"/exemplaires/{id_exemplaire}")
    assert r.json()["etat"] == "Disponible" 
