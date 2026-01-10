from pydantic import ConfigDict, BaseModel
from typing import Optional
from datetime import date


class ExemplaireBase(BaseModel):
    code_barre: str
    etat: str
    statut_logique: str
    date_acquisition: Optional[date] = None
    localisation: Optional[str] = None
    id_livre: int


class ExemplaireCreate(ExemplaireBase):
    pass


class ExemplaireOut(ExemplaireBase):
    id_exemplaire: int

    model_config = ConfigDict(from_attributes=True)
