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

## Configuración de la Base de Datos

#### Pasos Comunes

### 1. Crear base de datos y usuarios

```sql
-- Accede a PostgreSQL con tu usuario
psql -U postgres

-- Crear la base de datos principal
CREATE DATABASE cadqm_db;

-- Crear base de datos para almacenar resultados de ejecución (DQ Metadata)
CREATE DATABASE cadqm_dqmetadata_db;
```

### 2. Configurar credenciales de conexión (`settings.py`)

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
Asegurarse de actualizar y completar los campos de conexión con los datos reales del entorno de trabajo: nombre de base de datos, usuario, contraseña, host y puerto de PostgreSQL.


### 3. Carga inicial de Tablas

La inicialización del sistema requiere una estructura de tablas requerido en cada una de las bases de datos creadas y la carga mínima de un conjunto de datos iniciales para su correcto funcionamiento.

#### Opción A. Restauración a partir de Dumps

En el directorio `db_dumps/` del repositorio se disponibilizan dos archivos pg_dump, `cadqm\_db.sql` y `cadqm_dqmetadata_db.sql` para su restauración en las bases de datos vacías. Esta opción permite obtener una base de datos lista para su uso de forma inmediata. 

Ejecutar los siguientes comandos para generar las estructuras de tabla requeridas para cada base, **incluyendo los datos iniciales necesarios**:

```bash
psql -U <tu_usuario> -d cadqm_db -f db_dumps/cadqm_db.sql

psql -U <tu_usuario> -d cadqm_dqmetadata_db -f db_dumps/cadqm_dqmetadata_db.sql
```


#### Opción B. Migraciones Django

Mediante esta vía, el usuario construirá la estructura de la base de datos, con sus respectivas tablas, desde cero. 

Ejecutar las siguientes en **estricto orden:**
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

### 4. Carga Inicial de Datos (Requerido con Migraciones)

El sistema requiere una carga inicial de un conjunto dimensiones y factores de calidad de datos predefinidos.
La ejecución de este paso es **obligatorio** si se optó por la Opción B, luego de finalizar la ejecución de las migraciones. Las bases de datos restauradas ya incluyen estos datos.

```bash
# Ejecutar (ubicado en el directorio raíz del proyecto backend) la carga inicial de dimensiones y factores base 
python manage.py load_dqtemplate --template preset_dq_dimensions_factors_base
```

**¿Qué carga este comando?**
- Definición de las dimensiones: Accuracy, Completeness, Consistency, Uniqueness, Freshness
- Factores de calidad asociados a cada dimensión.
Sin esta carga inicial, la aplicación no tendrá los conceptos de CD básicos necesarios para todas las funcionalidades de la aplicación, requeridos para la generación de recomendaciones con IA. Las definiciones se basan en el Curso de Calidad de Datos (Facultad de Ingeniería, UdelaR), y se cargar a traves del archivo preset_dq_dimensions_factors_base.md ubicado en el directorio `dqmodel/templates/definitions/`


## Panel Admin (Crear superusuario)

El siguiente comando  permite crear una cuenta de superusuario para el panel de administración de Django, herramienta poderosa que permite gestionar el contenido y los modelos de datos de la aplicación de forma sencilla.

```bash
python manage.py createsuperuser
```

Una vez creada, se podrá acceder al panel en `http://localhost:8000/admin`

---

## Ejecución de la aplicación

```bash
python manage.py runserver
```

La aplicación estará disponible en `http://127.0.0.1:8000/` o `http://localhost:8000/`

---

## Carga Artefactos Base Predefinidos (Opcional)

### Definición de Templates con conceptos de CD

Adicionalmente, el sistema ofrece la posibilidad de cargar artefactos, correspondientes a conceptos de calidad de datos (dimensiones, factores, métricas y métodos) predefinidos en forma de templates que pueden ser reutilizados en múltiples proyectos de calidad de datos. Esto permite iniciar la aplicación con un repositorio de conceptos de CD predefinidos disponibles, para agilizar la construcción de modelos de CD mediante su selección.

Un template consiste en un archivo de tipo markdown (.md) definido manualmente por el usuario siguiendo la siguiente estructura y formato, asegurando el cumplimiento de la jerarquía de los conceptos de CD:

```
## DQ Dimension: [Nombre de la Dimensión]
**Semantic:** [Descripción semántica de la dimensión]

### DQ Factor: [Nombre del Factor]  
**Semantic:** [Descripción semántica del factor]
**Facet of (DQ Dimension):** [Nombre de la Dimensión padre]

#### DQ Metric: [Nombre de la Métrica]  
**Purpose:** [Propósito de la métrica]  
**Granularity:** [Nivel de granularidad]  
**Result Domain:** [Dominio del resultado]  
**Measures (DQ Factor):** [Nombre del Factor padre]

##### DQ Method: [Nombre del Método]
**Name:** [Nombre del método]  
**Input data type:** [Tipo de dato de entrada]
**Output data type:** [Tipo de dato de salida]  
**Algorithm:**  
	[código o descripción del algoritmo]
**Implements (DQ Metric):** [Nombre de la Métrica padre]
```

**Ejemplo especifico:**
```
## DQ Dimension: Completeness
**Semantic:** Refers to the availability of all necessary data, ensuring that no important data is missing for analysis or decision-making.

### DQ Factor: Density  
**Semantic:** Describes the proportion of actual data entries compared to the total number of expected entries.
**Facet of (DQ Dimension):** Completeness

#### DQ Metric: Value Density Ratio  
**Purpose:** Proportion of non-null values relative to the total number of expected values.  
**Granularity:** Table  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Density

#### DQ Metric: Non-Null Values Ratio  
**Purpose:** Proportion of non-null values in a column relative to its total number of expected values.  
**Granularity:** Column  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Density

##### DQ Method: calculateNonNullValuesRatio
**Name:** calculateNonNullValuesRatio  
**Input data type:** Column<any>
**Output data type:** Float  
**Algorithm:**  
	```sql
	SELECT 
    SUM(CASE WHEN {{column_name}} IS NOT NULL THEN 1 ELSE 0 END) * 1.0 
    / COUNT(*) AS non_null_ratio
  FROM 
    {{table_name}};
	```
**Implements (DQ Metric):** Non-Null Values Ratio
```

**Observaciones:**
- Estos templates deben ser ubicados en el directorio `dqmodel/templates/definitions/`.
- En el comando de carga, se debe especificar el nombre del archivo sin la extensión .md (`python manage.py load_dqtemplate --template <nombre_archivo_template>`)
- Para extender el repositorio de artefactos de calidad base, no es necesario definir en el archivo nuevamente toda la jerarquia desde las dimensiones, pero sí es requerido que todo concepto debe respetar la jerarquia incluyendo correctamente el nombre del concepto de CD que lo antecede.
- La estructura con encabezados markdown (##, ###, ####, #####) ayuda visualmente a respetar la jerarquia y es utilizada por el parser para identificar el nivel de cada concepto.
- Si encuentra conceptos ya existentes en la base de datos se incluye un control de no cargar repetidos.


### Carga de Template Extendido (Opcional)
Como soporte adicional para la herramienta, se proporciona un template extendido (`preset_dqmodel_template.md`) que incluye dimensiones y factores (de carga obligatoria), y además métricas genéricas y métodos de calidad predefinidos. Este template ofrece un conjunto completo de artefactos de calidad de datos listos para usar, incluyendo métricas clásicas y definiciones genéricas que cubren los principales factores de calidad. El archivo se encuentra ubicado en `dqmodel/templates/definitions/` y puede ser modificado para adaptarse a necesidades específicas.

Carga del template extendido:
```bash
python manage.py load_dqtemplate --template dqconcepts_template
```

---------


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

Asegurate de tener en tu archivo `settings.py` algo como:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'cadqm_db',
        'USER': 'dq_user',
        'PASSWORD': 'dq_password',
        'HOST': 'localhost',
        'PORT': '5432',
    },
    'metadata_db': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'cadqm_dqmetadata_db',
        'USER': 'dq_user',
        'PASSWORD': 'dq_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

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

### 3. (Opcional) Cargar datos iniciales desde archivos JSON o fixtures
```bash
python manage.py loaddata initial_data.json
```

---

## Ejecución de la aplicación

```bash
python manage.py runserver
```

La aplicación estará disponible en `http://127.0.0.1:8000/` o `http://localhost:8000/`

---

## Otros comandos útiles

- Revisar estado de migraciones:
```bash
python manage.py showmigrations
```

- Ingresar a la consola interactiva:
```bash
python manage.py shell
```

---

## Notas adicionales

- Asegurate de que `psycopg2` esté instalado si usas PostgreSQL:
```bash
pip install psycopg2-binary
```

- Usa `.env` y `python-decouple` o similares para separar credenciales de `settings.py` en ambientes productivos.

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
Asegurarse de actualizar y completar los campos de conexión con los datos reales del entorno de trabajo: nombre de base de datos, usuario, contraseña, host y puerto de PostgreSQL.

---

## Migraciones y Carga inicial de Datos

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

### 3. Carga Inicial de Datos (Obligatorio)

El sistema requiere una carga inicial de un conjunto dimensiones y factores de calidad de datos predefinidos.
Este paso es REQUERIDO para el funcionamiento adecuado de la aplicación.

```bash
# Ejecutar (ubicado en el directorio raíz del proyecto backend) la carga inicial de dimensiones y factores base 
python manage.py load_dqtemplate --template preset_dq_dimensions_factors_base
```

**¿Qué carga este comando?**
- Definición de las dimensiones: Accuracy, Completeness, Consistency, Uniqueness, Freshness
- Factores de calidad asociados a cada dimensión.
Sin esta carga inicial, la aplicación no tendrá los conceptos de CD básicos necesarios para todas las funcionalidades de la aplicación, requeridos para la generación de recomendaciones con IA. Las definiciones se basan en el Curso de Calidad de Datos (Facultad de Ingeniería, UdelaR), y se cargar a traves del archivo preset_dq_dimensions_factors_base.md ubicado en el directorio `dqmodel/templates/definitions/`


## Panel Admin (Crear superusuario)

El panel de administración de Django es una herramienta poderosa que permite gestionar los datos de la aplicación de forma sencilla. Desde aquí, es posible crear, modificar y eliminar cualquier elemento almacenado en la base de datos para los modelos que se han registrado en el panel de administración.

Para acceder a este panel, primero se debe crear una cuenta de superusuario. Para ello, ejecuta el siguiente comando en la terminal:

```bash
python manage.py createsuperuser
```
Este panel se encuentra accesible en la dirección: `http://localhost:8000/admin`


---

## Configuración de variables de entorno

Para poder ejecutar las funciones de la aplicación mediante IA, para la recomendación y generación automática de contenido, se requiere una clave de acceso a la API de Groq.
funciones de la aplicación (particularmente aquellas relacionadas con la generación automática de elementos y recomendaciones mediante IA) requieren una clave de acceso a la API de Groq.
Groq es una plataforma de inferencia que permite ejecutar modelos de lenguaje (LLM) de manera optimizada y eficiente.

En el directorio `myproject/` se encuentra un archivo `.env.example.` Este archivo debe copiarse y renombrarse como `.env`.

Dentro del archivo .env debe configurarse la variable correspondiente a la clave de la API de Groq:

`GROQ_API_KEY=tu_api_key_aqui`

Para obtener una API Key:
  1. Acceder a https://console.groq.com/keys
  2. Crear una cuenta (gratuita) en caso de no disponer de una.
  3. Generar una nueva API Key y copiarla.


---

## Ejecución de la aplicación

```bash
python manage.py runserver
```

La aplicación estará disponible en `http://127.0.0.1:8000/` o `http://localhost:8000/`

---

## Carga Artefactos Base Predefinidos (Opcional)

### Definición de Templates con conceptos de CD

Adicionalmente, el sistema ofrece la posibilidad de cargar artefactos, correspondientes a conceptos de calidad de datos (dimensiones, factores, métricas y métodos) predefinidos en forma de templates que pueden ser reutilizados en múltiples proyectos de calidad de datos. Esto permite iniciar la aplicación con un repositorio de conceptos de CD predefinidos disponibles, para agilizar la construcción de modelos de CD mediante su selección.

Un template consiste en un archivo de tipo markdown (.md) definido manualmente por el usuario siguiendo la siguiente estructura y formato, asegurando el cumplimiento de la jerarquía de los conceptos de CD:

```
## DQ Dimension: [Nombre de la Dimensión]
**Semantic:** [Descripción semántica de la dimensión]

### DQ Factor: [Nombre del Factor]  
**Semantic:** [Descripción semántica del factor]
**Facet of (DQ Dimension):** [Nombre de la Dimensión padre]

#### DQ Metric: [Nombre de la Métrica]  
**Purpose:** [Propósito de la métrica]  
**Granularity:** [Nivel de granularidad]  
**Result Domain:** [Dominio del resultado]  
**Measures (DQ Factor):** [Nombre del Factor padre]

##### DQ Method: [Nombre del Método]
**Name:** [Nombre del método]  
**Input data type:** [Tipo de dato de entrada]
**Output data type:** [Tipo de dato de salida]  
**Algorithm:**  
	[código o descripción del algoritmo]
**Implements (DQ Metric):** [Nombre de la Métrica padre]
```

**Ejemplo especifico:**
```
## DQ Dimension: Completeness
**Semantic:** Refers to the availability of all necessary data, ensuring that no important data is missing for analysis or decision-making.

### DQ Factor: Density  
**Semantic:** Describes the proportion of actual data entries compared to the total number of expected entries.
**Facet of (DQ Dimension):** Completeness

#### DQ Metric: Value Density Ratio  
**Purpose:** Proportion of non-null values relative to the total number of expected values.  
**Granularity:** Table  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Density

#### DQ Metric: Non-Null Values Ratio  
**Purpose:** Proportion of non-null values in a column relative to its total number of expected values.  
**Granularity:** Column  
**Result Domain:** [0, 1]  
**Measures (DQ Factor):** Density

##### DQ Method: calculateNonNullValuesRatio
**Name:** calculateNonNullValuesRatio  
**Input data type:** Column<any>
**Output data type:** Float  
**Algorithm:**  
	```sql
	SELECT 
    SUM(CASE WHEN {{column_name}} IS NOT NULL THEN 1 ELSE 0 END) * 1.0 
    / COUNT(*) AS non_null_ratio
  FROM 
    {{table_name}};
	```
**Implements (DQ Metric):** Non-Null Values Ratio
```

**Observaciones:**
- Estos templates deben ser ubicados en el directorio `dqmodel/templates/definitions/`.
- En el comando de carga, se debe especificar el nombre del archivo sin la extensión .md (`python manage.py load_dqtemplate --template <nombre_archivo_template>`)
- Para extender el repositorio de artefactos de calidad base, no es necesario definir en el archivo nuevamente toda la jerarquia desde las dimensiones, pero sí es requerido que todo concepto debe respetar la jerarquia incluyendo correctamente el nombre del concepto de CD que lo antecede.
- La estructura con encabezados markdown (##, ###, ####, #####) ayuda visualmente a respetar la jerarquia y es utilizada por el parser para identificar el nivel de cada concepto.
- Si encuentra conceptos ya existentes en la base de datos se incluye un control de no cargar repetidos.


### Carga de Template Extendido (Opcional)
Como soporte adicional para la herramienta, se proporciona un template extendido (`preset_dqmodel_template.md`) que incluye dimensiones y factores (de carga obligatoria), y además métricas genéricas y métodos de calidad predefinidos. Este template ofrece un conjunto completo de artefactos de calidad de datos listos para usar, incluyendo métricas clásicas y definiciones genéricas que cubren los principales factores de calidad. El archivo se encuentra ubicado en `dqmodel/templates/definitions/` y puede ser modificado para adaptarse a necesidades específicas.

Carga del template extendido:
```bash
python manage.py load_dqtemplate --template dqconcepts_template
```

---

## Estructura del proyecto

```
project-root/
├── manage.py # Punto de entrada servidor Django
├── README.md
├── requirements.txt
│
├── dqmodel/ # App dedicada a definición y ejecución de Modelos de CD
│ ├── ai_modules/ # Módulos de IA (recomendación/generación)
│ ├── management/ # Comandos de Django personalizados
│ └── templates/ # Plantillas base y loaders
│ │ └── definitions/ # Plantillas con conceptos de CD base  
│ │ └── loaders/ # Procesamiento y carga de plantillas a BD
│ ├── migrations/ # Migraciones de Django
│
├── project/ # App: gestión de Proyectos y flujo metodológico CaDQM
│ ├── (models, views, signals, urls etc.)
│ ├── migrations/
│
└── myproject/ # Configuración principal de Django
├── settings.py
├── urls.py
├── wsgi.py
├── asgi.py
└── MetadataRouter.py # Router de bases de datos Metadata
```

**Resumen:**
- `dqmodel/` → define los conceptos de calidad (dimensiones, factores, métricas, métodos) y su ejecución.  
- `project/` → gestiona los **Proyectos** y articula contexto, problemas de calidad y datos fuente; referencia directamente a `dqmodel/`.  
- `myproject/` → configuración central del servidor Django (multi-DB, routers, CORS, etc.).  


---

