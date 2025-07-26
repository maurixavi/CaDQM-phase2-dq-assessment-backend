from rest_framework import serializers
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
    DQModelExecution,
    DQMethodExecutionResult,
    ExecutionTableResult,
    ExecutionColumnResult,
    ExecutionRowResult
)


# ==============================================
# Base Model Serializers
# ==============================================

class DQDimensionBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = DQDimensionBase
        fields = '__all__'  
        
class DQFactorBaseSerializer(serializers.ModelSerializer):
    facetOf = serializers.PrimaryKeyRelatedField(queryset=DQDimensionBase.objects.all(), required=False)

    class Meta:
        model = DQFactorBase
        fields = '__all__'   
    
class DQMetricBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = DQMetricBase
        fields = '__all__'   

class DQMethodBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = DQMethodBase
        fields = '__all__'   
    


# ==============================================
# DQ Model Component Serializers
# ==============================================

class MeasurementDQMethodSerializer(serializers.ModelSerializer):
    """Serializer for Measurement Applied DQ Method in DQ Model"""
    class Meta:
        model = MeasurementDQMethod
        fields = ['id', 'name', 'appliedTo', 'algorithm', 'associatedTo']


class AggregationDQMethodSerializer(serializers.ModelSerializer):
    """Serializer for Aggregation Applied DQ Method in DQ Model"""
    class Meta:
        model = AggregationDQMethod
        fields = ['id', 'name', 'appliedTo', 'algorithm', 'associatedTo']
        
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.appliedTo = validated_data.get('appliedTo', instance.appliedTo)
        instance.algorithm = validated_data.get('algorithm', instance.algorithm)
        instance.save()
        return instance


class DQModelMethodSerializer(serializers.ModelSerializer):
    method_base = serializers.PrimaryKeyRelatedField(
        queryset=DQMethodBase.objects.all()
    )
    method_name = serializers.CharField(source='method_base.name', read_only=True)
    metric = serializers.PrimaryKeyRelatedField(
        queryset=DQModelMetric.objects.all()
    )
    
    applied_methods = serializers.SerializerMethodField()

    class Meta:
        model = DQModelMethod
        fields = ['id', 'method_base', 'method_name', 'metric', 'dq_model', 'applied_methods', 'context_components']
    
    def get_applied_methods(self, obj):
        measurements = MeasurementDQMethodSerializer(obj.measurementdqmethod_applied_methods.all(), many=True).data
        aggregations = AggregationDQMethodSerializer(obj.aggregationdqmethod_applied_methods.all(), many=True).data
        return {
            'measurements': measurements,
            'aggregations': aggregations
        }


class DQModelMetricSerializer(serializers.ModelSerializer):
    metric_base = serializers.PrimaryKeyRelatedField(
        queryset=DQMetricBase.objects.all()
    )
    metric_name = serializers.CharField(source='metric_base.name', read_only=True)
    factor = serializers.PrimaryKeyRelatedField(
        queryset=DQModelFactor.objects.all()
    )
    
    methods = DQModelMethodSerializer(many=True, required=False, allow_empty=True)

    class Meta:
        model = DQModelMetric
        fields = ['id', 'metric_base', 'metric_name', 'factor', 'dq_model', 'methods', 'context_components']
        
        
class DQModelFactorSerializer(serializers.ModelSerializer):
    """Serializer for DQModelFactor model"""
    factor_base = serializers.PrimaryKeyRelatedField(
        queryset=DQFactorBase.objects.all()
    )
    factor_name = serializers.CharField(source='factor_base.name', read_only=True)
    dimension = serializers.PrimaryKeyRelatedField(
        queryset=DQModelDimension.objects.all()
    )
    
    dq_model = serializers.PrimaryKeyRelatedField(queryset=DQModel.objects.all()) 

    class Meta:
        model = DQModelFactor
        fields = ['id', 'factor_base', 'factor_name', 'dimension', 'dq_model', 'context_components', 'dq_problems']


class DQModelDimensionSerializer(serializers.ModelSerializer):
    dq_model = serializers.PrimaryKeyRelatedField(queryset=DQModel.objects.all()) 
    dimension_base = serializers.PrimaryKeyRelatedField(
        queryset=DQDimensionBase.objects.all()
    )
    dimension_name = serializers.CharField(source='dimension_base.name', read_only=True)
    
    class Meta:
        model = DQModelDimension
        fields = ['id', 'dq_model', 'dimension_base', 'dimension_name', 'context_components', 'dq_problems'] 

    def create(self, validated_data):
        dq_model = validated_data['dq_model']
        dimension_base = validated_data['dimension_base']

        # Verifica si ya existe una dimensión con el mismo dq_model y dimension_base
        if DQModelDimension.objects.filter(dq_model=dq_model, dimension_base=dimension_base).exists():
            raise serializers.ValidationError("Esta dimensión ya existe para el DQ Model.")

        return super().create(validated_data)



class DQModelSerializer(serializers.ModelSerializer):
    # Serializadores de escritura (write-only)
    model_dimensions = DQModelDimensionSerializer(many=True, write_only=True, required=False)
    model_factors = DQModelFactorSerializer(many=True, write_only=True, required=False)
    model_metrics = DQModelMetricSerializer(many=True, write_only=True, required=False)
    model_methods = DQModelMethodSerializer(many=True, write_only=True, required=False)
    measurement_methods = MeasurementDQMethodSerializer(many=True, required=False, write_only=True)
    aggregation_methods = AggregationDQMethodSerializer(many=True, required=False, write_only=True)

    class Meta:
        model = DQModel
        fields = [
            'id',
            'name',
            'version',
            'created_at',
            'status',
            'finished_at',
            'model_dimensions',
            'model_factors',
            'model_metrics',
            'model_methods',
            'measurement_methods',
            'aggregation_methods',
            #'dimensions',
            'previous_version',
        ]

    def create(self, validated_data):
        # Extraer datos de asociaciones
        model_dimensions_data = validated_data.pop('model_dimensions', [])
        model_factors_data = validated_data.pop('model_factors', [])
        model_metrics_data = validated_data.pop('model_metrics', [])
        model_methods_data = validated_data.pop('model_methods', [])
        measurement_methods_data = validated_data.pop('measurement_methods', [])
        aggregation_methods_data = validated_data.pop('aggregation_methods', [])

        # Crear DQModel
        dq_model = DQModel.objects.create(**validated_data)

        # Asociar DQModelDimensions
        for dimension_data in model_dimensions_data:
            DQModelDimension.objects.create(
                dq_model=dq_model,
                dimension_base=dimension_data['dimension_base']
            )

        # Asociar DQModelFactors
        for factor_data in model_factors_data:
            DQModelFactor.objects.create(
                dq_model=dq_model,
                factor_base=factor_data['factor_base'],
                dimension_id=factor_data['dimension']
            )

        # Asociar DQModelMetrics
        for metric_data in model_metrics_data:
            DQModelMetric.objects.create(
                dq_model=dq_model,
                metric_base=metric_data['metric_base'],
                factor_id=metric_data['factor']
            )

        # Asociar DQModelMethods
        for method_data in model_methods_data:
            DQModelMethod.objects.create(
                dq_model=dq_model,
                method_base=method_data['method_base'],
                metric_id=method_data['metric']
            )

        # Asociar MeasurementDQMethods
        for measurement_data in measurement_methods_data:
            MeasurementDQMethod.objects.create(
                name=measurement_data['name'],
                appliedTo=measurement_data['appliedTo'],
                associatedTo=measurement_data['associatedTo']
            )

        # Asociar AggregationDQMethods
        for aggregation_data in aggregation_methods_data:
            AggregationDQMethod.objects.create(
                name=aggregation_data['name'],
                appliedTo=aggregation_data['appliedTo'],
                associatedTo=aggregation_data['associatedTo']
            )

        return dq_model
    
    def increment_version(self, current_version):
        """
        Incrementa el primer dígito de la versión 
        Ejemplo: "1.0.0" → "2.0.0"
        """
        if not current_version:
            return "1.0.0"  # Versión inicial si no hay versión
        
        try:
            parts = current_version.split('.')
            major = int(parts[0]) + 1  # Incrementa el primer número
            return f"{major}.0.0"      # Reinicia MINOR y PATCH
        except (ValueError, IndexError):
            return "1.0.0"  # Fallback si el formato es incorrecto
    
    def create_new_version(self, original_instance):
        """
        Crea una nueva versión basada en una instancia existente
        Copia todas las relaciones asociadas (dimensiones, factores, etc.)
        """
        current_version_number = original_instance.version
        new_version_number = self.increment_version(current_version_number) # Ejemplo version "1.0.0" -> "2.0.0"
        
        # Crear la nueva instancia de DQModel
        new_instance = DQModel.objects.create(
            name=original_instance.name, # Mantener el mismo nombre 
            version=new_version_number,
            status='draft',
            previous_version=original_instance
        )
        
        # Clonar las dimensiones
        dimension_map = {}
        for dimension in original_instance.model_dimensions.all():
            new_dimension = DQModelDimension.objects.create(
                dq_model=new_instance,
                dimension_base=dimension.dimension_base,
                context_components=dimension.context_components,  
                dq_problems=dimension.dq_problems   
            )
            dimension_map[dimension.id] = new_dimension
        
        # Clonar los factores
        factor_map = {}
        for factor in original_instance.model_factors.all():
            original_dimension = factor.dimension
            new_dimension = dimension_map.get(original_dimension.id)
            if not new_dimension:
                raise serializers.ValidationError(f"Dimension with ID {original_dimension.id} not found.")
            new_factor = DQModelFactor.objects.create(
                dq_model=new_instance,
                factor_base=factor.factor_base,
                dimension=new_dimension,
                context_components=factor.context_components,
                dq_problems=factor.dq_problems
            )
            factor_map[factor.id] = new_factor
        
        # Clonar las métricas
        metric_map = {}
        for metric in original_instance.model_metrics.all():
            original_factor = metric.factor
            new_factor = factor_map.get(original_factor.id)
            if not new_factor:
                raise serializers.ValidationError(f"Factor with ID {original_factor.id} not found.")
            new_metric = DQModelMetric.objects.create(
                dq_model=new_instance,
                metric_base=metric.metric_base,
                factor=new_factor,
                context_components=metric.context_components
            )
            metric_map[metric.id] = new_metric
        
        # Clonar los métodos
        method_map = {}
        for method in original_instance.model_methods.all():
            original_metric = method.metric
            new_metric = metric_map.get(original_metric.id)
            if not new_metric:
                raise serializers.ValidationError(f"Metric with ID {original_metric.id} not found.")
            new_method = DQModelMethod.objects.create(
                dq_model=new_instance,
                method_base=method.method_base,
                metric=new_metric,
                context_components=method.context_components
            )
            method_map[method.id] = new_method
        
        # Clonar MeasurementDQMethods y AggregationDQMethods
        for old_method in original_instance.model_methods.all():
            new_method = method_map.get(old_method.id)
            if not new_method:
                raise serializers.ValidationError(f"Method with ID {old_method.id} not found.")
            
            # Clonar MeasurementDQMethods
            for measurement in old_method.measurementdqmethod_applied_methods.all():
                MeasurementDQMethod.objects.create(
                    name=measurement.name,
                    appliedTo=measurement.appliedTo,
                    algorithm=measurement.algorithm,
                    associatedTo=new_method
                )
            
            # Clonar AggregationDQMethods
            for aggregation in old_method.aggregationdqmethod_applied_methods.all():
                AggregationDQMethod.objects.create(
                    name=aggregation.name,
                    appliedTo=aggregation.appliedTo,
                    algorithm=aggregation.algorithm,
                    associatedTo=new_method
                )
        
        return new_instance
    
    
    def update(self, instance, validated_data):
        # Si Finalizo -> Se crea version nueva
        if instance.status == 'finished':
            return self.create_new_version(instance)

        # Actualizar campos básicos
        instance.version = validated_data.get('version', instance.version)
        instance.status = validated_data.get('status', instance.status)
        instance.finished_at = validated_data.get('finished_at', instance.finished_at)
        instance.save()

        return instance


# ==============================================
# Execution Result Serializers (DQ METADATA DB)
# ==============================================

class DQModelExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DQModelExecution
        fields = '__all__'  


class TableResultSerializer(serializers.ModelSerializer):
    execution_id = serializers.UUIDField(source='execution_result.execution.execution_id')
    applied_method_id = serializers.IntegerField(source='execution_result.object_id')
    
    class Meta:
        model = ExecutionTableResult
        fields = [
            'id',
            'table_id',
            'table_name',
            'dq_value',
            'executed_at',
            'execution_id',
            'applied_method_id'
        ]

class ColumnResultSerializer(serializers.ModelSerializer):
    execution_id = serializers.UUIDField(source='execution_result.execution.execution_id')
    applied_method_id = serializers.IntegerField(source='execution_result.object_id')
    
    class Meta:
        model = ExecutionColumnResult
        fields = [
            'id',
            'table_id',
            'table_name',
            'column_id',
            'column_name',
            'dq_value',
            'executed_at',
            'execution_id',
            'applied_method_id'
        ]

class RowResultSerializer(serializers.ModelSerializer):
    execution_id = serializers.UUIDField(source='execution_result.execution.execution_id')
    applied_method_id = serializers.IntegerField(source='applied_method_id', read_only=True)
    
    class Meta:
        model = ExecutionRowResult
        fields = [
            'id',
            'table_id',
            'table_name',
            'column_id',
            'column_name',
            'row_id',
            'dq_value',
            'executed_at',
            'execution_id',
            'applied_method_id'
        ]
        

class DQMethodExecutionResultSerializer(serializers.ModelSerializer):
    results = serializers.SerializerMethodField()

    class Meta:
        model = DQMethodExecutionResult
        fields = '__all__'

    def get_results(self, obj):
        if obj.result_type == 'multiple':
            return {
                'type': 'multiple',
                'total_rows': len(obj.dq_value.get('rows', [])),
                'columns': obj.dq_value.get('columns', []),
                'sample_data': obj.dq_value.get('rows', [])[:5]  # Muestra parcial
            }
        else:
            return {
                'type': 'single',
                'value': obj.dq_value.get('value')
            }