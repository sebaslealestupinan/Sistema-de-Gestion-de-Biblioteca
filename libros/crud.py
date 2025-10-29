from typing import Optional
from fastapi import HTTPException
from sqlmodel import select
from db.models import (
    Libro, Autor,
    DepositoLibro, DepositoAutores,
    LinkAutorLibro, LinkAutorLibroDeposito
)
from db.database import sessionDep
from .schemas import CrearLibro, ActualizarLibro


# Crear libro nuevo
def ingresar_libro(datos: CrearLibro, session: sessionDep):

    existente = session.exec(select(Libro).where(Libro.ISBN == datos.ISBN)).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe un libro con ese ISBN")

    nuevo_libro = Libro(
        titulo=datos.titulo,
        resumen=datos.resumen,
        numero_paginas=datos.numero_paginas,
        editorial=datos.editorial,
        año_publicacion=datos.año_publicacion,
        copias_disponibles=datos.copias_disponibles,
        ISBN=datos.ISBN,
    )
    session.add(nuevo_libro)
    session.commit()
    session.refresh(nuevo_libro)

    if datos.nombre_autores:
        for nombre in datos.nombre_autores:
            autor = session.exec(select(Autor).where(Autor.nombre_apellidos == nombre)).first()
            if not autor:
                raise HTTPException(status_code=404, detail=f"El autor {nombre} no se esta registrado en la bibliote caencontrado")

            link = LinkAutorLibro(id_libros=nuevo_libro.id, id_autor=autor.id)
            session.add(link)

        session.commit()

    return {
        "mensaje": "Libro creado correctamente",
        "libro": nuevo_libro,
        "autores_vinculados": datos.nombre_autores,
    }


# Ver todos los libros o filtrar por año de publicacion
def ver_libros(año_publicacion: Optional[int], session: sessionDep):
    query = select(Libro)
    if año_publicacion:
        query = query.where(Libro.año_publicacion == año_publicacion)

    libros = session.exec(query).all()

    if not libros:
        raise HTTPException(status_code=404, detail="No se encontraron libros para ese año")

    return libros


# Buscar un libro por su titulo
def ver_libro_titulo(titulo: str, session: sessionDep):
    libro = session.exec(select(Libro).where(Libro.titulo == titulo)).first()
    if not libro:
        raise HTTPException(status_code=404, detail=f"El libro '{titulo}' no existe")

    autores = libro.autores
    return {
        "titulo": libro.titulo,
        "autores": [{"nombre": a.nombre_apellidos, "pais": a.pais_origen} for a in autores],
        "resumen": libro.resumen,
        "numero_paginas": libro.numero_paginas,
        "editorial": libro.editorial,
        "año_publicacion": libro.año_publicacion,
        "copias_disponibles": libro.copias_disponibles,
        "ISBN": libro.ISBN
    }

# Buscar un libro por su id
def ver_libro_id(id_libro: int, session: sessionDep):
    libro = session.exec(select(Libro).where(Libro.id == id_libro)).first()
    if not libro:
        raise HTTPException(status_code=404, detail=f"El libro con '{id}' no existe")

    autores = libro.autores
    return {
        "titulo": libro.titulo,
        "autores": [{"nombre": a.nombre_apellidos, "pais": a.pais_origen} for a in autores],
        "resumen": libro.resumen,
        "numero_paginas": libro.numero_paginas,
        "editorial": libro.editorial,
        "año_publicacion": libro.año_publicacion,
        "copias_disponibles": libro.copias_disponibles,
        "ISBN": libro.ISBN
    }

# Actualizar datos del libro
def actualizar_libro_existente(session: sessionDep, data: ActualizarLibro, titulo: str):
    libro = session.exec(select(Libro).where(Libro.titulo == titulo)).first()
    if not libro:
        raise HTTPException(status_code=404, detail=f"El libro '{titulo}' no existe")

    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(libro, campo, valor)

    session.add(libro)
    session.commit()
    return {"message": f"El libro '{titulo}' fue actualizado correctamente"}


# Mover libro al depósito
def mover_a_deposito_libro(titulo: str, session: sessionDep):

    libro = session.exec(
        select(Libro).where(Libro.titulo == titulo)
    ).first()

    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado en el catálogo activo")


    libro_deposito = session.exec(
        select(DepositoLibro).where(DepositoLibro.id_libro_original == libro.id)
    ).first()

    for autor in libro.autores:
        autor_deposito = session.exec(
            select(DepositoAutores).where(DepositoAutores.nombre_apellidos == autor.nombre_apellidos)
        ).first()

        if not autor_deposito:
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

        relacion_existente = session.exec(
            select(LinkAutorLibroDeposito).where(
                (LinkAutorLibroDeposito.id_autor_deposito == autor_deposito.id)
                & (LinkAutorLibroDeposito.id_libro_deposito == libro_deposito.id)
            )
        ).first()

        if not relacion_existente:
            session.add(
                LinkAutorLibroDeposito(
                    id_autor_deposito=autor_deposito.id,
                    id_libro_deposito=libro_deposito.id
                )
            )

    session.delete(libro)
    session.commit()

    return {
        "message": f"El libro '{titulo}' y sus autores fueron movidos (o actualizados) correctamente al depósito."
    }

def ver_deposito_libros(session: sessionDep, año_publicacion: int = None):
    query = select(DepositoLibro)
    if año_publicacion:
        query = query.where(DepositoLibro.año_publicacion == año_publicacion)

    libros = session.exec(query).all()
    if not libros:
        raise HTTPException(status_code=404, detail=f"No se encontraron libros{f' de {año_publicacion}' if año_publicacion else ''}")

    return libros

def buscar_libro_en_deposito(titulo: str, session: sessionDep):
    libro = session.exec(select(DepositoLibro).where(DepositoLibro.titulo == titulo)).first()
    if not libro:
        raise HTTPException(status_code=404, detail=f"El libro '{titulo}' no está en el depósito")

    autores = libro.autores
    return {
        "titulo": libro.titulo,
        "editorial": libro.editorial,
        "ISBN": libro.ISBN,
        "autores_asociados": [autor.nombre_apellidos for autor in autores]
    }

def sacar_libro_de_deposito(titulo: str, session: sessionDep):
    libro_deposito = session.exec(select(DepositoLibro).where(DepositoLibro.titulo == titulo)).first()
    if not libro_deposito:
        raise HTTPException(status_code=404, detail=f"El libro '{titulo}' no está en el depósito")

    nuevo_libro = Libro(
        titulo=libro_deposito.titulo,
        resumen=libro_deposito.resumen,
        numero_paginas=libro_deposito.numero_paginas,
        editorial=libro_deposito.editorial,
        año_publicacion=libro_deposito.año_publicacion,
        copias_disponibles=libro_deposito.copias_disponibles,
        ISBN=libro_deposito.ISBN
    )
    session.add(nuevo_libro)
    session.commit()
    session.refresh(nuevo_libro)

    relaciones = session.exec(
        select(LinkAutorLibroDeposito).where(LinkAutorLibroDeposito.id_libro_deposito == libro_deposito.id)
    ).all()

    for rel in relaciones:
        autor_deposito = session.exec(
            select(DepositoAutores).where(DepositoAutores.id == rel.id_autor_deposito)
        ).first()
        if autor_deposito:
            autor_catalogo = session.exec(
                select(Autor).where(Autor.nombre_apellidos == autor_deposito.nombre_apellidos)
            ).first()
            if not autor_catalogo:
                autor_catalogo = Autor(
                    nombre_apellidos=autor_deposito.nombre_apellidos,
                    pais_origen=autor_deposito.pais_origen,
                    descripcion=autor_deposito.descripcion,
                    año_nacimiento=autor_deposito.año_nacimiento,
                    año_muerte=autor_deposito.año_muerte,
                )
                session.add(autor_catalogo)
                session.commit()
                session.refresh(autor_catalogo)

            session.add(LinkAutorLibro(id_libros=nuevo_libro.id, id_autor=autor_catalogo.id))

    session.delete(libro_deposito)
    session.commit()

    return {"message": f"El libro '{titulo}' fue restaurado al catálogo correctamente"}