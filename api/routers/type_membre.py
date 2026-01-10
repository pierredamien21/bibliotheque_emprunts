from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.models import TypeMembre
from schemas.type_membre import TypeMembreCreate, TypeMembreOut
from security import get_current_staff
from models.models import Bibliothecaire

router = APIRouter(prefix="/types-membre", tags=["Types Membre"])


@router.get("/", response_model=list[TypeMembreOut])
def get_all(db: Session = Depends(get_db)):
    return db.query(TypeMembre).all()


@router.post("/", response_model=TypeMembreOut)
def create(data: TypeMembreCreate, db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    obj = TypeMembre(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{id_type_membre}", response_model=TypeMembreOut)
def get_one(id_type_membre: int, db: Session = Depends(get_db)):
    obj = db.get(TypeMembre, id_type_membre)
    if not obj:
        raise HTTPException(404, "Type membre introuvable")
    return obj


@router.put("/{id_type_membre}", response_model=TypeMembreOut)
def update(id_type_membre: int, data: TypeMembreCreate, db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    obj = db.get(TypeMembre, id_type_membre)
    if not obj:
        raise HTTPException(404, "Type membre introuvable")
    for key, value in data.model_dump().items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj
