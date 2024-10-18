from django.db import models
from dqmodel.models import DQModel
from contextmodel.models import ContextModel
from django.core.exceptions import ValidationError

class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField() 
    dqmodel_version = models.ForeignKey(DQModel, on_delete=models.CASCADE, null=True, blank=True)
    context_version = models.ForeignKey(ContextModel, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    
    STATUS_CHOICES = [
        ('to_do', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ]
    stage = models.IntegerField(default=1)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='to_do'
    )

    class Meta:
        unique_together = ('context_version', 'dqmodel_version')

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.pk: # proyecto ya existe
            # Obtener la instancia original desde la base de datos
            original = Project.objects.get(pk=self.pk)
            if original.dqmodel_version != self.dqmodel_version:
                raise ValidationError("No se puede cambiar 'dqmodel_version' una vez asignado.")
            if original.context_version != self.context_version:
                raise ValidationError("No se puede cambiar 'context_version' una vez asignado.")
        super().save(*args, **kwargs)
