from pydantic import ConfigDict, BaseModel
from typing import Optional
from datetime import date
from decimal import Decimal


class SanctionCreate(BaseModel):
    type_sanction: str
    montant: Optional[Decimal] = None
    date_fin_suspension: Optional[date] = None
    statut: str
    id_membre: int
    id_emprunt: int
    id_bibliotecaire: int


class SanctionOut(SanctionCreate):
    id_sanction: int
    date_sanction: date

    model_config = ConfigDict(from_attributes=True)
