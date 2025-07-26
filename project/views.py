import json
import os

import psycopg2
import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from rest_framework import status, viewsets
#from rest_framework import serializers
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import (
    DataAtHand,
    DataSchema,
    Project,
    Context,
    ContextComponent,
    ApplicationDomain,
    BusinessRule,
    DataFiltering,
    DQMetadata,
    DQRequirement,
    OtherData,
    OtherMetadata,
    SystemRequirement,
    TaskAtHand,
    UserType,
    UserData,
    QualityProblem,
    QualityProblemProject
)
from .serializer import (
    DataAtHandSerializer,
    DataSchemaSerializer,
    ProjectSerializer,
    ContextSerializer,
    ContextComponentSerializer,
    ApplicationDomainSerializer,
    BusinessRuleSerializer,
    DataFilteringSerializer,
    DQMetadataSerializer,
    DQRequirementSerializer,
    OtherDataSerializer,
    OtherMetadataSerializer,
    SystemRequirementSerializer,
    TaskAtHandSerializer,
    UserTypeSerializer,
    UserDataSerializer,
    QualityProblemSerializer,
    QualityProblemProjectSerializer
)


# ==============================================
# Quality Problems Views
# ==============================================

class QualityProblemViewSet(viewsets.ModelViewSet):
    queryset = QualityProblem.objects.all()
    serializer_class = QualityProblemSerializer
    

class QualityProblemProjectViewSet(viewsets.ModelViewSet):
    serializer_class = QualityProblemProjectSerializer

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        return QualityProblemProject.objects.filter(project_id=project_id)
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_id')
        project = get_object_or_404(Project, id=project_id)
        serializer.save(project=project)


@api_view(['GET'])
def quality_problems_by_project(request, project_id):
    # Obtener IDs de problemas asociados a este proyecto
    problem_ids = QualityProblemProject.objects.filter(
        project_id=project_id
    ).values_list('quality_problem_id', flat=True)

    # Traer solo problemas asociados a ese proyecto
    problems = QualityProblem.objects.filter(id__in=problem_ids)

    data = [
        {
            "id": p.id,
            "description": p.description,
            "date": p.date,
            #"date": int(p.date.strftime('%s'))  # timestamp
        }
        for p in problems
    ]
    return Response(data)


@api_view(['GET'])
def get_selected_prioritized_quality_problems_by_project(request, project_id):
    """
    Get only selected (is_selected=True) quality problems for a project.
    """
    project = get_object_or_404(Project, pk=project_id)
    
    selected_problems = QualityProblemProject.objects.filter(
        project=project,
        is_selected=True
    )

    if selected_problems.exists():
        serializer = QualityProblemProjectSerializer(selected_problems, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(
        {"detail": "No selected prioritized quality problems found for this Project"},
        status=status.HTTP_404_NOT_FOUND
    )


@api_view(['POST'])
def copy_problems_from_project(request, source_project_id, target_project_id):
    """
    Copia todos los QualityProblemProject de un proyecto origen a un proyecto destino.
    """
    source_project = get_object_or_404(Project, id=source_project_id)
    target_project = get_object_or_404(Project, id=target_project_id)

    # Verifica si el proyecto destino ya tiene problemas asociados
    if target_project.project_problems.exists():
        return Response(
            {"error": "El proyecto destino ya tiene problemas asociados. No se pueden copiar."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Obtiene todas las asociaciones del proyecto origen
    source_problems = QualityProblemProject.objects.filter(project=source_project)

    # Prepara las nuevas asociaciones para el proyecto destino
    new_associations = [
        QualityProblemProject(
            project=target_project,
            quality_problem=assoc.quality_problem,
            priority=assoc.priority,
            is_selected=assoc.is_selected
        )
        for assoc in source_problems
    ]

    # Crea todas las asociaciones en una sola operación (óptimo para muchos registros)
    QualityProblemProject.objects.bulk_create(new_associations)

    return Response(
        {
            "status": "success",
            "copied_problems": len(new_associations),
            "source_project_id": source_project_id,
            "target_project_id": target_project_id
        },
        status=status.HTTP_201_CREATED
    )

    
# ==============================================
# Context Components Views
# ==============================================

def filter_by_model(queryset, model_class):
    return [obj for obj in queryset if isinstance(obj, model_class)]

class ContextComponentsDetail(APIView):
    def get(self, request, pk):
        context = get_object_or_404(Context, pk=pk)

        data = {
            "applicationDomain": ApplicationDomainSerializer(
                ApplicationDomain.objects.filter(related_contexts=context), many=True
            ).data,
            "businessRule": BusinessRuleSerializer(
                BusinessRule.objects.filter(related_contexts=context), many=True
            ).data,
            "dataFiltering": DataFilteringSerializer(
                DataFiltering.objects.filter(related_contexts=context), many=True
            ).data,
            "dqMetadata": DQMetadataSerializer(
                DQMetadata.objects.filter(related_contexts=context), many=True
            ).data,
            "dqRequirement": DQRequirementSerializer(
                DQRequirement.objects.filter(related_contexts=context), many=True
            ).data,
            "otherData": OtherDataSerializer(
                OtherData.objects.filter(related_contexts=context), many=True
            ).data,
            "otherMetadata": OtherMetadataSerializer(
                OtherMetadata.objects.filter(related_contexts=context), many=True
            ).data,
            "systemRequirement": SystemRequirementSerializer(
                SystemRequirement.objects.filter(related_contexts=context), many=True
            ).data,
            "taskAtHand": TaskAtHandSerializer(
                TaskAtHand.objects.filter(related_contexts=context), many=True
            ).data,
            "userType": UserTypeSerializer(
                UserType.objects.filter(related_contexts=context), many=True
            ).data,
        }

        return Response(data)
  

class ContextViewSet(viewsets.ModelViewSet):
    queryset = Context.objects.all()
    serializer_class = ContextSerializer

class ContextComponentViewSet(viewsets.ModelViewSet):
    queryset = ContextComponent.objects.all()
    serializer_class = ContextComponentSerializer
    
class ApplicationDomainViewSet(viewsets.ModelViewSet):
    queryset = ApplicationDomain.objects.all()
    serializer_class = ApplicationDomainSerializer

class BusinessRuleViewSet(viewsets.ModelViewSet):
    queryset = BusinessRule.objects.all()
    serializer_class = BusinessRuleSerializer

class DataFilteringViewSet(viewsets.ModelViewSet):
    queryset = DataFiltering.objects.all()
    serializer_class = DataFilteringSerializer

class DQMetadataViewSet(viewsets.ModelViewSet):
    queryset = DQMetadata.objects.all()
    serializer_class = DQMetadataSerializer

class DQRequirementViewSet(viewsets.ModelViewSet):
    queryset = DQRequirement.objects.all()
    serializer_class = DQRequirementSerializer

class OtherDataViewSet(viewsets.ModelViewSet):
    queryset = OtherData.objects.all()
    serializer_class = OtherDataSerializer

class OtherMetadataViewSet(viewsets.ModelViewSet):
    queryset = OtherMetadata.objects.all()
    serializer_class = OtherMetadataSerializer

class SystemRequirementViewSet(viewsets.ModelViewSet):
    queryset = SystemRequirement.objects.all()
    serializer_class = SystemRequirementSerializer

class TaskAtHandViewSet(viewsets.ModelViewSet):
    queryset = TaskAtHand.objects.all()
    serializer_class = TaskAtHandSerializer

class UserTypeViewSet(viewsets.ModelViewSet):
    queryset = UserType.objects.all()
    serializer_class = UserTypeSerializer

class UserDataViewSet(viewsets.ModelViewSet):
    queryset = UserData.objects.all()
    serializer_class = UserDataSerializer


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
        new_status = request.data.get('status')

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

        if stage_code == 'ST4':
            project.stage = 'ST4'
            project.status = new_status.lower()
            project.save(update_fields=['stage', 'status'])

        return Response({
            "message": f"Stage {stage_code} actualizado",
            "new_status": new_status
        })
    
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
# Data Source and Schema Related Views
# ==============================================

class DataAtHandViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing DataAtHand instances (data sources).
    """
    queryset = DataAtHand.objects.all()
    serializer_class = DataAtHandSerializer
    
    def perform_create(self, serializer):
        instance = serializer.save()
        instance.create_initial_schema() 
    
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
                dbname=instance.name,
                user=instance.user_db,
                password=instance.pass_db,
                host=instance.url_db,
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
                dbname=instance.name,
                user=instance.user_db,
                password=instance.pass_db,
                host=instance.url_db,
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
                    dbname=instance.name,
                    user=instance.user_db,
                    password=instance.pass_db,
                    host=instance.url_db,
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
