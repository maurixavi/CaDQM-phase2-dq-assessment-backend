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
    
    STAGE_CHOICES = [
        ('ST1', 'Stage 1'),
        ('ST2', 'Stage 2'),
        ('ST3', 'Stage 3'),
        ('ST4', 'Stage 4'),
        ('ST5', 'Stage 5'),
        ('ST6', 'Stage 6'),
    ]
     
    STATUS_CHOICES = [
        ('to_do', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ]
    
    #stage = models.IntegerField(default=1)
    stage = models.CharField(
        max_length=3,  # Longitud máxima para las etapas como 'ST1'
        choices=STAGE_CHOICES,
        default='ST4'  # Por defecto en 'ST4'
    )
    
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
        if self.pk:
            original = Project.objects.get(pk=self.pk)
            # Solo validar si el campo no es null y está intentando cambiar
            if original.dqmodel_version is not None and self.dqmodel_version != original.dqmodel_version:
                raise ValidationError("No se puede cambiar 'dqmodel_version' una vez asignado. 1")
            if original.context_version is not None and self.context_version != original.context_version:
                raise ValidationError("No se puede cambiar 'context_version' una vez asignado. 2")
        super().save(*args, **kwargs)
