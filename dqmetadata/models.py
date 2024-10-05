from django.db import models
from dataqualitymodel.models import DQModel, DQDimension, DQFactor, DQMetric, DQMethod, MeasurementDQMethod, AggregationDQMethod

class ExecutionResult(models.Model):
    dq_value = models.FloatField()  #Resultado de la ejecución del metodo aplicado
    execution_date = models.DateTimeField(auto_now_add=True)  #Fecha de ejecución

    # relaciones para rastrear el origen del resultado
    applied_method = models.ForeignKey(
        MeasurementDQMethod, null=True, blank=True, on_delete=models.CASCADE, related_name='execution_results_measurement'
    )
    applied_method_aggregation = models.ForeignKey(
        AggregationDQMethod, null=True, blank=True, on_delete=models.CASCADE, related_name='execution_results_aggregation'
    )
    metric = models.ForeignKey(DQMetric, on_delete=models.CASCADE, related_name='execution_results')
    factor = models.ForeignKey(DQFactor, on_delete=models.CASCADE, related_name='execution_results')
    dimension = models.ForeignKey(DQDimension, on_delete=models.CASCADE, related_name='execution_results')

    def __str__(self):
        return f"Execution Result for {self.metric.name} on {self.execution_date}"
