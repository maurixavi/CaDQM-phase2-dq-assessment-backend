from django.urls import path, include
# from rest_framework.routers import DefaultRouter
from rest_framework import routers
from rest_framework.documentation import include_docs_urls

from . import views
from .views import DataAtHandViewSet, DataSchemaViewSet, ContextComponentViewSet, ApplicationDomainViewSet, BusinessRuleViewSet, DataFilteringViewSet, DQMetadataViewSet, DQRequirementViewSet, OtherDataViewSet, OtherMetadataViewSet, SystemRequirementViewSet, TaskAtHandViewSet, UserTypeViewSet, UserDataViewSet
#from .views import DataAtHandViewSet, DataSchemaViewSet, PrioritizedDQProblemViewSet, get_dq_problem_by_id, load_dq_problems_dataset, get_project_dq_problems, get_selected_prioritized_dq_problems_by_project, ContextComponentViewSet, ApplicationDomainViewSet, BusinessRuleViewSet, DataFilteringViewSet, DQMetadataViewSet, DQRequirementViewSet, OtherDataViewSet, OtherMetadataViewSet, SystemRequirementViewSet, TaskAtHandViewSet, UserTypeViewSet, UserDataViewSet

from .views import ContextViewSet, ContextComponentsDetail, QualityProblemViewSet, QualityProblemProjectViewSet, quality_problems_by_project, get_selected_prioritized_quality_problems_by_project, copy_problems_from_project


router = routers.DefaultRouter()

router.register(r'dq-problems', QualityProblemViewSet, basename='data-quality-problem')


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


router.register(r'projects', views.ProjectViewSet, basename='project')
#router.register(r'prioritized-dq-problems', PrioritizedDQProblemViewSet, basename='prioritized-dq-problem')

router.register(r'data-at-hand', DataAtHandViewSet, basename='data-at-hand')  
router.register(r'data-schema', DataSchemaViewSet, basename='data-schema')

quality_problem_project_list = QualityProblemProjectViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
quality_problem_project_detail = QualityProblemProjectViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update'
})

urlpatterns = [
    path("", include(router.urls)),
     path('contexts/<int:pk>/context-components/', ContextComponentsDetail.as_view(), name='context-components-detail'),
     
    
    
    # QUALITY PROBLEMS de UN PROJECT
    path(
        'projects/<int:project_id>/quality-problems/',
        quality_problems_by_project,
        name='quality_problems_by_project'
    ),
    
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
    
    path('projects/<int:project_id>/selected-prioritized-quality-problems/', get_selected_prioritized_quality_problems_by_project, name='get_selected_prioritized_quality_problems'),
    
    
    
    path(
        'projects/<int:source_project_id>/copy-problems-to/<int:target_project_id>/',
        copy_problems_from_project,
        name='copy-problems-between-projects'
    ),
    
    
    
    path('data-at-hand/<int:pk>/data-schema/', DataAtHandViewSet.as_view({'get': 'data_schema'}), name='data-at-hand-data-schema'),
]


# DQ PROBLEMS (VERSION ANTERIOR)
    
    #path('dq-problems/', load_dq_problems_dataset, name='dq_problems'),
    #path('projects/<int:project_id>/dq-problems/', get_project_dq_problems, name='project_dq_problems'),
    
    # Ruta para listar problemas priorizados de un proyecto
    #path('projects/<int:project_id>/prioritized-dq-problems/', PrioritizedDQProblemViewSet.as_view({'get': 'list'}), name='project_prioritized_dq_problems'),
    
    #path(
    #    'projects/<int:project_id>/prioritized-dq-problems/<int:pk>/',
    #    PrioritizedDQProblemViewSet.as_view({
    #        'get': 'retrieve',  # Use the built-in retrieve method for GET
    #        'patch': 'partial_update'
    #    }),
    #    name='prioritized_dq_problem_detail'
    #),
    
    #path('projects/<int:project_id>/selected-prioritized-dq-problems/', get_selected_prioritized_dq_problems_by_project, name='get_selected_prioritized_dq_problems'),
    
    #path('projects/<int:project_id>/dq-problems/<int:problem_id>/', get_dq_problem_by_id, name='dq_problem_by_id'),