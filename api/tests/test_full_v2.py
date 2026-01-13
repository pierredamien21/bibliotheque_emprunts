import pytest
from datetime import date, timedelta
from models.models import Livre, Categorie, Exemplaire, Emprunt, Membre, TypeMembre, Sanction, Bibliothecaire
from security import create_access_token

def test_search_and_availability(member_client, db_session):
    # Setup
    cat = Categorie(nom_categorie="Science-Fiction", description="Futur")
    db_session.add(cat)
    db_session.commit()
    livre = Livre(titre="Dune", id_categorie=cat.id_categorie)
    db_session.add(livre)
    db_session.commit()
    ex = Exemplaire(code_barre="DUNE-001", etat="Disponible", statut_logique="Actif", id_livre=livre.id_livre)
    db_session.add(ex)
    db_session.commit()

    # Recherche (V1)
    r = member_client.get(f"/livres/?titre=Dune")
    assert r.status_code == 200
    assert r.json()[0]["nb_disponible"] == 1

def test_member_flow(member_client, db_session):
    # Setup book
    cat = Categorie(nom_categorie="SF", description="...")
    db_session.add(cat)
    db_session.commit()
    livre = Livre(titre="Foundation", id_categorie=cat.id_categorie)
    db_session.add(livre)
    db_session.commit()
    ex = Exemplaire(code_barre="FOU-001", etat="Disponible", statut_logique="Actif", id_livre=livre.id_livre)
    db_session.add(ex)
    db_session.commit()

    # 1. Réservation (V1/V2)
    r = member_client.post("/reservations/", json={"id_livre": livre.id_livre, "priorite": 1})
    assert r.status_code in [200, 201]

    # 2. Avis (V2)
    r = member_client.post("/avis/", json={"id_livre": livre.id_livre, "note": 5, "commentaire": "Excellent"})
    assert r.status_code in [200, 201]

    # 3. Favoris (V2)
    r = member_client.post("/favoris/", json={"id_livre": livre.id_livre})
    assert r.status_code in [200, 201]

def test_staff_flow_and_fines(authorized_client, db_session):
    # 1. Stats (V1/V2)
    r = authorized_client.get("/stats/")
    assert r.status_code == 200
    assert "top_livres" in r.json()

    # 2. Emprunt et Retour avec Amende (V2)
    # Setup member and book
    tm = TypeMembre(nom_type="Test", duree_max_emprunt=14, nb_max_emprunt=5)
    db_session.add(tm)
    db_session.commit()
    mem = Membre(numero_carte="M1", nom="N", prenom="P", email="m@e.com", login="m", statut_compte="Actif", id_type_membre=tm.id_type_membre)
    db_session.add(mem)
    db_session.commit()
    livre = Livre(titre="Test", id_categorie=1) # Cat 1 should exist from previous tests or conftest if we were careful
    # Re-create cat if needed to be safe
    cat = db_session.query(Categorie).first()
    if not cat:
        cat = Categorie(nom_categorie="C", description="D")
        db_session.add(cat)
        db_session.commit()
    livre.id_categorie = cat.id_categorie
    db_session.add(livre)
    db_session.commit()
    ex = Exemplaire(code_barre="T1", etat="Disponible", statut_logique="Actif", id_livre=livre.id_livre)
    db_session.add(ex)
    db_session.commit()

    # Emprunt
    emp_data = {"id_membre": mem.id_membre, "id_exemplaire": ex.id_exemplaire, "id_bibliotecaire": 1}
    r = authorized_client.post("/emprunts/", json=emp_data)
    assert r.status_code in [200, 201]
    emp_id = r.json()["id_emprunt"]

    # Simulation retard
    emp_obj = db_session.get(Emprunt, emp_id)
    emp_obj.date_retour_prevue = date.today() - timedelta(days=5)
    db_session.commit()

    # Retour -> Amende
    r = authorized_client.put(f"/emprunts/{emp_id}/retour")
    assert r.status_code == 200
    assert "Sanction générée" in r.json()["message"]
    assert "500 FCFA" in r.json()["message"]

def test_prolongation_logic(member_client, authorized_client, db_session):
    # We need to be careful with double clients.
    # We will use member_client to prolong.
    # Setup
    livre = Livre(titre="P", id_categorie=1)
    cat = db_session.query(Categorie).first() or Categorie(nom_categorie="C", description="D")
    if not cat.id_categorie: db_session.add(cat); db_session.commit()
    livre.id_categorie = cat.id_categorie
    db_session.add(livre)
    db_session.commit()
    ex = Exemplaire(code_barre="P1", etat="Disponible", statut_logique="Actif", id_livre=livre.id_livre)
    db_session.add(ex)
    db_session.commit()
    
    # Need current member from member_client
    # In conftest, member_test has id_membre 1 usually
    mem = db_session.query(Membre).filter(Membre.login == "member_test").first()
    
    emp = Emprunt(id_membre=mem.id_membre, id_exemplaire=ex.id_exemplaire, id_bibliotecaire=1, statut="En cours", date_retour_prevue=date.today()+timedelta(days=7))
    db_session.add(emp)
    db_session.commit()

    # Prolongation
    r = member_client.patch(f"/emprunts/{emp.id_emprunt}/prolonger")
    # If 403, it means authorized_client overrode the token.
    # Let's see. If it fails, I'll use a different approach.
    assert r.status_code == 200
    assert r.json()["nouvelle_date_retour"] is not None
