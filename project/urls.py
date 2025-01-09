from django.urls import path, include
# from rest_framework.routers import DefaultRouter
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from . import views
from .views import get_dq_problems_dataset

router = routers.DefaultRouter()
router.register(r'projects', views.ProjectViewSet, basename='project')

urlpatterns = [
    path("", include(router.urls)),
    path('dq-problems/', get_dq_problems_dataset, name='dq_problems'),
]
