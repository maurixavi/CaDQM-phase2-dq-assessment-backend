from django.shortcuts import render
from rest_framework import viewsets
from .models import Project
from .serializer import ProjectSerializer
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import ContextModel

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

