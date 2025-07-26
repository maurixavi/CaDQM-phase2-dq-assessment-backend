from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from dqmodel.models import DQMethodExecutionResult
from .models import (
    DataAtHand, DataSchema, Project, ProjectStage,
    Context, ContextComponent, ApplicationDomain, BusinessRule,
    DataFiltering, DQMetadata, DQRequirement, OtherData,
    OtherMetadata, SystemRequirement, TaskAtHand, UserType,
    UserData, QualityProblem, QualityProblemProject
)


# ==============================================
# Quality Problems Serializers
# ==============================================

class QualityProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = QualityProblem
        fields = ['id', 'description', 'date']

class QualityProblemProjectSerializer(serializers.ModelSerializer):
    dq_problem_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = QualityProblemProject
        fields = ['id', 'dq_problem_id', 'priority', 'is_selected', 'project']

    def create(self, validated_data):
        dq_problem_id = validated_data.pop('dq_problem_id')
        quality_problem = get_object_or_404(QualityProblem, id=dq_problem_id)
        return QualityProblemProject.objects.create(quality_problem=quality_problem, **validated_data)

    def to_representation(self, instance):
        """Include dq_problem_id in the response"""
        rep = super().to_representation(instance)
        rep['dq_problem_id'] = instance.quality_problem.id
        return rep


# ==============================================
# Context Components Serializers
# ==============================================

class ContextComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContextComponent
        fields = '__all__'

class ContextSerializer(serializers.ModelSerializer):
    context_components = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ContextComponent.objects.all()
    )

    class Meta:
        model = Context
        fields = ['id', 'name', 'version', 'previous_version', 'context_components']


# Serializers for specific context components

class ApplicationDomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationDomain
        fields = '__all__'

class BusinessRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessRule
        fields = '__all__'

class DataFilteringSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataFiltering
        fields = '__all__'

class DQMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DQMetadata
        fields = '__all__'

class DQRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = DQRequirement
        fields = '__all__'

class OtherDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherData
        fields = '__all__'

class OtherMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherMetadata
        fields = '__all__'

class SystemRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemRequirement
        fields = '__all__'

class TaskAtHandSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAtHand
        fields = '__all__'

class UserTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserType
        fields = '__all__'

class UserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserData
        fields = '__all__'


# ==============================================
# Project Serializers
# ==============================================

class ProjectStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectStage
        fields = ['stage', 'status']

class ProjectSerializer(serializers.ModelSerializer):
    stages = ProjectStageSerializer(many=True, read_only=True)
    current_stage = serializers.SerializerMethodField()
    context_obj = ContextSerializer(source='context', read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'dqmodel_version',
            'data_at_hand', 'created_at', 'stages',
            'current_stage', 'context_obj', 'context',
            'estimation', 'user'
        ]
        read_only_fields = ['created_at']

    def get_current_stage(self, obj):
        current = obj.current_stage
        if current:
            return {
                'stage': current.stage,
                'status': current.status
            }
        return None

    def update(self, instance, validated_data):
        try:
            instance.name = validated_data.get('name', instance.name)
            instance.description = validated_data.get('description', instance.description)
            
            # Manejar dqmodel_version
            new_dqmodel = validated_data.get('dqmodel_version')
            if new_dqmodel is not None:
                if instance.dqmodel_version is None:
                    instance.dqmodel_version = new_dqmodel
                elif new_dqmodel != instance.dqmodel_version:
                    raise serializers.ValidationError({
                        "dqmodel_version": "No se puede cambiar 'dqmodel_version' una vez asignado."
                    })
            
            instance.save()
            return instance

        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        except Exception as e:
            raise serializers.ValidationError(f"Error al actualizar el proyecto: {str(e)}")


# ==============================================
# Data at Hand & Data Schema Serializers
# ==============================================

class DataAtHandSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataAtHand
        fields = '__all__'  
        
        
class DataSchemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSchema
        fields = '__all__'
     

# ==============================================
# DQ Method Execution Serializer
# ==============================================

class DQMethodExecutionResultSerializer(serializers.ModelSerializer):
    execution_time = serializers.SerializerMethodField()
    
    class Meta:
        model = DQMethodExecutionResult
        fields = '__all__'
    
    def get_execution_time(self, obj):
        return obj.details.get('execution_time')