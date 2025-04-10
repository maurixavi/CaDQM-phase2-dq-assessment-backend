from django.db import models
from dqmodel.models import DQModel
from contextmodel.models import ContextModel
from django.core.exceptions import ValidationError
from django.db import models

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
        
        
class DataSchema(models.Model):
    """
    Model to store the schema of a database.
    """
    data_at_hand = models.OneToOneField(
        DataAtHand,
        on_delete=models.CASCADE,
        related_name='data_schema'
    )
    schema = models.JSONField()  
    
    # el esquema de la base de datos podría cambiar si:
    # Se agregan o eliminan tablas.
    # Se modifican columnas (por ejemplo, se cambia el tipo de dato de una columna).
    # updated_at ayudaría a saber cuándo se detectó un cambio en el esquema.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Schema for {self.data_at_hand.dbname}"


class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField() 
    dqmodel_version = models.ForeignKey(DQModel, on_delete=models.CASCADE, null=True, blank=True)
    
    #context_version = models.ForeignKey(ContextModel, on_delete=models.CASCADE, null=True, blank=True)
    context_version = models.IntegerField(null=True, blank=True)  
    
    data_at_hand = models.ForeignKey(DataAtHand, on_delete=models.CASCADE, null=True, blank=True)
    
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
        # Validación para campos que no deben cambiar una vez asignados
        if self.pk:
            original = Project.objects.get(pk=self.pk)
            # Solo validar si el campo no es null y está intentando cambiar
            if original.dqmodel_version is not None and self.dqmodel_version != original.dqmodel_version:
                raise ValidationError("No se puede cambiar 'dqmodel_version' una vez asignado.")
            if original.context_version is not None and self.context_version != original.context_version:
                raise ValidationError("No se puede cambiar 'context_version' una vez asignado.")
        super().save(*args, **kwargs)
        
    #def initialize_stages(self):
    #    """
    #    Crea las 6 etapas del proyecto al crearlo
    #    ST4 se crea como etapa activa (To Do) por defecto
    #    """
    #    for stage_value in ProjectStage.Stage.values:
    #        status = ProjectStage.Status.TO_DO
    #        ProjectStage.objects.create(
    #            project=self,
    #            stage=stage_value,
    #            status=status #Todas las etapas se crean con status "To Do" por defecto
    #        )
    
    def initialize_stages(self):
        """
        Crea las 6 etapas del proyecto al crearlo:
        - ST1, ST2 y ST3 con status DONE (como si ya estuvieran completados)
        - ST4, ST5 y ST6 con status TO_DO
        - ST4 es la etapa activa inicial
        """
        for stage_value in ProjectStage.Stage.values:
            # Definir el status según la etapa
            if stage_value in ['ST1', 'ST2', 'ST3']:
                status = ProjectStage.Status.DONE
            else:
                status = ProjectStage.Status.TO_DO
            
            ProjectStage.objects.create(
                project=self,
                stage=stage_value,
                status=status
            )
        
        # Sincronizar campos legacy para mantener consistencia
        self.stage = 'ST4'
        self.status = 'to_do'
        self.save(update_fields=['stage', 'status'])
    
    @property
    def current_stage(self):
        """Devuelve el stage activo según esta prioridad:
        1. ST4 si existe (sin importar su estado)
        2. Cualquier stage con IN_PROGRESS
        3. El primer stage con TO_DO (ordenado por ST1, ST2, etc.)
        4. El último stage con DONE
        """
        # 1. ST4 inicialmente
        st4 = self.stages.filter(stage='ST4', status='TO_DO').first()
        if st4:
            return st4
        
        # 2. Cualquier stage en progreso
        in_progress = self.stages.filter(status='IN_PROGRESS').first()
        if in_progress:
            return in_progress
        
        # 3. Primer stage pendiente
        to_do = self.stages.filter(status='TO_DO').order_by('stage').first()
        if to_do:
            return to_do
        
        # 4. Último stage completado
        return self.stages.filter(status='DONE').order_by('-stage').first()

    #@property
    #def current_stage(self):
      #  return self.stages.filter(stage='ST4', status='TO_DO').first()
        #st4 = self.stages.filter(stage='ST4', status='TO_DO').first()
        #if st4:
        #    return st4

        #current = self.stages.filter(status='IN_PROGRESS').first()
        #if current:
         #   return current

        #current = self.stages.filter(status='TO_DO').order_by('stage').first()
        #if current:
         #   return current

        #return self.stages.filter(status='DONE').order_by('-stage').first()
    
    def get_stage(self, stage_code):
        """Obtiene un stage específico"""
        return self.stages.filter(stage=stage_code).first()

from django.utils.translation import gettext_lazy as _
#  _() es una función de internacionalización (i18n) de Django


class ProjectStage(models.Model):
    class Meta:
        db_table = "project_stage"
        unique_together = ('project', 'stage')
        ordering = ['stage']  # Orden natural por stage

    class Stage(models.TextChoices):
        ST1 = "ST1", _("ST1")
        ST2 = "ST2", _("ST2")
        ST3 = "ST3", _("ST3")
        ST4 = "ST4", _("ST4")  # Stage por defecto
        ST5 = "ST5", _("ST5")
        ST6 = "ST6", _("ST6")

    class Status(models.TextChoices):
        TO_DO = "TO_DO", _("To Do")
        IN_PROGRESS = "IN_PROGRESS", _("In Progress")
        DONE = "DONE", _("Done")

    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name="stages"
    )
    stage = models.CharField(max_length=100, choices=Stage.choices)
    status = models.CharField(
        max_length=50, 
        choices=Status.choices, 
        default=Status.TO_DO
    )
    
    class Meta:
        unique_together = ('project', 'stage')
        ordering = ['stage']

    def __str__(self):
        return f"{self.project.name} - {self.get_stage_display()} ({self.get_status_display()})"






# PRIORITIZED DQ PROBLEMS
class PriorityType(models.TextChoices):
    HIGH = 'High', 'High'
    MEDIUM = 'Medium', 'Medium'
    LOW = 'Low', 'Low'

class PrioritizedDQProblem(models.Model):
    dq_problem_id = models.IntegerField() 
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='prioritized_dq_problems', db_column='project_id')

    priority = models.CharField(max_length=10, choices=PriorityType.choices, default=PriorityType.MEDIUM)
    
    is_selected = models.BooleanField(default=False)  # if added to DQ Model

    def __str__(self):
        return f"Prioritized DQ Problem {self.id} (Priority: {self.priority}, Selected: {self.is_selected})"


