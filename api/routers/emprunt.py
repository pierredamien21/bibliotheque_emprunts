from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import DBAPIError
from database import get_db
from models.models import Emprunt, Membre, TypeMembre, Exemplaire
from schemas.emprunt import EmpruntCreate, EmpruntOut
from datetime import date, timedelta
from security import get_current_user, get_current_staff
from models.models import Bibliothecaire, Membre

router = APIRouter(prefix="/emprunts", tags=["Emprunts"])


@router.get("/", response_model=list[EmpruntOut])
def get_all(db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    return db.query(Emprunt).all()


@router.post("/", response_model=EmpruntOut)
def create(data: EmpruntCreate, db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    # 1. Vérifier le membre et ses droits
    membre = db.get(Membre, data.id_membre)
    if not membre:
        raise HTTPException(404, "Membre introuvable")

    # 1.1 Vérifier la limite d’emprunts
    type_membre = db.get(TypeMembre, membre.id_type_membre)
    if not type_membre:
         raise HTTPException(400, "Type de membre invalide")

    nb_emprunts_actifs = db.query(Emprunt).filter(
        Emprunt.id_membre == data.id_membre,
        Emprunt.statut == "En cours"
    ).count()

    if nb_emprunts_actifs >= type_membre.nb_max_emprunt:
        raise HTTPException(400, f"Limite d'emprunts atteinte ({type_membre.nb_max_emprunt} max)")

    # 2. Vérifier l'exemplaire
    exemplaire = db.get(Exemplaire, data.id_exemplaire)
    if not exemplaire:
        raise HTTPException(404, "Exemplaire introuvable")
    
    if exemplaire.etat != "Disponible":
        raise HTTPException(400, f"Exemplaire non disponible (Etat: {exemplaire.etat})")

    # 3. Création de l'emprunt
    # Calcul de la date de retour prévue
    date_retour = date.today() + timedelta(days=type_membre.duree_max_emprunt)
    
    obj = Emprunt(
        **data.model_dump(), 
        date_retour_prevue=date_retour
    )
    
    try:
        # A. Sauvegarder l'emprunt
        db.add(obj)
        
        # B. Mettre à jour l'état de l'exemplaire
        exemplaire.etat = "Emprunte"
        
        db.commit()
        db.refresh(obj)
        return obj
    except DBAPIError as e:
        db.rollback()
        raise HTTPException(400, str(e.orig))


@router.put("/{id_emprunt}/retour")
def retour(id_emprunt: int, db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    emp = db.get(Emprunt, id_emprunt)
    if not emp:
        raise HTTPException(404, "Emprunt introuvable")
    
    if emp.statut == "Termine":
        raise HTTPException(400, "Cet emprunt est déjà terminé")

    # 1. Mettre à jour l'emprunt
    emp.statut = "Termine"
    emp.date_retour_effective = date.today()
    
    # 2. Libérer l'exemplaire
    exemplaire = db.get(Exemplaire, emp.id_exemplaire)
    if exemplaire:
        exemplaire.etat = "Disponible"

    db.commit()
    return {"message": "Retour effectué"}


@router.get("/{id_emprunt}", response_model=EmpruntOut)
def get_one(id_emprunt: int, db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_user)):
    obj = db.get(Emprunt, id_emprunt)
    if not obj:
        raise HTTPException(404, "Emprunt introuvable")
    return obj


@router.get("/membre/{id_membre}", response_model=list[EmpruntOut])
def get_by_membre(id_membre: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if isinstance(current_user, Membre) and current_user.id_membre != id_membre:
        raise HTTPException(403, "Vous ne pouvez consulter que vos propres emprunts")
    return db.query(Emprunt).filter(Emprunt.id_membre == id_membre).all()
