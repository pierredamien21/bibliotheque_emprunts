from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.models import Reservation
from schemas.reservation import ReservationCreate, ReservationOut
from security import get_current_staff, get_current_user
from models.models import Bibliothecaire, Membre

router = APIRouter(prefix="/reservations", tags=["Reservations"])


@router.get("/", response_model=list[ReservationOut])
def get_all(db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    return db.query(Reservation).all()


@router.post("/", response_model=ReservationOut)
def create(data: ReservationCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    from fastapi import HTTPException
    data_dict = data.model_dump()
    
    # Logic for Members: forced to their own id, and no librarian assigned yet
    if isinstance(current_user, Membre):
        data_dict["id_membre"] = current_user.id_membre
        data_dict["id_bibliotecaire"] = None
    
    # If it's staff, they must specify a member id (since it's optional in schema now)
    elif isinstance(current_user, Bibliothecaire):
        if data_dict.get("id_membre") is None:
            raise HTTPException(400, "Le champ 'id_membre' est obligatoire pour le staff")
            
        if data_dict.get("id_bibliotecaire") is None:
            data_dict["id_bibliotecaire"] = current_user.id_bibliotecaire

    obj = Reservation(**data_dict)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{id_reservation}", response_model=ReservationOut)
def get_one(id_reservation: int, db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    from fastapi import HTTPException
    obj = db.get(Reservation, id_reservation)
    if not obj:
        raise HTTPException(404, "Réservation introuvable")
    return obj


@router.patch("/{id_reservation}/statut")
def update_statut(id_reservation: int, statut: str, db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    from fastapi import HTTPException
    if statut not in ["En attente", "Confirmee", "Annulee"]:
        raise HTTPException(400, "Statut invalide. Valeurs: 'En attente', 'Confirmee', 'Annulee'")
    obj = db.get(Reservation, id_reservation)
    if not obj:
        raise HTTPException(404, "Réservation introuvable")
    obj.statut = statut
    db.commit()
    return {"message": f"Statut mis à jour: {statut}"}
