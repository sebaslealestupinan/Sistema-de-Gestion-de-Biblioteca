from fastapi import APIRouter, Query
from typing import Optional
from db.database import sessionDep
from .schemas import CrearAutor, ActualizarAutor
from .crud import (
    ingresar_autor,
    ver_autores,
    ver_autor_libros,
    ver_autor_por_id,
    actualizar_autor_existente,
    mover_a_deposito,
    ver_deposito,
    buscar_autor_en_deposito,
    sacar_de_deposito
)

router = APIRouter(
    prefix="/autores",
    tags=["Autores"],
    responses={404: {"description": "No encontrado"}},
)

# 1. Crear autor
@router.post("/", summary="Crear un nuevo autor")
def crear_autor(data: CrearAutor, session: sessionDep):
    return ingresar_autor(data, session)


#2. Ver todos los autores o filtrar por país
@router.get("/", summary="Listar autores")
def listar_autores(
    session: sessionDep,
    pais: Optional[str] = Query(default=None, description="Filtrar por país de origen")
):
    return ver_autores(session, pais)


# 3. Ver autor y sus libros
@router.get("/{nombre_apellidos}", summary="Buscar un autor por nombre")
def obtener_autor(nombre_apellidos: str, session: sessionDep):
    return ver_autor_libros(nombre_apellidos, session)

@router.get("/{id_autor}", summary="Buscar un autor por id")
def obtener_por_id(id_autor: str, session: sessionDep):
    return ver_autor_por_id(id_autor, session)

#4. Actualizar autor existente
@router.put("/{nombre_apellidos}", summary="Actualizar datos del autor")
def actualizar_autor(nombre_apellidos: str, data: ActualizarAutor, session: sessionDep):
    return actualizar_autor_existente(session, data, nombre_apellidos)


#5. DEPÓSITO: Mover autores#
@router.delete("/deposito/{nombre_apellidos}", summary="Mover autor al depósito")
def eliminar_autor(nombre_apellidos: str, session: sessionDep):
    return mover_a_deposito(nombre_apellidos, session)


#6. DEPÓSITO: Ver todos
@router.get("/deposito/", summary="Listar autores en el depósito")
def listar_autores_deposito(session: sessionDep):
    return ver_deposito(session)


#7. DEPÓSITO: Buscar un autor
@router.get("/deposito/buscar/{nombre_apellidos}", summary="Buscar autor en el depósito")
def buscar_autor_deposito(nombre_apellidos: str, session: sessionDep):
    return buscar_autor_en_deposito(nombre_apellidos, session)


#8. Restaurar autor
@router.post("/deposito/restaurar/{nombre_apellidos}", summary="Restaurar autor al catálogo")
def restaurar_autor(nombre_apellidos: str, session: sessionDep):
    return sacar_de_deposito(nombre_apellidos, session)