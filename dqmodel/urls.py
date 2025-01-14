from django.urls import path, include
from rest_framework import routers
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
    
    path("dqmodels/<int:pk>/dimensions/", DQModelViewSet.as_view({'get': 'get_dimensions'}), name='dqmodel-dimensions'),
    
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
    
    
    #path('dqmodels/<int:dq_model_id>/prioritized-dq-problems/<int:id>/', PrioritizedDqProblemDetailView.as_view(), name='prioritized-dq-problem-detail'),
    
    path(
        "dqmodels/<int:pk>/dimensions/<int:dimension_id>/",
        DQModelViewSet.as_view({'get': 'get_dimension'}),
        name="dqmodel-dimension-detail"
    ),
    
    
    path(
        "dqmodels/<int:pk>/dimensions/<int:dimension_id>/factors/<int:factor_id>/",
        DQModelViewSet.as_view({'get': 'get_factor'}),
        name='dqmodel-dimension-factors-detail'
    ),


]