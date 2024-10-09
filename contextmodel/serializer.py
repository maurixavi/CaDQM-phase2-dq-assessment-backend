from rest_framework import serializers
from .models import ContextModel, ApplicationDomain, BusinessRule, UserType, TaskAtHand, DQRequirement, DataFiltering, SystemRequirement, DQMetadata, OtherMetadata, OtherData

#class ContextModelSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = ContextModel
#        fields = '__all__'

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
        
class ContextModelSerializer(serializers.ModelSerializer):
    application_domains = ApplicationDomainSerializer(many=True, read_only=True)
    business_rules = BusinessRuleSerializer(many=True, read_only=True)
    user_types = UserTypeSerializer(many=True, read_only=True)
    tasks_at_hand = TaskAtHandSerializer(many=True, read_only=True)
    dq_requirements = DQRequirementSerializer(many=True, read_only=True)
    data_filtering = DataFilteringSerializer(many=True, read_only=True)
    system_requirements = SystemRequirementSerializer(many=True, read_only=True)
    dq_metadata = DQMetadataSerializer(many=True, read_only=True)
    other_metadata = OtherMetadataSerializer(many=True, read_only=True)
    other_data = OtherDataSerializer(many=True, read_only=True)

    class Meta:
        model = ContextModel
        fields = '__all__'