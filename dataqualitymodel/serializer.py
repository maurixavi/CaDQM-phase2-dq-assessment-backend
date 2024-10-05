from rest_framework import serializers
from .models import DQModel, DQDimension, DQFactor, DQMetric, DQMethod, MeasurementDQMethod, AggregationDQMethod, AppliedDQMethod


#class MeasurementDQMethodSerializer(serializers.ModelSerializer):
#    class Meta:
 #       model = MeasurementDQMethod
  #      fields = '__all__'

#class AggregationDQMethodSerializer(serializers.ModelSerializer):
 #   class Meta:
  #      model = AggregationDQMethod
   #     fields = '__all__'
 
 
#class DQMethodSerializer(serializers.ModelSerializer):
 #   class Meta:
  #      model = DQMethod
   #     fields = '__all__'
class MeasurementDQMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeasurementDQMethod
        fields = '__all__'

class AggregationDQMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = AggregationDQMethod
        fields = '__all__'
 
   
class AppliedDQMethodSerializer(serializers.ModelSerializer):
    method_type = serializers.SerializerMethodField()
    
    class Meta:
        model = AppliedDQMethod
        fields = ['id', 'name', 'appliedTo', 'associatedTo', 'method_type']

    def get_method_type(self, obj):
        if isinstance(obj, MeasurementDQMethod):
            return 'Measurement'
        elif isinstance(obj, AggregationDQMethod):
            return 'Aggregation'
        return 'Unknown'

class DQMethodSerializer(serializers.ModelSerializer):
    #applied_methods = AppliedDQMethodSerializer(many=True)

    applied_methods = serializers.SerializerMethodField()

    class Meta:
        model = DQMethod
        fields = ['id', 'name', 'inputDataType', 'outputDataType', 'algorithm', 'implements', 'mtIn', 'applied_methods']

    def get_applied_methods(self, obj):
        # obtiene metodos aplicados de ambos tipos
        measurement_methods = MeasurementDQMethod.objects.filter(associatedTo=obj)
        aggregation_methods = AggregationDQMethod.objects.filter(associatedTo=obj)
        
        measurement_serializer = MeasurementDQMethodSerializer(measurement_methods, many=True)
        aggregation_serializer = AggregationDQMethodSerializer(aggregation_methods, many=True)

        # Combina resultados
        return {
            'measurements': measurement_serializer.data,
            'aggregations': aggregation_serializer.data
        }



class DQMetricSerializer(serializers.ModelSerializer):
    methods = DQMethodSerializer(many=True, required=False, allow_empty=True)

    class Meta:
        model = DQMetric
        fields = ['id', 'name', 'purpose', 'granularity', 'measures', 'mIn', 'methods']
 

class DQFactorSerializer(serializers.ModelSerializer):
    metrics = DQMetricSerializer(many=True, required=False, allow_empty=True)

    class Meta:
        model = DQFactor
        fields = ['id', 'name', 'semantic', 'facetOf', 'fIn', 'metrics'] 
        
class DQDimensionSerializer(serializers.ModelSerializer):
    factors = DQFactorSerializer(many=True, required=False, allow_empty=True)

    class Meta:
        model = DQDimension
        fields = ['id', 'name', 'semantic', 'dIn', 'factors']

class DQModelSerializer(serializers.ModelSerializer):
    dimensions = DQDimensionSerializer(many=True, required=False, allow_empty=True)

    class Meta:
        model = DQModel
        fields = ['id', 'version', 'created_at', 'status', 'finished_at', 'dimensions']