from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.models import Avis, Membre, Livre
from schemas.v2_schemas import AvisCreate, AvisOut
from security import get_current_user

router = APIRouter(prefix="/avis", tags=["Avis"])

@router.post("/", response_model=AvisOut)
def leave_avis(data: AvisCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if not isinstance(current_user, Membre):
        raise HTTPException(403, "Seuls les membres peuvent laisser un avis")
    
    # Check note
    if data.note < 1 or data.note > 5:
        raise HTTPException(400, "La note doit être entre 1 et 5")
    
    # Check if book exists
    if not db.get(Livre, data.id_livre):
        raise HTTPException(404, "Livre introuvable")

    obj = Avis(**data.model_dump(), id_membre=current_user.id_membre)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/livre/{id_livre}", response_model=list[AvisOut])
def get_avis_by_livre(id_livre: int, db: Session = Depends(get_db)):
    return db.query(Avis).filter(Avis.id_livre == id_livre).all()
