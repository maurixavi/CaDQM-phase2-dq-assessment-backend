from rest_framework import serializers
from .models import ExecutionResult

class ExecutionResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExecutionResult
        fields = '__all__'