from pydantic import ConfigDict, BaseModel
from typing import Optional


class CategorieBase(BaseModel):
    nom_categorie: str
    description: Optional[str] = None


class CategorieCreate(CategorieBase):
    pass


class CategorieOut(CategorieBase):
    id_categorie: int

    model_config = ConfigDict(from_attributes=True)
