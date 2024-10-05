from rest_framework import viewsets
from .models import ContextModel, ApplicationDomain, BusinessRule, UserType, TaskAtHand, DQRequirement, DataFiltering, SystemRequirement, DQMetadata, OtherMetadata, OtherData
from .serializer import ContextModelSerializer, ApplicationDomainSerializer, BusinessRuleSerializer, UserTypeSerializer, TaskAtHandSerializer, DQRequirementSerializer, DataFilteringSerializer, SystemRequirementSerializer, DQMetadataSerializer, OtherMetadataSerializer, OtherDataSerializer

class ContextModelViewSet(viewsets.ModelViewSet):
    queryset = ContextModel.objects.all()
    serializer_class = ContextModelSerializer

class ApplicationDomainViewSet(viewsets.ModelViewSet):
    queryset = ApplicationDomain.objects.all()
    serializer_class = ApplicationDomainSerializer

class BusinessRuleViewSet(viewsets.ModelViewSet):
    queryset = BusinessRule.objects.all()
    serializer_class = BusinessRuleSerializer

class UserTypeViewSet(viewsets.ModelViewSet):
    queryset = UserType.objects.all()
    serializer_class = UserTypeSerializer

class TaskAtHandViewSet(viewsets.ModelViewSet):
    queryset = TaskAtHand.objects.all()
    serializer_class = TaskAtHandSerializer

class DQRequirementViewSet(viewsets.ModelViewSet):
    queryset = DQRequirement.objects.all()
    serializer_class = DQRequirementSerializer

class DataFilteringViewSet(viewsets.ModelViewSet):
    queryset = DataFiltering.objects.all()
    serializer_class = DataFilteringSerializer

class SystemRequirementViewSet(viewsets.ModelViewSet):
    queryset = SystemRequirement.objects.all()
    serializer_class = SystemRequirementSerializer

class DQMetadataViewSet(viewsets.ModelViewSet):
    queryset = DQMetadata.objects.all()
    serializer_class = DQMetadataSerializer

class OtherMetadataViewSet(viewsets.ModelViewSet):
    queryset = OtherMetadata.objects.all()
    serializer_class = OtherMetadataSerializer

class OtherDataViewSet(viewsets.ModelViewSet):
    queryset = OtherData.objects.all()
    serializer_class = OtherDataSerializer
