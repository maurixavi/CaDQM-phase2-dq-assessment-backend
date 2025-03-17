from rest_framework import serializers
from .models import DQModel, DQDimensionBase, DQFactorBase, DQMetricBase, DQMethodBase, DQModelDimension, DQModelFactor, DQModelMetric, DQModelMethod, MeasurementDQMethod, AggregationDQMethod, PrioritizedDqProblem


class PrioritizedDqProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrioritizedDqProblem
        fields = '__all__'  
    


class DQDimensionBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = DQDimensionBase
        fields = ['id', 'name', 'semantic']
    
    def update(self, instance, validated_data):
        try:
            # Crear un nuevo objeto usando validated_data (datos modificados)
            # Se pasa validated_data a `DQDimensionBase.objects.create` para crear un nuevo objeto
            new_instance = DQDimensionBase.objects.create(**validated_data)

            # Retorna la nueva instancia creada
            return new_instance

        except Exception as e:
            raise serializers.ValidationError(f"Error al crear el nuevo DQDimensionBase: {str(e)}")
        

class DQFactorBaseSerializer(serializers.ModelSerializer):
    facetOf = serializers.PrimaryKeyRelatedField(queryset=DQDimensionBase.objects.all(), required=False)

    class Meta:
        model = DQFactorBase
        fields = ['id', 'name', 'semantic', 'facetOf']    
    
    def update(self, instance, validated_data):
        try:
            # Crear un nuevo objeto usando validated_data (datos modificados)
            # Se pasa validated_data a `DQFactorBase.objects.create` para crear un nuevo objeto
            new_instance = DQFactorBase.objects.create(**validated_data)

            # Retorna la nueva instancia creada
            return new_instance

        except Exception as e:
            raise serializers.ValidationError(f"Error al crear el nuevo DQ Factor Base: {str(e)}")


class DQMetricBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = DQMetricBase
        fields = ['id', 'name', 'purpose', 'granularity', 'resultDomain', 'measures']
    
    def update(self, instance, validated_data):
        try:
            # Crear un nuevo objeto usando validated_data (datos modificados)
            # Se pasa validated_data a `DQMetricBase.objects.create` para crear un nuevo objeto
            new_instance = DQMetricBase.objects.create(**validated_data)

            # Retorna la nueva instancia creada
            return new_instance

        except Exception as e:
            raise serializers.ValidationError(f"Error al crear la nueva métrica: {str(e)}")



class DQMethodBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = DQMethodBase
        fields = ['id', 'name', 'inputDataType', 'outputDataType', 'algorithm', 'implements']
    
    def update(self, instance, validated_data):
        try:
            # Crear un nuevo objeto usando validated_data (datos modificados)
            # Se pasa validated_data a `DQMethodBase.objects.create` para crear un nuevo objeto
            new_instance = DQMethodBase.objects.create(**validated_data)

            # Retorna la nueva instancia creada
            return new_instance

        except Exception as e:
            raise serializers.ValidationError(f"Error al crear la nuevo Metodo: {str(e)}")


# DQ MODEL ------------------------------------------------------------------

# Serializador para MeasurementDQMethod
class MeasurementDQMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeasurementDQMethod
        fields = ['id', 'name', 'appliedTo', 'associatedTo']

# Serializador para AggregationDQMethod
class AggregationDQMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = AggregationDQMethod
        fields = ['id', 'name', 'appliedTo', 'associatedTo']

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
        fields = ['id', 'method_base', 'method_name', 'metric', 'dq_model', 'applied_methods']
    
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
    factor_base = serializers.PrimaryKeyRelatedField(
        queryset=DQFactorBase.objects.all()
    )
    factor_name = serializers.CharField(source='factor_base.name', read_only=True)
    dimension = serializers.PrimaryKeyRelatedField(
        queryset=DQModelDimension.objects.all()
    )
    
    # metrics = DQModelMetricSerializer(many=True, required=False, allow_empty=True)
    dq_model = serializers.PrimaryKeyRelatedField(queryset=DQModel.objects.all())  # Agregar este campo


    class Meta:
        model = DQModelFactor
        fields = ['id', 'factor_base', 'factor_name', 'dimension', 'dq_model', 'context_components', 'dq_problems']


class DQModelDimensionSerializer(serializers.ModelSerializer):
    #dq_model = serializers.PrimaryKeyRelatedField(read_only=True)  # Esto incluirá el dq_model id en la salida
    dq_model = serializers.PrimaryKeyRelatedField(queryset=DQModel.objects.all())  # Permitir que se establezca el dq_model

    dimension_base = serializers.PrimaryKeyRelatedField(
        queryset=DQDimensionBase.objects.all()
    )
    dimension_name = serializers.CharField(source='dimension_base.name', read_only=True)

    # factors = DQModelFactorSerializer(many=True, required=False, allow_empty=True)
    
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
    #class Meta:
    #    model = DQModelDimension
    #    fields = ['id', 'dimension_base', 'dimension_name', 'context_components']




# Serializador para DQModel
class DQModelSerializer(serializers.ModelSerializer):
    # Serializadores de escritura (write-only)
    model_dimensions = DQModelDimensionSerializer(many=True, write_only=True, required=False)
    model_factors = DQModelFactorSerializer(many=True, write_only=True, required=False)
    model_metrics = DQModelMetricSerializer(many=True, write_only=True, required=False)
    model_methods = DQModelMethodSerializer(many=True, write_only=True, required=False)
    measurement_methods = MeasurementDQMethodSerializer(many=True, required=False, write_only=True)
    aggregation_methods = AggregationDQMethodSerializer(many=True, required=False, write_only=True)

    # Serializadores de lectura (read-only)
    #dimensions = DQModelDimensionSerializer(source='model_dimensions', many=True, read_only=True)
    # campos de lectura que no se incluiran en 'fields'
    # factors = DQModelFactorSerializer(source='model_factors', many=True, read_only=True)
    # metrics = DQModelMetricSerializer(source='model_metrics', many=True, read_only=True)
    # methods = DQModelMethodSerializer(source='model_methods', many=True, read_only=True)
    # measurement_methods_read = MeasurementDQMethodSerializer(many=True, read_only=True)
    # aggregation_methods_read = AggregationDQMethodSerializer(many=True, read_only=True)

    class Meta:
        model = DQModel
        fields = [
            'id',
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

    """
    def get_new_version(self, current_version):
        
        Implementa una lógica para determinar la nueva versión.
        Por ejemplo, si la versión actual es 'v1.0', la nueva será 'v1.1'.
        
        try:
            prefix, number = current_version.split('v')
            new_number = float(number) + 0.1
            return f"{current_version} v{new_number:.1f}"
        except ValueError:
            # Si no sigue el formato esperado, asignar una versión por defecto
            new_version = current_version + " New Version"
            return new_version
    
    def create_new_version(self, instance, validated_data):
        
        Crea una nueva versión basada en una instancia existente.
        
        validated_data['previous_version'] = instance
        validated_data['status'] = 'draft'  # Iniciar la nueva versión como 'draft'
        validated_data['version'] = self.get_new_version(instance.version)

        # Crear una nueva instancia en lugar de modificar la existente
        serializer = DQModelSerializer(data=validated_data)
        serializer.is_valid(raise_exception=True)
        return serializer.save()
    
    """
    
    
    def create_new_version(self, original_instance):
        """
        Crea una nueva versión basada en una instancia existente
        Copia todas las relaciones asociadas (dimensiones, factores, etc.)
        """
        # Generar la nueva versión
        new_version_str = self.get_new_version(original_instance.version)
        
        # Crear la nueva instancia de DQModel
        new_instance = DQModel.objects.create(
            version=new_version_str,
            status='draft',
            previous_version=original_instance
        )
        
        # Clonar las dimensiones
        dimension_map = {}
        for dimension in original_instance.model_dimensions.all():
            new_dimension = DQModelDimension.objects.create(
                dq_model=new_instance,
                dimension_base=dimension.dimension_base
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
                dimension=new_dimension
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
                factor=new_factor
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
                metric=new_metric
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
                    associatedTo=new_method
                )
            
            # Clonar AggregationDQMethods
            for aggregation in old_method.aggregationdqmethod_applied_methods.all():
                AggregationDQMethod.objects.create(
                    name=aggregation.name,
                    appliedTo=aggregation.appliedTo,
                    associatedTo=new_method
                )
        
        return new_instance
    
    def get_new_version(self, current_version):
        
        """
        determinar la nueva version
        Ej.: si la versión actual es 'v1.0', la nueva será 'v1.1'.
        """
        try:
            prefix, number = current_version.split('v')
            new_number = float(number) + 0.1
            return f"{prefix} v{new_number:.1f}"
        except ValueError:
            # Si no sigue el formato esperado, asignar una versión por defecto
            new_version = current_version + " New Version"
            return new_version
        
        
    def update(self, instance, validated_data):
        # Verificar si el DQModel está finalizado
        if instance.status == 'finished':
            #raise serializers.ValidationError("No se pueden modificar DQModels finalizados. Crea una nueva versión.")
            return self.create_new_version(instance)
            #return self.create_new_version(instance, validated_data)

        # Actualizar campos básicos
        instance.version = validated_data.get('version', instance.version)
        instance.status = validated_data.get('status', instance.status)
        instance.finished_at = validated_data.get('finished_at', instance.finished_at)
        instance.save()

        # Manejar actualizaciones de asociaciones si es necesario
        # Esto puede ser complejo y requerir manejo adicional de relaciones

        return instance
