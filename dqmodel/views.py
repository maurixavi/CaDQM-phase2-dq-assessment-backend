from datetime import timezone
import time
from uuid import UUID, uuid4
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Value, CharField 
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action, api_view
from django.db import connections

from dqmodel.services import DQExecutionResultService
from .models import (
    DQMethodExecutionResult,
    DQModel,
    DQDimensionBase,
    DQFactorBase,
    DQMetricBase,
    DQMethodBase,
    DQModelDimension,
    DQModelExecution,
    DQModelFactor,
    DQModelMetric,
    DQModelMethod,
    ExecutionColumnResult,
    ExecutionRowResult,
    ExecutionTableResult,
    MeasurementDQMethod,
    AggregationDQMethod
    #,
    #PrioritizedDqProblem,
    #PrioritizedDqProblem
)
from .serializer import (
    ColumnResultSerializer,
    DQModelSerializer,
    DQDimensionBaseSerializer,
    DQFactorBaseSerializer,
    DQMetricBaseSerializer,
    DQMethodBaseSerializer,
    MeasurementDQMethodSerializer,
    AggregationDQMethodSerializer,
    DQModelDimensionSerializer,
    DQModelFactorSerializer,
    DQModelMetricSerializer,
    DQModelMethodSerializer,
    #PrioritizedDqProblemSerializer,
    RowResultSerializer,
    TableResultSerializer
)
#from .ai_utils import generate_ai_suggestion
#from .dq_dimension_factor_recommender import get_dq_recommendation
from dqmodel.ai_modules.dq_dimension_factor_recommender import generate_ai_dq_factor_recommendation
from dqmodel.ai_modules.dq_method_generator import generate_ai_dq_method

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db import transaction
import psycopg2
from decimal import Decimal
import json
from .models import DQModel, AppliedDQMethod, MeasurementDQMethod, AggregationDQMethod

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import MeasurementDQMethod, AggregationDQMethod
import psycopg2
import psycopg2.extras
from decimal import Decimal
import json

import sqlparse
import psycopg2
import time
from decimal import Decimal
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
import re

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType
from .models import (
    DQModelExecution, 
    DQMethodExecutionResult,
    MeasurementDQMethod,
    AggregationDQMethod
)


# AI SUGGESTIONS GENERATION

@api_view(['POST'])
def generate_dq_dim_factor_suggestion(request):
    try:
        print("[generate_dq_dim_factor_suggestion] Recibiendo datos...")

        data = request.data
        dimensions = data.get('dimensions_and_factors')
        problems = data.get('dq_problems')
        context = data.get('context_components')

        # Validación básica
        if not dimensions or not problems or not context:
            return Response({
                "status": "failed",
                "error": "Se requieren los campos 'dimensions_and_factors', 'dq_problems' y 'context_components' en el cuerpo del request."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Generar sugerencia con la función principal
        result = generate_ai_dq_factor_recommendation(
            dimensions=dimensions,
            problems=problems,
            context=context
        )

        if "error" in result:
            return Response({
                "status": "failed",
                "error": result["error"]
            }, status=status.HTTP_200_OK)   

        return Response({
            "status": "success",
            **result
        }, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return Response({
            "status": "failed",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def generate_dqmethod_suggestion(request):
    try:
        print("try")
        # Obtener los datos de la métrica desde el cuerpo del POST
        dq_metric_data = request.data
        print(dq_metric_data)
        
        required_fields = ['id', 'name', 'purpose', 'granularity', 'resultDomain']
        for field in required_fields:
            if field not in dq_metric_data:
                return Response({"error": f"'{field}' is required in the request body."}, status=status.HTTP_400_BAD_REQUEST)

        # Asegurarse de que resultDomain se maneje como un string (sin cambiarlo)
        if not isinstance(dq_metric_data['resultDomain'], str):
            return Response({"error": "'resultDomain' should be a string."}, status=status.HTTP_400_BAD_REQUEST)


        # Obtener la DQMetric correspondiente usando el ID
        try:
            dq_metric = DQMetricBase.objects.get(id=dq_metric_data['id'])
        except DQMetricBase.DoesNotExist:
            return Response({"error": "DQMetricBase not found."}, status=status.HTTP_404_NOT_FOUND)

        # Generar la sugerencia utilizando la función de IA (usando los datos proporcionados)
        suggestion = generate_ai_dq_method(dq_metric_data)

        # Incluir el ID de la métrica en la respuesta (para asociarlo en el método)
        suggestion['implements'] = dq_metric_data['id']

        # Retornar la sugerencia generada
        return Response(suggestion, status=status.HTTP_200_OK)
        #return Response({
        #    "suggestion": suggestion,
        #    "message": "Suggestion generated successfully"
        #}, status=status.HTTP_200_OK)
    
    except Exception as e:
        print("Exception")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# DQ DIMENSIONS, FACTORS, METRICS AND METHODS BASE VIEWS

# ViewSet para DQDimensionBase
class DQDimensionBaseViewSet(viewsets.ModelViewSet):
    queryset = DQDimensionBase.objects.all()
    serializer_class = DQDimensionBaseSerializer


# ViewSet para DQFactorBase
class DQFactorBaseViewSet(viewsets.ModelViewSet):
    queryset = DQFactorBase.objects.all()
    serializer_class = DQFactorBaseSerializer
    
    @action(detail=True, methods=['get'], url_path='factors-base')
    def get_factors_by_dimension(self, request, pk=None):
        # Filtrar factores basados en el dimension_id
        factors = self.queryset.filter(facetOf_id=pk)
        serializer = self.get_serializer(factors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# ViewSet para DQMetricBase
class DQMetricBaseViewSet(viewsets.ModelViewSet):
    queryset = DQMetricBase.objects.all()
    serializer_class = DQMetricBaseSerializer
    
    @action(detail=True, methods=['get'], url_path='metrics-base')
    def get_metrics_by_factor(self, request, pk=None, dim_id=None):
        # Filtrar factores basados en el factor_id
        metrics = self.queryset.filter(measures_id=pk)
        serializer = self.get_serializer(metrics, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='methods-base')
    def get_methods_base(self, request, pk=None):
        """Obtiene métodos base asociados a esta métrica base"""
        methods = DQMethodBase.objects.filter(implements_id=pk)
        serializer = DQMethodBaseSerializer(methods, many=True)
        return Response(serializer.data)
    
        
# ViewSet para DQMethodBase
class DQMethodBaseViewSet(viewsets.ModelViewSet):
    queryset = DQMethodBase.objects.all()
    serializer_class = DQMethodBaseSerializer
    
    @action(detail=True, methods=['get'], url_path='methods-base')
    def get_methods_by_metric(self, request, pk=None, dim_id=None, factor_id=None):
        # Filtrar factores basados en el dimension_id
        methods = self.queryset.filter(implements_id=pk)
        serializer = self.get_serializer(methods, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



# ViewSet para DQModel
class DQModelViewSet(viewsets.ModelViewSet):
    queryset = DQModel.objects.all().prefetch_related(
        'model_dimensions__dimension_base',
        'model_factors__factor_base',
        'model_factors__dimension__dimension_base',
        'model_metrics__metric_base',
        'model_metrics__factor__factor_base',
        'model_metrics__methods__method_base',
        'model_metrics__methods__metric__metric_base',
        'model_methods__measurementdqmethod_applied_methods',
        'model_methods__aggregationdqmethod_applied_methods',
        'next_versions',
    )
    serializer_class = DQModelSerializer

    @action(detail=True, methods=['post'])
    def create_version(self, request, pk=None):
        original = self.get_object()
        if original.status != 'finished':
            return Response(
                {"error": "Solo se pueden crear versiones de DQModels finalizados."},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            serializer = self.get_serializer()
            new_instance = serializer.create_new_version(original)
        
        # Serializar y devolver la nueva version
        serializer = self.get_serializer(new_instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'], url_path='next-version')
    def get_next_version(self, request, pk=None):
        dq_model = self.get_object()
        
        # Buscar el modelo que tenga como previous_version este dq_model
        next_version = DQModel.objects.filter(previous_version=dq_model).first()

        if next_version:
            serializer = self.get_serializer(next_version)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "No next version found for this DQModel"}, status=status.HTTP_404_NOT_FOUND)
    
    # DQ Dimensions en un DQModel especifico
    @action(detail=True, methods=['get'], url_path='dimensions')
    def get_dimensions(self, request, pk=None):
        dq_model = get_object_or_404(DQModel, pk=pk)
        dimensions = DQModelDimension.objects.filter(dq_model=dq_model).prefetch_related('dimension_base')
        
        if dimensions.exists():
            serializer = DQModelDimensionSerializer(dimensions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response({"detail": "No dimensions found for this DQModel"}, status=status.HTTP_404_NOT_FOUND)
    
    def get_dimension(self, request, pk=None, dimension_id=None):
        """
        Devuelve una dimensión específica de un modelo.
        """
        dq_model = get_object_or_404(DQModel, pk=pk)
        dimension = get_object_or_404(DQModelDimension, id=dimension_id, dq_model=dq_model)
        serializer = DQModelDimensionSerializer(dimension)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='factors')
    def get_factors(self, request, pk=None):
        """
        Devuelve todos los factores asociados a un DQModel.
        """
        dq_model = get_object_or_404(DQModel, pk=pk)
        factors = DQModelFactor.objects.filter(dq_model=dq_model)
        serializer = DQModelFactorSerializer(factors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], url_path='factors/(?P<factor_id>[^/.]+)')
    def get_factor_in_dqmodel(self, request, pk=None, factor_id=None):
        """
        Devuelve un factor específico de un DQModel.
        """
        dq_model = get_object_or_404(DQModel, pk=pk)
        factor = get_object_or_404(DQModelFactor, id=factor_id, dq_model=dq_model)
        serializer = DQModelFactorSerializer(factor)
        return Response(serializer.data)
    
    # DQ Factors de una DQ Dimension especifica en un DQModel
    @action(detail=True, methods=['get'], url_path='dimensions/(?P<dimension_id>[^/.]+)/factors')
    def get_factors_by_dimension(self, request, pk=None, dimension_id=None):
        dq_model = get_object_or_404(DQModel, pk=pk)
        dimension = get_object_or_404(DQModelDimension, pk=dimension_id, dq_model=dq_model)
        factors = DQModelFactor.objects.filter(dimension=dimension)
        
        serializer = DQModelFactorSerializer(factors, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='dimensions/(?P<dimension_id>[^/.]+)/factors/(?P<factor_id>[^/.]+)')
    def get_factor(self, request, pk=None, dimension_id=None, factor_id=None):
        """
        Devuelve un factor específico de una dimensión específica dentro de un modelo.
        """
        # Obtener el modelo
        dq_model = get_object_or_404(DQModel, pk=pk)

        # Obtener la dimensión asociada al modelo
        dimension = get_object_or_404(DQModelDimension, pk=dimension_id, dq_model=dq_model)

        # Obtener el factor asociado a la dimensión
        factor = get_object_or_404(DQModelFactor, pk=factor_id, dimension=dimension)

        # Serializar y devolver la respuesta
        serializer = DQModelFactorSerializer(factor)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], url_path='metrics')
    def get_metrics(self, request, pk=None):
        """
        Devuelve todas las métricas asociadas a un DQModel.
        """
        dq_model = get_object_or_404(DQModel, pk=pk)
        factors = DQModelFactor.objects.filter(dq_model=dq_model)
        metrics = DQModelMetric.objects.filter(factor__in=factors)
        serializer = DQModelMetricSerializer(metrics, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], url_path='metrics/(?P<metric_id>[^/.]+)')
    def get_metric_in_dqmodel(self, request, pk=None, metric_id=None):
        """
        Devuelve una métrica específica de un DQModel.
        """
        dq_model = get_object_or_404(DQModel, pk=pk)
        metric = get_object_or_404(DQModelMetric, id=metric_id, factor__dq_model=dq_model)
        serializer = DQModelMetricSerializer(metric)
        return Response(serializer.data)
    
    # DQ Metrics de un DQ Factor especifico en un DQModel
    @action(detail=True, methods=['get'], url_path='dimensions/(?P<dimension_id>[^/.]+)/factors/(?P<factor_id>[^/.]+)/metrics')
    def get_metrics_by_factor(self, request, pk=None, dimension_id=None, factor_id=None):
        dq_model = get_object_or_404(DQModel, pk=pk)
        dimension = get_object_or_404(DQModelDimension, pk=dimension_id, dq_model=dq_model)
        factor = get_object_or_404(DQModelFactor, pk=factor_id, dimension=dimension)
        metrics = DQModelMetric.objects.filter(factor=factor)
        
        serializer = DQModelMetricSerializer(metrics, many=True)
        return Response(serializer.data)
    
    
    @action(detail=True, methods=['get'], url_path='methods')
    def get_methods(self, request, pk=None):
        """
        Devuelve todos los métodos asociados a un DQModel.
        """
        dq_model = get_object_or_404(DQModel, pk=pk)
        factors = DQModelFactor.objects.filter(dq_model=dq_model)
        metrics = DQModelMetric.objects.filter(factor__in=factors)
        methods = DQModelMethod.objects.filter(metric__in=metrics)
        serializer = DQModelMethodSerializer(methods, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], url_path='methods/(?P<method_id>[^/.]+)')
    def get_method_in_dqmodel(self, request, pk=None, method_id=None):
        """
        Devuelve un método específico de un DQModel.
        """
        dq_model = get_object_or_404(DQModel, pk=pk)
        method = get_object_or_404(DQModelMethod, id=method_id, metric__factor__dq_model=dq_model)
        serializer = DQModelMethodSerializer(method)
        return Response(serializer.data)
    
    # DQ Methods de una DQ Metric especifica en un DQModel
    @action(detail=True, methods=['get'], url_path='dimensions/(?P<dimension_id>[^/.]+)/factors/(?P<factor_id>[^/.]+)/metrics/(?P<metric_id>[^/.]+)/methods')
    def get_methods_by_metric(self, request, pk=None, dimension_id=None, factor_id=None, metric_id=None):
        dq_model = get_object_or_404(DQModel, pk=pk)
        dimension = get_object_or_404(DQModelDimension, pk=dimension_id, dq_model=dq_model)
        factor = get_object_or_404(DQModelFactor, pk=factor_id, dimension=dimension)
        metric = get_object_or_404(DQModelMetric, pk=metric_id, factor=factor)
        methods = DQModelMethod.objects.filter(metric=metric)
        
        serializer = DQModelMethodSerializer(methods, many=True)
        return Response(serializer.data)
    
    # En DQModelViewSet
    @action(detail=True, methods=['get'], url_path='applied-dq-methods/(?P<applied_method_id>[^/.]+)')
    def get_applied_method(self, request, pk=None, applied_method_id=None):
        """
        Devuelve los detalles de un método aplicado (Measurement o Aggregation) en un DQModel específico.
        """
        # Obtener el DQModel
        dq_model = get_object_or_404(DQModel, pk=pk)

        # Buscar el método aplicado (Measurement o Aggregation)
        try:
            applied_method = MeasurementDQMethod.objects.get(id=applied_method_id, associatedTo__metric__factor__dq_model=dq_model)
            serializer = MeasurementDQMethodSerializer(applied_method)
        except MeasurementDQMethod.DoesNotExist:
            try:
                applied_method = AggregationDQMethod.objects.get(id=applied_method_id, associatedTo__metric__factor__dq_model=dq_model)
                serializer = AggregationDQMethodSerializer(applied_method)
            except AggregationDQMethod.DoesNotExist:
                return Response(
                    {"error": "Applied method not found in this DQModel"},
                    status=status.HTTP_404_NOT_FOUND
                )

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch', 'put'], url_path='applied-dq-methods/(?P<applied_method_id>\d+)')
    def update_applied_method(self, request, pk=None, applied_method_id=None):
        try:
            # Buscar primero en Measurement
            try:
                method = MeasurementDQMethod.objects.get(
                    id=applied_method_id,
                    associatedTo__metric__factor__dq_model_id=pk
                )
                serializer = MeasurementDQMethodSerializer(method, data=request.data, partial=True)
            except MeasurementDQMethod.DoesNotExist:
                # Si no es Measurement, buscar en Aggregation
                method = AggregationDQMethod.objects.get(
                    id=applied_method_id,
                    associatedTo__metric__factor__dq_model_id=pk
                )
                serializer = AggregationDQMethodSerializer(method, data=request.data, partial=True)
            
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
            
        except (MeasurementDQMethod.DoesNotExist, AggregationDQMethod.DoesNotExist):
            return Response(
                {"error": "Applied DQ method not found in this model"},
                status=status.HTTP_404_NOT_FOUND
            )
        
    """
    Casos de Uso EXPLAIN ANALYZE: 
    Caso 1: Métodos Agregados (COUNT, AVG, etc.)
    # Consulta: SELECT COUNT(*) FROM users WHERE is_active = true
    rows_affected = 1  # (solo 1 fila devuelta)
    total_records = 1000  # (filas escaneadas)

    Caso 2: Métodos por Fila (Ejecución por fila)
    # Consulta: SELECT id, (CASE WHEN email IS VALID THEN 1 ELSE 0 END) FROM users
    rows_affected = 500  # (filas devueltas)
    total_records = 500  # (filas procesadas)

    Caso 3: JOINs Complejos
    # Consulta: SELECT COUNT(DISTINCT u.id) FROM users u JOIN orders o ON u.id = o.user_id
    rows_affected = 1    # (COUNT devuelve 1 fila)
    total_records = 1200 # (filas procesadas en el JOIN)
    """   
    def parse_explain_analyze2(self, explain_output):
        """Extrae 'actual rows' del EXPLAIN ANALYZE"""
        for line in explain_output:
            if "actual rows" in line[0]:
                return int(line[0].split("rows=")[1].split()[0])
        return 0   

    # Función para extraer las columnas de una consulta SQL
    def extract_columns_from_query(query):
        parsed = sqlparse.parse(query)
        columns = []
        for stmt in parsed:
            for token in stmt.tokens:
                if isinstance(token, sqlparse.sql.Identifier):
                    columns.append(token.get_real_name())
        return columns
   
    @action(detail=True, methods=['post'], url_path='applied-dq-methods/(?P<applied_method_id>[^/.]+)/assess')
    def assess_applied_method(self, request, pk=None, applied_method_id=None):
        try:
            dq_model = get_object_or_404(DQModel, pk=pk)

            try:
                applied_method = MeasurementDQMethod.objects.get(
                    id=applied_method_id,
                    associatedTo__metric__factor__dq_model=dq_model
                )
            except MeasurementDQMethod.DoesNotExist:
                try:
                    applied_method = AggregationDQMethod.objects.get(
                        id=applied_method_id,
                        associatedTo__metric__factor__dq_model=dq_model
                    )
                except AggregationDQMethod.DoesNotExist:
                    return Response({"status": "error", "message": "Método aplicado no encontrado"}, status=404)

            content_type = ContentType.objects.get_for_model(applied_method)

            try:
                result = DQMethodExecutionResult.objects.get(
                    content_type=content_type,
                    object_id=applied_method.id
                )
            except DQMethodExecutionResult.DoesNotExist:
                return Response({"status": "error", "message": "Ejecución no encontrada para este método"}, status=404)

            thresholds = result.assessment_thresholds
            if not thresholds:
                return Response({"status": "error", "message": "No se definieron thresholds"}, status=400)

            # Validación mínima
            if not isinstance(thresholds, list) or not all('min' in t and 'max' in t and 'name' in t for t in thresholds):
                return Response({"status": "error", "message": "Thresholds mal definidos"}, status=400)

            updated_count = 0
            now = timezone.now()

            def get_score(value):
                if value is None:
                    return None
                for t in thresholds:
                    if t['min'] <= value <= t['max']:
                        return t['name']
                return "Not Assessed"

            if result.result_type == 'single':
                #rows = ExecutionColumnResult.objects.filter(execution_result=result)
                rows = ExecutionColumnResult.objects.using('metadata_db').filter(execution_result=result)
            elif result.result_type == 'multiple':
                #rows = ExecutionRowResult.objects.filter(execution_result=result)
                
                rows = ExecutionRowResult.objects.using('metadata_db').filter(execution_result=result)
            else:
                return Response({"status": "error", "message": f"Tipo de resultado '{result.result_type}' no soportado"}, status=400)

            for row in rows:
                score = get_score(row.dq_value)
                if score != row.assessment_score:
                    row.assessment_score = score
                    #row.assessed_at = now
                    #row.save(update_fields=["assessment_score", "assessed_at"])
                    row.save(update_fields=["assessment_score"])
                    # row.save()
                    updated_count += 1

            # Actualizar assessed_at en el resultado principal
            result.assessed_at = now
            result.save(update_fields=["assessed_at"])

            return Response({
                "status": "success",
                "message": "Evaluación completada correctamente",
                "evaluated_rows": updated_count,
                "method": applied_method.name,
                "result_type": result.result_type
            }, status=200)

        except Exception as e:
            return Response({
                "status": "error",
                "message": f"Error inesperado durante la evaluación: {str(e)}"
            }, status=500)


    @action(detail=True, methods=['post'], url_path='start-dq-model-execution')
    @transaction.atomic
    def start_dq_model_execution(self, request, pk=None):
        """
        Crea una nueva ejecución para el DQ Model 
        Ejemplo de request: POST /api/dqmodels/{pk}/start-dq-model-execution/
        Response: {
            "execution_id": "uuid",
            "status": "created",
            "model_id": 123
        }
        """
        try:
            execution = DQModelExecution.objects.using('metadata_db').create(
                dq_model_id=pk,
                status='in_progress',
                execution_id=uuid4()
            )
            
            return Response({
                'execution_id': str(execution.execution_id),
                'status': 'created',
                'model_id': pk,
                'started_at': execution.started_at
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'error': 'Failed to create execution',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
     
    @action(detail=True, methods=['post'], url_path='applied-dq-methods/(?P<applied_method_id>[^/.]+)/execute')
    def execute_applied_methodOk(self, request, pk=None, applied_method_id=None):
        """
        Ejecuta un método aplicado
        """
        debug_info = []
        response_data = {
            'status': 'started',
            'dq_model_id': pk,
            'method_id': applied_method_id,
            'debug_info': debug_info
        }
        

        try:
            start_time = timezone.now()
            debug_info.append(f"Inicio ejecución: {start_time}")
            
            # 1. Obtener el modelo y método
            dq_model = get_object_or_404(DQModel, pk=pk)
            debug_info.append(f"DQModel encontrado (ID: {dq_model.id}, Versión: {dq_model.version})")

            # Buscar el método aplicado
            try:
                applied_method = MeasurementDQMethod.objects.get(
                    id=applied_method_id,
                    associatedTo__metric__factor__dq_model=dq_model
                )
                method_type = 'measurement'
            except MeasurementDQMethod.DoesNotExist:
                try:
                    applied_method = AggregationDQMethod.objects.get(
                        id=applied_method_id,
                        associatedTo__metric__factor__dq_model=dq_model
                    )
                    method_type = 'aggregation'
                except AggregationDQMethod.DoesNotExist:
                    debug_info.append("Método no encontrado")
                    return Response(
                        {"error": "Applied method not found in this DQModel", "debug_info": debug_info},
                        status=status.HTTP_404_NOT_FOUND
                    )

            debug_info.append(f"Método aplicado: {applied_method.name} (ID: {applied_method.id}, Tipo: {method_type})")
            debug_info.append(f"Algoritmo: {applied_method.algorithm}")

            # 2. Conectar a la base de datos y ejecutar
            try:
                conn = psycopg2.connect(
                    dbname='data_at_hand_v01',
                    user='postgres',
                    password='password',
                    host='localhost',
                    port=5432
                )
                debug_info.append("Conexión a PostgreSQL establecida")

                # Medición de tiempo de ejecución
                query_start_time = time.time()
                
                with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute(applied_method.algorithm)
                    columns = [desc[0] for desc in cursor.description]
                    raw_rows = cursor.fetchall()
                    
                    # Convertir Decimal a float para serialización JSON
                    def convert_decimals(obj):
                        if isinstance(obj, Decimal):
                            return float(obj)
                        elif isinstance(obj, dict):
                            return {k: convert_decimals(v) for k, v in obj.items()}
                        elif isinstance(obj, (list, tuple)):
                            return [convert_decimals(item) for item in obj]
                        return obj
                    
                    rows = [convert_decimals(dict(row)) for row in raw_rows]
                    
                    query_time = time.time() - query_start_time
                    debug_info.append(f"Tiempo de ejecución SQL: {query_time:.4f} segundos")
                    
                    # 3. Determinar el tipo de resultado y procesarlo
                    is_aggregation = len(rows) <= 1  # Si es 0 o 1 fila, lo consideramos agregación

                    if is_aggregation:
                        # Método de agregación - obtener el valor DQ inteligentemente
                        if not rows:
                            result_value = None
                        else:
                            # Estrategia para encontrar el valor DQ:
                            # 1. Buscar columna llamada 'dq_value'
                            # 2. Si no existe, usar la última columna
                            # 3. Si tampoco, usar el primer valor
                            row = rows[0]
                            if 'dq_value' in row:
                                result_value = row['dq_value']
                            elif columns:
                                result_value = row.get(columns[-1])  # Última columna por defecto
                            else:
                                result_value = next(iter(row.values())) if row else None
                        
                        result_type = 'single'
                        
                        processed_results = {
                            'applied_dq_method_name': applied_method.name,
                            'applied_dq_method_id': applied_method.id,
                            'applied_to': applied_method.appliedTo,
                            'execution_time_seconds': round(query_time, 4),
                            'dq_value': result_value,
                            'value_source': 'explicit_dq_column' if 'dq_value' in (rows[0] if rows else {}) else 'last_column'
                        }
                    else:
                        # Método por fila - múltiples resultados
                        result_type = 'multiple'
                        
                        # Asegurar que cada fila tenga un ID único
                        rows_with_ids = []
                        for idx, row in enumerate(rows, start=1):
                            if 'id' not in row:
                                row['row_id'] = idx
                            rows_with_ids.append(row)
                        
                        # Determinar qué columna es el valor DQ
                        dq_column = None
                        if 'dq_value' in columns:
                            dq_column = 'dq_value'
                        elif len(columns) == 1:
                            dq_column = columns[0]  # Si solo hay una columna, usa esa
                        elif columns:
                            dq_column = columns[-1] # Si hay múltiples, usa la última por defecto
                        
                        
                        processed_results = {
                            'total_rows': len(rows_with_ids),
                            'columns': columns,
                            'dq_column': dq_column,  # Indicar qué columna se usó como DQ value
                            'sample_data': rows_with_ids[:5],  # Mostrar muestra reducida
                            'applied_dq_method_name': applied_method.name,
                            'applied_dq_method_id': applied_method.id,
                            'applied_to': applied_method.appliedTo
                        }
                        
                        result_value = {
                            'rows': rows_with_ids,
                            'columns': columns,
                            'dq_column': dq_column
                        }

                    # 4. Obtener estadísticas de ejecución
                    cursor.execute(f"EXPLAIN ANALYZE {applied_method.algorithm}")
                    explain_output = cursor.fetchall()
                    total_records = self.parse_explain_analyze(explain_output)
                    debug_info.append(f"Total de registros recorridos: {total_records}")

                    # 5. Guardar resultados en metadata_db
                    try:
                        DQExecutionResultService.save_execution_result(
                            dq_model_id=pk,
                            applied_method=applied_method,
                            result_value=result_value if is_aggregation else result_value,
                            result_type=result_type,
                            execution_details={
                                'query_time_seconds': query_time,
                                'rows_affected': cursor.rowcount,
                                'total_records': total_records,
                                'query': applied_method.algorithm,
                                'columns': columns
                            }
                        )
                    except Exception as e:
                        debug_info.append(f"Advertencia al guardar resultados: {str(e)}")

                    # 6. Construir respuesta
                    response_data.update({
                        'status': 'success',
                        'result_type': result_type,
                        'results': processed_results,
                        'execution_details': {
                            'total_time_seconds': round((timezone.now() - start_time).total_seconds(), 4),
                            'query_time_seconds': round(query_time, 4),
                            'rows_affected': cursor.rowcount,
                            'total_records': total_records
                        },
                        'debug_info': debug_info
                    })

                    return Response(response_data)

            except Exception as e:
                debug_info.append(f"Error ejecutando consulta: {str(e)}")
                return Response(
                    {'error': f"Query execution failed: {str(e)}", 'debug_info': debug_info},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            debug_info.append(f"Error inesperado: {str(e)}")
            return Response(
                {'error': f"Unexpected error: {str(e)}", 'debug_info': debug_info},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            if 'conn' in locals():
                conn.close()
                debug_info.append("Conexión cerrada")
     
     
    @action(detail=True, methods=['post'], url_path='applied-dq-methods/(?P<applied_method_id>[^/.]+)/execute')
    def execute_applied_method(self, request, pk=None, applied_method_id=None):
        """
        Ejecuta un método aplicado
        """
        debug_info = []
        response_data = {
            'status': 'started',
            'dq_model_id': pk,
            'method_id': applied_method_id,
            'debug_info': debug_info
        }
        

        try:
            start_time = timezone.now()
            debug_info.append(f"Inicio ejecución: {start_time}")
            
            # 1. Obtener el modelo y método
            dq_model = get_object_or_404(DQModel, pk=pk)
            debug_info.append(f"DQModel encontrado (ID: {dq_model.id}, Versión: {dq_model.version})")

            # Buscar el método aplicado
            try:
                applied_method = MeasurementDQMethod.objects.get(
                    id=applied_method_id,
                    associatedTo__metric__factor__dq_model=dq_model
                )
                method_type = 'measurement'
            except MeasurementDQMethod.DoesNotExist:
                try:
                    applied_method = AggregationDQMethod.objects.get(
                        id=applied_method_id,
                        associatedTo__metric__factor__dq_model=dq_model
                    )
                    method_type = 'aggregation'
                except AggregationDQMethod.DoesNotExist:
                    debug_info.append("Método no encontrado")
                    return Response(
                        {"error": "Applied method not found in this DQModel", "debug_info": debug_info},
                        status=status.HTTP_404_NOT_FOUND
                    )

            debug_info.append(f"Método aplicado: {applied_method.name} (ID: {applied_method.id}, Tipo: {method_type})")
            debug_info.append(f"Algoritmo: {applied_method.algorithm}")

            # 2. Conectar a la base de datos y ejecutar
            try:
                #conn = psycopg2.connect(
                #    dbname='data_at_hand_v01',
                #    user='postgres',
                #    password='password',
                #    host='localhost',
                #    port=5432
                #)
                #debug_info.append("Conexión a PostgreSQL establecida")
                
                raw_config = request.data.get("connection_config", {})

                # Verifica que request tenga las claves necesarias
                if not all(k in raw_config for k in ['name', 'user_db', 'pass_db', 'url_db', 'port']):
                    return Response(
                        {"error": "Faltan datos de conexión en connection_config"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Obtiene solo lo necesario para psycopg2
                conn_config = {
                    key: raw_config[key]
                    for key in ["name", "user_db", "pass_db", "url_db", "port"]
                    if key in raw_config
                }

                conn = psycopg2.connect(**conn_config)
                debug_info.append("Conexión a PostgreSQL establecida con datos externos")

                # Medición de tiempo de ejecución
                query_start_time = time.time()
                
                with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute(applied_method.algorithm)
                    columns = [desc[0] for desc in cursor.description]
                    raw_rows = cursor.fetchall()
                    
                    # Convertir Decimal a float para serialización JSON
                    def convert_decimals(obj):
                        if isinstance(obj, Decimal):
                            return float(obj)
                        elif isinstance(obj, dict):
                            return {k: convert_decimals(v) for k, v in obj.items()}
                        elif isinstance(obj, (list, tuple)):
                            return [convert_decimals(item) for item in obj]
                        return obj
                    
                    rows = [convert_decimals(dict(row)) for row in raw_rows]
                    
                    query_time = time.time() - query_start_time
                    debug_info.append(f"Tiempo de ejecución SQL: {query_time:.4f} segundos")
                    
                    # 3. Determinar el tipo de resultado y procesarlo
                    if len(rows) <= 1: # ResultType: Single DQ Value
                        # Método de agregación - obtener el valor DQ inteligentemente
                        if not rows:
                            result_value = None
                        else:
                            # Estrategia para encontrar el valor DQ:
                            # 1. Buscar columna llamada 'dq_value'
                            # 2. Si no existe, usar la última columna
                            # 3. Si tampoco, usar el primer valor
                            row = rows[0]
                            if 'dq_value' in row:
                                result_value = row['dq_value']
                            elif columns:
                                result_value = row.get(columns[-1])
                            else:
                                result_value = next(iter(row.values())) if row else None
                        
                        result_type = 'single'
                        
                        processed_results = {
                            'applied_dq_method_name': applied_method.name,
                            'applied_dq_method_id': applied_method.id,
                            'applied_to': applied_method.appliedTo,
                            'execution_time_seconds': round(query_time, 4),
                            'dq_value': result_value,
                            'value_source': 'explicit_dq_column' if 'dq_value' in (rows[0] if rows else {}) else 'last_column'
                        }
                    else:
                        # ResultType: Multiple DQ Value (row results)
                        result_type = 'multiple'
                        
                        # Asegurar que cada fila tenga un ID único
                        rows_with_ids = []
                        for idx, row in enumerate(rows, start=1):
                            if 'id' not in row:
                                row['row_id'] = idx
                            rows_with_ids.append(row)
                        
                        # Determinar qué columna es el valor DQ
                        dq_column = None
                        if 'dq_value' in columns:
                            dq_column = 'dq_value'
                        elif len(columns) == 1:
                            dq_column = columns[0]  # Si solo hay una columna, usa esa
                        elif columns:
                            dq_column = columns[-1] # Si hay múltiples, usa la última por defecto
                                              
                        processed_results = {
                            'total_rows': len(rows_with_ids),
                            'columns': columns,
                            'dq_column': dq_column,  # Indicar qué columna se usó como DQ value
                            'sample_data': rows_with_ids[:5], 
                            'applied_dq_method_name': applied_method.name,
                            'applied_dq_method_id': applied_method.id,
                            'applied_to': applied_method.appliedTo
                        }
                        
                        result_value = {
                            'rows': rows_with_ids,
                            'columns': columns,
                            'dq_column': dq_column
                        }

                    # 4. Obtener estadísticas de ejecución
                    cursor.execute(f"EXPLAIN ANALYZE {applied_method.algorithm}")
                    explain_output = cursor.fetchall()
                    total_records = self.parse_explain_analyze(explain_output)
                    debug_info.append(f"Total de registros recorridos: {total_records}")

                    # 5. Guardar resultados en metadata_db
                    try:
                        DQExecutionResultService.save_execution_result(
                            dq_model_id=pk,
                            applied_method=applied_method,
                            result_value=result_value,
                            result_type=result_type,
                            execution_details={
                                'query_time_seconds': query_time,
                                'rows_affected': cursor.rowcount,
                                'total_records': total_records,
                                'query': applied_method.algorithm,
                                'columns': columns
                            }
                        )
                    except Exception as e:
                        debug_info.append(f"Advertencia al guardar resultados: {str(e)}")

                    # 6. Construir respuesta
                    response_data.update({
                        'status': 'success',
                        'result_type': result_type,
                        'results': processed_results,
                        'execution_details': {
                            'total_time_seconds': round((timezone.now() - start_time).total_seconds(), 4),
                            'query_time_seconds': round(query_time, 4),
                            'rows_affected': cursor.rowcount,
                            'total_records': total_records
                        },
                        'debug_info': debug_info
                    })

                    return Response(response_data)

            except Exception as e:
                debug_info.append(f"Error ejecutando consulta: {str(e)}")
                return Response(
                    {'error': f"Query execution failed: {str(e)}", 'debug_info': debug_info},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            debug_info.append(f"Error inesperado: {str(e)}")
            return Response(
                {'error': f"Unexpected error: {str(e)}", 'debug_info': debug_info},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            if 'conn' in locals():
                conn.close()
                debug_info.append("Conexión cerrada")
     
    
    
    # Función para analizar la salida de EXPLAIN ANALYZE y obtener el número total de registros procesados         
    def parse_explain_analyze(self, explain_output):
        total_records = None
        for line in explain_output:
            if 'Total runtime' in line[0]:  # Verifica la línea con el tiempo de ejecución
                continue
            if 'rows' in line[0]:
                # Buscamos el rango de filas, si es que está presente
                match = re.search(r'(\d+(?:\.\d+)?)\.\.(\d+(?:\.\d+)?)', line[0])
                if match:
                    # Si hay un rango de filas, tomamos el primer valor del rango
                    total_records = int(float(match.group(1)))  # Convertimos el primer valor del rango a entero
                else:
                    # Si no hay rango, simplemente extraemos el número de filas como entero
                    try:
                        total_records = int(line[0].split('=')[1].strip())
                    except ValueError:
                        total_records = 0  # Si no podemos convertir, lo dejamos en 0
                break
        return total_records if total_records is not None else 0

    

    def extract_table_names(self, sql_query):
        """
        Extrae nombres de tablas de una consulta SQL (implementación básica)
        """
        # Implementación mejorada para extraer nombres de tablas
        tables = set()
        tokens = sql_query.split()
        from_index = -1
        
        try:
            from_index = tokens.index('FROM')
        except ValueError:
            try:
                from_index = tokens.index('from')
            except ValueError:
                return tables

        # Buscar nombres de tablas después de FROM
        for i in range(from_index + 1, len(tokens)):
            token = tokens[i].strip(';').strip(',')
            if token.upper() in ['WHERE', 'GROUP', 'ORDER', 'LIMIT', 'JOIN', 'INNER', 'LEFT', 'RIGHT']:
                break
            if token and token not in ['(', ')'] and not token.upper() in ['AS', 'ON']:
                tables.add(token.split('.')[0] if '.' in token else token)
                
        return tables
    
    


  
        


# ViewSet para MeasurementDQMethod
class MeasurementDQMethodViewSet(viewsets.ModelViewSet):
    queryset = MeasurementDQMethod.objects.all()
    serializer_class = MeasurementDQMethodSerializer



# ViewSet para AggregationDQMethod
class AggregationDQMethodViewSet(viewsets.ModelViewSet):
    queryset = AggregationDQMethod.objects.all()
    serializer_class = AggregationDQMethodSerializer

# ViewSet para DQModelDimension
class DQModelDimensionViewSet(viewsets.ModelViewSet):
    queryset = DQModelDimension.objects.all()
    serializer_class = DQModelDimensionSerializer
    
    def patch(self, request, dimension_id):
        try:
            dimension = DQModelDimension.objects.get(id=dimension_id)
            serializer = DQModelDimensionSerializer(dimension, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except DQModelDimension.DoesNotExist:
            return Response({"error": "Dimension not found"}, status=status.HTTP_404_NOT_FOUND)


# ViewSet para DQModelFactor
class DQModelFactorViewSet(viewsets.ModelViewSet):
    queryset = DQModelFactor.objects.all()
    serializer_class = DQModelFactorSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ViewSet para DQModelMetric
class DQModelMetricViewSet(viewsets.ModelViewSet):
    queryset = DQModelMetric.objects.all()
    serializer_class = DQModelMetricSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ViewSet para DQModelMethod
class DQModelMethodViewSet(viewsets.ModelViewSet):
    queryset = DQModelMethod.objects.all()
    serializer_class = DQModelMethodSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ViewSet para PrioritizedDqProblem
#class PrioritizedDqProblemDetailView(viewsets.ModelViewSet):
    #queryset = PrioritizedDqProblem.objects.all()
   # serializer_class = PrioritizedDqProblemSerializer
    
   # def get_queryset(self):
    #    dq_model_id = self.kwargs.get('dq_model_id')
    #    return PrioritizedDqProblem.objects.filter(dq_model_id=dq_model_id).order_by('priority')

   # def update(self, request, *args, **kwargs):
    #    instance = self.get_object()
        
        # Validar que no se modifique dq_model_id
   #     dq_model_id = request.data.get('dq_model')
  #      if dq_model_id and int(dq_model_id) != instance.dq_model.id:
  #          raise ValidationError({"dq_model": "No se permite cambiar el dqmodel de un problema priorizado existente."})
        
        # Validar que no se modifique description
  #      description = request.data.get('description')
  #      if description and description != instance.description:
  #          raise ValidationError({"description": "No se permite modificar la descripción."})
            

 #       return super().update(request, *args, **kwargs)
    
    
    


@api_view(['GET'])
def get_full_dqmodel(request, dq_model_id):
    dq_model = get_object_or_404(DQModel, pk=dq_model_id)
    
    # Serializar el modelo
    model_serializer = DQModelSerializer(dq_model)
    
    # Obtener y serializar las dimensiones
    dimensions = DQModelDimension.objects.filter(dq_model=dq_model)
    dimensions_serializer = DQModelDimensionSerializer(dimensions, many=True)
    
    # Obtener y serializar los factores, métricas y métodos
    full_data = {
        'model': model_serializer.data,
        'dimensions': []
    }
    
    for dimension in dimensions:
        dimension_data = DQModelDimensionSerializer(dimension).data
        factors = DQModelFactor.objects.filter(dimension=dimension)
        factors_serializer = DQModelFactorSerializer(factors, many=True)
        dimension_data['factors'] = []
        
        for factor in factors:
            factor_data = DQModelFactorSerializer(factor).data
            metrics = DQModelMetric.objects.filter(factor=factor)
            metrics_serializer = DQModelMetricSerializer(metrics, many=True)
            factor_data['metrics'] = []
            
            for metric in metrics:
                metric_data = DQModelMetricSerializer(metric).data
                methods = DQModelMethod.objects.filter(metric=metric)
                methods_serializer = DQModelMethodSerializer(methods, many=True)
                metric_data['methods'] = methods_serializer.data
                factor_data['metrics'].append(metric_data)
            
            dimension_data['factors'].append(factor_data)
        
        full_data['dimensions'].append(dimension_data)
    
    return Response(full_data, status=status.HTTP_200_OK)





class DQExecutionResultViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['get'], url_path='dqmodels/(?P<dq_model_id>\d+)/measurement-executions')
    def get_dqmodel_executions(self, request, dq_model_id=None):
        """
        Retorna todas las ejecuciones asociadas al DQModel dado,
        incluyendo cuántos métodos fueron ejecutados por cada ejecución.
        """
        try:
            executions = DQModelExecution.objects.using('metadata_db').filter(
                dq_model_id=dq_model_id
            ).order_by('-started_at')

            if not executions.exists():
                return Response({
                    "status": "success",
                    "message": "No hay ejecuciones registradas para este modelo",
                    "dq_model_id": dq_model_id,
                    "executions": []
                }, status=200)

            response_data = []
            for execution in executions:

                response_data.append({
                    "execution_id": str(execution.execution_id),
                    "status": execution.status,
                    "started_at": execution.started_at.isoformat(),
                    "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                })

            return Response({
                "dq_model_id": dq_model_id,
                "executions": response_data
            }, status=200)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({
                "status": "error",
                "message": f"Error al obtener ejecuciones: {str(e)}"
            }, status=500)


    @action(detail=False, methods=['get'], url_path=r'dqmodels/(?P<dq_model_id>\d+)/measurement-executions/(?P<execution_id>[0-9a-f-]+)')
    def get_specific_model_execution(self, request, dq_model_id=None, execution_id=None):
        """
        Devuelve una ejecución específica de un modelo DQModel usando execution_id (UUID).
        """
        try:
            # Buscar ejecución por ID
            execution = DQModelExecution.objects.using('metadata_db').filter(
                dq_model_id=dq_model_id,
                execution_id=execution_id
            ).first()

            if not execution:
                return Response({
                    "status": "error",
                    "message": "Ejecución no encontrada"
                }, status=404)

            # Obtener métodos ejecutados (metadata_db)
            executed_methods = execution.method_results.using('metadata_db').all()
            executed_ids = set(executed_methods.values_list('object_id', flat=True))

            # Obtener todos los métodos aplicados para este modelo (default)
            all_method_ids = list(
                MeasurementDQMethod.objects.using('default').filter(
                    associatedTo__metric__factor__dq_model_id=dq_model_id
                ).values_list('id', flat=True)
            ) + list(
                AggregationDQMethod.objects.using('default').filter(
                    associatedTo__metric__factor__dq_model_id=dq_model_id
                ).values_list('id', flat=True)
            )

            # Calcular métodos pendientes
            pending_ids = list(set(all_method_ids) - executed_ids)
            
            # ACTUALIZAR ejecución si todos los métodos se completaron
            if not pending_ids and execution.status == 'in_progress':
                execution.status = 'completed'
                execution.completed_at = timezone.now()
                execution.save(using='metadata_db')  # Guardamos en metadata_db

            return Response({
                "execution_id": str(execution.execution_id),
                "dq_model_id": execution.dq_model_id,
                "status": execution.status,
                "started_at": execution.started_at,
                "completed_at": execution.completed_at,
                "executed_methods_count": len(executed_ids),
                "pending_methods_count": len(all_method_ids),
                "applied_methods_executed": list(executed_ids),
                "applied_methods_pending": pending_ids
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({
                "status": "error",
                "message": f"Error al obtener la ejecución: {str(e)}"
            }, status=500)


    """
    ViewSet para manejar resultados de ejecución (usando metadata_db)
    """
    
    @action(detail=False, methods=['get'], url_path='dqmodels/(?P<dq_model_id>\d+)/current-execution')
    def get_current_execution(self, request, dq_model_id=None):
        """
        Obtiene la ejecución actual desde metadata_db
        """
        execution = DQModelExecution.objects.using('metadata_db').filter(
            dq_model_id=dq_model_id,
            status='in_progress'
        ).first()
        
        if not execution:
            return Response({'status': 'no_active_execution'})
        
        # Métodos ya ejecutados (desde metadata_db)
        executed_methods = execution.method_results.using('metadata_db').all()
        
        # Todos los métodos del modelo (desde default)
        all_methods = list(
            MeasurementDQMethod.objects.using('default').filter(
                associatedTo__metric__factor__dq_model_id=dq_model_id
            ).values_list('id', flat=True)
        ) + list(
            AggregationDQMethod.objects.using('default').filter(
                associatedTo__metric__factor__dq_model_id=dq_model_id
            ).values_list('id', flat=True)
        )
        
        return Response({
            'execution_id': str(execution.execution_id),
            'status': execution.status,
            'started_at': execution.started_at.isoformat(),
            'progress': {
                'executed': executed_methods.count(),
                'total': len(all_methods),
                'pending': list(set(all_methods) - set(
                    executed_methods.values_list('object_id', flat=True)
                ))
            }
        })
   
    
    @action(detail=False, methods=['get'], url_path='dqmodels/(?P<dq_model_id>\d+)/applied-dq-methods/(?P<applied_method_id>\d+)/execution-result')
    def get_specific_method_execution_result(self, request, dq_model_id=None, applied_method_id=None):
        """
        Obtiene el resultado de ejecución específico para un método aplicado,
        incluyendo información detallada de tablas y columnas utilizadas
        """
        try:
            # Buscar el método aplicado
            try:
                method = MeasurementDQMethod.objects.using('default').get(
                    id=applied_method_id,
                    associatedTo__metric__factor__dq_model_id=dq_model_id
                )
                content_type = ContentType.objects.db_manager('default').get_for_model(MeasurementDQMethod)
            except MeasurementDQMethod.DoesNotExist:
                try:
                    method = AggregationDQMethod.objects.using('default').get(
                        id=applied_method_id,
                        associatedTo__metric__factor__dq_model_id=dq_model_id
                    )
                    content_type = ContentType.objects.db_manager('default').get_for_model(AggregationDQMethod)
                except AggregationDQMethod.DoesNotExist:
                    return Response(
                        {"error": "Método no encontrado en este DQModel"},
                        status=status.HTTP_404_NOT_FOUND
                    )

            # Buscar el resultado más reciente
            result = DQMethodExecutionResult.objects.using('metadata_db').filter(
                content_type=content_type,
                object_id=applied_method_id
            ).select_related('execution').order_by('-executed_at').first()

            if not result:
                return Response(
                    {"error": "No se encontraron resultados de ejecución para este método"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Extraer información de tablas y columnas
            dq_value = result.dq_value if result.dq_value else {}
            applied_to = dq_value.get('applied_to', []) or result.details.get('applied_to', [])
            
            # Procesar información de tablas
            tables = []
            if 'tables' in dq_value:
                tables = dq_value['tables']
            elif applied_to:
                tables = []
                table_ids = set()
                for item in applied_to:
                    if 'table_id' in item and item['table_id'] not in table_ids:
                        tables.append({
                            'table_id': item['table_id'],
                            'table_name': item.get('table_name', '')
                        })
                        table_ids.add(item['table_id'])

            # Procesar información de columnas
            columns = []
            if 'columns' in dq_value:
                columns = dq_value['columns']
            elif applied_to:
                columns = []
                column_ids = set()
                for item in applied_to:
                    if 'column_id' in item and item['column_id'] not in column_ids:
                        columns.append({
                            'column_id': item['column_id'],
                            'column_name': item.get('column_name', ''),
                            'data_type': item.get('data_type', ''),
                            'table_id': item.get('table_id')
                        })
                        column_ids.add(item['column_id'])

            # Construir respuesta
            response_data = {
                'result_id': result.id,
                'dqmodel_execution_id': str(result.execution.execution_id),
                'dqmodel_execution_status': result.execution.status,
                'dq_model_id': dq_model_id,
                'method_id': applied_method_id,
                'method_name': method.name,
                'method_type': method.__class__.__name__,
                'executed_at': result.executed_at.isoformat(),
                'result_type': result.result_type,
                'tables': tables,
                'columns': columns
            }

            # Añadir datos específicos según el tipo de resultado
            # MEASUREMENT
            if result.result_type == 'multiple':
                response_data.update({
                    'dq_values': {
                        'rows': dq_value.get('rows', []) if isinstance(dq_value.get('rows'), list) else [],
                        'total_rows': dq_value.get('total_rows', 0),
                        'columns': dq_value.get('execution_columns', [])
                        #'dq_column': dq_value.get('dq_column')
                    },
                    'execution_details': {
                        'execution_time': result.details.get('execution_time'),
                        'rows_processed': result.details.get('rows_affected', 0),
                        'total_records': result.details.get('total_records', 0)
                    },
                    'assessment_details': {
                        'thresholds': result.assessment_thresholds,
                        'score': result.assessment_score,
                        'is_passing': result.is_passing,
                        'assessed_at': result.assessed_at.isoformat() if result.assessed_at else None
                    }
                })
            else: #AGGREGATED
                response_data.update({
                    'dq_value': dq_value.get('value'),
                    'dq_value_type': type(dq_value.get('value')).__name__ if 'value' in dq_value else 'undefined',
                    'execution_details': {
                        'execution_time': result.details.get('execution_time'),
                        'rows_affected': result.details.get('rows_affected', 1),
                        'total_records': result.details.get('total_records', 0)
                    },
                    'assessment_details': {
                        'thresholds': result.assessment_thresholds,
                        'score': result.assessment_score,
                        'is_passing': result.is_passing,
                        'assessed_at': result.assessed_at.isoformat() if result.assessed_at else None
                    }
                })

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {"error": f"Error al obtener resultados: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    # HELPERS
    def _get_method_and_content_type(self, dq_model_id, applied_method_id):
        try:
            method = MeasurementDQMethod.objects.using('default').get(
                id=applied_method_id,
                associatedTo__metric__factor__dq_model_id=dq_model_id
            )
            content_type = ContentType.objects.db_manager('default').get_for_model(MeasurementDQMethod)
        except MeasurementDQMethod.DoesNotExist:
            method = AggregationDQMethod.objects.using('default').get(
                id=applied_method_id,
                associatedTo__metric__factor__dq_model_id=dq_model_id
            )
            content_type = ContentType.objects.db_manager('default').get_for_model(AggregationDQMethod)

        return method, content_type

    def _get_latest_execution_result(self, content_type, applied_method_id):
        result = DQMethodExecutionResult.objects.using('metadata_db').filter(
            content_type=content_type,
            object_id=applied_method_id
        ).order_by('-executed_at').first()

        if not result:
            raise Exception("No se encontró resultado de ejecución para este método")

        return result


    # RESULTADOS POR METODO
    @action(detail=False, methods=['get'], url_path='dqmodels/(?P<dq_model_id>\d+)/applied-dq-methods/(?P<applied_method_id>\d+)/execution-method-results')
    def get_applied_method_results(self, request, dq_model_id=None, applied_method_id=None):
        try:
            # Obtener el método aplicado
            try:
                applied_method = MeasurementDQMethod.objects.get(
                    id=applied_method_id,
                    associatedTo__metric__factor__dq_model_id=dq_model_id
                )
                content_type = ContentType.objects.get_for_model(MeasurementDQMethod)
            except MeasurementDQMethod.DoesNotExist:
                try:
                    applied_method = AggregationDQMethod.objects.get(
                        id=applied_method_id,
                        associatedTo__metric__factor__dq_model_id=dq_model_id
                    )
                    content_type = ContentType.objects.get_for_model(AggregationDQMethod)
                except AggregationDQMethod.DoesNotExist:
                    return Response(
                        {"status": "error", "message": "Método aplicado no encontrado"},
                        status=404
                    )

            # Obtener los resultados asociados
            results = DQMethodExecutionResult.objects.using('metadata_db').filter(
                content_type=content_type,
                object_id=applied_method.id
            ).order_by('-executed_at')

            if not results.exists():
                return Response({
                    "status": "success",
                    "message": "No hay resultados para este método",
                    "results": []
                }, status=200)

            response_data = []
            for result in results:
                execution_details = {
                    "execution_time": result.details.get('execution_time'),
                    "rows_affected": result.details.get('rows_affected'),
                    "total_records": result.details.get('total_records')
                }

                # Construir la respuesta con los 'thresholds' y 'assessed_at'
                assessment = {
                    "thresholds": result.assessment_thresholds,
                    "assessed_at": result.assessed_at.isoformat() if result.assessed_at else None
                }

                response_data.append({
                    "result_id": result.id,
                    "dqmodel_execution_id": result.execution_id,
                    "executed_at": result.executed_at.isoformat(),
                    "result_type": result.result_type,
                    #"execution_details": execution_details,
                    "assessment": assessment
                })

            return Response({
                "status": "success",
                "method_id": applied_method.id,
                "method_name": applied_method.name,
                "results": response_data
            }, status=200)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({
                "status": "error",
                "message": f"Error inesperado: {str(e)}"
            }, status=500)

    # Get a specific execution result by result_id
    @action(detail=False, methods=['get'], url_path='dqmodels/(?P<dq_model_id>\d+)/applied-dq-methods/(?P<applied_method_id>\d+)/execution-method-results/(?P<result_id>\d+)')
    def get_specific_applied_method_results(self, request, dq_model_id=None, applied_method_id=None, result_id=None):
        try:
            # Obtener el método aplicado y su ContentType
            try:
                applied_method = MeasurementDQMethod.objects.get(
                    id=applied_method_id,
                    associatedTo__metric__factor__dq_model_id=dq_model_id
                )
                content_type = ContentType.objects.get_for_model(MeasurementDQMethod)
            except MeasurementDQMethod.DoesNotExist:
                try:
                    applied_method = AggregationDQMethod.objects.get(
                        id=applied_method_id,
                        associatedTo__metric__factor__dq_model_id=dq_model_id
                    )
                    content_type = ContentType.objects.get_for_model(AggregationDQMethod)
                except AggregationDQMethod.DoesNotExist:
                    return Response(
                        {"status": "error", "message": "Método aplicado no encontrado"},
                        status=404
                    )

            # Buscar el resultado específico
            try:
                result = DQMethodExecutionResult.objects.using('metadata_db').get(
                    id=result_id,
                    content_type=content_type,
                    object_id=applied_method.id
                )
            except DQMethodExecutionResult.DoesNotExist:
                return Response(
                    {"status": "error", "message": "Resultado no encontrado"},
                    status=404
                )

            execution_details = {
                "execution_time": result.details.get('execution_time'),
                "rows_affected": result.details.get('rows_affected'),
                "total_records": result.details.get('total_records')
            }

            assessment = {
                "thresholds": result.assessment_thresholds,
                "assessed_at": result.assessed_at.isoformat() if result.assessed_at else None
            }

            response_data = {
                "status": "success",
                "method_id": applied_method.id,
                "method_name": applied_method.name,
                "result": {
                    "result_id": result.id,
                    "dqmodel_execution_id": result.execution_id,
                    "executed_at": result.executed_at.isoformat(),
                    "result_type": result.result_type,
                    #"execution_details": execution_details,
                    "assessment": assessment
                }
            }

            return Response(response_data, status=200)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({
                "status": "error",
                "message": f"Error inesperado: {str(e)}"
            }, status=500)


    # RESULTADOS POR METODO y ROWS
    @action(detail=False, methods=['get'], url_path='dqmodels/(?P<dq_model_id>\d+)/applied-dq-methods/(?P<applied_method_id>\d+)/execution-row-results')
    def get_method_row_results(self, request, dq_model_id=None, applied_method_id=None):
        try:
            method, content_type = self._get_method_and_content_type(dq_model_id, applied_method_id)
            result = self._get_latest_execution_result(content_type, applied_method_id)

            rows = ExecutionRowResult.objects.using('metadata_db').filter(execution_result=result)

            # Asumimos que todos los valores comunes están presentes al menos en uno
            first_row = rows.first()

            data = [{
                'id': r.id,
                'dq_value': r.dq_value,
                'assessment_score': r.assessment_score,
                'row_id': r.row_id,
            } for r in rows]

            return Response({
                "method_execution_result_id": first_row.execution_result_id if first_row else None,
                "table_id": first_row.table_id if first_row else None,
                "table_name": first_row.table_name if first_row else None,
                "column_id": first_row.column_id if first_row else None,
                "column_name": first_row.column_name if first_row else None,
                "dq_values_count": len(data),
                "dq_values": data
            }, status=200)

        except Exception as e:
            return Response({
                "status": "error",
                "message": f"Error obteniendo row results: {str(e)}"
            }, status=500)


    # RESULTADOS POR METODO y COLUMNS
    @action(detail=False, methods=['get'], url_path='dqmodels/(?P<dq_model_id>\d+)/applied-dq-methods/(?P<applied_method_id>\d+)/execution-column-results')
    def get_method_column_results(self, request, dq_model_id=None, applied_method_id=None):
        try:
            method, content_type = self._get_method_and_content_type(dq_model_id, applied_method_id)
            result = self._get_latest_execution_result(content_type, applied_method_id)

            columns = ExecutionColumnResult.objects.using('metadata_db').filter(execution_result=result)

            data = [{
                'id': c.id,
                'execution_result_method_id': c.execution_result_id,
                'dq_value': c.dq_value,
                'assessment_score': c.assessment_score,
                'table_id': c.table_id,
                'table_name': c.table_name,
                'column_id': c.column_id,
                'column_name': c.column_name,
            } for c in columns]

            return Response({"results": data}, status=200)

        except Exception as e:
            return Response({
                "status": "error",
                "message": f"Error obteniendo column results: {str(e)}"
            }, status=500)
    
    
    # RESULTADO POR DATOS y GRANULARIDAD ----------
    # Endpoint 1: Obtener todos los resultados de ejecución de columna
    @action(detail=False, methods=['get'], url_path='column-results')
    def get_measurement_results_column_granularity(self, request):
        try:
            # Obtener todos los resultados de ejecución de columna
            results = ExecutionColumnResult.objects.using('metadata_db').all()

            # Serializar los resultados
            result_data = ColumnResultSerializer(results, many=True).data

            return Response({'results': result_data}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                "status": "error",
                "message": f"Error al obtener los resultados de ejecución de columna: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Endpoint 2: Obtener los resultados de ejecución de columna de un DQModel específico
    @action(detail=False, methods=['get'], url_path='column-results/dqmodel/(?P<dq_model_id>\d+)')
    def get_measurement_results_column_granularity_dq_model(self, request, dq_model_id=None):
        try:
            # Obtener los resultados de ejecución de columna asociados al DQModel
            results = ExecutionColumnResult.objects.using('metadata_db').filter(dq_model_id=dq_model_id)

            # Serializar los resultados con el serializador ya definido
            result_data = ColumnResultSerializer(results, many=True).data

            return Response({'results': result_data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "error",
                "message": f"Error al obtener los resultados de ejecución de columna para el DQModel {dq_model_id}: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='column-results/(?P<table_id>\d+)')
    def get_measurement_results_column_granularity_by_table(self, request, table_id):
        try:
            results = ExecutionColumnResult.objects.using('metadata_db').filter(table_id=table_id)

            if not results.exists():
                return Response({"message": "No se encontraron resultados para esta tabla."}, status=404)

            result_data = ColumnResultSerializer(results, many=True).data

            return Response({"results": result_data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "error",
                "message": f"Error al obtener resultados para la tabla: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    # Endpoint 3: Obtener los resultados de ejecución de columna para una columna específica
    @action(detail=False, methods=['get'], url_path='column-results/(?P<column_id>\d+)')
    def get_measurement_results_column_granularity_by_column(self, request, column_id):
        try:
            results = ExecutionColumnResult.objects.using('metadata_db').filter(column_id=column_id)
            
            if not results.exists():
                return Response({"message": "No se encontraron resultados para esta columna."}, status=404)

            result_data = ColumnResultSerializer(results, many=True).data

            # Extraer metadatos comunes del primer resultado
            first = results.first()
            context_data = {
                "table_id": first.table_id,
                "table_name": first.table_name,
                "column_id": first.column_id,
                "column_name": first.column_name,
                "results": [
                    {
                        "result_id": r["id"],
                        "dq_value": r["dq_value"],
                        "executed_at": r["executed_at"],
                        "execution_id": r["execution_id"],
                        "applied_method_id": r["applied_method_id"],
                        #"applied_method_execution_id": r["execution_result_id"],
                    }
                    for r in result_data
                ]
            }

            return Response(context_data, status=200)

        except Exception as e:
            return Response({
                "status": "error",
                "message": f"Error al obtener resultados por columna: {str(e)}"
            }, status=500)

      
    @action(detail=False, methods=['get'], url_path='dqmodels/(?P<dq_model_id>\d+)/latest-results')
    def get_latest_results(self, request, dq_model_id=None):
        # 1. Obtener ejecución
        execution = DQModelExecution.objects.using('metadata_db').filter(
            dq_model_id=dq_model_id
        ).order_by('-started_at').first()

        if not execution:
            return Response({"error": "No hay ejecuciones registradas"}, status=404)

        # 2. Obtener métodos aplicados desde default
        methods = list(MeasurementDQMethod.objects.using('default').filter(
            associatedTo__metric__factor__dq_model_id=dq_model_id
        )) + list(AggregationDQMethod.objects.using('default').filter(
            associatedTo__metric__factor__dq_model_id=dq_model_id
        ))

        # 3. Obtener IDs de content_types desde default
        from django.contrib.contenttypes.models import ContentType
        measurement_ct = ContentType.objects.db_manager('default').get_for_model(MeasurementDQMethod)
        aggregation_ct = ContentType.objects.db_manager('default').get_for_model(AggregationDQMethod)

        # 4. Buscar resultados usando RAW SQL para evitar problemas de content_types
        from django.db import connections
        with connections['metadata_db'].cursor() as cursor:
            cursor.execute("""
                SELECT id, object_id, dq_value, details, content_type_id, assessment_thresholds, assessment_score, is_passing, assessed_at
                FROM dq_method_execution_result
                WHERE execution_id = %s
                AND content_type_id IN (%s, %s)
            """, [str(execution.execution_id), measurement_ct.id, aggregation_ct.id])

            raw_results = cursor.fetchall()

        # 5. Mapear resultados
        results_map = {}
        for row in raw_results:
            result_id, object_id, dq_value, details, content_type_id, assessment_thresholds, assessment_score, is_passing, assessed_at = row
            # Aquí puedes convertir assessment_thresholds (si es necesario) para que sea una lista
            # Si los datos vienen como un string JSON, puedes hacer un `json.loads()`
            thresholds = json.loads(assessment_thresholds) if assessment_thresholds else []
            results_map[(content_type_id, object_id)] = {
                'result_id': result_id,
                'dq_value': dq_value,
                'dq_value_type': type(dq_value).__name__,
                'details': details,
                'assessment_details': {
                    'thresholds': thresholds,
                    'score': assessment_score,
                    'is_passing': is_passing,
                    'assessed_at': assessed_at.isoformat() if assessed_at else None
                }
            }

        # 6. Construir respuesta
        formatted = []
        completed_count = 0
        for method in methods:
            content_type_id = measurement_ct.id if isinstance(method, MeasurementDQMethod) else aggregation_ct.id
            key = (content_type_id, method.id)

            # Verificar si hay resultados de ejecución para el método
            if key in results_map:
                result = results_map[key]
                # Resultados completados
                formatted.append({
                    'execution_result_id': result['result_id'],
                    'method_id': method.id,
                    'method_name': method.name,
                    'method_type': method.__class__.__name__,
                    'status': 'completed',
                    'dq_value': result['dq_value'],
                    'dq_value_type': result['dq_value_type'],
                    'details': result['details'],
                    'assessment_details': result['assessment_details']  # Se incluyen los detalles de evaluación
                })
                completed_count += 1
            else:
                # Métodos pendientes
                formatted.append({
                    'method_id': method.id,
                    'method_name': method.name,
                    'method_type': method.__class__.__name__,
                    'status': 'pending'
                })

        # 7. Construir información sobre la ejecución
        execution_status = execution.status
        started_at = execution.started_at.isoformat() if execution.started_at else None
        completed_at = execution.completed_at.isoformat() if execution.completed_at else None

        progress = {
            'methods_completed': completed_count,
            'methods_pending': len(formatted) - completed_count,
            'methods_total': len(formatted)
        }

        # 8. Retornar la respuesta
        return Response({
            'execution_id': str(execution.execution_id),
            'execution_status': execution_status,
            'started_at': started_at,
            'completed_at': completed_at,
            'dqmodel_execution_progress': progress,
            'results': sorted(formatted, key=lambda x: x['status'])  # Ordenamos por estado
        })


  
    @action(detail=False, methods=['get'], url_path='applied-dq-methods/(?P<method_id>\d+)/results')
    def get_method_results(self, request, method_id=None):
        """
        Obtiene resultados históricos de un método desde metadata_db
        """
        # Determinar tipo de método (desde default)
        try:
            method = MeasurementDQMethod.objects.using('default').get(id=method_id)
            content_type = ContentType.objects.db_manager('default').get_for_model(MeasurementDQMethod)
        except MeasurementDQMethod.DoesNotExist:
            method = get_object_or_404(AggregationDQMethod.objects.using('default'), id=method_id)
            content_type = ContentType.objects.db_manager('default').get_for_model(AggregationDQMethod)
        
        # Resultados desde metadata_db
        results = DQMethodExecutionResult.objects.using('metadata_db').filter(
            content_type=content_type,
            object_id=method_id
        ).select_related('execution').order_by('-executed_at')
        
        return Response({
            'method_id': method_id,
            'method_name': method.name,
            'method_type': method.__class__.__name__,
            'results': [self._format_result(r) for r in results]
        })
    
    def _format_result(self, result):
        """Formatea un resultado individual"""
        return {
            'execution_id': str(result.execution.execution_id),
            'dq_model_id': result.execution.dq_model_id,
            'executed_at': result.executed_at.isoformat(),
            'dq_value': result.dq_value,
            'details': result.details
        }
    
    @action(detail=False, methods=['patch'], url_path='dqmodels/(?P<dq_model_id>\d+)/applied-dq-methods/(?P<applied_method_id>\d+)/execution-method-results/(?P<result_id>\d+)/thresholds')
    def update_execution_result_thresholds(self, request, dq_model_id=None, applied_method_id=None, result_id=None):
        """
        Updates the thresholds and related assessment fields for a specific execution result.
        """
        try:
            # Try to find the applied method and its content type
            try:
                applied_method = MeasurementDQMethod.objects.get(
                    id=applied_method_id,
                    associatedTo__metric__factor__dq_model_id=dq_model_id
                )
                content_type = ContentType.objects.get_for_model(MeasurementDQMethod)
            except MeasurementDQMethod.DoesNotExist:
                try:
                    applied_method = AggregationDQMethod.objects.get(
                        id=applied_method_id,
                        associatedTo__metric__factor__dq_model_id=dq_model_id
                    )
                    content_type = ContentType.objects.get_for_model(AggregationDQMethod)
                except AggregationDQMethod.DoesNotExist:
                    return Response(
                        {"error": "Applied method not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )

            # Find the execution result using the correct content_type and object_id
            try:
                result = DQMethodExecutionResult.objects.using('metadata_db').get(
                    id=result_id,
                    content_type=content_type,
                    object_id=applied_method.id
                )
            except DQMethodExecutionResult.DoesNotExist:
                return Response(
                    {"error": "Execution result not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Parse and validate thresholds
            thresholds = request.data.get('thresholds', [])
            if not isinstance(thresholds, list):
                return Response({"error": "Thresholds must be a list"}, status=status.HTTP_400_BAD_REQUEST)

            for threshold in thresholds:
                if not all(key in threshold for key in ['name', 'min', 'max']):
                    return Response(
                        {"error": "Each threshold must have 'name', 'min', 'max' fields"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Optional fields
            #score = request.data.get('score', None)
            #is_passing = request.data.get('is_passing', None)
            #assessed_at = request.data.get('assessed_at', None)

            # Apply updates
            result.assessment_thresholds = thresholds

            result.save(update_fields=['assessment_thresholds'])

            return Response({
                "status": "success",
                "message": "Thresholds updated successfully",
                "result_id": result.id,
                "assessment": {
                    "thresholds": result.assessment_thresholds,
                    #"assessed_at": result.assessed_at.isoformat() if result.assessed_at else None
                }
            }, status=200)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





    
   
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super().default(o)


def get_db_connection():
    """Obtiene conexión a la base de datos con verificación explícita"""
    try:
        conn = psycopg2.connect(
            dbname='data_at_hand_v01',
            user='postgres',
            password='password',
            host='localhost',
            port=5432
        )
        
        # Verificación extendida
        with conn.cursor() as cursor:
            # 1. Verificar conexión básica
            cursor.execute("SELECT 1")
            if cursor.fetchone()[0] != 1:
                raise Exception("Verificación básica de conexión falló")
            
            # 2. Verificar base de datos actual
            cursor.execute("SELECT current_database()")
            db_name = cursor.fetchone()[0]
            print(f"\n--- Conectado a la base de datos: {db_name} ---")  # Log en consola
            
            # 3. Verificar si la tabla existe
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'books_rating'
                )
            """)
            table_exists = cursor.fetchone()[0]
            print(f"--- ¿Existe la tabla 'books_rating'?: {table_exists} ---")
            
            if not table_exists:
                # 4. Listar tablas disponibles para debug
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """)
                print("Tablas disponibles:", [row[0] for row in cursor.fetchall()])
                
        return conn
        
    except Exception as e:
        print(f"\n--- Error de conexión: {str(e)} ---")  # Log en consola
        raise Exception(f"No se pudo conectar a la base de datos: {str(e)}")
    

    """
    Ejecuta un método aplicado con chequeo de conexión a BD
    """
    try:
        # 1. Buscar el método aplicado
        method = (MeasurementDQMethod.objects.filter(
                    dq_model_id=dq_model_id,
                    id=method_id
                 ).first() or 
                 AggregationDQMethod.objects.filter(
                    dq_model_id=dq_model_id,
                    id=method_id
                 ).first())
        
        if not method:
            return Response(
                {'error': 'Método no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2. Validar el algoritmo
        if not method.algorithm.strip():
            return Response(
                {'error': 'El método no tiene algoritmo definido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Conectar a la base de datos (con chequeo explícito)
        try:
            conn = get_db_connection()
        except Exception as e:
            return Response(
                {
                    'status': 'error',
                    'method_id': method_id,
                    'error': str(e),
                    'db_check': 'failed',
                    'timestamp': timezone.now().isoformat()
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        # 4. Ejecutar consulta
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(method.algorithm)
                
                # Procesar resultados
                columns = [desc[0] for desc in cursor.description]
                rows = [dict(row) for row in cursor.fetchall()]
                
                response_data = {
                    'status': 'success',
                    'method_id': method.id,
                    'method_name': method.name,
                    'applied_to': method.applied_to,
                    'columns': columns,
                    'data': rows,
                    'query': method.algorithm,
                    'db_check': 'success',
                    'timestamp': timezone.now().isoformat()
                }
                
                return Response(response_data)
                
        except Exception as e:
            return Response(
                {
                    'status': 'error',
                    'method_id': method_id,
                    'error': f"Error ejecutando consulta: {str(e)}",
                    'db_check': 'connection_ok',
                    'timestamp': timezone.now().isoformat()
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        return Response(
            {
                'status': 'error',
                'method_id': method_id,
                'error': f"Error inesperado: {str(e)}",
                'timestamp': timezone.now().isoformat()
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    finally:
        if 'conn' in locals():
            conn.close()
            
            

@api_view(['POST'])
def set_assessment_thresholds(request, result_id):
    result = get_object_or_404(DQMethodExecutionResult, result_id=result_id)
    result.assessment_thresholds = request.data.get('thresholds', [])
    result.save()
    
    return Response({
        'status': 'success',
        'result_id': str(result_id),
        'thresholds_set': len(result.assessment_thresholds)
    })

@api_view(['POST'])
def execute_assessment(request, result_id):
    result = get_object_or_404(DQMethodExecutionResult, result_id=result_id)
    
    # Opción 1: Usar thresholds del request
    if 'thresholds' in request.data:
        result.assess(thresholds=request.data['thresholds'])
    # Opción 2: Usar thresholds ya guardados
    else:
        result.assess()
    
    return Response({
        'status': 'success',
        'result_id': str(result_id),
        'assessment_score': result.assessment_score,
        'is_passing': result.is_passing,
        'assessed_at': result.assessed_at
    })
    
    
from rest_framework import viewsets
from django.db.models import Prefetch

class TableResultsViewSet(viewsets.ReadOnlyModelViewSet):
    """Endpoint para resultados a nivel de tabla"""
    queryset = ExecutionTableResult.objects.using('metadata_db').all()
    serializer_class = TableResultSerializer  # Debes crear este serializer
    
    def get_queryset(self):
        dq_model_id = self.kwargs['dq_model_id']
        return self.queryset.filter(
            execution_result__execution__dq_model_id=dq_model_id
        ).select_related('execution_result')

class ColumnResultsViewSet(viewsets.ReadOnlyModelViewSet):
    """Endpoint para resultados a nivel de columna"""
    queryset = ExecutionColumnResult.objects.using('metadata_db').all()
    serializer_class = ColumnResultSerializer
    
    def get_queryset(self):
        dq_model_id = self.kwargs['dq_model_id']
        return self.queryset.filter(
            execution_result__execution__dq_model_id=dq_model_id
        ).select_related('execution_result')

class RowResultsViewSet(viewsets.ReadOnlyModelViewSet):
    """Endpoint para resultados a nivel de fila"""
    queryset = ExecutionRowResult.objects.using('metadata_db').all()
    serializer_class = RowResultSerializer
    #pagination_class = LargeResultsSetPagination  # Para manejar muchos registros
    
    def get_queryset(self):
        dq_model_id = self.kwargs['dq_model_id']
        queryset = self.queryset.filter(
            execution_result__execution__dq_model_id=dq_model_id
        )
        
        # Filtros opcionales
        table_id = self.request.query_params.get('table_id')
        if table_id:
            queryset = queryset.filter(table_id=table_id)
            
        column_id = self.request.query_params.get('column_id')
        if column_id:
            queryset = queryset.filter(column_id=column_id)
            
        return queryset.select_related('execution_result')