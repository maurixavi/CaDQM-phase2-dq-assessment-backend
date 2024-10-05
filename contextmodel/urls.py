from django.urls import path, include
# from rest_framework.routers import DefaultRouter
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from . import views

router = routers.DefaultRouter()
router.register(r'context-model', views.ContextModelViewSet)
router.register(r'aplication-domain', views.ApplicationDomainViewSet)
router.register(r'business-rule', views.BusinessRuleViewSet)
router.register(r'user-type', views.UserTypeViewSet)
router.register(r'task-at-tand', views.TaskAtHandViewSet)
router.register(r'dq-requirement', views.DQRequirementViewSet)
router.register(r'data-filtering', views.DataFilteringViewSet)
router.register(r'system-requirement', views.SystemRequirementViewSet)
router.register(r'dq-metadata', views.DQMetadataViewSet)
router.register(r'other-metadata', views.OtherMetadataViewSet)
router.register(r'other-data', views.OtherDataViewSet)


urlpatterns = [
    path("context/", include(router.urls)),
]
