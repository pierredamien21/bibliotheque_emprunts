from datetime import date
from fastapi.testclient import TestClient

def test_sanction_flow(authorized_client):
    client = authorized_client
    # 1. Setup necessary data
    # Create TypeMembre
    tm_data = {"nom_type": "Standard", "duree_max_emprunt": 14, "nb_max_emprunt": 5}
    r = client.post("/types-membre/", json=tm_data)
    if r.status_code == 404:
        r = client.post("/type_membre/", json=tm_data)
    id_tm = r.json()["id_type_membre"]

    # Create Membre
    mem_data = {
        "numero_carte": "SANC-001", "nom": "Sanction", "prenom": "User",
        "email": "sanction@test.com", "password": "password123", "statut_compte": "Actif", "id_type_membre": id_tm
    }
    r = client.post("/membres/", json=mem_data)
    id_mem = r.json()["id_membre"]

    # Create Bibliothecaire
    bib_data = {
        "matricule": "BIB-SANC", "nom": "Bib", "prenom": "Sanc",
        "email": "bib.sanc@test.com", "login": "bibsanc", "mot_de_passe": "pass", "role": "Admin"
    }
    r = client.post("/bibliothecaires/", json=bib_data)
    assert r.status_code in [200, 201], f"Bib creation failed: {r.text}"
    id_bib = r.json()["id_bibliotecaire"]

    # Create Emprunt (Dummy one, usually sanctions are linked to emprunts)
    # We need a book and copy first
    cat_data = {"nom_categorie": "TestCat", "description": "desc"}
    id_cat = client.post("/categories/", json=cat_data).json()["id_categorie"]
    
    livre_data = {"titre": "Livre Sanction", "id_categorie": id_cat}
    id_livre = client.post("/livres/", json=livre_data).json()["id_livre"]
    
    ex_data = {"code_barre": "BSANC-1", "etat": "Disponible", "statut_logique": "Actif", "id_livre": id_livre}
    id_ex = client.post("/exemplaires/", json=ex_data).json()["id_exemplaire"]

    emp_data = {
        "id_membre": id_mem, "id_exemplaire": id_ex, "id_bibliotecaire": id_bib,
        "statut": "En cours"
    }
    id_emp = client.post("/emprunts/", json=emp_data).json()["id_emprunt"]

    # 2. Create Sanction
    sanction_data = {
        "type_sanction": "Retard",
        "montant": 5.00,
        "statut": "Non payee",
        "id_membre": id_mem,
        "id_emprunt": id_emp,
        "id_bibliotecaire": id_bib
    }
    r = client.post("/sanctions/", json=sanction_data)
    assert r.status_code in [200, 201]
    data = r.json()
    assert data["statut"] == "Non payee"
    assert float(data["montant"]) == 5.0
    id_sanction = data["id_sanction"]

    # 3. Update Status
    r = client.patch(f"/sanctions/{id_sanction}/statut?statut=Payee")
    assert r.status_code == 200
    assert "Payee" in r.json()["message"]

    # Verify update
    r = client.get(f"/sanctions/{id_sanction}")
    assert r.json()["statut"] == "Payee"

    # 4. Invalid Status Update
    r = client.patch(f"/sanctions/{id_sanction}/statut?statut=Invalid")
    assert r.status_code == 400


def test_reservation_flow(authorized_client):
    client = authorized_client
    # Setup
    # Reuse valid IDs from previous logic concept, but better to recreate for isolation if needed.
    # We need Membre, Livre, Bibliothecaire
    
    # TypeMembre
    tm_data = {"nom_type": "Reser", "duree_max_emprunt": 14, "nb_max_emprunt": 5}
    r = client.post("/types-membre/", json=tm_data)
    if r.status_code == 404:
        r = client.post("/type_membre/", json=tm_data)
    id_tm = r.json()["id_type_membre"]

    # Membre
    mem_data = {
        "numero_carte": "RES-001", "nom": "Res", "prenom": "User",
        "email": "res@test.com", "password": "password123", "statut_compte": "Actif", "id_type_membre": id_tm
    }
    id_mem = client.post("/membres/", json=mem_data).json()["id_membre"]

    # Cat & Livre
    cat_data = {"nom_categorie": "ResCat", "description": "desc"}
    id_cat = client.post("/categories/", json=cat_data).json()["id_categorie"]
    livre_data = {"titre": "Livre Res", "id_categorie": id_cat}
    id_livre = client.post("/livres/", json=livre_data).json()["id_livre"]

    # Bib
    bib_data = {
        "matricule": "BIB-RES", "nom": "Bib", "prenom": "Res",
        "email": "bib.res@test.com", "login": "bibres", "mot_de_passe": "pass", "role": "Admin"
    }
    id_bib = client.post("/bibliothecaires/", json=bib_data).json()["id_bibliotecaire"]

    # 1. Create Reservation
    res_data = {
        "statut": "En attente",
        "priorite": 1,
        "id_membre": id_mem,
        "id_livre": id_livre,
        "id_bibliotecaire": id_bib
    }
    r = client.post("/reservations/", json=res_data)
    assert r.status_code in [200, 201]
    data = r.json()
    assert data["statut"] == "En attente"
    id_res = data["id_reservation"]

    # 2. Update Status
    r = client.patch(f"/reservations/{id_res}/statut?statut=Confirmee")
    assert r.status_code == 200
    
    # Verify
    r = client.get(f"/reservations/{id_res}")
    assert r.json()["statut"] == "Confirmee"

    # 3. Invalid Status
    r = client.patch(f"/reservations/{id_res}/statut?statut=X")
    assert r.status_code == 400


def test_emprunt_limit(authorized_client):
    client = authorized_client
    # 1. TypeMembre with limit 1
    tm_data = {"nom_type": "Limit1", "duree_max_emprunt": 14, "nb_max_emprunt": 1}
    r = client.post("/types-membre/", json=tm_data)
    if r.status_code == 404:
        r = client.post("/type_membre/", json=tm_data)
    id_tm = r.json()["id_type_membre"]

    # 2. Membre
    mem_data = {
        "numero_carte": "LIM-001", "nom": "Lim", "prenom": "User",
        "email": "lim@test.com", "password": "password123", "statut_compte": "Actif", "id_type_membre": id_tm
    }
    id_mem = client.post("/membres/", json=mem_data).json()["id_membre"]

    # 3. Bib
    bib_data = {
        "matricule": "BIB-LIM", "nom": "Bib", "prenom": "Lim",
        "email": "bib.lim@test.com", "login": "biblim", "mot_de_passe": "ps", "role": "Admin"
    }
    id_bib = client.post("/bibliothecaires/", json=bib_data).json()["id_bibliotecaire"]

    # 4. Resources
    cat_data = {"nom_categorie": "LimCat", "description": "desc"}
    id_cat = client.post("/categories/", json=cat_data).json()["id_categorie"]
    livre_data = {"titre": "Livre Lim", "id_categorie": id_cat}
    id_livre = client.post("/livres/", json=livre_data).json()["id_livre"]
    
    # Ex 1
    ex1_data = {"code_barre": "L-1", "etat": "Disponible", "statut_logique": "Actif", "id_livre": id_livre}
    id_ex1 = client.post("/exemplaires/", json=ex1_data).json()["id_exemplaire"]
    
    # Ex 2
    ex2_data = {"code_barre": "L-2", "etat": "Disponible", "statut_logique": "Actif", "id_livre": id_livre}
    id_ex2 = client.post("/exemplaires/", json=ex2_data).json()["id_exemplaire"]

    # 5. Borrow 1st -> Should succeed
    emp_data = {
        "id_membre": id_mem, "id_exemplaire": id_ex1, "id_bibliotecaire": id_bib,
        "statut": "En cours"
    }
    r = client.post("/emprunts/", json=emp_data)
    assert r.status_code in [200, 201]

    # 6. Borrow 2nd -> Should fail due to limit
    emp_data["id_exemplaire"] = id_ex2
    r = client.post("/emprunts/", json=emp_data)
    assert r.status_code == 400
    assert "Limite" in r.text
