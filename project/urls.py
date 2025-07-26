from django.urls import path, include
from rest_framework import routers
from rest_framework.documentation import include_docs_urls

from . import views
from .views import (
    # ViewSets
    DataAtHandViewSet,
    DataSchemaViewSet,
    ContextViewSet,
    ContextComponentsDetail,
    ContextComponentViewSet,
    ApplicationDomainViewSet,
    BusinessRuleViewSet,
    DataFilteringViewSet,
    DQMetadataViewSet,
    DQRequirementViewSet,
    OtherDataViewSet,
    OtherMetadataViewSet,
    SystemRequirementViewSet,
    TaskAtHandViewSet,
    UserTypeViewSet,
    UserDataViewSet,
    QualityProblemViewSet,
    QualityProblemProjectViewSet,
    
    # API Views
    quality_problems_by_project,
    get_selected_prioritized_quality_problems_by_project,
    copy_problems_from_project
)

# Initialize DefaultRouter
router = routers.DefaultRouter()


# ==============================================
# API Endpoints Registration
# ==============================================

# Quality Problems Endpoints
router.register(r'dq-problems', QualityProblemViewSet, basename='data-quality-problem')

# Context Endpoints
router.register(r'contexts', ContextViewSet, basename='context')
router.register(r'context-components', ContextComponentViewSet, basename='context-component')
router.register(r'application-domains', ApplicationDomainViewSet)
router.register(r'business-rules', BusinessRuleViewSet)
router.register(r'data-filterings', DataFilteringViewSet)
router.register(r'dq-metadata', DQMetadataViewSet)
router.register(r'dq-requirements', DQRequirementViewSet)
router.register(r'other-data', OtherDataViewSet)
router.register(r'other-metadata', OtherMetadataViewSet)
router.register(r'system-requirements', SystemRequirementViewSet)
router.register(r'tasks-at-hand', TaskAtHandViewSet)
router.register(r'user-types', UserTypeViewSet)
router.register(r'user-data', UserDataViewSet)

# Project Endpoints
router.register(r'projects', views.ProjectViewSet, basename='project')

# Data Endpoints
router.register(r'data-at-hand', DataAtHandViewSet, basename='data-at-hand')  
router.register(r'data-schema', DataSchemaViewSet, basename='data-schema')


# ==============================================
# Custom Endpoints
# ==============================================

# QualityProblemProject custom views
quality_problem_project_list = QualityProblemProjectViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
quality_problem_project_detail = QualityProblemProjectViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update'
})

urlpatterns = [
    # Include all router URLs
    path("", include(router.urls)),

    # Context Components Detail
    path(
        'contexts/<int:pk>/context-components/',
        ContextComponentsDetail.as_view(),
        name='context-components-detail'
    ),
    
    # Quality Problems by Project
    path(
        'projects/<int:project_id>/quality-problems/',
        quality_problems_by_project,
        name='quality_problems_by_project'
    ),
    
    # QualityProblemProject endpoints
    path(
        'projects/<int:project_id>/prioritized-quality-problems/',
        quality_problem_project_list,
        name='project_quality_problems'
    ),
    path(
        'projects/<int:project_id>/prioritized-quality-problems/<int:pk>/',
        quality_problem_project_detail,
        name='project_quality_problem_detail'
    ),
    path(
        'projects/<int:project_id>/selected-prioritized-quality-problems/', get_selected_prioritized_quality_problems_by_project, name='get_selected_prioritized_quality_problems'
    ),
    
    # Copy problems between projects
    path(
        'projects/<int:source_project_id>/copy-problems-to/<int:target_project_id>/',
        copy_problems_from_project,
        name='copy-problems-between-projects'
    ),
    
    # Data Schema for DataAtHand
    path(
        'data-at-hand/<int:pk>/data-schema/',
        DataAtHandViewSet.as_view({'get': 'data_schema'}),
        name='data-at-hand-data-schema'
    ),
]