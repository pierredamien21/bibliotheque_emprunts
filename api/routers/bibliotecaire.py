from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.models import Bibliothecaire
from schemas.bibliothecaire import BibliothecaireCreate, BibliothecaireOut
from security import get_current_admin

router = APIRouter(prefix="/bibliothecaires", tags=["Bibliothecaires"])


@router.get("/", response_model=list[BibliothecaireOut])
def get_all(db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_admin)):
    return db.query(Bibliothecaire).all()


@router.get("/{id_bibliotecaire}", response_model=BibliothecaireOut)
def get_one(id_bibliotecaire: int, db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_admin)):
    obj = db.get(Bibliothecaire, id_bibliotecaire)
    if not obj:
        raise HTTPException(404, "Bibliothécaire introuvable")
    return obj


@router.post("/", response_model=BibliothecaireOut)
def create(data: BibliothecaireCreate, db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_admin)):
    from security import hash_password
    # Hash the password before storing
    data_dict = data.model_dump()
    if "mot_de_passe" in data_dict:
        data_dict["mot_de_passe_hash"] = hash_password(data_dict.pop("mot_de_passe"))
    obj = Bibliothecaire(**data_dict)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/{id_bibliotecaire}", response_model=BibliothecaireOut)
def update(id_bibliotecaire: int, data: BibliothecaireCreate, db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_admin)):
    from security import hash_password
    obj = db.get(Bibliothecaire, id_bibliotecaire)
    if not obj:
        raise HTTPException(404, "Bibliothécaire introuvable")
    data_dict = data.model_dump()
    # Hash the password if it's being updated
    if "mot_de_passe" in data_dict:
        data_dict["mot_de_passe_hash"] = hash_password(data_dict.pop("mot_de_passe"))
    for key, value in data_dict.items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.patch("/{id_bibliotecaire}/role")
def update_role(id_bibliotecaire: int, role: str, db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_admin)):
    if role not in ["Admin", "Agent"]:
        raise HTTPException(400, "Rôle invalide. Valeurs acceptées: 'Admin', 'Agent'")
    obj = db.get(Bibliothecaire, id_bibliotecaire)
    if not obj:
        raise HTTPException(404, "Bibliothécaire introuvable")
    obj.role = role
    db.commit()
    return {"message": f"Rôle mis à jour: {role}"}
