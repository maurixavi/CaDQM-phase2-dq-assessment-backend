# Standard library imports
import json
import os

# Third-party imports
import psycopg2
import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

# Local application imports
from .models import (
    ContextModel,
    DataAtHand,
    DataSchema,
    PrioritizedDQProblem,
    Project
)
from .serializer import (
    DataAtHandSerializer,
    DataSchemaSerializer,
    PrioritizedDqProblemSerializer,
    ProjectSerializer
)

# ==============================================
# Project Related Views
# ==============================================

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by('-id')
    serializer_class = ProjectSerializer
    
    @action(detail=True, methods=['patch'], url_path='update-stage')
    def update_stage_status(self, request, pk=None):
        project = self.get_object()
        stage_code = request.data.get('stage')
        new_status = request.data.get('status')  # 'TO_DO', 'IN_PROGRESS' o 'DONE'

        if not stage_code or not new_status:
            return Response(
                {"error": "Se requieren 'stage' y 'status'"},
                status=status.HTTP_400_BAD_REQUEST
            )

        stage = project.get_stage(stage_code)
        if not stage:
            return Response(
                {"error": f"Stage {stage_code} no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Actualizar ProjectStage
        stage.status = new_status
        stage.save()

        # Si es ST4, actualizar también los campos legacy
        if stage_code == 'ST4':
            project.stage = 'ST4'
            project.status = new_status.lower()
            project.save(update_fields=['stage', 'status'])

        return Response({
            "message": f"Stage {stage_code} actualizado",
            "new_status": new_status
        })
    
    # Método para obtener proyectos por dqmodel_version
    @action(detail=False, methods=['get'], url_path='by-dqmodel')
    def get_by_dqmodel(self, request):
        dqmodel_version_id = request.query_params.get('dqmodel_version')

        if not dqmodel_version_id:
            return Response(
                {"error": "Se requiere el parámetro 'dqmodel_version'"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            dqmodel_version_id = int(dqmodel_version_id)
        except ValueError:
            return Response(
                {"error": "'dqmodel_version' debe ser un número entero"},
                status=status.HTTP_400_BAD_REQUEST
            )

        project = Project.objects.filter(dqmodel_version_id=dqmodel_version_id).first()

        if not project:
            return Response(
                {"error": "No se encontró un proyecto con ese dqmodel_version"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(project)
        return Response(serializer.data)



# ==============================================
# DQ Problems Related Views
# ==============================================

def load_dq_problems_dataset():
    """
    Load and return the predefined dataset of DQ problems from a JSON file.
    """
    file_path = os.path.join(os.path.dirname(__file__), 'dq_problems_dataset.json')  
    
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
        return JsonResponse(data, safe=False)
    
    except FileNotFoundError:
        return JsonResponse({"error": "Archivo no encontrado"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



def get_project_dq_problems(request, project_id):
    """
    Get DQ problems associated with a specific project.
    Currently returns the static JSON dataset.
    """
    project = get_object_or_404(Project, id=project_id)
    file_path = os.path.join(os.path.dirname(__file__), 'dq_problems_dataset.json')
    
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
        return JsonResponse(data, safe=False)
    except FileNotFoundError:
        return JsonResponse({"error": "Archivo no encontrado"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def get_dq_problem_by_id(request, project_id, problem_id):
    """
    Get a specific DQ problem by its ID from the dataset.
    """
    file_path = os.path.join(os.path.dirname(__file__), 'dq_problems_dataset.json')
    
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
        
        problem = next((item for item in data if item["id"] == problem_id), None)
        
        if problem:
            return JsonResponse(problem, safe=False)
        return JsonResponse({"error": "Problema no encontrado"}, status=404)
    
    except FileNotFoundError:
        return JsonResponse({"error": "Archivo no encontrado"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


class PrioritizedDQProblemViewSet(viewsets.ModelViewSet):
    serializer_class = PrioritizedDqProblemSerializer

    def get_queryset(self):
        """
        Filter prioritized problems by project_id
        """
        queryset = PrioritizedDQProblem.objects.all()
        project_id = self.kwargs.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset
    
    
    def partial_update(self, request, *args, **kwargs):
        """
        Handle PATCH requests for partial updates.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@api_view(['GET'])
def get_selected_prioritized_dq_problems_by_project(request, project_id):
    """
    Get only selected (is_selected=True) prioritized DQ problems for a project.
    """
    project = get_object_or_404(Project, pk=project_id)
    selected_problems = PrioritizedDQProblem.objects.filter(
        project=project, 
        is_selected=True
    )

    if selected_problems.exists():
        serializer = PrioritizedDqProblemSerializer(selected_problems, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(
        {"detail": "No selected prioritized problems found for this Project"},
        status=status.HTTP_404_NOT_FOUND
    )



# ==============================================
# Data Source and Schema Related Views
# ==============================================

class DataAtHandViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing DataAtHand instances (data sources).
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
        Test the database connection for a specific DataAtHand instance.
        """
        instance = self.get_object()

        try:
            connection = psycopg2.connect(
                dbname=instance.dbname,
                user=instance.user,
                password=instance.password,
                host=instance.host,
                port=instance.port
            )
            connection.close() 
            return Response({"status": "Connection successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def test_connection_and_get_schema(self, request, pk=None):
        """
        Test database connection and retrieve schema information.
        """
        instance = self.get_object()

        try:
            connection = psycopg2.connect(
                dbname=instance.dbname,
                user=instance.user,
                password=instance.password,
                host=instance.host,
                port=instance.port
            )

            schema = self.get_database_schema(connection)
            connection.close() 

            return Response({
                "status": "Connection successful",
                "schema": schema
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def data_schema(self, request, pk=None):
        """
        Retrieve or generate schema information for a DataAtHand instance.
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
        Retrieve database schema as a structured list of tables with columns.
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
        Retrieve detailed information about tables in the database.
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
        Retrieve enhanced column information for a specific table.
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
    API endpoint for managing DataSchema instances.
    """
    queryset = DataSchema.objects.all()
    serializer_class = DataSchemaSerializer