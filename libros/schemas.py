from typing import Optional, List
from sqlmodel import SQLModel, Field


class CrearLibro(SQLModel):
    titulo: str
    resumen: Optional[str] = None
    numero_paginas: Optional[int] = None
    editorial: Optional[str] = None
    año_publicacion: Optional[int] = None
    copias_disponibles: int = 1
    ISBN: str
    nombre_autores: Optional[List[str]] = None


class ActualizarLibro(SQLModel):
    resumen: Optional[str] = None
    numero_paginas: Optional[int] = None
    editorial: Optional[str] = None
    año_publicacion: Optional[int] = None
    copias_disponibles: Optional[int] = None
