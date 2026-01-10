import pytest

def test_member_login_flow(client, db_session):
    # 1. Setup TypeMembre
    from models.models import TypeMembre
    tm = TypeMembre(nom_type="Etudiant", duree_max_emprunt=14, nb_max_emprunt=5)
    db_session.add(tm)
    db_session.commit()
    db_session.refresh(tm)

    # 2. Register a member (requires admin/staff auth for registration endpoint)
    from models.models import Bibliothecaire
    from security import create_access_token
    
    staff = Bibliothecaire(
        matricule="STAFF-001", nom="S", prenom="S", email="s@t.com",
        login="admin", mot_de_passe_hash="h", role="Admin"
    )
    db_session.add(staff)
    db_session.commit()
    
    staff_token = create_access_token(data={"sub": "admin", "role": "Admin"})
    headers = {"Authorization": f"Bearer {staff_token}"}
    
    member_data = {
        "numero_carte": "LOGIN-001",
        "nom": "Login",
        "prenom": "User",
        "email": "login@test.com",
        "login": "logintest",
        "password": "strongpassword123",
        "statut_compte": "Actif",
        "id_type_membre": tm.id_type_membre
    }
    r = client.post("/membres/", json=member_data, headers=headers)
    assert r.status_code in [200, 201]

    # 3. Test Login with Email
    login_data = {"username": "login@test.com", "password": "strongpassword123"}
    r = client.post("/auth/login/member", data=login_data)
    assert r.status_code == 200
    assert "access_token" in r.json()
    assert r.json()["role"] == "Membre"

    # 4. Test Login with Card Number
    login_data = {"username": "LOGIN-001", "password": "strongpassword123"}
    r = client.post("/auth/login/member", data=login_data)
    assert r.status_code == 200

    # 5. Test Login with Username (login)
    login_data = {"username": "logintest", "password": "strongpassword123"}
    r = client.post("/auth/login/member", data=login_data)
    assert r.status_code == 200

    # 6. Test Login Failure (Wrong password)
    login_data = {"username": "logintest", "password": "wrongpassword"}
    r = client.post("/auth/login/member", data=login_data)
    assert r.status_code == 401

def test_member_access_restrictions(member_client):
    # A regular member should NOT be able to create categories
    r = member_client.post("/categories/", json={"nom_categorie": "Secret", "description": "xxx"})
    assert r.status_code == 403
    assert "Staff access required" in r.text

    # A regular member should NOT be able to list all members
    r = member_client.get("/membres/")
    assert r.status_code == 403

def test_member_own_data_access(client, db_session):
    # Setup two members
    from models.models import Membre, TypeMembre, Emprunt, Exemplaire, Livre, Categorie, Bibliothecaire
    from security import hash_password, create_access_token
    
    tm = TypeMembre(nom_type="Test", duree_max_emprunt=14, nb_max_emprunt=5)
    db_session.add(tm)
    db_session.commit()

    m1 = Membre(numero_carte="M1", nom="M1", prenom="M1", email="m1@t.com", mot_de_passe_hash=hash_password("p"), id_type_membre=tm.id_type_membre, statut_compte="Actif")
    m2 = Membre(numero_carte="M2", nom="M2", prenom="M2", email="m2@t.com", mot_de_passe_hash=hash_password("p"), id_type_membre=tm.id_type_membre, statut_compte="Actif")
    db_session.add_all([m1, m2])
    db_session.commit()

    # Create an emprunt for m1
    cat = Categorie(nom_categorie="C")
    db_session.add(cat)
    db_session.commit()
    l = Livre(titre="L", id_categorie=cat.id_categorie)
    db_session.add(l)
    db_session.commit()
    ex = Exemplaire(code_barre="EX1", etat="Emprunte", statut_logique="Actif", id_livre=l.id_livre)
    db_session.add(ex)
    db_session.commit()
    bib = Bibliothecaire(matricule="B1", nom="B", prenom="B", email="b@t.com", login="b", mot_de_passe_hash="h", role="Agent")
    db_session.add(bib)
    db_session.commit()

    emp = Emprunt(id_membre=m1.id_membre, id_exemplaire=ex.id_exemplaire, id_bibliotecaire=bib.id_bibliotecaire, statut="En cours")
    db_session.add(emp)
    db_session.commit()

    # Authenticate as m1
    t1 = create_access_token(data={"sub": m1.email, "role": "Membre", "id": m1.id_membre})
    # Authenticate as m2
    t2 = create_access_token(data={"sub": m2.email, "role": "Membre", "id": m2.id_membre})

    # m1 should see their emprunts
    r = client.get(f"/emprunts/membre/{m1.id_membre}", headers={"Authorization": f"Bearer {t1}"})
    assert r.status_code == 200
    assert len(r.json()) == 1

    # m2 should NOT see m1's emprunts
    r = client.get(f"/emprunts/membre/{m1.id_membre}", headers={"Authorization": f"Bearer {t2}"})
    assert r.status_code == 403
    assert "propres emprunts" in r.json()["detail"]
