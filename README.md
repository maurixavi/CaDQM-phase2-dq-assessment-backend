# Proyecto Django: Instrucciones de Instalación y Configuración

Este proyecto utiliza Django como framework backend y PostgreSQL como base de datos relacional.

---

## Requisitos

- Python 3.8+
- pip
- PostgreSQL 12+
- virtualenv

---

## Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/maurixavi/CaDQM-phase2-dq-assessment-backend
```

### 2. Crear y activar entorno virtual
```bash
python -m venv env
source env/bin/activate  # En Windows: env\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

---

## Configuración de la base de datos PostgreSQL

### 1. Crear base de datos y usuarios

```sql
-- Accede a PostgreSQL con tu usuario
psql -U postgres

-- Crear la base de datos principal
CREATE DATABASE cadqm_db;

-- Crear base de datos para almacenar resultados de ejecución (DQ Metadata)
CREATE DATABASE cadqm_dqmetadata_db;
```

### 2. Configurar `settings.py`

El archivo `settings.py`, ubicado en el directorio `myproject/`, ya incluye la estructura necesaria para conectar con PostgreSQL mediante dos bases de datos:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'cadqm_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    },
    'metadata_db': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'cadqm_dqmetadata_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```
Asegúrate de actualizar y completar los campos de conexión con los datos reales de tu entorno: nombre de base de datos, usuario, contraseña, host y puerto de PostgreSQL.

---

## Migraciones y carga inicial

### 1. Orden de las migraciones

El backend esta implementado mediante un proyecto Django, dividido en dos modulos, llamados apps: `dqmodel` y `project` (tiene dependencias hacia `dqmodel`).

Ejecuta los siguientes comandos en el siguiente orden para poder crear las tablas necesarias en las bases de datos definidas:
```bash
# Crear tablas django
python manage.py migrate contenttypes
python manage.py migrate auth
python manage.py migrate sessions

# Crear tablas DQ Model
## Importante seguir cuidadosamente el siguiente flujo de ejecucionespara cargar crear y cargar correctamente
## las tablas de DQ Model en sus bases de datos correspondientes (cadqm_db o cadqm_dqmetadata_db)
python manage.py migrate dqmodel 0001
python manage.py migrate dqmodel 0001 --database=metadata_db --fake  # Importante para evitar crear nuevamente las tablas ya cargadas en la base principal en la base de metadata
python manage.py migrate dqmodel 0002 --database=metadata_db
python manage.py migrate dqmodel 0002 --fake

# Crear tablas Project
python manage.py migrate project 0001

# Crear tablas Admin
python manage.py admin
```

### 2. Crear superusuario (opcional para admin)
```bash
python manage.py createsuperuser
```

---

## Ejecución de la aplicación

```bash
python manage.py runserver
```

La aplicación estará disponible en `http://127.0.0.1:8000/` o `http://localhost:8000/`

---

