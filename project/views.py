from rest_framework.response import Response
from django.shortcuts import render
from rest_framework import viewsets
from .models import DataAtHand, DataSchema, PrioritizedDQProblem, Project
from .serializer import DataAtHandSerializer, DataSchemaSerializer, PrioritizedDqProblemSerializer, ProjectSerializer
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

import psycopg2
from rest_framework.response import Response
from rest_framework import status



class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by('-id')
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
    

#DATA AT HAND and DATA SCHEMA

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import DataAtHand, DataSchema
from .serializer import DataAtHandSerializer, DataSchemaSerializer
import psycopg2

class DataAtHandViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing DataAtHand instances.
    """
    queryset = DataAtHand.objects.all()
    serializer_class = DataAtHandSerializer

    def get_queryset(self):
        """
        Optionally filters the queryset based on query parameters.
        """
        queryset = super().get_queryset()
        db_type = self.request.query_params.get('type', None)
        host = self.request.query_params.get('host', None)

        if db_type:
            queryset = queryset.filter(type=db_type)
        if host:
            queryset = queryset.filter(host=host)

        return queryset

    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """
        Custom action to test the database connection for a specific DataAtHand instance.
        """
        instance = self.get_object()

        try:
            # Intenta conectarte a la base de datos
            connection = psycopg2.connect(
                dbname=instance.dbname,
                user=instance.user,
                password=instance.password,
                host=instance.host,
                port=instance.port
            )
            connection.close()  # Cierra la conexión
            return Response({"status": "Connection successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def test_connection_and_get_schema(self, request, pk=None):
        """
        Custom action to test the database connection and retrieve the schema.
        """
        instance = self.get_object()

        try:
            # Conéctate a la base de datos
            connection = psycopg2.connect(
                dbname=instance.dbname,
                user=instance.user,
                password=instance.password,
                host=instance.host,
                port=instance.port
            )

            # Obtén el esquema de la base de datos
            schema = self.get_database_schema(connection)

            connection.close()  # Cierra la conexión

            return Response({
                "status": "Connection successful",
                "schema": schema
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def data_schema(self, request, pk=None):
        """
        Custom action to retrieve the schema for a specific DataAtHand instance.
        """
        instance = self.get_object()

        try:
            # Check if schema already exists
            try:
                data_schema = DataSchema.objects.get(data_at_hand=instance)
                # If schema exists but is empty, update it
                if not data_schema.schema:
                    raise DataSchema.DoesNotExist
            except DataSchema.DoesNotExist:
                # Connect to the database to get the schema
                connection = psycopg2.connect(
                    dbname=instance.dbname,
                    user=instance.user,
                    password=instance.password,
                    host=instance.host,
                    port=instance.port
                )
                schema = self.get_database_schema(connection)
                connection.close()

                if not schema:  # If no tables, return a message
                    return Response({"message": "La base de datos no tiene tablas."}, status=status.HTTP_200_OK)
                
                # Now create or update with the schema data
                data_schema, created = DataSchema.objects.update_or_create(
                    data_at_hand=instance,
                    defaults={'schema': schema}
                )

            return Response(data_schema.schema, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    
    def get_database_schema(self, connection):
        """
        Retrieves the schema of the database as a flat list of tables.
        """
        try:
            tables = self.get_tables_info(connection)
            schema = []
            
            for table_info in tables:
                table_id = table_info[0]
                table_name = table_info[1]
                
                columns = self.get_table_columns_enhanced(connection, table_name)
                
                # Create structured table information
                table_data = {
                    "table_id": table_id,
                    "table_name": table_name,
                    "columns": columns
                }
                
                schema.append(table_data)

            return schema

        except Exception as e:
            raise e

    def get_tables_info(self, connection):
        """
        Retrieves detailed information about tables in the database.
        """
        cursor = connection.cursor()
        cursor.execute("""
            SELECT 
                t.oid as table_id,
                t.relname as table_name,
                n.nspname as schema_name
            FROM 
                pg_class t
                JOIN pg_namespace n ON n.oid = t.relnamespace
            WHERE 
                t.relkind = 'r'
                AND n.nspname = 'public';
        """)
        tables = cursor.fetchall()
        return tables

    def get_table_columns_enhanced(self, connection, table_name):
        """
        Retrieves enhanced information about columns of a specific table.
        """
        cursor = connection.cursor()
        cursor.execute("""
            SELECT
                a.attnum as column_id,
                a.attname as column_name,
                format_type(a.atttypid, a.atttypmod) as data_type,
                a.attnotnull as is_required,
                CASE 
                    WHEN ct.contype = 'p' THEN TRUE 
                    ELSE FALSE 
                END as is_primary_key
            FROM
                pg_attribute a
                LEFT JOIN pg_constraint ct ON ct.conrelid = a.attrelid 
                    AND a.attnum = ANY(ct.conkey) AND ct.contype = 'p'
                JOIN pg_class c ON a.attrelid = c.oid
                JOIN pg_namespace n ON c.relnamespace = n.oid
            WHERE
                c.relname = %s
                AND a.attnum > 0
                AND NOT a.attisdropped
                AND n.nspname = 'public'
            ORDER BY a.attnum;
        """, (table_name,))
        
        columns = []
        for col in cursor.fetchall():
            columns.append({
                "column_id": col[0],
                "column_name": col[1],
                "data_type": col[2]
            })
        
        return columns

class DataSchemaViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing DataSchema instances.
    """
    queryset = DataSchema.objects.all()
    serializer_class = DataSchemaSerializer