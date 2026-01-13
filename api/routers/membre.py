from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.models import Membre
from schemas.membre import MembreCreate, MembreOut
from security import get_current_staff, hash_password
from models.models import Bibliothecaire

router = APIRouter(prefix="/membres", tags=["Membres"])


@router.get("/", response_model=list[MembreOut])
def get_all(db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    return db.query(Membre).all()


@router.get("/{id_membre}", response_model=MembreOut)
def get_one(id_membre: int, db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    obj = db.get(Membre, id_membre)
    if not obj:
        raise HTTPException(404, "Membre introuvable")
    return obj


    from sqlalchemy.exc import IntegrityError
    try:
        obj = Membre(**data_dict)
        obj.mot_de_passe_hash = hash_password(password)
        
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Un membre avec cet email, ce numéro de carte ou ce login existe déjà."
        )


@router.put("/{id_membre}", response_model=MembreOut)
def update(id_membre: int, data: MembreCreate, db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    obj = db.get(Membre, id_membre)
    if not obj:
        raise HTTPException(404, "Membre introuvable")
    
    data_dict = data.model_dump()
    password = data_dict.pop("password")
    
    for key, value in data_dict.items():
        setattr(obj, key, value)
    
    obj.mot_de_passe_hash = hash_password(password)
    
    db.commit()
    db.refresh(obj)
    return obj


@router.patch("/{id_membre}/statut")
def update_statut(id_membre: int, statut: str, db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    if statut not in ["Actif", "Suspendu"]:
        raise HTTPException(400, "Statut invalide. Valeurs acceptées: 'Actif', 'Suspendu'")
    obj = db.get(Membre, id_membre)
    if not obj:
        raise HTTPException(404, "Membre introuvable")
    obj.statut_compte = statut
    db.commit()
    return {"message": f"Statut mis à jour: {statut}"}
@router.delete("/{id_membre}")
def delete(id_membre: int, db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    obj = db.get(Membre, id_membre)
    if not obj:
        raise HTTPException(404, "Membre introuvable")
    
    # Check for active loans
    from models.models import Emprunt
    active_loans = db.query(Emprunt).filter(
        Emprunt.id_membre == id_membre,
        Emprunt.statut.in_(["En cours", "Retard"])
    ).count()
    
    if active_loans > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Impossible de supprimer le membre : il a {active_loans} emprunt(s) en cours ou en retard."
        )
    
    db.delete(obj)
    db.commit()
    return {"message": "Membre supprimé avec succès"}
