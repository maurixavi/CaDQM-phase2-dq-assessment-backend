from django.urls import path, include
# from rest_framework.routers import DefaultRouter
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from . import views

router = routers.DefaultRouter()
# router.register(r'dqmetadata', views.DQMetadataViewSet)
router.register(r'dqmetadata', views.ExecutionResultViewSet)

urlpatterns = [
    path("api/dqmetadata/", include(router.urls)),
]
