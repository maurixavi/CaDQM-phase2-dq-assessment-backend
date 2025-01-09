from django.urls import path, include
# from rest_framework.routers import DefaultRouter
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from . import views
from .views import get_context_versions

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
    path("", include(router.urls)),
    path('context-versions/', get_context_versions, name='context_versions'),
    path('context-versions/<int:id>/', views.get_context_by_id, name='get-context-by-id'),
     path('context-versions/<int:id>/context-components/', views.get_context_components, name='get-context-components'),  

]
