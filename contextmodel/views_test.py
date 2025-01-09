import json
import os

# Definir la ruta del archivo JSON
file_path = os.path.join(os.path.dirname(__file__), 'context_versions.json')  # Ajusta la ruta si es necesario

# Imprimir la ruta para verificar que es la correcta
print(f"Ruta del archivo JSON: {file_path}")

try:
    # Leer el archivo JSON
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        
    # Imprimir el contenido del archivo si se lee correctamente
    print("Archivo JSON leído correctamente.")
    print("Contenido del archivo JSON:", data)
    
except FileNotFoundError:
    print(f"Error: El archivo {file_path} no se encuentra.")  # Si el archivo no existe
except json.JSONDecodeError:
    print("Error: El archivo no tiene un formato JSON válido.")  # Si el archivo no es un JSON válido
except Exception as e:
    print(f"Error inesperado: {e}")  # Para cualquier otro error inesperado
