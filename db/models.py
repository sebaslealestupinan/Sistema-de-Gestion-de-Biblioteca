from datetime import datetime, UTC
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

# Tabla intermedia: relación N:M entre autores y libros
class LinkAutorLibroDeposito(SQLModel, table=True):
    id_libro_deposito: Optional[int] = Field(default=None, foreign_key="depositolibro.id", primary_key=True)
    id_autor_deposito: Optional[int] = Field(default=None, foreign_key="depositoautores.id", primary_key=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

#Tabla intermedia: relación N:M entre autores y libros
class LinkAutorLibro(SQLModel, table=True):
    id_libros: Optional[int] = Field(
        default=None, foreign_key="libro.id", primary_key=True
    )
    id_autor: Optional[int] = Field(
        default=None, foreign_key="autor.id", primary_key=True
    )

#Tabla de autores activos
class Autor(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre_apellidos: str = Field(index=True, unique=True)
    pais_origen: str
    descripcion: str
    año_nacimiento: str
    año_muerte: Optional[str] = None

    libros: List["Libro"] = Relationship(
        back_populates="autores",
        link_model=LinkAutorLibro
    )


#Tabla de libros activos
class Libro(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str
    resumen: Optional[str] = None
    numero_paginas: Optional[int] = None
    editorial: Optional[str] = None
    año_publicacion: Optional[int] = None
    copias_disponibles: int = Field(default=0)
    ISBN: str = Field(unique=True, index=True)

    autores: List[Autor] = Relationship(
        back_populates="libros",
        link_model=LinkAutorLibro
    )


# Tabla histórica de autores
class DepositoAutores(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    id_autor_original: int
    nombre_apellidos: str
    pais_origen: str
    descripcion: str
    año_nacimiento: str
    año_muerte: Optional[str] = None

    libros: List["DepositoLibro"] = Relationship(
        back_populates="autores",
        link_model=LinkAutorLibroDeposito
    )


# Tabla histórica de libros
class DepositoLibro(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    id_libro_original: int
    titulo: str
    resumen: Optional[str] = None
    numero_paginas: Optional[int] = None
    editorial: Optional[str] = None
    año_publicacion: Optional[int] = None
    copias_disponibles: int
    ISBN: str
    autores: List["DepositoAutores"] = Relationship(back_populates="libros", link_model=LinkAutorLibroDeposito)