from django.shortcuts import render
from rest_framework import viewsets
from .models import Project
from .serializer import ProjectSerializer
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import ContextModel

# ENDPOINTS PROJECTS

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


# ENDPOINTS DATA QUALITY PROBLEMS

import json
from django.http import JsonResponse
from django.conf import settings
import os


# Vista para devolver el JSON
def get_dq_problems_dataset(request):
    # Ruta del archivo JSON
    file_path = os.path.join(os.path.dirname(__file__), 'dq_problems_dataset.json')  # Ajusta la ruta si es necesario
    
    print(f"Ruta del archivo JSON: {file_path}")  # Imprimir la ruta del archivo para verificar
    
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            
        print("Archivo JSON leído correctamente.")  # Verificar si se leyó bien el archivo
        print("Contenido del archivo JSON:", data)  # Verificar el contenido del JSON
        
        # Agregando los headers a la respuesta
        #response = JsonResponse(data, safe=False)
        #response['access-token'] = 'your_access_token_here'
        #response['project-id'] = 'your_project_id_here'
        #return response
        
        return JsonResponse(data, safe=False)
    except FileNotFoundError:
        print("Error: El archivo JSON no se encuentra.")  # Verificar si el archivo no se encuentra
        return JsonResponse({"error": "Archivo no encontrado"}, status=404)
    except Exception as e:
        print(f"Error al procesar el archivo JSON: {str(e)}")  # Mostrar el error si ocurre
        return JsonResponse({"error": str(e)}, status=500)