from rest_framework import serializers
from .models import ContextModel, ApplicationDomain, BusinessRule, UserType, TaskAtHand, DQRequirement, DataFiltering, SystemRequirement, DQMetadata, OtherMetadata, OtherData

class ContextModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContextModel
        fields = '__all__'

class ApplicationDomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationDomain
        fields = '__all__'

class BusinessRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessRule
        fields = '__all__'

class UserTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserType
        fields = '__all__'

class TaskAtHandSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAtHand
        fields = '__all__'

class DQRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = DQRequirement
        fields = '__all__'

class DataFilteringSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataFiltering
        fields = '__all__'
        
class SystemRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemRequirement
        fields = '__all__'
        
class DQMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DQMetadata
        fields = '__all__'
        
class OtherMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherMetadata
        fields = '__all__'
        
class OtherDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherData
        fields = '__all__'