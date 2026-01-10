from pydantic import ConfigDict, BaseModel
from datetime import date


class ReservationCreate(BaseModel):
    id_membre: int
    id_livre: int
    id_bibliotecaire: int
    priorite: int
    statut: str


class ReservationOut(BaseModel):
    id_reservation: int
    date_reservation: date
    statut: str
    priorite: int
    id_membre: int
    id_livre: int
    id_bibliotecaire: int

    model_config = ConfigDict(from_attributes=True)
