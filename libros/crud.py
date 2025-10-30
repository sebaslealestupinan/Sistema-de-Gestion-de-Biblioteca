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


def ingresar_libro(datos: CrearLibro, session: sessionDep):
    """Crea un nuevo libro en el catálogo y vincula sus autores si existen.

    Args:
        datos (CrearLibro): Objeto con los datos necesarios para crear un libro.
        session (sessionDep): Sesión activa de la base de datos.

    Raises:
        HTTPException: Si ya existe un libro con el mismo ISBN.
        HTTPException: Si alguno de los autores no está registrado en la biblioteca.

    Returns:
        dict: Mensaje de confirmación con la información del libro creado y los autores asociados.
    """
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
                raise HTTPException(
                    status_code=404,
                    detail=f"El autor {nombre} no se encuentra registrado en la biblioteca"
                )

            link = LinkAutorLibro(id_libros=nuevo_libro.id, id_autor=autor.id)
            session.add(link)

        session.commit()

    return {
        "mensaje": "Libro creado correctamente",
        "libro": nuevo_libro,
        "autores_vinculados": datos.nombre_autores,
    }


def ver_libros(session: sessionDep, año_publicacion: Optional[int] = None):
    """Obtiene todos los libros o filtra por año de publicación.

    Args:
        session (sessionDep): Sesión activa de la base de datos.
        año_publicacion (Optional[int], optional): Año específico de publicación. Por defecto None.

    Raises:
        HTTPException: Si no se encuentran libros para el año indicado.

    Returns:
        list[Libro]: Lista de libros encontrados.
    """
    query = select(Libro)
    if año_publicacion:
        query = query.where(Libro.año_publicacion == año_publicacion)

    libros = session.exec(query).all()

    if not libros:
        raise HTTPException(status_code=404, detail="No se encontraron libros para ese año")

    return libros


def ver_libro_titulo(titulo: str, session: sessionDep):
    """Busca un libro por su título y muestra su información junto a los autores.

    Args:
        titulo (str): Título del libro a consultar.
        session (sessionDep): Sesión activa de la base de datos.

    Raises:
        HTTPException: Si el libro no existe.

    Returns:
        dict: Información detallada del libro y sus autores.
    """
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
        f"Auto{'res' if len(autores) > 1 else 'r'}": autores,
        "ISBN": libro.ISBN
    }


def actualizar_libro_existente(session: sessionDep, data: ActualizarLibro, titulo: str):
    """Actualiza los datos de un libro existente.

    Args:
        session (sessionDep): Sesión activa de la base de datos.
        data (ActualizarLibro): Datos actualizados del libro.
        titulo (str): Título del libro a actualizar.

    Raises:
        HTTPException: Si el libro no se encuentra en el catálogo.

    Returns:
        dict: Mensaje confirmando la actualización.
    """
    libro = session.exec(select(Libro).where(Libro.titulo == titulo)).first()
    if not libro:
        raise HTTPException(status_code=404, detail=f"El libro '{titulo}' no existe")

    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(libro, campo, valor)

    session.add(libro)
    session.commit()
    return {"message": f"El libro '{titulo}' fue actualizado correctamente"}


def mover_a_deposito_libro(titulo: str, session: sessionDep):
    """Mueve un libro y sus autores al depósito, manteniendo sus relaciones.

    Esta función crea una copia del libro y sus autores en las tablas de depósito.
    - Si el autor ya existe en el depósito, se reutiliza.
    - Si el libro ya está en el depósito, se evita la duplicación.
    - La relación entre libro y autor se conserva en `LinkAutorLibroDeposito`.

    Si ocurre un error en la transacción, se revierte la sesión para evitar corrupción
    de datos y se lanza una excepción HTTP con un mensaje descriptivo.

    Args:
        titulo (str): Título del libro que se desea mover al depósito.
        session (sessionDep): Sesión activa de la base de datos.

    Raises:
        HTTPException:
            - 404: Si el libro no se encuentra en el catálogo activo.
            - 400: Si el libro ya existe en el depósito.
            - 500: Si ocurre un error inesperado durante el proceso.

    Returns:
        dict: Mensaje de confirmación indicando que el libro y sus autores
              fueron movidos correctamente al depósito.
    """
    libro = session.exec(select(Libro).where(Libro.titulo == titulo)).first()
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado en el catálogo activo")

    existente = session.exec(
        select(DepositoLibro).where(DepositoLibro.ISBN == libro.ISBN)
    ).first()
    if existente:
        raise HTTPException(status_code=400, detail="El libro ya está en el depósito")

    libro_deposito = DepositoLibro(
        id_libro_original=libro.id,
        titulo=libro.titulo,
        resumen=libro.resumen,
        numero_paginas=libro.numero_paginas,
        editorial=libro.editorial,
        año_publicacion=libro.año_publicacion,
        copias_disponibles=libro.copias_disponibles,
        ISBN=libro.ISBN,
    )
    session.add(libro_deposito)
    session.commit()
    session.refresh(libro_deposito)

    if not libro.autores:
        raise HTTPException(
            status_code=400,
            detail=f"El libro '{titulo}' no tiene autores asociados en el catálogo.",
        )

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
                año_muerte=autor.año_muerte,
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
                    id_libro_deposito=libro_deposito.id,
                 )
            )

    session.delete(libro)
    session.commit()

    return {
            "message": f"El libro '{titulo}' y sus autores fueron movidos correctamente al depósito."
        }


def ver_deposito_libros(session: sessionDep):
    """Muestra todos los libros que se encuentran actualmente en el depósito.

    Args:
        session (sessionDep): Sesión activa de la base de datos.

    Raises:
        HTTPException: Si no hay libros en el depósito.

    Returns:
        list[DepositoLibro]: Lista de libros en el depósito.
    """
    libros = session.exec(select(DepositoLibro)).all()

    if not libros:
        raise HTTPException(status_code=404, detail=f"No se encontraron libros")

    return libros


def buscar_libro_en_deposito(titulo: str, session: sessionDep):
    """Busca un libro en el depósito por su título.

    Args:
        titulo (str): Título del libro.
        session (sessionDep): Sesión activa de la base de datos.

    Raises:
        HTTPException: Si el libro no se encuentra en el depósito.

    Returns:
        dict: Información del libro y sus autores asociados en el depósito.
    """
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
    """Restaura un libro y sus autores desde el depósito al catálogo principal.

    Args:
        titulo (str): Título del libro a restaurar.
        session (sessionDep): Sesión activa de la base de datos.

    Raises:
        HTTPException: Si el libro no se encuentra en el depósito.

    Returns:
        dict: Mensaje de confirmación indicando que el libro fue restaurado.
    """
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