from rest_framework import serializers

from dqmodel.models import DQMethodExecutionResult
from .models import DataAtHand, DataSchema, Project, ProjectStage
#from .models import DataAtHand, DataSchema, PrioritizedDQProblem, Project, ProjectStage
from django.core.exceptions import ValidationError


from rest_framework import serializers
from .models import Context, ContextComponent, ApplicationDomain, BusinessRule, DataFiltering, DQMetadata, DQRequirement, OtherData, OtherMetadata, SystemRequirement, TaskAtHand, UserType, UserData, QualityProblem, QualityProblemProject

from django.shortcuts import get_object_or_404


### DQ PROBLEMS
class QualityProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = QualityProblem
        fields = ['id', 'description', 'date']


#class QualityProblemProjectSerializer(serializers.ModelSerializer):
 #   dq_problem_id = serializers.IntegerField(source='quality_problem.id')

  #  class Meta:
   #     model = QualityProblemProject
    #    fields = ['id', 'dq_problem_id', 'priority', 'is_selected', 'project']

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
        # Así devolvés dq_problem_id en la respuesta
        rep = super().to_representation(instance)
        rep['dq_problem_id'] = instance.quality_problem.id
        return rep


## --------------

##### CONTEXT COMPONENTS

class ContextComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContextComponent
        fields = '__all__'

#class ContextSerializer(serializers.ModelSerializer):
 #   context_components = ContextComponentSerializer(many=True, read_only=True)
#
  #  class Meta:
   #     model = Context
    #    fields = '__all__'

class ContextSerializer(serializers.ModelSerializer):
    context_components = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ContextComponent.objects.all()
    )

    class Meta:
        model = Context
        fields = ['id', 'name', 'version', 'previous_version', 'context_components']
        
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


##-----------------------




class ProjectStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectStage
        fields = ['stage', 'status']

class ProjectSerializer(serializers.ModelSerializer):
    stages = ProjectStageSerializer(many=True, read_only=True)
    current_stage = serializers.SerializerMethodField()
    context_obj = ContextSerializer(source='context', read_only=True)
    #context = serializers.SerializerMethodField()  #  Campo personalizado para el ID

    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'description',
            'dqmodel_version',
            #'context_version',
            'data_at_hand',
            #'stage',  # Mantener por compatibilidad
            #'status', # Mantener por compatibilidad
            'created_at',
            'stages', # Nuevo campo
            'current_stage', # Nuevo campo
            'context_obj',
            'context',
            'estimation','user'
        ]
        read_only_fields = ['created_at']


    def get_context(self, obj):
        # Obtiene el contexto asociado y devuelve solo su ID (o `null`)
        return obj.context.id if obj.context else None
        #context = obj.context.first()
        #return context.id if context else None  # 🔹 Solo el ID
    
    def get_current_stage(self, obj):
        current = obj.current_stage
        if current:
            return {
                'stage': current.stage,
                'status': current.status
            }
        return None

    #def validate(self, attrs):
     #   if self.instance:
      #      # Verificar si se está intentando cambiar dqmodel_version o context_version
       #     if 'dqmodel_version' in attrs and attrs['dqmodel_version'] != self.instance.dqmodel_version:
        #        raise serializers.ValidationError("No se puede cambiar 'dqmodel_version' una vez asignado.")
         #   if 'context_version' in attrs and attrs['context_version'] != self.instance.context_version:
          #      raise serializers.ValidationError("No se puede cambiar 'context_version' una vez asignado.")
       # return attrs
       
    def update(self, instance, validated_data):
        try:
            # Actualizar campos normales
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

            # Manejar context_version
            #new_context = validated_data.get('context_version')
            #if new_context is not None:
            #    if instance.context_version is None:
            #        instance.context_version = new_context
            #    elif new_context != instance.context_version:
            #        raise serializers.ValidationError({
            #            "context_version": "No se puede cambiar 'context_version' una vez asignado."
            #        })

            instance.save()
            return instance

        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        except Exception as e:
            raise serializers.ValidationError(f"Error al actualizar el proyecto: {str(e)}")


#class PrioritizedDqProblemSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = PrioritizedDQProblem
#        fields = '__all__'  


class DataAtHandSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataAtHand
        fields = '__all__'  
        
        
class DataSchemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSchema
        fields = '__all__'
     

class DQMethodExecutionResultSerializer(serializers.ModelSerializer):
    execution_time = serializers.SerializerMethodField()
    
    class Meta:
        model = DQMethodExecutionResult
        fields = '__all__'
    
    def get_execution_time(self, obj):
        return obj.details.get('execution_time')