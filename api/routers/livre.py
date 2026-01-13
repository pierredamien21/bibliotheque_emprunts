from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.models import Livre, Exemplaire, Bibliothecaire
from schemas.livre import LivreCreate, LivreOut
from security import get_current_staff

router = APIRouter(prefix="/livres", tags=["Livres"])


@router.get("/", response_model=list[LivreOut])
def get_all(
    titre: Optional[str] = None, 
    id_categorie: Optional[int] = None, 
    db: Session = Depends(get_db)
):
    query = db.query(Livre)
    if titre:
        query = query.filter(Livre.titre.ilike(f"%{titre}%"))
    if id_categorie:
        query = query.filter(Livre.id_categorie == id_categorie)
    
    livres = query.all()
    
    # Calculate availability for each book
    result = []
    for livre in livres:
        nb_dispo = db.query(Exemplaire).filter(
            Exemplaire.id_livre == livre.id_livre,
            Exemplaire.etat == "Disponible",
            Exemplaire.statut_logique == "Actif"
        ).count()
        
        # We need to add nb_disponible to the object for Pydantic to pick it up
        livre_dict = {c.name: getattr(livre, c.name) for c in livre.__table__.columns}
        livre_dict["nb_disponible"] = nb_dispo
        result.append(livre_dict)
        
    return result


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
