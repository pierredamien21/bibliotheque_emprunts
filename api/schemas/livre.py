from pydantic import ConfigDict, BaseModel, Field
from typing import Optional
from datetime import date


class LivreBase(BaseModel):
    titre: str = Field(..., description="Titre complet du livre", json_schema_extra={"example": "Les Misérables"})
    descriptions: Optional[str] = Field(None, description="Résumé ou description du livre")
    isbn: Optional[str] = Field(None, description="Code ISBN (International Standard Book Number)", json_schema_extra={"example": "978-0-123-45678-9"})
    editeur: Optional[str] = Field(None, description="Maison d'édition", json_schema_extra={"example": "Gallimard"})
    langue: Optional[str] = Field(None, description="Langue du livre", json_schema_extra={"example": "Français"})
    annee_publication: Optional[int] = Field(None, description="Année de publication", json_schema_extra={"example": 1862})
    id_categorie: int = Field(..., description="ID de la catégorie associée")
    image_url: Optional[str] = Field(None, description="URL de la couverture du livre", json_schema_extra={"example": "https://images.com/book.jpg"})


class LivreCreate(LivreBase):
    pass


from typing import Optional

class LivreOut(LivreBase):
    id_livre: int = Field(..., description="Identifiant unique du livre")
    date_ajout_catalogue: date = Field(..., description="Date d'ajout au catalogue")
    nb_disponible: Optional[int] = Field(0, description="Nombre d'exemplaires disponibles")

    model_config = ConfigDict(from_attributes=True)
