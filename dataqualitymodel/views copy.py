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
    
    
class DQFactorViewSet(viewsets.ModelViewSet):
    queryset = DQFactor.objects.all()
    serializer_class = DQFactorSerializer

class DQMetricViewSet(viewsets.ModelViewSet):
    queryset = DQMetric.objects.all()
    serializer_class = DQMetricSerializer

class DQMethodViewSet(viewsets.ModelViewSet):
    queryset = DQMethod.objects.all()
    serializer_class = DQMethodSerializer

class MeasurementDQMethodViewSet(viewsets.ModelViewSet):
    queryset = MeasurementDQMethod.objects.all()
    serializer_class = MeasurementDQMethodSerializer

class AggregationDQMethodViewSet(viewsets.ModelViewSet):
    queryset = AggregationDQMethod.objects.all()
    serializer_class = AggregationDQMethodSerializer