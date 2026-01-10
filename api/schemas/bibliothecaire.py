from pydantic import ConfigDict, BaseModel, EmailStr
from typing import Optional


class BibliothecaireBase(BaseModel):
    matricule: str
    nom: str
    prenom: str
    email: EmailStr
    telephone: Optional[str] = None
    login: str
    role: str


class BibliothecaireCreate(BibliothecaireBase):
    mot_de_passe: str  # Plain password, will be hashed by the router


class BibliothecaireOut(BibliothecaireBase):
    id_bibliotecaire: int

    model_config = ConfigDict(from_attributes=True)
