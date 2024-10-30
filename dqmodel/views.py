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
        
        # Serializar y devolver la nueva versión
        serializer = self.get_serializer(new_instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    # Acción para obtener dimensiones relacionadas con un DQModel específico
    @action(detail=True, methods=['get'], url_path='dimensions')
    def get_dimensions(self, request, pk=None):
        dq_model = get_object_or_404(DQModel, pk=pk)
        dimensions = DQModelDimension.objects.filter(dq_model=dq_model).prefetch_related('dimension_base')
        
        if dimensions.exists():
            serializer = DQModelDimensionSerializer(dimensions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response({"detail": "No dimensions found for this DQModel"}, status=status.HTTP_404_NOT_FOUND)


"""
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
        'next_versions',  # Asegúrate de que 'next_versions' está correctamente definido
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
            # Definir una función para obtener la nueva versión
            def get_new_version(current_version):
                try:
                    prefix, number = current_version.split('v')
                    new_number = float(number) + 0.1
                    return f"v{new_number:.1f}"
                except ValueError:
                    # Si no sigue el formato esperado, asignar una versión por defecto
                    return "v1.0"

            # Crear una nueva instancia de DQModel
            new_version = DQModel.objects.create(
                version=get_new_version(original.version),
                status='draft',
                previous_version=original,
                # 'finished_at' permanece como None ya que el estado es 'draft'
            )

            # Clonar las relaciones relacionadas
            # Mapeos para relacionar objetos antiguos con los nuevos
            dimension_map = {}
            factor_map = {}
            metric_map = {}
            method_map = {}

            # Clonar model_dimensions
            for dimension in original.model_dimensions.all():
                new_dimension = DQModelDimension.objects.create(
                    dq_model=new_version,
                    dimension_base=dimension.dimension_base
                )
                dimension_map[dimension.id] = new_dimension

            # Clonar model_factors
            for factor in original.model_factors.all():
                original_dimension = factor.dimension
                new_dimension = dimension_map.get(original_dimension.id)
                if not new_dimension:
                    return Response(
                        {"error": f"No se encontró la dimensión original con ID {original_dimension.id} para el factor."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                new_factor = DQModelFactor.objects.create(
                    dq_model=new_version,
                    factor_base=factor.factor_base,
                    dimension=new_dimension
                )
                factor_map[factor.id] = new_factor

            # Clonar model_metrics
            for metric in original.model_metrics.all():
                original_factor = metric.factor
                new_factor = factor_map.get(original_factor.id)
                if not new_factor:
                    return Response(
                        {"error": f"No se encontró el factor original con ID {original_factor.id} para la métrica."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                new_metric = DQModelMetric.objects.create(
                    dq_model=new_version,
                    metric_base=metric.metric_base,
                    factor=new_factor
                )
                metric_map[metric.id] = new_metric

            # Clonar model_methods
            for method in original.model_methods.all():
                original_metric = method.metric
                new_metric = metric_map.get(original_metric.id)
                if not new_metric:
                    return Response(
                        {"error": f"No se encontró la métrica original con ID {original_metric.id} para el método."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                new_method = DQModelMethod.objects.create(
                    dq_model=new_version,
                    method_base=method.method_base,
                    metric=new_metric
                )
                method_map[method.id] = new_method

            # Clonar MeasurementDQMethods y AggregationDQMethods
            for old_method in original.model_methods.all():
                new_method = method_map.get(old_method.id)
                if not new_method:
                    return Response(
                        {"error": f"No se encontró el método original con ID {old_method.id} para clonar."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                # Clonar MeasurementDQMethods
                for measurement in old_method.measurementdqmethod_applied_methods.all():
                    MeasurementDQMethod.objects.create(
                        name=measurement.name,
                        appliedTo=measurement.appliedTo,
                        associatedTo=new_method
                    )
                # Clonar AggregationDQMethods
                for aggregation in old_method.aggregationdqmethod_applied_methods.all():
                    AggregationDQMethod.objects.create(
                        name=aggregation.name,
                        appliedTo=aggregation.appliedTo,
                        associatedTo=new_method
                    )

            # Serializar y devolver la nueva versión
            serializer = DQModelSerializer(new_version)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


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

        # Definir una función para obtener la nueva versión
        def get_new_version(current_version):
            try:
                prefix, number = current_version.split('v')
                new_number = float(number) + 0.1
                return f"v{new_number:.1f}"
            except ValueError:
                # Si no sigue el formato esperado, asignar una versión por defecto
                return "Modelo v1.0"

        # Crear una nueva instancia de DQModel
        new_version = DQModel.objects.create(
            version=get_new_version(original.version),
            status='draft',
            previous_version=original,
            # 'finished_at' permanece como None ya que el estado es 'draft'
        )

        # Clonar las relaciones relacionadas
        dimension_map = {}
        for dimension in original.model_dimensions.all():
            new_dimension = DQModelDimension.objects.create(
                dq_model=new_version,
                dimension_base=dimension.dimension_base
            )
            dimension_map[dimension.id] = new_dimension

        factor_map = {}
        for factor in original.model_factors.all():
            new_factor = DQModelFactor.objects.create(
                dq_model=new_version,
                factor_base=factor.factor_base,
                dimension=dimension_map[factor.dimension.id]
            )
            factor_map[factor.id] = new_factor

        metric_map = {}
        for metric in original.model_metrics.all():
            new_metric = DQModelMetric.objects.create(
                dq_model=new_version,
                metric_base=metric.metric_base,
                factor=factor_map[metric.factor.id]
            )
            metric_map[metric.id] = new_metric

        method_map = {}
        for method in original.model_methods.all():
            new_method = DQModelMethod.objects.create(
                dq_model=new_version,
                method_base=method.method_base,
                metric=metric_map[method.metric.id]
            )
            method_map[method.id] = new_method

        # Clonar MeasurementDQMethods y AggregationDQMethods
        for old_method in original.model_methods.all():
            new_method = method_map[old_method.id]
            # Clonar MeasurementDQMethods
            for measurement in old_method.measurementdqmethod_applied_methods.all():
                MeasurementDQMethod.objects.create(
                    name=measurement.name,
                    appliedTo=measurement.appliedTo,
                    associatedTo=new_method
                )
            # Clonar AggregationDQMethods
            for aggregation in old_method.aggregationdqmethod_applied_methods.all():
                AggregationDQMethod.objects.create(
                    name=aggregation.name,
                    appliedTo=aggregation.appliedTo,
                    associatedTo=new_method
                )

        # Serializar y devolver la nueva versión
        serializer = DQModelSerializer(new_version)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class DQModelViewSet(viewsets.ModelViewSet):
    queryset = DQModel.objects.all()
    serializer_class = DQModelSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dq_model = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(self.get_serializer(dq_model).data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        dq_model = serializer.save()
        return Response(self.get_serializer(dq_model).data)
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
class DQModelFactorViewSet(viewsets.ModelViewSet):
    queryset = DQModelFactor.objects.all()
    serializer_class = DQModelFactorSerializer

# ViewSet para DQModelMetric
class DQModelMetricViewSet(viewsets.ModelViewSet):
    queryset = DQModelMetric.objects.all()
    serializer_class = DQModelMetricSerializer

# ViewSet para DQModelMethod
class DQModelMethodViewSet(viewsets.ModelViewSet):
    queryset = DQModelMethod.objects.all()
    serializer_class = DQModelMethodSerializer
