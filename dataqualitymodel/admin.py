from django.contrib import admin
from .models import DQModel, DQDimension, DQFactor, DQMetric, DQMethod, MeasurementDQMethod, AggregationDQMethod

admin.site.register(DQModel)
admin.site.register(DQDimension)
admin.site.register(DQFactor)
admin.site.register(DQMetric)
admin.site.register(DQMethod)
admin.site.register(MeasurementDQMethod)
admin.site.register(AggregationDQMethod)