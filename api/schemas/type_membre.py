from pydantic import ConfigDict, BaseModel


class TypeMembreBase(BaseModel):
    nom_type: str
    duree_max_emprunt: int
    nb_max_emprunt: int


class TypeMembreCreate(TypeMembreBase):
    pass


class TypeMembreOut(TypeMembreBase):
    id_type_membre: int

    model_config = ConfigDict(from_attributes=True)
