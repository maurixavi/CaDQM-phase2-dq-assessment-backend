# dqmodel/admin.py

from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import (
    DQModel,
    DQDimensionBase,
    DQFactorBase,
    DQMetricBase,
    DQMethodBase,
    DQModelDimension,
    DQModelFactor,
    DQModelMetric,
    DQModelMethod,
    MeasurementDQMethod,
    AggregationDQMethod,
)

# ### 1. Registro de Modelos Base ###

@admin.register(DQDimensionBase)
class DQDimensionBaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'semantic')
    search_fields = ('name',)
    ordering = ('name',)
    list_filter = ('name',)


@admin.register(DQFactorBase)
class DQFactorBaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'semantic', 'facetOf')
    search_fields = ('name', 'facetOf__name')
    list_filter = ('facetOf',)
    ordering = ('name',)


@admin.register(DQMetricBase)
class DQMetricBaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'purpose', 'granularity', 'resultDomain', 'measures')
    search_fields = ('name', 'measures__name')
    list_filter = ('granularity', 'resultDomain', 'measures')
    ordering = ('name',)


@admin.register(DQMethodBase)
class DQMethodBaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'inputDataType', 'outputDataType', 'algorithm', 'implements')
    search_fields = ('name', 'implements__name')
    list_filter = ('inputDataType', 'outputDataType', 'implements')
    ordering = ('name',)


# ### 2. Registro de Modelos de Asociación ###

@admin.register(DQModelDimension)
class DQModelDimensionAdmin(admin.ModelAdmin):
    list_display = ('id', 'dq_model', 'dimension_base')
    search_fields = ('dq_model__version', 'dimension_base__name')
    list_filter = ('dimension_base', 'dq_model__version')
    ordering = ('dq_model__version', 'dimension_base__name')


@admin.register(DQModelFactor)
class DQModelFactorAdmin(admin.ModelAdmin):
    list_display = ('id', 'dq_model', 'factor_base', 'dimension')
    search_fields = ('dq_model__version', 'factor_base__name', 'dimension__dimension_base__name')
    list_filter = ('factor_base', 'dimension__dimension_base', 'dq_model__version')
    ordering = ('dq_model__version', 'factor_base__name')


@admin.register(DQModelMetric)
class DQModelMetricAdmin(admin.ModelAdmin):
    list_display = ('id', 'dq_model', 'metric_base', 'factor')
    search_fields = ('dq_model__version', 'metric_base__name', 'factor__factor_base__name')
    list_filter = ('metric_base', 'factor__factor_base', 'dq_model__version')
    ordering = ('dq_model__version', 'metric_base__name')


# ### 3. Inlines para `AppliedDQMethod` y Subclases ###

class MeasurementDQMethodInline(admin.StackedInline):
    model = MeasurementDQMethod
    extra = 1
    autocomplete_fields = ['associatedTo']
    readonly_fields = ['__str__']
    show_change_link = True


class AggregationDQMethodInline(admin.StackedInline):
    model = AggregationDQMethod
    extra = 1
    autocomplete_fields = ['associatedTo']
    readonly_fields = ['__str__']
    show_change_link = True


# ### 4. Registro de `DQModelMethod` con sus Inlines ###

@admin.register(DQModelMethod)
class DQModelMethodAdmin(admin.ModelAdmin):
    list_display = ('id', 'dq_model', 'method_base', 'metric')
    search_fields = ('dq_model__version', 'method_base__name', 'metric__metric_base__name')
    list_filter = ('method_base', 'metric__metric_base', 'dq_model__version')
    ordering = ('dq_model__version', 'method_base__name')
    inlines = [
        MeasurementDQMethodInline,
        AggregationDQMethodInline,
    ]


# ### 5. Registro de `DQModel` sin Inlines ###

@admin.register(DQModel)
class DQModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'version', 'status', 'created_at', 'finished_at')
    list_filter = ('status', 'created_at')
    search_fields = ('version',)
    ordering = ('-created_at',)
    # No incluir inlines aquí para evitar conflictos
