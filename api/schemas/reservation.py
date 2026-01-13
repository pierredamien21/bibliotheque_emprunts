from pydantic import ConfigDict, BaseModel
from datetime import date


from typing import Optional

class ReservationCreate(BaseModel):
    id_membre: Optional[int] = None
    id_livre: int
    id_bibliotecaire: Optional[int] = None
    priorite: int = 1
    statut: Optional[str] = "En attente"


class ReservationOut(BaseModel):
    id_reservation: int
    date_reservation: date
    statut: str
    priorite: int
    id_membre: int
    id_livre: int
    id_bibliotecaire: Optional[int]

    model_config = ConfigDict(from_attributes=True)
