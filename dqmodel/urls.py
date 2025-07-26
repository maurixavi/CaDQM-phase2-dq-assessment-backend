from django.urls import path, include
from rest_framework import routers
from . import views 
from .views import (
    ColumnResultsViewSet,
    DQExecutionResultViewSet,
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
    RowResultsViewSet,
    TableResultsViewSet,
    generate_dqmethod_suggestion,
    generate_dq_dim_factor_suggestion,
    get_full_dqmodel,
)

router = routers.DefaultRouter()

router.register(r'dimensions-base', DQDimensionBaseViewSet)
router.register(r'factors-base', DQFactorBaseViewSet)
router.register(r'metrics-base', DQMetricBaseViewSet)
router.register(r'methods-base', DQMethodBaseViewSet)

router.register(r'dqmodels', DQModelViewSet)
router.register(r'dimensions', DQModelDimensionViewSet)
router.register(r'factors', DQModelFactorViewSet)
router.register(r'metrics', DQModelMetricViewSet)
router.register(r'methods', DQModelMethodViewSet)
router.register(r'measurement-methods', MeasurementDQMethodViewSet)
router.register(r'aggregation-methods', AggregationDQMethodViewSet)

router.register(r'execution-results', DQExecutionResultViewSet, basename='execution-results')

router.register(
    r'dqmodels/(?P<dq_model_id>\d+)/table-results',
    TableResultsViewSet,
    basename='table-results'
)
router.register(
    r'dqmodels/(?P<dq_model_id>\d+)/column-results',
    ColumnResultsViewSet,
    basename='column-results'
)
router.register(
    r'dqmodels/(?P<dq_model_id>\d+)/row-results',
    RowResultsViewSet,
    basename='row-results'
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
    
    path(
        "dqmodels/<int:dq_model_id>/applied-dq-methods/<int:applied_method_id>/",
        DQModelViewSet.as_view({
            'get': 'get_applied_method',
            'patch': 'update_applied_method',
            'put': 'update_applied_method'
        }),
        name='dqmodel-applied-method-detail'
    ),

    path(
        "dqmodels/<int:dq_model_id>/applied-dq-methods/<int:applied_method_id>/assess/",
        DQModelViewSet.as_view({'post': 'assess_applied_method'}),
        name='dqmodel-applied-method-assess'
    ),
    
    path(
        "dqmodels/<int:dq_model_id>/start-dq-model-execution/",
        DQModelViewSet.as_view({'post': 'start_dq_model_execution'}),
        name='dqmodel-create-execution'
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
    
    # Asegúrate de que esta ruta esté correctamente configurada:
    path(
        "dqmodels/<int:dq_model_id>/applied-dq-methods/<int:applied_method_id>/execute/",
        DQModelViewSet.as_view({'post': 'execute_applied_method'}),
        name='dqmodel-applied-method-execute'
    ),
    
    # Resultados de ejecución
    path(
        'dqmodels/<int:dq_model_id>/latest-results/',
        DQExecutionResultViewSet.as_view({'get': 'get_latest_results'}),
        name='dqmodel-latest-results'
    ),
    path(
        'methods/<int:method_id>/execution-history/',
        DQExecutionResultViewSet.as_view({'get': 'get_method_execution_history'}),
        name='method-execution-history'
    ),
    
    path(
        'dqmodels/<int:dq_model_id>/applied-dq-methods/<int:applied_method_id>/execution-result/',
        DQExecutionResultViewSet.as_view({'get': 'get_specific_method_execution_result'}),
        name='specific-method-execution-result'
    ),
    
    # RESULTADOS POR METODO y GRANULARIDAD
    path(
        'dqmodels/<int:dq_model_id>/applied-dq-methods/<int:applied_method_id>/execution-column-results/',
        DQExecutionResultViewSet.as_view({'get': 'get_method_column_results'}),
        name='execution-column-results'
    ),
    path(
        'dqmodels/<int:dq_model_id>/applied-dq-methods/<int:applied_method_id>/execution-row-results/',
        DQExecutionResultViewSet.as_view({'get': 'get_method_row_results'}),
        name='execution-row-results'
    ),
    path(
        'dqmodels/<int:dq_model_id>/applied-dq-methods/<int:applied_method_id>/execution-method-results/',
        DQExecutionResultViewSet.as_view({'get': 'get_applied_method_results'}),
        name='execution-method-results'
    ),path(
        'dqmodels/<int:dq_model_id>/applied-dq-methods/<int:applied_method_id>/execution-method-results/<int:result_id>',
        DQExecutionResultViewSet.as_view({'get': 'get_specific_applied_method_results'}),
        name='execution-method-results-detail'
    ),
    
    # update assessment thresholds
    path(
        'dqmodels/<int:dq_model_id>/applied-dq-methods/<int:applied_method_id>/execution-method-results/<int:result_id>/thresholds/',
        DQExecutionResultViewSet.as_view({'patch': 'update_execution_result_thresholds'}),
        name='update-method-execution-assessment'
    ),
    
    # EJECUCIONES POR DQMODEL
    path(
        'dqmodels/<int:dq_model_id>/measurement-executions/',
        DQExecutionResultViewSet.as_view({'get': 'get_dqmodel_executions'}),
        name='dqmodel-measurement-executions'
    ),
    path(
        'dqmodels/<int:dq_model_id>/measurement-executions/<uuid:execution_id>/',
        DQExecutionResultViewSet.as_view({'get': 'get_specific_model_execution'}),
        name='dqmodel-measurement-execution-detail'
    ),
    
    # RESULTADOS POR DATOS 
    path("dq-measurement/column-results/", views.DQExecutionResultViewSet.as_view({'get': 'get_measurement_results_column_granularity'}), name="get-column-results"),
    
    path("dq-measurement/column-results/dqmodel/<int:dq_model_id>/", views.DQExecutionResultViewSet.as_view({'get': 'get_measurement_results_column_granularity_dq_model'}), name="get-column-results-by-dqmodel"),
    
    path("dq-measurement/column-results/column/<int:column_id>/", views.DQExecutionResultViewSet.as_view({'get': 'get_measurement_results_column_granularity_by_column'}), name="get-column-results-by-column"),
    
    path("dq-measurement/column-results/table/<int:table_id>/", views.DQExecutionResultViewSet.as_view({'get': 'get_measurement_results_column_granularity_by_table'}), name="get-column-results-by-table"),
    
    path(
        'dqmodels/<int:dq_model_id>/applied-dq-methods/<int:applied_method_id>/execution-result/<int:result_id>/thresholds/',
        DQExecutionResultViewSet.as_view({'patch': 'update_execution_result_thresholds'}),
        name='update-execution-result-thresholds'
    ),
    
    path(
        'dqmodels/<int:dq_model_id>/current-execution/',
        DQExecutionResultViewSet.as_view({'get': 'get_current_execution'}),
        name='dqmodel-current-execution'
    ),
    
    # ==============================================
    # AI Suggestion Endpoints
    # ==============================================
    path('generate-dqmethod-suggestion/', generate_dqmethod_suggestion, name='generate_dqmethod_suggestion'),
    
    path('generate-dq-dimension-factor-suggestion/', generate_dq_dim_factor_suggestion, name='generate_dq_dim_factor_suggestion'),

]