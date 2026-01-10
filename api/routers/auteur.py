from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.models import Auteur
from schemas.auteur import AuteurCreate, AuteurOut
from security import get_current_staff
from models.models import Bibliothecaire

router = APIRouter(prefix="/auteurs", tags=["Auteurs"])


@router.get("/", response_model=list[AuteurOut])
def get_all(db: Session = Depends(get_db)):
    return db.query(Auteur).all()


@router.post("/", response_model=AuteurOut)
def create(data: AuteurCreate, db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    obj = Auteur(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{id_auteur}", response_model=AuteurOut)
def get_one(id_auteur: int, db: Session = Depends(get_db)):
    from fastapi import HTTPException
    obj = db.get(Auteur, id_auteur)
    if not obj:
        raise HTTPException(404, "Auteur introuvable")
    return obj


@router.put("/{id_auteur}", response_model=AuteurOut)
def update(id_auteur: int, data: AuteurCreate, db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    from fastapi import HTTPException
    obj = db.get(Auteur, id_auteur)
    if not obj:
        raise HTTPException(404, "Auteur introuvable")
    for key, value in data.model_dump().items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{id_auteur}")
def delete(id_auteur: int, db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    from fastapi import HTTPException
    obj = db.get(Auteur, id_auteur)
    if not obj:
        raise HTTPException(404, "Auteur introuvable")
    db.delete(obj)
    db.commit()
    return {"message": "Auteur supprimé"}
