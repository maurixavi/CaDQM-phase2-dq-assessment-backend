import pandas as pd
import psycopg2
from psycopg2 import sql
import os

# Configuración de la base de datos PostgreSQL
DB_CONFIG = {
    "dbname": "data_at_hand_v01",
    "user": "postgres",
    "password": "password",
    "host": "localhost",
    "port": "5432",
}

# Ruta de la carpeta que contiene los archivos CSV
DATA_FOLDER = "data"

def infer_column_types(df):
    """
    Infiere los tipos de columnas en función de los datos del DataFrame.
    """
    column_types = {}
    for column in df.columns:
        dtype = df[column].dtype
        if pd.api.types.is_integer_dtype(dtype):
            # Verificar si hay algún valor que exceda el rango de INTEGER
            if df[column].max() > 2147483647 or df[column].min() < -2147483648:
                column_types[column] = "BIGINT"
            else:
                column_types[column] = "INTEGER"
        elif pd.api.types.is_float_dtype(dtype):
            column_types[column] = "FLOAT"
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            column_types[column] = "TIMESTAMP"
        elif pd.api.types.is_bool_dtype(dtype):
            column_types[column] = "BOOLEAN"
        else:
            column_types[column] = "TEXT"  # Usamos TEXT como predeterminado para strings y otros tipos
    return column_types

def create_table_query(table_name, column_types):
    """
    Genera una consulta SQL para crear una tabla con columnas basadas en el CSV.
    """
    columns = [f"{col} {dtype}" for col, dtype in column_types.items()]
    columns_definition = ", ".join(columns)
    return f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_definition});"

def create_table_and_populate(csv_file, table_name):
    """Crea la tabla basada en el CSV y carga los datos."""
    # Leer el CSV con pandas
    try:
        df = pd.read_csv(csv_file, encoding="utf-8")
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo CSV '{csv_file}'.")
        return
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
        return

    # Inferir tipos de columna
    column_types = infer_column_types(df)

    # Conectar a la base de datos
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Crear la tabla basada en las columnas del CSV
    try:
        create_query = create_table_query(table_name, column_types)
        cursor.execute(create_query)
        print(f"Tabla '{table_name}' creada o ya existente.")

        # Insertar datos del CSV en la tabla
        for _, row in df.iterrows():
            placeholders = ", ".join(["%s"] * len(row))
            insert_query = f"INSERT INTO {table_name} VALUES ({placeholders})"
            cursor.execute(insert_query, tuple(row))

        conn.commit()
        print(f"Datos cargados exitosamente en la tabla '{table_name}'.")
    except Exception as e:
        conn.rollback()
        print(f"Error al crear la tabla o insertar datos: {e}")
    finally:
        cursor.close()
        conn.close()

def process_csv_files_in_folder(folder_path):
    """
    Procesa todos los archivos CSV en la carpeta especificada.
    """
    # Obtener la lista de archivos CSV en la carpeta
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

    if not csv_files:
        print(f"No se encontraron archivos CSV en la carpeta '{folder_path}'.")
        return

    for csv_file in csv_files:
        # Construir la ruta completa al archivo CSV
        csv_file_path = os.path.join(folder_path, csv_file)
        
        # Generar el nombre de la tabla basado en el nombre del archivo CSV
        table_name = os.path.splitext(csv_file)[0]

        # Crear la tabla y cargar los datos
        create_table_and_populate(csv_file_path, table_name)

if __name__ == "__main__":
    process_csv_files_in_folder(DATA_FOLDER)