from pydantic import ConfigDict, BaseModel, EmailStr, Field
from typing import Optional
from datetime import date


class MembreBase(BaseModel):
    numero_carte: str = Field(..., description="Numéro unique de la carte de membre", json_schema_extra={"example": "2023-001"})
    nom: str = Field(..., description="Nom de famille du membre", json_schema_extra={"example": "Dupont"})
    prenom: str = Field(..., description="Prénom du membre", json_schema_extra={"example": "Jean"})
    email: EmailStr = Field(..., description="Adresse email unique", json_schema_extra={"example": "jean.dupont@example.com"})
    telephone: Optional[str] = Field(None, description="Numéro de téléphone", json_schema_extra={"example": "+33612345678"})
    adresse: Optional[str] = Field(None, description="Adresse postale complète", json_schema_extra={"example": "123 Rue de la Paix, 75000 Paris"})
    date_naissance: Optional[date] = Field(None, description="Date de naissance")
    statut_compte: str = Field(..., description="Statut du compte (Actif, Suspendu)", json_schema_extra={"example": "Actif"})
    login: Optional[str] = Field(None, description="Nom d'utilisateur pour la connexion", json_schema_extra={"example": "jdupont"})
    id_type_membre: int = Field(..., description="ID du type de membre (ex: Étudiant, Enseignant)")


class MembreCreate(MembreBase):
    password: str = Field(..., description="Mot de passe en clair (sera haché)", min_length=8)


class MembreOut(MembreBase):
    id_membre: int = Field(..., description="Identifiant unique en base")
    date_inscription: date = Field(..., description="Date d'inscription automatique")
    derniere_connexion: Optional[date] = Field(None, description="Date de dernière connexion")

    model_config = ConfigDict(from_attributes=True)
