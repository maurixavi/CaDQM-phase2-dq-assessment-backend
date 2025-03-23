from django.urls import path, include
# from rest_framework.routers import DefaultRouter
from rest_framework import routers
from rest_framework.documentation import include_docs_urls

from . import views
from .views import DataAtHandViewSet, DataSchemaViewSet, PrioritizedDQProblemViewSet, get_dq_problem_by_id, load_dq_problems_dataset, get_project_dq_problems, get_selected_prioritized_dq_problems_by_project

router = routers.DefaultRouter()
router.register(r'projects', views.ProjectViewSet, basename='project')
router.register(r'prioritized-dq-problems', PrioritizedDQProblemViewSet, basename='prioritized-dq-problem')

router.register(r'data-at-hand', DataAtHandViewSet, basename='data-at-hand')  
router.register(r'data-schema', DataSchemaViewSet, basename='data-schema')

urlpatterns = [
    path("", include(router.urls)),
    path('dq-problems/', load_dq_problems_dataset, name='dq_problems'),
    path('projects/<int:project_id>/dq-problems/', get_project_dq_problems, name='project_dq_problems'),
    
    # Ruta para listar problemas priorizados de un proyecto
    path('projects/<int:project_id>/prioritized-dq-problems/', PrioritizedDQProblemViewSet.as_view({'get': 'list'}), name='project_prioritized_dq_problems'),
    
    path(
        'projects/<int:project_id>/prioritized-dq-problems/<int:pk>/',
        PrioritizedDQProblemViewSet.as_view({
            'get': 'retrieve',  # Use the built-in retrieve method for GET
            'patch': 'partial_update'
        }),
        name='prioritized_dq_problem_detail'
    ),
    
    path('projects/<int:project_id>/selected-prioritized-dq-problems/', get_selected_prioritized_dq_problems_by_project, name='get_selected_prioritized_dq_problems'),
    
    path('projects/<int:project_id>/dq-problems/<int:problem_id>/', get_dq_problem_by_id, name='dq_problem_by_id'),
    
    path('data-at-hand/<int:pk>/data-schema/', DataAtHandViewSet.as_view({'get': 'data_schema'}), name='data-at-hand-data-schema'),
]
