from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from models.models import Livre, Bibliothecaire
from security import get_current_staff
import os
import shutil
import uuid

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "covers")

@router.post("/livre/{id_livre}")
async def upload_book_cover(
    id_livre: int, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user: Bibliothecaire = Depends(get_current_staff)
):
    # 1. Vérifier si le livre existe
    livre = db.get(Livre, id_livre)
    if not livre:
        raise HTTPException(404, "Livre introuvable")

    # 2. Valider le type de fichier
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "Le fichier doit être une image")

    # 3. Créer le dossier s'il n'existe pas
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # 4. Générer un nom de fichier unique
    extension = file.filename.split(".")[-1]
    filename = f"book_{id_livre}_{uuid.uuid4().hex[:8]}.{extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    # 5. Enregistrer le fichier physiquement
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(500, f"Erreur lors de l'enregistrement du fichier: {str(e)}")

    # 6. Mettre à jour l'URL dans la base de données
    # L'URL sera relative, ex: /static/covers/filename.jpg
    relative_url = f"/static/covers/{filename}"
    livre.image_url = relative_url
    db.commit()

    return {
        "message": "Image uploadée avec succès",
        "image_url": relative_url
    }
