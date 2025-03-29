from django.urls import path, include
from rest_framework import routers
from . import views 
from .views import (
    DQModelViewSet,
    DQDimensionBaseViewSet,
    DQFactorBaseViewSet,
    DQMetricBaseViewSet,
    DQMethodBaseViewSet,
    MeasurementDQMethodViewSet,
    AggregationDQMethodViewSet,
    DQModelDimensionViewSet,
    DQModelFactorViewSet,
    DQModelMetricViewSet,
    DQModelMethodViewSet,
    generate_dqmethod_suggestion,
    create_initial_prioritized_dq_problems,
    get_full_dqmodel,
    get_prioritized_dq_problems,
    get_selected_prioritized_dq_problems,
    PrioritizedDqProblemDetailView
)

router = routers.DefaultRouter()
router.register(r'dqmodels', DQModelViewSet)
router.register(r'dimensions', DQModelDimensionViewSet)
router.register(r'factors', DQModelFactorViewSet)
router.register(r'metrics', DQModelMetricViewSet)
router.register(r'methods', DQModelMethodViewSet)


router.register(r'dimensions-base', DQDimensionBaseViewSet)
router.register(r'factors-base', DQFactorBaseViewSet)
router.register(r'metrics-base', DQMetricBaseViewSet)
router.register(r'methods-base', DQMethodBaseViewSet)
router.register(r'measurement-methods', MeasurementDQMethodViewSet)
router.register(r'aggregation-methods', AggregationDQMethodViewSet)
router.register(
    r'dqmodels/(?P<dq_model_id>\d+)/prioritized-dq-problems',
    PrioritizedDqProblemDetailView,
    basename='prioritized-dq-problem'
)

urlpatterns = [
    path("", include(router.urls)),
    path("dimensions-base/<int:pk>/factors-base/", DQFactorBaseViewSet.as_view({'get': 'get_factors_by_dimension'}), name='factors-by-dimension'),
    path("dimensions-base/<int:dim_id>/factors-base/<int:pk>/metrics-base/", DQMetricBaseViewSet.as_view({'get': 'get_metrics_by_factor'}), name='metrics-by-factor'),
    path("dimensions-base/<int:dim_id>/factors-base/<int:factor_id>/metrics-base/<int:pk>/methods-base/", DQMethodBaseViewSet.as_view({'get': 'get_methods_by_metric'}), name='methods-by-metric'),
    
    path("dqmodels/<int:pk>/dimensions/", DQModelViewSet.as_view({'get': 'get_dimensions'}), name='dqmodel-dimensions'),
    path("dqmodels/<int:pk>/factors/", DQModelViewSet.as_view({'get': 'get_factors'}), name='dqmodel-factors'),
    path("dqmodels/<int:pk>/metrics/", DQModelViewSet.as_view({'get': 'get_metrics'}), name='dqmodel-metrics'),
    path("dqmodels/<int:pk>/methods/", DQModelViewSet.as_view({'get': 'get_methods'}), name='dqmodel-methods'),
    
    path(
        "dqmodels/<int:pk>/dimensions/<int:dimension_id>/factors/",
        DQModelViewSet.as_view({'get': 'get_factors_by_dimension'}),
        name='dqmodel-dimension-factors'
    ),
    
    path(
        "dqmodels/<int:pk>/dimensions/<int:dimension_id>/factors/<int:factor_id>/metrics/",
        DQModelViewSet.as_view({'get': 'get_metrics_by_factor'}),
        name='dqmodel-dimension-factor-metrics'
    ),

    path(
        "dqmodels/<int:pk>/dimensions/<int:dimension_id>/factors/<int:factor_id>/metrics/<int:metric_id>/methods/",
        DQModelViewSet.as_view({'get': 'get_methods_by_metric'}),
        name='dqmodel-dimension-factor-metric-methods'
    ),
    
    path('generate-dqmethod-suggestion/', generate_dqmethod_suggestion, name='generate_dqmethod_suggestion'),
    path('prioritized-dq-problems/', create_initial_prioritized_dq_problems, name='create_initial_prioritized_dq_problems'),
    path('dqmodels/<int:dq_model_id>/prioritized-dq-problems/', get_prioritized_dq_problems, name='get_prioritized_dq_problems'),
    path('dqmodels/<int:dq_model_id>/selected-prioritized-dq-problems/', get_selected_prioritized_dq_problems, name='get_selected_prioritized_dq_problems'),
    
    # Individual Views: Dim, Factor, Metric and Method in DQ Model
    path(
        "dqmodels/<int:pk>/dimensions/<int:dimension_id>/",
        DQModelViewSet.as_view({'get': 'get_dimension'}),
        name="dqmodel-dimension-detail"
    ),
    path(
        "dqmodels/<int:pk>/factors/<int:factor_id>/",
        DQModelViewSet.as_view({'get': 'get_factor_in_dqmodel'}),
        name="dqmodel-factor-detail"
    ),
    path(
        "dqmodels/<int:pk>/metrics/<int:metric_id>/",
        DQModelViewSet.as_view({'get': 'get_metric_in_dqmodel'}),
        name="dqmodel-metric-detail"
    ),
    path(
        "dqmodels/<int:pk>/methods/<int:method_id>/",
        DQModelViewSet.as_view({'get': 'get_method_in_dqmodel'}),
        name="dqmodel-method-detail"
    ),
    
    path(
        "dqmodels/<int:pk>/dimensions/<int:dimension_id>/factors/<int:factor_id>/",
        DQModelViewSet.as_view({'get': 'get_factor'}),
        name='dqmodel-dimension-factors-detail'
    ),
    
    path('dqmodels/<int:dq_model_id>/full/', get_full_dqmodel, name='get_full_dqmodel'),
    
    # Rutas para métodos aplicados (integradas en el ViewSet)
    path(
        "dqmodels/<int:dq_model_id>/applied-dq-methods/<int:applied_method_id>/",
        DQModelViewSet.as_view({'get': 'get_applied_method'}),
        name='dqmodel-applied-method-detail'
    ),
    path(
        "dqmodels/<int:dq_model_id>/applied-dq-methods/<int:applied_method_id>/execute/",
        DQModelViewSet.as_view({'post': 'execute_applied_method'}),
        name='dqmodel-applied-method-execute'
    ),
    path(
        "dqmodels/<int:dq_model_id>/methods/execute/",
        DQModelViewSet.as_view({'post': 'execute_multiple_methods'}),
        name='dqmodel-methods-execute'
    ),
    
    # Métodos base de una métrica base
    path(
        "metrics-base/<int:metric_id>/methods-base/",
        DQMetricBaseViewSet.as_view({'get': 'get_methods_base'}),
        name='metric-base-methods'
    ),
    
    # Resultados de ejecución (ahora manejado por ExecutionLogViewSet a través del router)
    #path(
    #    'api/dqmodels/<int:dq_model_id>/applied-dq-methods/<int:applied_method_id>/execute/',
    #    views.execute_applied_method,
    #    name='execute_applied_method'
    #),
    
    # Asegúrate de que esta ruta esté correctamente configurada:
    path(
        "dqmodels/<int:dq_model_id>/applied-dq-methods/<int:applied_method_id>/execute/",
        DQModelViewSet.as_view({'post': 'execute_applied_method'}),
        name='dqmodel-applied-method-execute'
    ),
    
    # Puedes eliminar esta ruta si ahora manejas todo desde el ViewSet:
    # path('api/dqmodels/<int:dq_model_id>/applied-dq-methods/<int:method_id>/execute/', ...
]