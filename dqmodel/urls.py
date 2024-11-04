from django.urls import path, include
# from rest_framework.routers import DefaultRouter
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
#from . import views
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
    DQModelMethodViewSet
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

""""
urlpatterns = [
    path("", include(router.urls)),
]
"""

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
    #path(
    #    "dqmodels/<int:pk>/dimensions/<int:dimension_id>/factors/<int:factor_id>/metrics/<int:metric_id>/methods/<int:method_id>/measurement-methods/",
    #    DQModelViewSet.as_view({'get': 'get_measurement_methods'}),
    #    name='dqmodel-dimension-factor-metric-method-measurement-methods'
    #),
    #path(
    #    "dqmodels/<int:pk>/dimensions/<int:dimension_id>/factors/<int:factor_id>/metrics/<int:metric_id>/methods/<int:method_id>/aggregation-methods/",
    #    DQModelViewSet.as_view({'get': 'get_aggregation_methods'}),
    #    name='dqmodel-dimension-factor-metric-method-aggregation-methods'
    #),
]