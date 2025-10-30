from fastapi import APIRouter, Query
from typing import Optional
from db.database import sessionDep
from .schemas import CrearLibro, ActualizarLibro
from .crud import (
    ingresar_libro,
    ver_libro_titulo,
    ver_libros,
    actualizar_libro_existente,
    mover_a_deposito_libro,
    ver_deposito_libros,
    buscar_libro_en_deposito,
    sacar_libro_de_deposito
)

router = APIRouter(
    prefix="/libros",
    tags=["Libros"],
    responses={404: {"description": "No encontrado"}},
)

@router.post("/", summary="Crear nuevo libro")
def crear_libro(data: CrearLibro, session: sessionDep):
    return ingresar_libro(data, session)

@router.get("/", summary="Listar libros y/o filtrar por año")
def listar_libros(session: sessionDep,
                  año_publicacion: Optional[int] = Query(None, description="Filtrar por eaño")):
    return ver_libros(session, año_publicacion)

@router.get("/{titulo}", summary="Buscar un libro por el titulo")
def obtener_libro(titulo: str, session: sessionDep):
    return ver_libro_titulo(titulo, session)

@router.put("/{titulo}", summary="Actualizar información de un libro")
def actualizar_libro(titulo: str, data: ActualizarLibro, session: sessionDep):
    return actualizar_libro_existente(session, data, titulo)

@router.delete("/deposito/{titulo}", summary="Mover libro al depósito")
def eliminar_libro(titulo: str, session: sessionDep):
    return mover_a_deposito_libro(titulo, session)

@router.get("/deposito/", summary="Listar libros en el depósito")
def listar_libros_deposito(session: sessionDep):
    return ver_deposito_libros(session)

@router.get("/deposito/{titulo}", summary="Buscar libro en el depósito")
def buscar_libro_deposito(titulo: str, session: sessionDep):
    return buscar_libro_en_deposito(titulo, session)

@router.post("/deposito/sacar/{titulo}", summary="Restaurar libro al catálogo")
def restaurar_libro(titulo: str, session: sessionDep):
    return sacar_libro_de_deposito(titulo, session)