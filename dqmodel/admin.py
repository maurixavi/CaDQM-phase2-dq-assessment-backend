from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import (
    DQModel, DQDimensionBase, DQFactorBase, DQMetricBase, DQMethodBase,
    DQModelDimension, DQModelFactor, DQModelMetric, DQModelMethod,
    MeasurementDQMethod, AggregationDQMethod
)
"""
@admin.register(DQModel)
class DQModelAdmin(admin.ModelAdmin):
    readonly_fields = ('finished_at', 'previous_version')
    list_display = ('id', 'version', 'status', 'created_at', 'finished_at')
    list_filter = ('status', 'created_at')
    search_fields = ('version',)
    ordering = ('-created_at',)

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status == 'finished':
            return self.readonly_fields + ('version', 'status', 'model_dimensions', 'model_factors', 'model_metrics', 'model_methods')
        return self.readonly_fields
"""
    

class DQModelFactorAdmin(admin.ModelAdmin):
    list_display = ('factor_base', 'dq_model', 'get_dimension')
    
    def get_dimension(self, obj):
        return obj.dimension if obj.dimension else "Pendiente de asignación"
    get_dimension.short_description = 'Dimensión'

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        return [f for f in fields if f != 'dimension']

    def save_model(self, request, obj, form, change):
        if obj.factor_base.facetOf:
            try:
                dimension = DQModelDimension.objects.get(
                    dq_model=obj.dq_model,
                    dimension_base=obj.factor_base.facetOf
                )
                obj.dimension = dimension
            except DQModelDimension.DoesNotExist:
                raise ValidationError(
                    f"No existe una dimensión en el modelo {obj.dq_model.version} "
                    f"para el factor base {obj.factor_base.name} "
                    f"(debería estar asociado a {obj.factor_base.facetOf.name})"
                )
        super().save_model(request, obj, form, change)


class DQModelMetricAdmin(admin.ModelAdmin):
    list_display = ('metric_base', 'dq_model', 'get_factor')
    
    def get_factor(self, obj):
        return obj.factor if obj.factor else "Pendiente de asignación"
    get_factor.short_description = 'Factor'

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        return [f for f in fields if f != 'factor']

    def save_model(self, request, obj, form, change):
        if obj.metric_base.measures:
            try:
                factor = DQModelFactor.objects.get(
                    dq_model=obj.dq_model,
                    factor_base=obj.metric_base.measures
                )
                obj.factor = factor
            except DQModelFactor.DoesNotExist:
                raise ValidationError(
                    f"No existe un factor en el modelo {obj.dq_model.version} "
                    f"para la métrica base {obj.metric_base.name} "
                    f"(debería estar asociado a {obj.metric_base.measures.name})"
                )
        super().save_model(request, obj, form, change)


class DQModelMethodAdmin(admin.ModelAdmin):
    list_display = ('method_base', 'dq_model', 'get_metric')
    
    def get_metric(self, obj):
        return obj.metric if obj.metric else "Pendiente de asignación"
    get_metric.short_description = 'Métrica'

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        return [f for f in fields if f != 'metric']

    def save_model(self, request, obj, form, change):
        if obj.method_base.implements:
            try:
                metric = DQModelMetric.objects.get(
                    dq_model=obj.dq_model,
                    metric_base=obj.method_base.implements
                )
                obj.metric = metric
            except DQModelMetric.DoesNotExist:
                raise ValidationError(
                    f"No existe una métrica en el modelo {obj.dq_model.version} "
                    f"para el método base {obj.method_base.name} "
                    f"(debería estar asociado a {obj.method_base.implements.name})"
                )
        super().save_model(request, obj, form, change)


# Registramos todos los modelos
admin.site.register(DQModel)
admin.site.register(DQDimensionBase)
admin.site.register(DQFactorBase)
admin.site.register(DQMetricBase)
admin.site.register(DQMethodBase)
admin.site.register(DQModelDimension)
admin.site.register(DQModelFactor, DQModelFactorAdmin)
admin.site.register(DQModelMetric, DQModelMetricAdmin)
admin.site.register(DQModelMethod, DQModelMethodAdmin)
admin.site.register(MeasurementDQMethod)
admin.site.register(AggregationDQMethod)

#admin.site.register(PrioritizedDqProblem)