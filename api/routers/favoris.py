from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.models import Favoris, Membre, Livre
from schemas.v2_schemas import FavorisOut, FavorisCreate
from security import get_current_user

router = APIRouter(prefix="/favoris", tags=["Favoris"])

@router.post("/", response_model=FavorisOut)
def add_favori(data: FavorisCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if not isinstance(current_user, Membre):
        raise HTTPException(403, "Seuls les membres gèrent des favoris")
    
    # Check if book exists
    if not db.get(Livre, data.id_livre):
        raise HTTPException(404, "Livre introuvable")
    
    # Check if already in favorites
    exists = db.query(Favoris).filter(Favoris.id_membre == current_user.id_membre, Favoris.id_livre == data.id_livre).first()
    if exists:
        return exists

    obj = Favoris(id_membre=current_user.id_membre, id_livre=data.id_livre)
    db.add(obj)
    db.commit()
    return obj

@router.get("/", response_model=list[FavorisOut])
def get_my_favoris(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if not isinstance(current_user, Membre):
         raise HTTPException(403, "Seuls les membres gèrent des favoris")
    return db.query(Favoris).filter(Favoris.id_membre == current_user.id_membre).all()

@router.delete("/{id_livre}")
def remove_favori(id_livre: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if not isinstance(current_user, Membre):
        raise HTTPException(403, "Seuls les membres gèrent des favoris")
        
    obj = db.query(Favoris).filter(Favoris.id_membre == current_user.id_membre, Favoris.id_livre == id_livre).first()
    if not obj:
        raise HTTPException(404, "Favori introuvable")
    
    db.delete(obj)
    db.commit()
    return {"message": "Livre retiré des favoris"}
