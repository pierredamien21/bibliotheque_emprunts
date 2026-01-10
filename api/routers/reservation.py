from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.models import Reservation
from schemas.reservation import ReservationCreate, ReservationOut
from security import get_current_staff
from models.models import Bibliothecaire

router = APIRouter(prefix="/reservations", tags=["Reservations"])


@router.get("/", response_model=list[ReservationOut])
def get_all(db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    return db.query(Reservation).all()


@router.post("/", response_model=ReservationOut)
def create(data: ReservationCreate, db: Session = Depends(get_db), current_user: Bibliothecaire = Depends(get_current_staff)):
    obj = Reservation(**data.model_dump())
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
