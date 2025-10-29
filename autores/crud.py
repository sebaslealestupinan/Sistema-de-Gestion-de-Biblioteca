from typing import Optional
from fastapi import HTTPException
from sqlmodel import select
from db.models import (
    Autor, Libro,
    DepositoAutores, DepositoLibro,
    LinkAutorLibro, LinkAutorLibroDeposito
)
from db.database import sessionDep
from .schemas import CrearAutor, ActualizarAutor


def ingresar_autor(data: CrearAutor, session: sessionDep):
    autor_existente = session.exec(
        select(Autor).where(Autor.nombre_apellidos == data.nombre_apellidos)
    ).first()

    if autor_existente:
        raise HTTPException(status_code=400, detail=f"El autor {data.nombre_apellidos} ya existe")

    autor = Autor.model_validate(data)
    session.add(autor)
    session.commit()
    session.refresh(autor)
    return {"message": f"El autor {autor.nombre_apellidos} fue creado correctamente"}

def ver_autores(session: sessionDep, pais: Optional[str] = None):
    query = select(Autor)
    if pais:
        query = query.where(Autor.pais_origen == pais)

    autores = session.exec(query).all()

    if not autores:
        raise HTTPException(status_code=404, detail=f"No se encontraron autores{f' de {pais}' if pais else ''}")

    return autores

def ver_autor_libros(nombre_apellidos: str, session: sessionDep):
    autor = session.exec(
        select(Autor).where(Autor.nombre_apellidos == nombre_apellidos)
    ).first()

    if not autor:
        raise HTTPException(status_code=404, detail=f"{nombre_apellidos} no existe")

    libros = autor.libros
    return {
        "autor": autor.nombre_apellidos,
        "libros": [{"titulo": l.titulo, "ISBN": l.ISBN} for l in libros],
        "cantidad": len(libros)
    }

def ver_autor_por_id(id_autor: str, session:sessionDep):
    autor = session.exec(select(Autor).where(Autor.id == id_autor)).first()
    if not autor:
        raise HTTPException(status_code=404, detail=f"{id_autor} no existe")
    libros = autor.libros
    return {
        "autor": autor.nombre_apellidos,
        "libros": [{"titulo": l.titulo, "ISBN": l.ISBN} for l in libros],
        "cantidad": len(libros)
    }

def actualizar_autor_existente(session: sessionDep, data: ActualizarAutor       , nombre_apellidos: str):
    autor = session.exec(
        select(Autor).where(Autor.nombre_apellidos == nombre_apellidos)
    ).first()

    if not autor:
        raise HTTPException(status_code=404, detail=f"{nombre_apellidos} no se encuentra")

    autor.descripcion = data.descripcion or autor.descripcion
    autor.año_muerte = data.año_muerte or autor.año_muerte
    session.add(autor)
    session.commit()
    return {"message": f"El autor {nombre_apellidos} fue actualizado correctamente"}

def mover_a_deposito(nombre_apellidos: str, session: sessionDep):
    autor_deposito = session.exec(select(DepositoAutores).
                                where(DepositoAutores.nombre_apellidos == nombre_apellidos)).first()
    Deposito= False
    if not autor_deposito:
        autor = session.exec(select(Autor).
                            where(Autor.nombre_apellidos == nombre_apellidos)).first()
        Deposito = True
        if not autor:
            raise HTTPException(status_code=404, detail="Autor no encontrado")

        autor_deposito = DepositoAutores(
            id_autor_original=autor.id,
            nombre_apellidos=autor.nombre_apellidos,
            pais_origen=autor.pais_origen,
            descripcion=autor.descripcion,
            año_nacimiento=autor.año_nacimiento,
            año_muerte=autor.año_muerte
        )
        session.add(autor_deposito)
        session.commit()
        session.refresh(autor_deposito)

    for libro in autor.libros:

        libro_en_deposito = session.exec(
            select(DepositoLibro).where(DepositoLibro.id_libro_original == libro.id)
        ).first()

        if not libro_en_deposito:
            libro_deposito = DepositoLibro(
                id_libro_original=libro.id,
                titulo=libro.titulo,
                resumen=libro.resumen,
                numero_paginas=libro.numero_paginas,
                editorial=libro.editorial,
                año_publicacion=libro.año_publicacion,
                copias_disponibles=libro.copias_disponibles,
                ISBN=libro.ISBN
            )
            session.add(libro_deposito)
            session.commit()
            session.refresh(libro_deposito)
        else:
            libro_deposito = libro_en_deposito

        session.add(
            LinkAutorLibroDeposito(
                id_libro_deposito=libro_deposito.id,
                id_autor_deposito=autor_deposito.id
            )
        )

    if Deposito:
        session.delete(autor)
        session.commit()

    return {"message": f"El autor {nombre_apellidos} y sus libros fueron movidos al depósito correctamente"}

def ver_deposito(session: sessionDep, pais: Optional[str] = None):
    query = select(DepositoAutores)
    if pais:
        query = query.where(Autor.pais_origen == pais)

    autores = session.exec(query).all()

    if not autores:
        raise HTTPException(status_code=404, detail=f"No se encontraron autores{f' de {pais}' if pais else ''}")

    return autores

def buscar_autor_en_deposito(nombre_apellidos: str, session:sessionDep):

    autor = session.exec(
        select(DepositoAutores).where(
            DepositoAutores.nombre_apellidos == nombre_apellidos)).first()

    if not autor:
        raise HTTPException(
            status_code=404,
            detail=f"El autor '{nombre_apellidos}' no está en el depósito"
        )

    libros = autor.libros

    return {
        "nombre_apellidos": autor.nombre_apellidos,
        "pais_origen": autor.pais_origen,
        "descripcion": autor.descripcion,
        "año_nacimiento": autor.año_nacimiento,
        "año_muerte": autor.año_muerte,
        "libros_asociados": [libro.titulo for libro in libros]
    }

def sacar_de_deposito(nombre: str, session: sessionDep):
    autor_deposito = session.exec(
        select(DepositoAutores).where(DepositoAutores.nombre_apellidos == nombre)
    ).first()

    if not autor_deposito:
        raise HTTPException(status_code=404, detail=f"{nombre} no está en el depósito")

    nuevo_autor = Autor(
        nombre_apellidos=autor_deposito.nombre_apellidos,
        pais_origen=autor_deposito.pais_origen,
        descripcion=autor_deposito.descripcion,
        año_nacimiento=autor_deposito.año_nacimiento,
        año_muerte=autor_deposito.año_muerte,
    )
    session.add(nuevo_autor)
    session.commit()
    session.refresh(nuevo_autor)

    relaciones = session.exec(
        select(LinkAutorLibroDeposito).where(LinkAutorLibroDeposito.id_autor_deposito == autor_deposito.id)
    ).all()

    for rel in relaciones:
        libro_deposito = session.exec(
            select(DepositoLibro).where(DepositoLibro.id == rel.id_libro_deposito)
        ).first()

        if libro_deposito:
            libro_restaurado = Libro(
                titulo=libro_deposito.titulo,
                resumen=libro_deposito.resumen,
                numero_paginas=libro_deposito.numero_paginas,
                editorial=libro_deposito.editorial,
                año_publicacion=libro_deposito.año_publicacion,
                copias_disponibles=libro_deposito.copias_disponibles,
                ISBN=libro_deposito.ISBN
            )
            session.add(libro_restaurado)
            session.commit()
            session.refresh(libro_restaurado)

            session.add(LinkAutorLibro(id_autor=nuevo_autor.id, id_libros=libro_restaurado.id))

    session.delete(autor_deposito)
    session.commit()

    return {"message": f"El autor {nombre} y sus libros fueron restaurados al catálogo correctamente"}