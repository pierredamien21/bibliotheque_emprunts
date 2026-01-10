from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.models import Livre
from schemas.livre import LivreCreate, LivreOut
from security import get_current_staff
from models.models import Bibliothecaire

router = APIRouter(prefix="/livres", tags=["Livres"])


@router.get("/", response_model=list[LivreOut])
def get_all(db: Session = Depends(get_db)):
    return db.query(Livre).all()


@router.post("/", response_model=LivreOut)
def create(data: LivreCreate, db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    obj = Livre(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{id_livre}", response_model=LivreOut)
def get_one(id_livre: int, db: Session = Depends(get_db)):
    from fastapi import HTTPException
    obj = db.get(Livre, id_livre)
    if not obj:
        raise HTTPException(404, "Livre introuvable")
    return obj


@router.put("/{id_livre}", response_model=LivreOut)
def update(id_livre: int, data: LivreCreate, db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    from fastapi import HTTPException
    obj = db.get(Livre, id_livre)
    if not obj:
        raise HTTPException(404, "Livre introuvable")
    for key, value in data.model_dump().items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj
@router.delete("/{id_livre}")
def delete(id_livre: int, db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    from fastapi import HTTPException
    obj = db.get(Livre, id_livre)
    if not obj:
        raise HTTPException(404, "Livre introuvable")
    db.delete(obj)
    db.commit()
    return {"message": "Livre supprimé avec succès"}
