from rest_framework.response import Response
from django.shortcuts import render
from rest_framework import viewsets
from .models import PrioritizedDQProblem, Project
from .serializer import PrioritizedDqProblemSerializer, ProjectSerializer
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import ContextModel
import json
from django.http import JsonResponse
from django.conf import settings
import os
from django.core.exceptions import ImproperlyConfigured
from .models import PrioritizedDQProblem, Project
from rest_framework import viewsets, status
import requests
from rest_framework.decorators import action, api_view

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


# Endpoint genérico para obtener todos los problemas de calidad disponibles en el sistema
def load_dq_problems_dataset():
    # Ruta del archivo JSON
    file_path = os.path.join(os.path.dirname(__file__), 'dq_problems_dataset.json')  
    
    print(f"Ruta del archivo JSON: {file_path}")  # Imprimir la ruta del archivo para verificar
    
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            
        print("Archivo JSON leído correctamente.")  
        print("Contenido del archivo JSON:", data) 
        
        # Agregando los headers a la respuesta
        #response = JsonResponse(data, safe=False)
        #response['access-token'] = 'your_access_token_here'
        #response['project-id'] = 'your_project_id_here'
        #return response
        
        return JsonResponse(data, safe=False)
    
    except FileNotFoundError:
        print("Error: El archivo JSON no se encuentra.") 
        return JsonResponse({"error": "Archivo no encontrado"}, status=404)
    except Exception as e:
        print(f"Error al procesar el archivo JSON: {str(e)}") 
        return JsonResponse({"error": str(e)}, status=500)
    

# Endpoint especifico para obtener problemas de calidad asociados a un proyecto específico
def get_project_dq_problems(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # agregar la logica para obtener los problemas de calidad asociados al proyecto
    # Por ahora, simplemente devolvemos el JSON estático como en load_dq_problems_dataset
    file_path = os.path.join(os.path.dirname(__file__), 'dq_problems_dataset.json')
    
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
        # modificar `data` para incluir información específica del proyecto si es necesario
        # por ejemplo, data['project_id'] = project_id
        return JsonResponse(data, safe=False)
    except FileNotFoundError:
        return JsonResponse({"error": "Archivo no encontrado"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def get_dq_problem_by_id(request, project_id, problem_id):
    """
    Obtiene un problema de calidad específico por su ID.
    """
    # Ruta del archivo JSON
    file_path = os.path.join(os.path.dirname(__file__), 'dq_problems_dataset.json')
    
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
        
        # Buscar el problema por su ID
        problem = next((item for item in data if item["id"] == problem_id), None)
        
        if problem:
            return JsonResponse(problem, safe=False)
        else:
            return JsonResponse({"error": "Problema no encontrado"}, status=404)
    
    except FileNotFoundError:
        return JsonResponse({"error": "Archivo no encontrado"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)




class PrioritizedDQProblemViewSet(viewsets.ModelViewSet):
    serializer_class = PrioritizedDqProblemSerializer

    def get_queryset(self):
        """
        Filtra los problemas priorizados por proyecto si se proporciona un project_id.
        """
        queryset = PrioritizedDQProblem.objects.all()
        project_id = self.kwargs.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset
    
    # El método retrieve ya está implementado por ModelViewSet
    # No necesitas definir get_prioritized_dq_problem si usas retrieve
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

#class PrioritizedDQProblemViewSet(viewsets.ModelViewSet):
#    queryset = PrioritizedDQProblem.objects.all()
#    serializer_class = PrioritizedDqProblemSerializer
    
    #def get_queryset(self):
        # Filtrar los problemas priorizados por DQModel si se proporciona un dq_model_id
        #dq_model_id = self.request.query_params.get('dq_model_id')
        #if dq_model_id:
        #    return PrioritizedDQProblem.objects.filter(dq_model_id=dq_model_id)
        #return PrioritizedDQProblem.objects.all()


@api_view(['GET'])
def get_selected_prioritized_dq_problems_by_project(request, project_id):
    """
    Devuelve solo los problemas priorizados seleccionados (is_selected=True) para un Project específico.
    """
    project = get_object_or_404(Project, pk=project_id)
    selected_problems = PrioritizedDQProblem.objects.filter(project=project, is_selected=True)

    if selected_problems.exists():
        serializer = PrioritizedDqProblemSerializer(selected_problems, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(
        {"detail": "No selected prioritized problems found for this Project"},
        status=status.HTTP_404_NOT_FOUND
    )