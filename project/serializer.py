from rest_framework import serializers
from .models import Project
from django.core.exceptions import ValidationError


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'description',
            'dqmodel_version',
            'context_version',
            'stage',
            'status',
            'created_at',
        ]
        read_only_fields = ['stage', 'status', 'created_at']

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
            new_context = validated_data.get('context_version')
            if new_context is not None:
                if instance.context_version is None:
                    instance.context_version = new_context
                elif new_context != instance.context_version:
                    raise serializers.ValidationError({
                        "context_version": "No se puede cambiar 'context_version' una vez asignado."
                    })

            instance.save()
            return instance

        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        except Exception as e:
            raise serializers.ValidationError(f"Error al actualizar el proyecto: {str(e)}")
