from django.db import models
from dqmodel.models import DQModel
from contextmodel.models import ContextModel
from django.core.exceptions import ValidationError

class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField() 
    dqmodel_version = models.ForeignKey(DQModel, on_delete=models.CASCADE, null=True, blank=True)
    
    #context_version = models.ForeignKey(ContextModel, on_delete=models.CASCADE, null=True, blank=True)
    context_version = models.IntegerField(null=True, blank=True)  
    
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
                raise ValidationError("No se puede cambiar 'dqmodel_version' una vez asignado.")
            if original.context_version is not None and self.context_version != original.context_version:
                raise ValidationError("No se puede cambiar 'context_version' una vez asignado.")
        super().save(*args, **kwargs)




# PRIORITIZED DQ PROBLEMS
# Enumerado para los tipos de prioridad
class PriorityType(models.TextChoices):
    HIGH = 'High', 'High'
    MEDIUM = 'Medium', 'Medium'
    LOW = 'Low', 'Low'

class PrioritizedDQProblem(models.Model):
    dq_problem_id = models.IntegerField() 
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='prioritized_dq_problems')

    priority = models.CharField(max_length=10, choices=PriorityType.choices, default=PriorityType.MEDIUM)
    
    is_selected = models.BooleanField(default=False)  # if added to DQ Model
    #dq_model = models.ForeignKey(DQModel, on_delete=models.CASCADE, related_name='prioritized_dq_problems') 

    def __str__(self):
        return f"Prioritized DQ Problem {self.id} (Priority: {self.priority}, Selected: {self.is_selected})"

