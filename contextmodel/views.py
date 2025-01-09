from rest_framework import viewsets
from .models import ContextModel, ApplicationDomain, BusinessRule, UserType, TaskAtHand, DQRequirement, DataFiltering, SystemRequirement, DQMetadata, OtherMetadata, OtherData
from .serializer import ContextModelSerializer, ApplicationDomainSerializer, BusinessRuleSerializer, UserTypeSerializer, TaskAtHandSerializer, DQRequirementSerializer, DataFilteringSerializer, SystemRequirementSerializer, DQMetadataSerializer, OtherMetadataSerializer, OtherDataSerializer

import json
from django.http import JsonResponse
from django.conf import settings
import os


# Vista para devolver el JSON
def get_context_versions(request):
    # Ruta del archivo JSON
    #file_path = os.path.join(settings.BASE_DIR, 'data', 'context_components.json')
    # Definir la ruta del archivo JSON
    file_path = os.path.join(os.path.dirname(__file__), 'context_versions.json')  # Ajusta la ruta si es necesario

    
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

# Vista para devolver un contexto específico por su id
def get_context_by_id(request, id):
    # Ruta del archivo JSON
    file_path = os.path.join(os.path.dirname(__file__), 'context_versions.json')

    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)

        # Buscar el contexto por su `context_id`
        context = next((item for item in data if item['context_id'] == id), None)

        if context:
            return JsonResponse(context)
        else:
            return JsonResponse({"error": "Contexto no encontrado"}, status=404)

    except FileNotFoundError:
        return JsonResponse({"error": "Archivo no encontrado"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# Vista para devolver los contextComponents de un contexto específico
def get_context_components(request, id):
    # Ruta del archivo JSON
    file_path = os.path.join(os.path.dirname(__file__), 'context_versions.json')

    try:
        # Cargar el archivo JSON
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)

        # Buscar el contexto por su `context_id`
        context = next((item for item in data if item['context_id'] == id), None)

        if context:
            # Extraer solo el campo 'contextComponents' del contexto encontrado
            context_components = context.get('contextComponents', {})
            return JsonResponse(context_components)

        else:
            return JsonResponse({"error": "Contexto no encontrado"}, status=404)

    except FileNotFoundError:
        return JsonResponse({"error": "Archivo no encontrado"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    


class ContextModelViewSet(viewsets.ModelViewSet):
    queryset = ContextModel.objects.all()
    serializer_class = ContextModelSerializer

class ApplicationDomainViewSet(viewsets.ModelViewSet):
    queryset = ApplicationDomain.objects.all()
    serializer_class = ApplicationDomainSerializer

class BusinessRuleViewSet(viewsets.ModelViewSet):
    queryset = BusinessRule.objects.all()
    serializer_class = BusinessRuleSerializer

class UserTypeViewSet(viewsets.ModelViewSet):
    queryset = UserType.objects.all()
    serializer_class = UserTypeSerializer

class TaskAtHandViewSet(viewsets.ModelViewSet):
    queryset = TaskAtHand.objects.all()
    serializer_class = TaskAtHandSerializer

class DQRequirementViewSet(viewsets.ModelViewSet):
    queryset = DQRequirement.objects.all()
    serializer_class = DQRequirementSerializer

class DataFilteringViewSet(viewsets.ModelViewSet):
    queryset = DataFiltering.objects.all()
    serializer_class = DataFilteringSerializer

class SystemRequirementViewSet(viewsets.ModelViewSet):
    queryset = SystemRequirement.objects.all()
    serializer_class = SystemRequirementSerializer

class DQMetadataViewSet(viewsets.ModelViewSet):
    queryset = DQMetadata.objects.all()
    serializer_class = DQMetadataSerializer

class OtherMetadataViewSet(viewsets.ModelViewSet):
    queryset = OtherMetadata.objects.all()
    serializer_class = OtherMetadataSerializer

class OtherDataViewSet(viewsets.ModelViewSet):
    queryset = OtherData.objects.all()
    serializer_class = OtherDataSerializer
