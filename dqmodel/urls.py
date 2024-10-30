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

]