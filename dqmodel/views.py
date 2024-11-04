from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from django.db import transaction

from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework import viewsets, status
from rest_framework.response import Response
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
    AggregationDQMethod
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
    DQModelMethodSerializer
)

# ViewSet para DQDimensionBase
#class DQDimensionBaseViewSet(viewsets.ReadOnlyModelViewSet):
class DQDimensionBaseViewSet(viewsets.ModelViewSet):
    queryset = DQDimensionBase.objects.all()
    serializer_class = DQDimensionBaseSerializer

# ViewSet para DQFactorBase
#class DQFactorBaseViewSet(viewsets.ReadOnlyModelViewSet):
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
class DQMetricBaseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DQMetricBase.objects.all()
    serializer_class = DQMetricBaseSerializer
    
    
    
# ViewSet para DQMethodBase
class DQMethodBaseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DQMethodBase.objects.all()
    serializer_class = DQMethodBaseSerializer

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

    # DQ Factors de una DQ Dimension especifica en un DQModel
    @action(detail=True, methods=['get'], url_path='dimensions/(?P<dimension_id>[^/.]+)/factors')
    def get_factors_by_dimension(self, request, pk=None, dimension_id=None):
        dq_model = get_object_or_404(DQModel, pk=pk)
        dimension = get_object_or_404(DQModelDimension, pk=dimension_id, dq_model=dq_model)
        factors = DQModelFactor.objects.filter(dimension=dimension)
        
        serializer = DQModelFactorSerializer(factors, many=True)
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

# ViewSet para DQModelFactor
#class DQModelFactorViewSet(viewsets.ModelViewSet):
#    queryset = DQModelFactor.objects.all()
#    serializer_class = DQModelFactorSerializer
class DQModelFactorViewSet(viewsets.ModelViewSet):
    queryset = DQModelFactor.objects.all()
    serializer_class = DQModelFactorSerializer

    #def perform_create(self, serializer):
    #    dq_model = self.request.data.get('dq_model')  # Asegúrate de que el cliente envíe este ID
    #    serializer.save(dq_model=dq_model)  # Establece el dq_model aquí
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# ViewSet para DQModelMetric
class DQModelMetricViewSet(viewsets.ModelViewSet):
    queryset = DQModelMetric.objects.all()
    serializer_class = DQModelMetricSerializer

# ViewSet para DQModelMethod
class DQModelMethodViewSet(viewsets.ModelViewSet):
    queryset = DQModelMethod.objects.all()
    serializer_class = DQModelMethodSerializer
