from rest_framework import viewsets
from .models import ExecutionResult
from .serializer import ExecutionResultSerializer

class ExecutionResultViewSet(viewsets.ModelViewSet):
    queryset = ExecutionResult.objects.all()
    serializer_class = ExecutionResultSerializer