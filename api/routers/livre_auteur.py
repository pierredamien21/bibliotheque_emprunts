from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.models import LivreAuteur
from schemas.livre_auteur import LivreAuteurCreate, LivreAuteurOut

router = APIRouter(prefix="/livres-auteurs", tags=["Livre-Auteur"])


@router.get("/", response_model=list[LivreAuteurOut])
def get_all(db: Session = Depends(get_db)):
    return db.query(LivreAuteur).all()


@router.post("/", response_model=LivreAuteurOut)
def create(data: LivreAuteurCreate, db: Session = Depends(get_db)):
    obj = LivreAuteur(**data.model_dump())
    db.add(obj)
    db.commit()
    return obj


@router.delete("/")
def delete(id_livre: int, id_auteur: int, db: Session = Depends(get_db)):
    from fastapi import HTTPException
    obj = db.query(LivreAuteur).filter(
        LivreAuteur.id_livre == id_livre,
        LivreAuteur.id_auteur == id_auteur
    ).first()
    if not obj:
        raise HTTPException(404, "Association livre-auteur introuvable")
    db.delete(obj)
    db.commit()
    return {"message": "Association supprimée"}
