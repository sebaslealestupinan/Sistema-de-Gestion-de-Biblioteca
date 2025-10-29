from contextlib import asynccontextmanager
from fastapi import FastAPI
from db.database import create_database
from autores import autor
from libros import libro

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_database()
    print("Base de datos en linea")
    yield
    print("Catalogo cerrado finalizado")

app = FastAPI(lifespan=lifespan)

app.include_router(autor.router)
app.include_router(libro.router)