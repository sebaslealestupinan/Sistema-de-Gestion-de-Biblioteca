"""Módulo principal de la aplicación FastAPI para el catálogo de libros y autores.

Este módulo inicializa la aplicación FastAPI, gestiona la creación de la base de datos
y define el ciclo de vida de la aplicación utilizando un contexto asíncrono.
También incluye los routers correspondientes a los módulos de autores y libros.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from db.database import create_database
from autores import autor
from libros import libro


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestiona el ciclo de vida de la aplicación FastAPI.

    Esta función utiliza un contexto asíncrono (`asynccontextmanager`) para ejecutar acciones
    antes de que la aplicación inicie y después de que finalice.

    Args:
        app (FastAPI): Instancia principal de la aplicación FastAPI.

    Yields:
        None: Control temporal del flujo para ejecutar el servidor.
    """
    create_database()
    print("Base de datos en línea")
    yield
    print("Catálogo cerrado correctamente")


# Inicialización de la aplicación principal
app = FastAPI(lifespan=lifespan)

# Inclusión de los routers de los módulos
app.include_router(autor.router)
app.include_router(libro.router)