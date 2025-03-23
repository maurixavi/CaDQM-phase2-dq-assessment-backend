from django.db import models
from dqmodel.models import DQModel
from contextmodel.models import ContextModel
from django.core.exceptions import ValidationError
from django.db import models


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


# DATA AT HAND
def validate_database_type(value):
    """
    Validates that the database type is supported.
    """
    supported_types = ['postgresql', 'mysql', 'sqlite', 'oracle']
    if value not in supported_types:
        raise ValidationError(f"Unsupported database type: {value}. Supported types are: {', '.join(supported_types)}")

class DataAtHand(models.Model):
    # Essential parameters (required fields)
    dbname = models.CharField(max_length=255, verbose_name="Database Name")
    user = models.CharField(max_length=255, verbose_name="User")
    password = models.CharField(max_length=255, verbose_name="Password")
    host = models.CharField(max_length=255, verbose_name="Host")

    # Optional parameters (can be blank or null)
    port = models.IntegerField(
        default=5432,  # Default port for PostgreSQL
        blank=True,    # Allows the field to be blank in forms
        null=True,     # Allows the field to be NULL in the database
        verbose_name="Port"
    )
    description = models.TextField(
        blank=True,   # Allows the field to be blank in forms
        null=True,    # Allows the field to be NULL in the database
        verbose_name="Description"
    )
    type = models.CharField(
        max_length=50,
        default='postgresql',  # Default database type
        validators=[validate_database_type],  # Custom validator
        verbose_name="Database Type"
    )

    def __str__(self):
        return f"{self.dbname} ({self.type})"

    def get_connection_string(self):
        """
        Generates a connection string based on the database type.
        """
        if self.type == 'postgresql':
            return f"dbname='{self.dbname}' user='{self.user}' password='{self.password}' host='{self.host}' port='{self.port}'"
        elif self.type == 'mysql':
            return f"mysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}"
        elif self.type == 'sqlite':
            return f"sqlite:///{self.dbname}"
        elif self.type == 'oracle':
            return f"oracle://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}"
        else:
            raise ValueError(f"Unsupported database type: {self.type}")
        
        
