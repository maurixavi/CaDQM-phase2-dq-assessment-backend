from rest_framework import serializers
from .models import Project

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

    def validate(self, attrs):
        if self.instance:
            # Verificar si se está intentando cambiar dqmodel_version o context_version
            if 'dqmodel_version' in attrs and attrs['dqmodel_version'] != self.instance.dqmodel_version:
                raise serializers.ValidationError("No se puede cambiar 'dqmodel_version' una vez asignado.")
            if 'context_version' in attrs and attrs['context_version'] != self.instance.context_version:
                raise serializers.ValidationError("No se puede cambiar 'context_version' una vez asignado.")
        return attrs
