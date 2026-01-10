from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.models import Categorie
from schemas.categorie import CategorieCreate, CategorieOut
from security import get_current_staff
from models.models import Bibliothecaire

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", response_model=list[CategorieOut])
def get_all(db: Session = Depends(get_db)):
    return db.query(Categorie).all()


@router.post("/", response_model=CategorieOut)
def create(data: CategorieCreate, db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    obj = Categorie(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{id_categorie}", response_model=CategorieOut)
def get_one(id_categorie: int, db: Session = Depends(get_db)):
    from fastapi import HTTPException
    obj = db.get(Categorie, id_categorie)
    if not obj:
        raise HTTPException(404, "Catégorie introuvable")
    return obj


@router.put("/{id_categorie}", response_model=CategorieOut)
def update(id_categorie: int, data: CategorieCreate, db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    from fastapi import HTTPException
    obj = db.get(Categorie, id_categorie)
    if not obj:
        raise HTTPException(404, "Catégorie introuvable")
    for key, value in data.model_dump().items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{id_categorie}")
def delete(id_categorie: int, db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    from fastapi import HTTPException
    obj = db.get(Categorie, id_categorie)
    if not obj:
        raise HTTPException(404, "Catégorie introuvable")
    db.delete(obj)
    db.commit()
    return {"message": "Catégorie supprimée"}
