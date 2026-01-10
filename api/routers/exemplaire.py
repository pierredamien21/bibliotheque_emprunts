from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.models import Exemplaire
from schemas.exemplaire import ExemplaireCreate, ExemplaireOut
from security import get_current_staff
from models.models import Bibliothecaire

router = APIRouter(prefix="/exemplaires", tags=["Exemplaires"])


@router.get("/", response_model=list[ExemplaireOut])
def get_all(db: Session = Depends(get_db)):
    return db.query(Exemplaire).all()


@router.post("/", response_model=ExemplaireOut)
def create(data: ExemplaireCreate, db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    obj = Exemplaire(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{id_exemplaire}", response_model=ExemplaireOut)
def get_one(id_exemplaire: int, db: Session = Depends(get_db)):
    from fastapi import HTTPException
    obj = db.get(Exemplaire, id_exemplaire)
    if not obj:
        raise HTTPException(404, "Exemplaire introuvable")
    return obj


@router.put("/{id_exemplaire}", response_model=ExemplaireOut)
def update(id_exemplaire: int, data: ExemplaireCreate, db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    from fastapi import HTTPException
    obj = db.get(Exemplaire, id_exemplaire)
    if not obj:
        raise HTTPException(404, "Exemplaire introuvable")
    for key, value in data.model_dump().items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.patch("/{id_exemplaire}/etat")
def update_etat(id_exemplaire: int, etat: str, db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    from fastapi import HTTPException
    if etat not in ["Disponible", "Emprunte", "Reserve", "Abime"]:
        raise HTTPException(400, "État invalide. Valeurs: 'Disponible', 'Emprunte', 'Reserve', 'Abime'")
    obj = db.get(Exemplaire, id_exemplaire)
    if not obj:
        raise HTTPException(404, "Exemplaire introuvable")
    obj.etat = etat
    db.commit()
    return {"message": f"État mis à jour: {etat}"}
