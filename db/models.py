"""
models.py
---------
Define los modelos de base de datos utilizando SQLModel, incluyendo las tablas
principales (Autor, Libro) y sus versiones históricas en el depósito
(DepositoAutores, DepositoLibro), así como las tablas intermedias que
establecen relaciones N:M entre autores y libros.
"""

from datetime import datetime, UTC
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class LinkAutorLibroDeposito(SQLModel, table=True):
    """
    Representa la relación N:M entre autores y libros en el depósito.
    Guarda el historial de las asociaciones originales.
    """
    id_libro_deposito: Optional[int] = Field(default=None, foreign_key="depositolibro.id", primary_key=True)
    id_autor_deposito: Optional[int] = Field(default=None, foreign_key="depositoautores.id", primary_key=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class LinkAutorLibro(SQLModel, table=True):
    """
    Tabla intermedia que relaciona autores con libros activos (catálogo).
    """
    id_libros: Optional[int] = Field(default=None, foreign_key="libro.id", primary_key=True)
    id_autor: Optional[int] = Field(default=None, foreign_key="autor.id", primary_key=True)


class Autor(SQLModel, table=True):
    """
    Representa a un autor activo en el catálogo.
    """
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


class Libro(SQLModel, table=True):
    """
    Representa un libro activo en el catálogo.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str = Field(unique=True)
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


class DepositoAutores(SQLModel, table=True):
    """
    Contiene una copia histórica de los autores eliminados o trasladados del catálogo.
    """
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


class DepositoLibro(SQLModel, table=True):
    """
    Contiene una copia histórica de los libros eliminados o trasladados del catálogo.
    """
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

    autores: List["DepositoAutores"] = Relationship(
        back_populates="libros",
        link_model=LinkAutorLibroDeposito
    )