from rest_framework import viewsets
from .models import DQModel, DQDimension, DQFactor, DQMetric, DQMethod, AppliedDQMethod, MeasurementDQMethod, AggregationDQMethod
from .serializer import DQModelSerializer, DQDimensionSerializer, DQFactorSerializer, DQMetricSerializer, DQMethodSerializer, MeasurementDQMethodSerializer, AggregationDQMethodSerializer

class DQModelViewSet(viewsets.ModelViewSet):
    queryset = DQModel.objects.all()
    serializer_class = DQModelSerializer

#class DQDimensionViewSet(viewsets.ModelViewSet):
#    queryset = DQDimension.objects.all()
#    serializer_class = DQDimensionSerializer
class DQDimensionViewSet(viewsets.ModelViewSet):
    serializer_class = DQDimensionSerializer

    def get_queryset(self):
        dqmodel_id = self.kwargs.get('dqmodel_id')
        if dqmodel_id:
            return DQDimension.objects.filter(dIn_id=dqmodel_id)
        return DQDimension.objects.all()
    
    
#class DQFactorViewSet(viewsets.ModelViewSet):
#    queryset = DQFactor.objects.all()
#    serializer_class = DQFactorSerializer  
class DQFactorViewSet(viewsets.ModelViewSet):
    serializer_class = DQFactorSerializer

    def get_queryset(self):
        dimension_id = self.kwargs.get('dimension_id')
        if dimension_id:
            return DQFactor.objects.filter(facetOf_id=dimension_id)
        return DQFactor.objects.all()

#class DQMetricViewSet(viewsets.ModelViewSet):
#    queryset = DQMetric.objects.all()
#    serializer_class = DQMetricSerializer
class DQMetricViewSet(viewsets.ModelViewSet):
    serializer_class = DQMetricSerializer

    def get_queryset(self):
        factor_id = self.kwargs.get('factor_id')
        if factor_id:
            return DQMetric.objects.filter(measures_id=factor_id)
        return DQMetric.objects.all()

#class DQMethodViewSet(viewsets.ModelViewSet):
#    queryset = DQMethod.objects.all()
#    serializer_class = DQMethodSerializer
class DQMethodViewSet(viewsets.ModelViewSet):
    serializer_class = DQMethodSerializer

    def get_queryset(self):
        dqmodel_id = self.kwargs.get('dqmodel_id')
        if dqmodel_id:
            return DQMethod.objects.filter(mtIn_id=dqmodel_id)
        return DQMethod.objects.all()

#class MeasurementDQMethodViewSet(viewsets.ModelViewSet):
#    queryset = MeasurementDQMethod.objects.all()
#    serializer_class = MeasurementDQMethodSerializer
class MeasurementDQMethodViewSet(viewsets.ModelViewSet):
    serializer_class = MeasurementDQMethodSerializer

    def get_queryset(self):
        method_id = self.kwargs.get('method_id')
        if method_id:
            return MeasurementDQMethod.objects.filter(associatedTo_id=method_id)
        return MeasurementDQMethod.objects.all()

#class AggregationDQMethodViewSet(viewsets.ModelViewSet):
#    queryset = AggregationDQMethod.objects.all()
#    serializer_class = AggregationDQMethodSerializer
class AggregationDQMethodViewSet(viewsets.ModelViewSet):
    serializer_class = AggregationDQMethodSerializer

    def get_queryset(self):
        method_id = self.kwargs.get('method_id')
        if method_id:
            return AggregationDQMethod.objects.filter(associatedTo_id=method_id)
        return AggregationDQMethod.objects.all()