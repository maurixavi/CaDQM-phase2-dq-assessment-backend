from django.urls import path, include
# from rest_framework.routers import DefaultRouter
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from . import views

router = routers.DefaultRouter()
#router.register(r'dqmodel', views.DQModelViewSet)
router.register(r'dqmodels', views.DQModelViewSet, basename='dqmodel')

router.register(r'dqmodels/(?P<dqmodel_id>\d+)/dimensions', views.DQDimensionViewSet, basename='dimension')
# router.register(r'dimensions', views.DQDimensionViewSet)

router.register(r'dqmodels/(?P<dqmodel_id>\d+)/dimensions/(?P<dimension_id>\d+)/factors', views.DQFactorViewSet, basename='factor')
#router.register(r'factors', views.DQFactorViewSet)

#router.register(r'metrics', views.DQMetricViewSet)
router.register(r'dqmodels/(?P<dqmodel_id>\d+)/dimensions/(?P<dimension_id>\d+)/factors/(?P<factor_id>\d+)/metrics', views.DQMetricViewSet, basename='metric')


#router.register(r'methods', views.DQMethodViewSet)
router.register(r'dqmodels/(?P<dqmodel_id>\d+)/dimensions/(?P<dimension_id>\d+)/factors/(?P<factor_id>\d+)/metrics/(?P<metric_id>\d+)/methods', views.DQMethodViewSet, basename='method')

#router.register(r'applied_measurement_methods', views.MeasurementDQMethodViewSet)
router.register(r'dqmodels/(?P<dqmodel_id>\d+)/dimensions/(?P<dimension_id>\d+)/factors/(?P<factor_id>\d+)/metrics/(?P<metric_id>\d+)/methods/(?P<method_id>\d+)/applied-measurement-methods', views.MeasurementDQMethodViewSet, basename='measurement_dq_method')

#router.register(r'applied_aggregation_methods', views.AggregationDQMethodViewSet)
router.register(r'dqmodels/(?P<dqmodel_id>\d+)/dimensions/(?P<dimension_id>\d+)/factors/(?P<factor_id>\d+)/metrics/(?P<metric_id>\d+)/methods/(?P<method_id>\d+)/applied-aggregation-methods', views.AggregationDQMethodViewSet, basename='aggregation_dq_method')


urlpatterns = [
    path("", include(router.urls)),
]
