from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import DBAPIError
from database import get_db
from models.models import Emprunt, Membre, TypeMembre, Exemplaire, Sanction, Reservation
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

    today = date.today()
    
    # 1. Calcul des amendes si retard
    sanction_msg = ""
    if today > emp.date_retour_prevue:
        retard_jours = (today - emp.date_retour_prevue).days
        montant = retard_jours * 100 # 100 FCFA par jour
        
        nueva_sanction = Sanction(
            type_sanction="Retard",
            montant=montant,
            statut="Non payee",
            id_membre=emp.id_membre,
            id_emprunt=emp.id_emprunt,
            id_bibliotecaire=current_user.id_bibliotecaire
        )
        db.add(nueva_sanction)
        sanction_msg = f" | Sanction générée : {montant} FCFA ({retard_jours} jours de retard)"

    # 2. Mettre à jour l'emprunt
    emp.statut = "Termine"
    emp.date_retour_effective = today
    
    # 3. Libérer l'exemplaire
    exemplaire = db.get(Exemplaire, emp.id_exemplaire)
    if exemplaire:
        exemplaire.etat = "Disponible"

    db.commit()
    return {"message": f"Retour effectué{sanction_msg}"}


@router.patch("/{id_emprunt}/prolonger")
def prolonger(id_emprunt: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    emp = db.get(Emprunt, id_emprunt)
    if not emp:
        raise HTTPException(404, "Emprunt introuvable")
    
    # Restriction : Seul le membre concerné ou le staff peut prolonger
    if isinstance(current_user, Membre) and emp.id_membre != current_user.id_membre:
        raise HTTPException(403, "Vous ne pouvez prolonger que vos propres emprunts")
    
    if emp.statut != "En cours":
        raise HTTPException(400, f"Prolongation impossible : l'emprunt est en statut '{emp.statut}'")
    
    if emp.renouvellement_count >= 1:
        raise HTTPException(400, "Limite de prolongation atteinte (max 1)")
    
    # Vérifier si le livre est réservé
    # On récupère le id_livre via l'exemplaire
    exemplaire = db.get(Exemplaire, emp.id_exemplaire)
    res_active = db.query(Reservation).filter(
        Reservation.id_livre == exemplaire.id_livre,
        Reservation.statut == "En attente"
    ).first()
    
    if res_active:
        raise HTTPException(400, "Prolongation impossible : ce livre est réservé par un autre membre")

    # Prolongation de 7 jours
    emp.date_retour_prevue = emp.date_retour_prevue + timedelta(days=7)
    emp.renouvellement_count += 1
    
    db.commit()
    return {
        "message": "Emprunt prolongé de 7 jours", 
        "nouvelle_date_retour": emp.date_retour_prevue
    }


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
