from typing import Optional, List
from sqlmodel import Field, SQLModel


class CrearAutor(SQLModel):
    nombre_apellidos: str = Field(min_length=2, max_length=50)
    pais_origen: str
    descripcion: str = Field(
        default="Aún no se conoce mucho de este autor",
        min_length=2,
        max_length=200
    )
    año_nacimiento: str
    año_muerte: Optional[str] = Field(
        default="Este autor aún sigue con vida",
        max_length=50
    )

class ActualizarAutor(SQLModel):
    descripcion: Optional[str] = Field(default=None, min_length=2, max_length=200)
    año_muerte: Optional[str] = Field(default=None, max_length=50)