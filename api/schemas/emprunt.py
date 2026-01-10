from pydantic import ConfigDict, BaseModel
from typing import Optional
from datetime import date


class EmpruntCreate(BaseModel):
    id_membre: int
    id_exemplaire: int
    id_bibliotecaire: int
    statut: str = "En cours"
    renouvellement_count: Optional[int] = 0
    commentaire: Optional[str] = None


class EmpruntOut(BaseModel):
    id_emprunt: int
    date_emprunt: date
    date_retour_prevue: Optional[date]
    date_retour_effective: Optional[date]
    statut: str
    renouvellement_count: int
    commentaire: Optional[str]
    id_membre: int
    id_exemplaire: int
    id_bibliotecaire: int

    model_config = ConfigDict(from_attributes=True)
