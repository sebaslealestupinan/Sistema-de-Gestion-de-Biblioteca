# 📚 Catálogo de Libros y Autores – API con FastAPI y SQLModel

Esta API gestiona un **catálogo de autores y libros**, permitiendo crear, consultar, actualizar, eliminar y mover registros a un **depósito histórico** (una especie de “papelera” o archivo).  
Está construida con **FastAPI**, **SQLModel** y **SQLite**, e implementa un diseño modular que facilita su mantenimiento y escalabilidad.

---

## 🚀 Características principales

- CRUD completo para **autores** y **libros**.  
- Relación **N:M** entre autores y libros.  
- Sistema de **depósito histórico** para almacenar eliminaciones sin pérdida de datos.  
- **Rutas RESTful** organizadas por módulos.  
- Uso de **lifespan** en FastAPI para inicialización de base de datos.  
- Documentación automática en `/docs` y `/redoc`.

---

## 🧱 Estructura del proyecto

```
catalogo_biblioteca/
│
├── main.py                  # Punto de entrada principal de la API
├── db/
│   ├── database.py          # Configuración del motor SQLModel y sesión
│
├── autores/
│   ├── autor.py             # Rutas relacionadas con los autores
│   ├── crud.py              # Lógica de negocio para autores
│   ├── schemas.py           # Modelos de entrada/salida (Pydantic)
│
├── libros/
│   ├── libro.py             # Rutas relacionadas con los libros
│   ├── crud.py              # Lógica de negocio para libros
│   ├── schemas.py           # Modelos de entrada/salida (Pydantic)
│
├── db/
│   └── models.py            # Modelos SQLModel (Autor, Libro, Depósito, etc.)
│
├── .gitignore
└── requirements.txt         # Dependencias del proyecto
```

---

## ⚙️ Instalación

### 1️⃣ Clonar el repositorio

```bash
git clone https://github.com/<tu_usuario>/<nombre_del_repositorio>.git
cd <nombre_del_repositorio>
```

### 2️⃣ Crear un entorno virtual

```bash
python -m venv .venv
```

Actívalo:

- **Windows**
  ```bash
  .venv\Scripts\activate
  ```
- **Linux/Mac**
  ```bash
  source .venv/bin/activate
  ```

### 3️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
```

*(Opcional: agrega `python-dotenv` si usas variables de entorno.)*

---

## 🧩 Ejecución

Inicia el servidor con:

```bash
uvicorn main:app --reload
```

La API estará disponible en:
- Documentación interactiva Swagger UI: 👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Documentación alternativa ReDoc: 👉 [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🧠 Endpoints principales

### 📘 Autores (`/autores`)

| Método | Endpoint | Descripción |
|---------|-----------|-------------|
| `POST` | `/autores/` | Crear un nuevo autor |
| `GET` | `/autores/` | Listar autores (opcional filtrar por país) |
| `GET` | `/autores/{nombre_apellidos}` | Obtener autor y sus libros |
| `PUT` | `/autores/{nombre_apellidos}` | Actualizar información del autor |
| `DELETE` | `/autores/deposito/{nombre_apellidos}` | Mover autor al depósito |
| `GET` | `/autores/deposito/` | Listar autores en el depósito |
| `GET` | `/autores/deposito/buscar/{nombre_apellidos}` | Buscar autor en el depósito |
| `POST` | `/autores/deposito/restaurar/{nombre_apellidos}` | Restaurar autor desde el depósito |

---

### 📗 Libros (`/libros`)

| Método | Endpoint | Descripción |
|---------|-----------|-------------|
| `POST` | `/libros/` | Crear un nuevo libro |
| `GET` | `/libros/` | Listar libros (opcional filtrar por año) |
| `GET` | `/libros/{titulo}` | Buscar libro por título |
| `PUT` | `/libros/{titulo}` | Actualizar información del libro |
| `DELETE` | `/libros/deposito/{titulo}` | Mover libro al depósito |
| `GET` | `/libros/deposito/` | Listar libros en el depósito |
| `GET` | `/libros/deposito/{titulo}` | Buscar libro en el depósito |
| `POST` | `/libros/deposito/sacar/{titulo}` | Restaurar libro desde el depósito |

---

## 🧮 Base de datos

- **Motor:** SQLite (por defecto: `databaseCatalogo.db`)
- **ORM:** SQLModel (basado en SQLAlchemy y Pydantic)
- Se inicializa automáticamente al iniciar la app gracias al `lifespan` en `main.py`.

---

## 🧰 Dependencias principales

| Librería | Versión sugerida | Descripción |
|-----------|------------------|-------------|
| `fastapi` | >=0.115 | Framework principal |
| `uvicorn` | >=0.30 | Servidor ASGI |
| `sqlmodel` | >=0.0.22 | ORM para los modelos de datos |

*(Opcional: puedes incluir `pydantic` o `python-dotenv` según tus necesidades.)*

---

## 🧪 Ejemplo de uso (con `curl`)

```bash
# Crear un autor
curl -X POST "http://127.0.0.1:8000/autores/" -H "Content-Type: application/json" -d '{
  "nombre_apellidos": "Gabriel García Márquez",
  "pais_origen": "Colombia",
  "descripcion": "Escritor de realismo mágico",
  "año_nacimiento": "1927"
}'
```

---

## 🧤 Notas de desarrollo

- Al eliminar autores/libros, no se pierden los datos: se mueven al **depósito histórico**.
- El `lifespan` en `main.py` crea automáticamente las tablas al iniciar el servidor.
- Cada módulo (`autores`, `libros`) mantiene independencia lógica (Router + CRUD + Schemas).

---

## 👨‍💻 Autor

Desarrollado por **Sebastián Leal Estupiñán**  
Estudiante de Ingeniería en Sistemas y Computación.

---
