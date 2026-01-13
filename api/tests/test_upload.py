import pytest
import io
import os
from models.models import Livre, Categorie

def test_upload_book_cover(authorized_client, db_session):
    # 1. Setup : Créer un livre de test
    cat = Categorie(nom_categorie="Test Upload", description="...")
    db_session.add(cat)
    db_session.commit()
    
    livre = Livre(titre="Livre de Test Upload", id_categorie=cat.id_categorie)
    db_session.add(livre)
    db_session.commit()
    
    # 2. Préparer un fichier image factice
    file_content = b"fake image content"
    file_name = "test_cover.jpg"
    files = {"file": (file_name, io.BytesIO(file_content), "image/jpeg")}
    
    # 3. Exécuter la requête d'upload (en tant que Staff)
    response = authorized_client.post(f"/upload/livre/{livre.id_livre}", files=files)
    
    # 4. Assertions sur la réponse
    assert response.status_code == 200
    data = response.json()
    assert "image_url" in data
    assert data["image_url"].startswith("/static/covers/")
    
    # 5. Vérifier la présence du fichier sur le disque
    filename = data["image_url"].split("/")[-1]
    # UPLOAD_DIR is api/static/covers relative to project root
    file_path = os.path.join("api", "static", "covers", filename)
    assert os.path.exists(file_path)
    
    # 6. Vérifier la mise à jour en base de données
    db_session.refresh(livre)
    assert livre.image_url == data["image_url"]

def test_upload_invalid_file_type(authorized_client, db_session):
    # 1. Setup : Créer un livre
    livre = Livre(titre="Livre Test Type", id_categorie=1)
    db_session.add(livre)
    db_session.commit()
    
    # 2. Préparer un fichier non-image
    files = {"file": ("test.txt", io.BytesIO(b"not an image"), "text/plain")}
    
    # 3. Exécuter la requête
    response = authorized_client.post(f"/upload/livre/{livre.id_livre}", files=files)
    
    # 4. Vérifier l'erreur 400
    assert response.status_code == 400
    assert "doit être une image" in response.json()["detail"]
