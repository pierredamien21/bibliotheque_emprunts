import pytest
from models.models import Message, Livre, Categorie, Emprunt, Exemplaire, TypeMembre, Membre, Bibliothecaire
from security import hash_password

def test_internal_messaging_flow(member_client, db_session):
    # 1. Membre envoie un message (member_client est déjà authentifié)
    resp = member_client.post("/messages/", json={"contenu": "Bonjour, avez-vous le tome 2 de Dune ?"})
    assert resp.status_code == 200
    msg_id = resp.json()["id_message"]
    
    # 2. Staff répond au message
    # Au lieu d'utiliser authorized_client (qui conflit), on va tricher en changeant le token du member_client
    from security import create_access_token
    from models.models import Bibliothecaire
    bib = db_session.query(Bibliothecaire).first()
    if not bib:
        from security import hash_password
        bib = Bibliothecaire(matricule="B-SEC", nom="S", prenom="S", email="s@s.com", login="staff_sec", mot_de_passe_hash=hash_password("123"), role="Agent")
        db_session.add(bib)
        db_session.commit()
    
    admin_token = create_access_token(data={"sub": bib.login, "role": bib.role})
    member_client.headers["Authorization"] = f"Bearer {admin_token}"
    
    resp_reply = member_client.patch(f"/messages/{msg_id}/repondre", json={"reponse": "Oui, il est disponible."})
    assert resp_reply.status_code == 200
    assert resp_reply.json()["statut"] == "Repondu"

def test_recommendations_logic(member_client, authorized_client, db_session):
    # Setup : On s'assure d'avoir tout en DB
    # member_client a déjà créé un membre et type_membre
    member = db_session.query(Membre).first()
    bib = db_session.query(Bibliothecaire).first()
    
    cat = Categorie(nom_categorie="Science-Fiction", description="Test SF")
    db_session.add(cat)
    db_session.commit()
    
    livre1 = Livre(titre="Dune", id_categorie=cat.id_categorie)
    livre2 = Livre(titre="Foundation", id_categorie=cat.id_categorie)
    db_session.add_all([livre1, livre2])
    db_session.commit()
    
    # Simuler un exemplaire actif
    ex = Exemplaire(id_livre=livre1.id_livre, code_barre="DUNE_REC", etat="Disponible", statut_logique="Actif")
    db_session.add(ex)
    db_session.commit()
    
    # Créer un emprunt terminé pour livre1
    emp = Emprunt(id_membre=member.id_membre, id_exemplaire=ex.id_exemplaire, id_bibliotecaire=bib.id_bibliotecaire, statut="Termine")
    db_session.add(emp)
    db_session.commit()
    
    # Demander des recommandations
    resp = member_client.get("/livres/recommandations")
    assert resp.status_code == 200
    recomms = resp.json()
    
    # Vérifications
    assert len(recomms) > 0
    titres = [r["titre"] for r in recomms]
    assert "Foundation" in titres
    assert "Dune" not in titres
