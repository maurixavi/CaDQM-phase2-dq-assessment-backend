from datetime import timezone
import time
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Value, CharField 
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action, api_view

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
    MeasurementDQMethod,
    AggregationDQMethod,
    PrioritizedDqProblem,
    PrioritizedDqProblem
)
from .serializer import (
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
    PrioritizedDqProblemSerializer
)
from .ai_utils import generate_ai_suggestion
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# AI SUGGESTIONS GENERATION
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
        suggestion = generate_ai_suggestion(dq_metric_data)

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


# SELECTED PRIORITIZED PROBLEMS VIEW
@api_view(['GET'])
def get_selected_prioritized_dq_problems(request, dq_model_id):
    """
    Devuelve solo los problemas priorizados seleccionados (is_selected=True) para un DQModel específico.
    """
    dq_model = get_object_or_404(DQModel, pk=dq_model_id)
    selected_problems = PrioritizedDqProblem.objects.filter(dq_model=dq_model, is_selected=True)

    if selected_problems.exists():
        serializer = PrioritizedDqProblemSerializer(selected_problems, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(
        {"detail": "No selected prioritized problems found for this DQModel"},
        status=status.HTTP_404_NOT_FOUND
    )

# PRIORITIZED PROBLEMS VIEW
@api_view(['GET'])
def get_prioritized_dq_problems(request, dq_model_id):
    print(f"Buscando problemas para model_id: {dq_model_id}")
    
    # Verificar que el modelo existe
    try:
        model = DQModel.objects.get(id=dq_model_id)
    except DQModel.DoesNotExist:
        return Response(
            {"error": f"DQModel with id {dq_model_id} not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    problems = PrioritizedDqProblem.objects.filter(dq_model=dq_model_id)
    
    if not problems:
        return Response({
            "error": f"No prioritized problems found for DQModel {dq_model_id}"
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = PrioritizedDqProblemSerializer(problems, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# INITIALIZE PRIORITIZED PROBLEMS FROM PROJECT DQ PROBLEMS
@api_view(['POST'])
def create_initial_prioritized_dq_problems(request):
    if request.method == 'POST':
        # Obtener el DQModel
        dq_model_id = request.data[0].get('dq_model')
        try:
            dq_model = DQModel.objects.get(id=dq_model_id)
        except DQModel.DoesNotExist:
            return Response({"error": "DQModel not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar si ya existen problemas priorizados
        existing_problems = PrioritizedDqProblem.objects.filter(dq_model=dq_model)
        if existing_problems.exists():
            return Response({"error": "DQModel already has prioritized problems"}, status=status.HTTP_400_BAD_REQUEST)

        # Crear los problemas priorizados
        prioritized_problems = []
        for problem_data in request.data:
            prioritized_problem = PrioritizedDqProblem(
                dq_model=dq_model,
                description=problem_data['description'],
                priority=-1,  # valor por defecto
                priority_type='Medium',  # valor por defecto
                date=problem_data['date'] 
            )
            prioritized_problems.append(prioritized_problem)

        # Guardar los problemas priorizados
        PrioritizedDqProblem.objects.bulk_create(prioritized_problems)

        return Response({"message": "Prioritized problems created successfully"}, status=status.HTTP_201_CREATED)



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
        if factors.exists():
            serializer = self.get_serializer(factors, many=True)
            return Response(serializer.data)
        return Response({"detail": "No factors found for this dimension"}, status=status.HTTP_404_NOT_FOUND)
    

# ViewSet para DQMetricBase
class DQMetricBaseViewSet(viewsets.ModelViewSet):
    queryset = DQMetricBase.objects.all()
    serializer_class = DQMetricBaseSerializer

    @action(detail=True, methods=['get'], url_path='metrics-base')
    def get_metrics_by_factor(self, request, pk=None, dim_id=None):
        # Filtrar factores basados en el dimension_id
        metrics = self.queryset.filter(measures_id=pk)
        if metrics.exists():
            serializer = self.get_serializer(metrics, many=True)
            return Response(serializer.data)
        return Response({"detail": "No metrics found for this factor"}, status=status.HTTP_404_NOT_FOUND)
 
    # En DQMetricBaseViewSet
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
        if methods.exists():
            serializer = self.get_serializer(methods, many=True)
            return Response(serializer.data)
        return Response({"detail": "No methods found for this metric"}, status=status.HTTP_404_NOT_FOUND)



# DQ MODEL VIEWS:




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


    @action(detail=True, methods=['post'], url_path='applied-dq-methods/(?P<applied_method_id>[^/.]+)/execute')
    def execute_applied_method(self, request, pk=None, applied_method_id=None):
        """
        Ejecuta un método aplicado con manejo explícito de tipos Decimal
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
            debug_info.append(f"DQModel encontrado (ID: {dq_model.id}, Versión: {dq_model.version}")

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
                    
                    # Función para convertir Decimal a float
                    def convert_decimals(obj):
                        if isinstance(obj, Decimal):
                            return float(obj)
                        elif isinstance(obj, dict):
                            return {k: convert_decimals(v) for k, v in obj.items()}
                        elif isinstance(obj, (list, tuple)):
                            return [convert_decimals(item) for item in obj]
                        return obj
                    
                    # Obtener y convertir los resultados
                    rows = [convert_decimals(dict(row)) for row in cursor.fetchall()]
                    
                    query_time = time.time() - query_start_time
                    debug_info.append(f"Tiempo de ejecución SQL: {query_time:.4f} segundos")
                    
                    # Guardar resultados en metadata_db
                    try:
                        DQExecutionResultService.save_execution_result(
                            dq_model_id=pk,
                            applied_method=applied_method,
                            result_value=rows[0].get(columns[0]),
                            execution_details={
                                'query_time_seconds': query_time,
                                'rows_affected': cursor.rowcount,
                                'columns': columns,
                                'sample_data': rows[:5],
                                'query': applied_method.algorithm
                            }
                        )
                    except Exception as e:
                        debug_info.append(f"Advertencia al guardar resultados: {str(e)}")

                    # Procesar resultados para la respuesta
                    processed_results = []
                    for row in rows:
                        processed_row = {
                            'dq_metric_name': applied_method.name,
                            'dq_metric_id': applied_method.id,
                            'applied_to': applied_method.appliedTo,
                            'execution_time_seconds': round(query_time, 4),
                            'dq_value': row.get(columns[0])
                        }
                        processed_results.append(processed_row)

                    debug_info.append(f"Consulta ejecutada con éxito. Filas devueltas: {len(rows)}")
                    
                    response_data.update({
                        'status': 'success',
                        'dq_results': processed_results,
                        'execution_details': {
                            'total_time_seconds': round((timezone.now() - start_time).total_seconds(), 4),
                            'query_time_seconds': round(query_time, 4),
                            'rows_affected': cursor.rowcount
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
    def execute_applied_method_problemaconjson(self, request, pk=None, applied_method_id=None):
        """
        Ejecuta un método aplicado con resultados mejor formateados y medición de tiempo
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
            debug_info.append(f"DQModel encontrado (ID: {dq_model.id}, Versión: {dq_model.version}")

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
            # After finding the applied_method
            #debug_info.append(f"Método aplicado: {applied_method.name} (ID: {applied_method.id}, Tipo: {method_type})")
            #debug_info.append(f"Todos los campos: {applied_method.__dict__}")
            #debug_info.append(f"¿Tiene atributo 'algorithm'?: {'algorithm' in applied_method.__dict__}")
            #debug_info.append(f"Valor directo: {getattr(applied_method, 'algorithm', 'NO EXISTE')}")
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
                    rows = [dict(row) for row in cursor.fetchall()]
                    
                    query_time = time.time() - query_start_time
                    debug_info.append(f"Tiempo de ejecución SQL: {query_time:.4f} segundos")
                    
                    # Guardar resultados en metadata_db
                    DQExecutionResultService.save_execution_result(
                        dq_model_id=pk,
                        applied_method=applied_method,
                        result_value=rows[0].get(columns[0]),  # Cerrar el paréntesis de get()
                        execution_details={
                            'query_time_seconds': query_time,
                            'rows_affected': cursor.rowcount,
                            'columns': columns,
                            'sample_data': rows[:5],  # Guardar solo 5 filas como muestra
                            'query': applied_method.algorithm
                        }
                    )

                    # Procesar resultados para mejor claridad
                    processed_results = []
                    for row in rows:
                        processed_row = {
                            'dq_metric_name': applied_method.name,
                            'dq_metric_id': applied_method.id,
                            'applied_to': applied_method.appliedTo,
                            'execution_time_seconds': round(query_time, 4),
                            'dq_value': row.get(columns[0], None)  # Tomamos el primer valor como dq_value
                        }
                        processed_results.append(processed_row)

                    debug_info.append(f"Consulta ejecutada con éxito. Filas devueltas: {len(rows)}")
                    
                    response_data.update({
                        'status': 'success',
                        'dq_results': processed_results,
                        'execution_details': {
                            'total_time_seconds': round((timezone.now() - start_time).total_seconds(), 4),
                            'query_time_seconds': round(query_time, 4),
                            'rows_affected': cursor.rowcount
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
    def execute_applied_method_funciona_noguarda(self, request, pk=None, applied_method_id=None):
        """
        Ejecuta un método aplicado con resultados mejor formateados y medición de tiempo
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
            debug_info.append(f"DQModel encontrado (ID: {dq_model.id}, Versión: {dq_model.version}")

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
            # After finding the applied_method
            #debug_info.append(f"Método aplicado: {applied_method.name} (ID: {applied_method.id}, Tipo: {method_type})")
            #debug_info.append(f"Todos los campos: {applied_method.__dict__}")
            #debug_info.append(f"¿Tiene atributo 'algorithm'?: {'algorithm' in applied_method.__dict__}")
            #debug_info.append(f"Valor directo: {getattr(applied_method, 'algorithm', 'NO EXISTE')}")
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
                    rows = [dict(row) for row in cursor.fetchall()]
                    
                    query_time = time.time() - query_start_time
                    debug_info.append(f"Tiempo de ejecución SQL: {query_time:.4f} segundos")

                    # Procesar resultados para mejor claridad
                    processed_results = []
                    for row in rows:
                        processed_row = {
                            'dq_metric_name': applied_method.name,
                            'dq_metric_id': applied_method.id,
                            'applied_to': applied_method.appliedTo,
                            'execution_time_seconds': round(query_time, 4),
                            'dq_value': row.get(columns[0], None)  # Tomamos el primer valor como dq_value
                        }
                        processed_results.append(processed_row)

                    debug_info.append(f"Consulta ejecutada con éxito. Filas devueltas: {len(rows)}")
                    
                    response_data.update({
                        'status': 'success',
                        'dq_results': processed_results,
                        'execution_details': {
                            'total_time_seconds': round((timezone.now() - start_time).total_seconds(), 4),
                            'query_time_seconds': round(query_time, 4),
                            'rows_affected': cursor.rowcount
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
class PrioritizedDqProblemDetailView(viewsets.ModelViewSet):
    #queryset = PrioritizedDqProblem.objects.all()
    serializer_class = PrioritizedDqProblemSerializer
    
    def get_queryset(self):
        dq_model_id = self.kwargs.get('dq_model_id')
        return PrioritizedDqProblem.objects.filter(dq_model_id=dq_model_id).order_by('priority')

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Validar que no se modifique dq_model_id
        dq_model_id = request.data.get('dq_model')
        if dq_model_id and int(dq_model_id) != instance.dq_model.id:
            raise ValidationError({"dq_model": "No se permite cambiar el dqmodel de un problema priorizado existente."})
        
        # Validar que no se modifique description
        description = request.data.get('description')
        if description and description != instance.description:
            raise ValidationError({"description": "No se permite modificar la descripción."})
            

        return super().update(request, *args, **kwargs)
    
    
    


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

class DQExecutionResultViewSet(viewsets.ViewSet):
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
        independientemente del estado de ejecución del modelo completo
        """
        # Buscar el método aplicado para validar que existe
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

        # Buscar TODAS las ejecuciones que incluyan este método (no solo las completadas)
        executions = DQModelExecution.objects.using('metadata_db').filter(
            dq_model_id=dq_model_id
        ).order_by('-started_at')

        # Buscar el resultado más reciente para este método en cualquier ejecución
        result = DQMethodExecutionResult.objects.using('metadata_db').filter(
            content_type=content_type,
            object_id=applied_method_id
        ).select_related('execution').order_by('-executed_at').first()

        if not result:
            return Response(
                {"error": "No se encontraron resultados de ejecución para este método"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response({
            'execution_id': str(result.execution.execution_id),
            'execution_status': result.execution.status,
            'dq_model_id': dq_model_id,
            'method_id': applied_method_id,
            'method_name': method.name,
            'method_type': method.__class__.__name__,
            'executed_at': result.executed_at.isoformat(),
            'dq_value': result.dq_value,
            'execution_time': result.details.get('execution_time'),
            'rows_affected': result.details.get('rows_affected'),
            'columns': result.details.get('columns'),
            'sample_data': result.details.get('sample_data'),
            'query': result.details.get('query')
        })
    
    
    
    @action(detail=False, methods=['get'], url_path='dqmodels/(?P<dq_model_id>\d+)/executions/(?P<execution_id>[^/.]+)')
    def get_execution_results2(self, request, dq_model_id=None, execution_id=None):
        """
        Obtiene resultados de una ejecución específica desde metadata_db
        """
        execution = get_object_or_404(
            DQModelExecution.objects.using('metadata_db'),
            execution_id=execution_id,
            dq_model_id=dq_model_id
        )
        
        results = execution.method_results.using('metadata_db').select_related('content_type').all()
        
        return Response({
            'execution_id': str(execution.execution_id),
            'status': execution.status,
            'started_at': execution.started_at.isoformat(),
            'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
            'results': [self._format_result(r) for r in results]
        })
    
    @action(detail=False, methods=['get'], url_path='dqmodels/(?P<dq_model_id>\d+)/latest-results')
    def get_latest_results(self, request, dq_model_id=None):
        """
        Versión final - Obtiene resultados actualizados incluyendo ejecuciones recientes
        """
        try:
            # 1. Obtener la ejecución activa
            execution = DQModelExecution.objects.using('metadata_db').filter(
                dq_model_id=dq_model_id
            ).order_by('-started_at').first()

            if not execution:
                return Response(
                    {"error": "No hay ejecuciones registradas para este modelo"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # 2. Obtener todos los métodos aplicados del modelo
            methods_qs = MeasurementDQMethod.objects.using('default').filter(
                associatedTo__metric__factor__dq_model_id=dq_model_id
            ).annotate(
                method_type=Value('MeasurementDQMethod', output_field=CharField())
            ).union(
                AggregationDQMethod.objects.using('default').filter(
                    associatedTo__metric__factor__dq_model_id=dq_model_id
                ).annotate(
                    method_type=Value('AggregationDQMethod', output_field=CharField())
                )
            )

            # 3. Obtener todos los resultados de ejecución
            executed_results = DQMethodExecutionResult.objects.using('metadata_db').filter(
                execution=execution
            ).select_related('content_type')

            # 4. Mapear content types
            content_types = {
                'MeasurementDQMethod': ContentType.objects.db_manager('default').get_for_model(MeasurementDQMethod),
                'AggregationDQMethod': ContentType.objects.db_manager('default').get_for_model(AggregationDQMethod)
            }

            # 5. Construir respuesta
            formatted_results = []
            completed_count = 0

            for method in methods_qs:
                content_type = content_types[method.method_type]
                result = executed_results.filter(
                    content_type=content_type,
                    object_id=method.id
                ).first()

                if result:
                    # Método ejecutado
                    formatted_results.append({
                        'method_id': method.id,
                        'method_name': method.name,
                        'method_type': method.method_type,
                        'executed_at': result.executed_at.isoformat(),
                        'dq_value': result.dq_value,
                        'execution_time': result.details.get('execution_time'),
                        'columns': result.details.get('columns'),
                        'sample_data': result.details.get('sample_data'),
                        'query': result.details.get('query'),
                        'status': 'completed'
                    })
                    completed_count += 1
                else:
                    # Método pendiente
                    formatted_results.append({
                        'method_id': method.id,
                        'method_name': method.name,
                        'method_type': method.method_type,
                        'status': 'pending'
                    })

            # 6. Ordenar resultados (completados primero)
            formatted_results.sort(key=lambda x: (0 if x['status'] == 'completed' else 1, x['method_id']))

            return Response({
                'execution_id': str(execution.execution_id),
                'execution_status': execution.status,
                'started_at': execution.started_at.isoformat(),
                'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
                'progress': {
                    'completed': completed_count,
                    'pending': len(formatted_results) - completed_count,
                    'total': len(formatted_results)
                },
                'results': formatted_results
            })

        except Exception as e:
            return Response(
                {"error": f"Error al obtener resultados: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    
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
                SELECT object_id, dq_value, details, content_type_id
                FROM dq_method_execution_result
                WHERE execution_id = %s
                AND content_type_id IN (%s, %s)
            """, [str(execution.execution_id), measurement_ct.id, aggregation_ct.id])
            
            raw_results = cursor.fetchall()

        # 5. Mapear resultados
        results_map = {}
        for row in raw_results:
            object_id, dq_value, details, content_type_id = row
            results_map[(content_type_id, object_id)] = {
                'dq_value': dq_value,
                'details': details
            }

        # 6. Construir respuesta
        formatted = []
        for method in methods:
            content_type_id = measurement_ct.id if isinstance(method, MeasurementDQMethod) else aggregation_ct.id
            key = (content_type_id, method.id)
            
            if key in results_map:
                result = results_map[key]
                formatted.append({
                    'method_id': method.id,
                    'method_name': method.name,
                    'method_type': method.__class__.__name__,
                    'status': 'completed',
                    'dq_value': result['dq_value'],
                    'details': result['details']
                })
            else:
                formatted.append({
                    'method_id': method.id,
                    'method_name': method.name,
                    'method_type': method.__class__.__name__,
                    'status': 'pending'
                })

        return Response({
            'execution_id': str(execution.execution_id),
            'results': sorted(formatted, key=lambda x: x['status'])
        })
    
    @action(detail=False, methods=['get'], url_path='dqmodels/(?P<dq_model_id>\d+)/latest-results')
    def get_latest_results222(self, request, dq_model_id=None):
        """
        Obtiene los últimos resultados para un DQModel con mensajes de debug
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"\n{'='*50}")
        logger.info(f"Iniciando búsqueda de resultados para DQModel {dq_model_id}")
        logger.info(f"{'='*50}\n")

        # 1. Obtener la ejecución activa
        execution = DQModelExecution.objects.using('metadata_db').filter(
            dq_model_id=dq_model_id
        ).order_by('-started_at').first()

        if not execution:
            logger.error("No se encontró ninguna ejecución para este modelo")
            return Response(
                {"error": "No hay ejecuciones registradas para este modelo"},
                status=status.HTTP_404_NOT_FOUND
            )

        logger.info(f"Ejecución encontrada - ID: {execution.execution_id}")
        logger.info(f"Estado: {execution.status}")
        logger.info(f"Iniciada: {execution.started_at}")
        logger.info(f"Completada: {execution.completed_at}\n")

        # 2. Obtener métodos aplicados
        logger.info("Buscando métodos Measurement...")
        measurement_methods = list(MeasurementDQMethod.objects.using('default').filter(
            associatedTo__metric__factor__dq_model_id=dq_model_id
        ))
        logger.info(f"Encontrados {len(measurement_methods)} métodos Measurement")
        
        logger.info("Buscando métodos Aggregation...")
        aggregation_methods = list(AggregationDQMethod.objects.using('default').filter(
            associatedTo__metric__factor__dq_model_id=dq_model_id
        ))
        logger.info(f"Encontrados {len(aggregation_methods)} métodos Aggregation")
        
        all_methods = measurement_methods + aggregation_methods
        logger.info(f"Total métodos aplicados: {len(all_methods)}\n")

        # 3. Obtener resultados ejecutados
        logger.info("Buscando resultados ejecutados en metadata_db...")
        executed_results = list(DQMethodExecutionResult.objects.using('metadata_db').filter(
            execution=execution
        ).select_related('content_type'))
        logger.info(f"Total resultados encontrados: {len(executed_results)}\n")

        # 4. Obtener ContentTypes
        logger.info("Obteniendo ContentTypes...")
        measurement_type = ContentType.objects.db_manager('default').get_for_model(MeasurementDQMethod)
        aggregation_type = ContentType.objects.db_manager('default').get_for_model(AggregationDQMethod)
        logger.info(f"ContentType para Measurement: {measurement_type.id}")
        logger.info(f"ContentType para Aggregation: {aggregation_type.id}\n")

        # 5. Loggear resultados encontrados
        logger.info("Resultados individuales encontrados:")
        for result in executed_results:
            logger.info(f"ID: {result.id} | ContentType: {result.content_type_id} | ObjectID: {result.object_id} | Método: {result.content_type.model}")

        # 6. Mapear resultados
        executed_map = {}
        for r in executed_results:
            if r.content_type_id in [measurement_type.id, aggregation_type.id]:
                executed_map[(r.content_type_id, r.object_id)] = r
                logger.info(f"Mapeado: ({r.content_type_id}, {r.object_id}) -> Resultado ID {r.id}")
        
        logger.info(f"\nTotal resultados mapeados: {len(executed_map)}\n")

        # 7. Procesar métodos
        formatted_results = []
        logger.info("Procesando métodos...")
        
        for method in all_methods:
            method_type = 'MeasurementDQMethod' if isinstance(method, MeasurementDQMethod) else 'AggregationDQMethod'
            content_type_id = measurement_type.id if method_type == 'MeasurementDQMethod' else aggregation_type.id
            key = (content_type_id, method.id)
            
            logger.info(f"\nProcesando método ID {method.id} ({method_type})")
            logger.info(f"Clave de búsqueda: {key}")

            if key in executed_map:
                result = executed_map[key]
                logger.info(f"Resultado ENCONTRADO - ID: {result.id}")
                logger.info(f"Detalles: {result.details}")
                
                formatted_results.append({
                    'method_id': method.id,
                    'method_name': method.name,
                    'method_type': method_type,
                    'executed_at': result.executed_at.isoformat(),
                    'dq_value': result.dq_value,
                    'execution_time': result.details.get('execution_time'),
                    'columns': result.details.get('columns'),
                    'sample_data': result.details.get('sample_data'),
                    'query': result.details.get('query'),
                    'status': 'completed'
                })
            else:
                logger.info("Resultado NO encontrado (pendiente)")
                formatted_results.append({
                    'method_id': method.id,
                    'method_name': method.name,
                    'method_type': method_type,
                    'status': 'pending'
                })

        # 8. Estadísticas finales
        completed = len([r for r in formatted_results if r['status'] == 'completed'])
        logger.info(f"\n{'='*50}")
        logger.info(f"RESUMEN FINAL")
        logger.info(f"Métodos completados: {completed}")
        logger.info(f"Métodos pendientes: {len(formatted_results) - completed}")
        logger.info(f"Total métodos: {len(formatted_results)}")
        logger.info(f"{'='*50}\n")

        return Response({
            'execution_id': str(execution.execution_id),
            'execution_status': execution.status,
            'started_at': execution.started_at.isoformat(),
            'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
            'progress': {
                'completed': completed,
                'pending': len(formatted_results) - completed,
                'total': len(formatted_results)
            },
            'results': sorted(formatted_results, key=lambda x: (0 if x['status'] == 'completed' else 1, x['method_id']))
        })      
        
    @action(detail=False, methods=['get'], url_path='dqmodels/(?P<dq_model_id>\d+)/latest-results')
    def get_latest_results___(self, request, dq_model_id=None):
        """
        Obtiene los últimos resultados para un DQModel, mostrando ejecutados y pendientes
        """
        # Obtener la ejecución activa más reciente (completada o en progreso)
        execution = DQModelExecution.objects.using('metadata_db').filter(
            dq_model_id=dq_model_id
        ).order_by('-started_at').first()

        if not execution:
            return Response(
                {"error": "No hay ejecuciones registradas para este modelo"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Obtener todos los métodos aplicados del modelo desde la base default
        measurement_methods = MeasurementDQMethod.objects.using('default').filter(
            associatedTo__metric__factor__dq_model_id=dq_model_id
        )
        aggregation_methods = AggregationDQMethod.objects.using('default').filter(
            associatedTo__metric__factor__dq_model_id=dq_model_id
        )
        all_methods = list(measurement_methods) + list(aggregation_methods)
        
        # Obtener TODOS los resultados de ejecución desde metadata_db
        executed_results = DQMethodExecutionResult.objects.using('metadata_db').filter(
            execution=execution
        ).select_related('content_type')
        
        # Mapear content_types para búsqueda eficiente
        measurement_type = ContentType.objects.db_manager('default').get_for_model(MeasurementDQMethod).id
        aggregation_type = ContentType.objects.db_manager('default').get_for_model(AggregationDQMethod).id

        # Crear diccionario de resultados ejecutados {(content_type_id, object_id): result}
        executed_map = {
            (r.content_type_id, r.object_id): r 
            for r in executed_results
            if r.content_type_id in [measurement_type, aggregation_type]
        }

        # Procesar todos los métodos
        formatted_results = []
        for method in all_methods:
            content_type_id = measurement_type if isinstance(method, MeasurementDQMethod) else aggregation_type
            key = (content_type_id, method.id)
            
            if key in executed_map:
                # Método ejecutado
                result = executed_map[key]
                formatted_results.append({
                    'method_id': method.id,
                    'method_name': method.name,
                    'method_type': method.__class__.__name__,
                    'executed_at': result.executed_at.isoformat(),
                    'dq_value': result.dq_value,
                    'execution_time': result.details.get('execution_time'),
                    'columns': result.details.get('columns'),
                    'sample_data': result.details.get('sample_data'),
                    'query': result.details.get('query'),
                    'status': 'completed'
                })
            else:
                # Método pendiente
                formatted_results.append({
                    'method_id': method.id,
                    'method_name': method.name,
                    'method_type': method.__class__.__name__,
                    'status': 'pending'
                })

        # Ordenar por status (completed primero) y luego por method_id
        formatted_results.sort(key=lambda x: (0 if x['status'] == 'completed' else 1, x['method_id']))
        
        import logging
        logger = logging.getLogger(__name__)

        # Dentro del método, antes del return:
        logger.info(f"Execution found: {execution.execution_id}")
        logger.info(f"Total methods: {len(all_methods)}")
        logger.info(f"Executed results: {len(executed_map)}")
        logger.info(f"Content Types - Measurement: {measurement_type}, Aggregation: {aggregation_type}")

        return Response({
            'execution_id': str(execution.execution_id),
            'execution_status': execution.status,
            'started_at': execution.started_at.isoformat(),
            'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
            'progress': {
                'completed': len([r for r in formatted_results if r['status'] == 'completed']),
                'pending': len([r for r in formatted_results if r['status'] == 'pending']),
                'total': len(formatted_results)
            },
            'results': formatted_results
        })
    
    
    @action(detail=False, methods=['get'], url_path='dqmodels/(?P<dq_model_id>\d+)/latest-results')
    def get_latest_results__(self, request, dq_model_id=None):
        """
        Obtiene los últimos resultados para un DQModel, incluyendo ejecuciones en progreso
        """
        # Obtener la ejecución más reciente (completada o en progreso)
        execution = DQModelExecution.objects.using('metadata_db').filter(
            dq_model_id=dq_model_id
        ).order_by('-started_at').first()

        if not execution:
            return Response(
                {"error": "No hay ejecuciones registradas para este modelo"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Obtener todos los métodos aplicados del modelo
        total_methods = list(
            MeasurementDQMethod.objects.using('default').filter(
                associatedTo__metric__factor__dq_model_id=dq_model_id
            ).values_list('id', flat=True)
        ) + list(
            AggregationDQMethod.objects.using('default').filter(
                associatedTo__metric__factor__dq_model_id=dq_model_id
            ).values_list('id', flat=True)
        )

        # Obtener resultados existentes
        results = execution.method_results.using('metadata_db').select_related('content_type').all()
        
        # Procesar resultados
        formatted_results = []
        for result in results:
            try:
                method = result.resolved_applied_method
                formatted_results.append({
                    'method_id': result.object_id,
                    'method_name': method.name,
                    'method_type': method.__class__.__name__,
                    'executed_at': result.executed_at.isoformat(),
                    'dq_value': result.dq_value,
                    'execution_time': result.details.get('execution_time'),
                    'columns': result.details.get('columns'),
                    'sample_data': result.details.get('sample_data'),
                    'status': 'completed'
                })
            except Exception as e:
                # Si hay error al resolver el método, lo omitimos
                continue

        # Identificar métodos pendientes
        executed_method_ids = [r.object_id for r in results]
        pending_methods = list(set(total_methods) - set(executed_method_ids))
        
        # Añadir métodos pendientes a la respuesta
        for method_id in pending_methods:
            try:
                # Buscar el método para obtener sus detalles
                method = (MeasurementDQMethod.objects.using('default').filter(id=method_id).first() or 
                        AggregationDQMethod.objects.using('default').filter(id=method_id).first())
                
                if method:
                    formatted_results.append({
                        'method_id': method_id,
                        'method_name': method.name,
                        'method_type': method.__class__.__name__,
                        'status': 'pending'
                    })
            except:
                continue

        return Response({
            'execution_id': str(execution.execution_id),
            'execution_status': execution.status,
            'started_at': execution.started_at.isoformat(),
            'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
            'progress': {
                'completed': len(executed_method_ids),
                'pending': len(pending_methods),
                'total': len(total_methods)
            },
            'results': formatted_results
        })
    
    @action(detail=False, methods=['get'], url_path='dqmodels/(?P<dq_model_id>\d+)/latest-results')
    def get_latest_results0(self, request, dq_model_id=None):
        """
        Obtiene los últimos resultados para un DQModel
        """
        # Obtener la última ejecución completada
        execution = DQModelExecution.objects.using('metadata_db').filter(
            dq_model_id=dq_model_id,
            status='completed'
        ).order_by('-completed_at').first()

        if not execution:
            return Response(
                {"error": "No hay ejecuciones completadas para este modelo"},
                status=status.HTTP_404_NOT_FOUND
            )

        results = execution.method_results.using('metadata_db').select_related('content_type').all()
        
        formatted_results = []
        for result in results:
            method = result.resolved_applied_method
            formatted_results.append({
                'method_id': result.object_id,
                'method_name': method.name,
                'method_type': method.__class__.__name__,
                'executed_at': result.executed_at.isoformat(),
                'dq_value': result.dq_value,
                'execution_time': result.details.get('execution_time'),
                'columns': result.details.get('columns'),
                'sample_data': result.details.get('sample_data')
            })

        return Response({
            'execution_id': str(execution.execution_id),
            'started_at': execution.started_at.isoformat(),
            'completed_at': execution.completed_at.isoformat(),
            'results': formatted_results
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

   
        
# views.py
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