from django.db import models
from dataqualitymodel.models import DQModel
from contextmodel.models import ContextModel

class Project(models.Model):
    name = models.CharField(max_length=100)
    dqmodel_version = models.ForeignKey(DQModel, on_delete=models.CASCADE, null=True, blank=True)
    context_version = models.ForeignKey(ContextModel, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True) 

    class Meta:
        unique_together = ('context_version', 'dqmodel_version')

    def __str__(self):
        return self.name
