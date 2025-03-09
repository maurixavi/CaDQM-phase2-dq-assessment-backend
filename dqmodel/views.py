from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action, api_view
from .models import (
    DQModel,
    DQDimensionBase,
    DQFactorBase,
    DQMetricBase,
    DQMethodBase,
    DQModelDimension,
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
    
    # DQ Metrics de un DQ Factor especifico en un DQModel
    @action(detail=True, methods=['get'], url_path='dimensions/(?P<dimension_id>[^/.]+)/factors/(?P<factor_id>[^/.]+)/metrics')
    def get_metrics_by_factor(self, request, pk=None, dimension_id=None, factor_id=None):
        dq_model = get_object_or_404(DQModel, pk=pk)
        dimension = get_object_or_404(DQModelDimension, pk=dimension_id, dq_model=dq_model)
        factor = get_object_or_404(DQModelFactor, pk=factor_id, dimension=dimension)
        metrics = DQModelMetric.objects.filter(factor=factor)
        
        serializer = DQModelMetricSerializer(metrics, many=True)
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
    
    """ 
    falta agregar dqmodel al metodo aplicado en definicion de model
    
    # Measurement Applied Methods un DQ Method especifico en un DQModel
    @action(detail=True, methods=['get'], url_path='dimensions/(?P<dimension_id>[^/.]+)/factors/(?P<factor_id>[^/.]+)/metrics/(?P<metric_id>[^/.]+)/methods/(?P<method_id>[^/.]+)/measurement-methods')
    def get_measurement_methods(self, request, pk=None, dimension_id=None, factor_id=None, metric_id=None, method_id=None):
        dq_model = get_object_or_404(DQModel, pk=pk)
        dimension = get_object_or_404(DQModelDimension, pk=dimension_id, dq_model=dq_model)
        factor = get_object_or_404(DQModelFactor, pk=factor_id, dimension=dimension)
        metric = get_object_or_404(DQModelMetric, pk=metric_id, factor=factor)
        method = get_object_or_404(DQModelMethod, pk=method_id, metric=metric)
        measurement_methods = MeasurementDQMethod.objects.filter(applied_methods=method)
        
        serializer = MeasurementDQMethodSerializer(measurement_methods, many=True)
        return Response(serializer.data)

    # Aggregation Applied Methods un DQ Method especifico en un DQModel
    @action(detail=True, methods=['get'], url_path='dimensions/(?P<dimension_id>[^/.]+)/factors/(?P<factor_id>[^/.]+)/metrics/(?P<metric_id>[^/.]+)/methods/(?P<method_id>[^/.]+)/aggregation-methods')
    def get_aggregation_methods(self, request, pk=None, dimension_id=None, factor_id=None, metric_id=None, method_id=None):
        dq_model = get_object_or_404(DQModel, pk=pk)
        dimension = get_object_or_404(DQModelDimension, pk=dimension_id, dq_model=dq_model)
        factor = get_object_or_404(DQModelFactor, pk=factor_id, dimension=dimension)
        metric = get_object_or_404(DQModelMetric, pk=metric_id, factor=factor)
        method = get_object_or_404(DQModelMethod, pk=method_id, metric=metric)
        aggregation_methods = AggregationDQMethod.objects.filter(applied_methods=method)
        
        serializer = AggregationDQMethodSerializer(aggregation_methods, many=True)
        return Response(serializer.data)
    """


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