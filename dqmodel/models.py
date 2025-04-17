import uuid
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import JSONField  # Django 3.1 y versiones posteriores
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
    
class DQModel(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('finished', 'Finished'),
    ]
    version = models.CharField(max_length=100)  # identificador de versión del DQModel
    created_at = models.DateTimeField(auto_now_add=True)
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
    )
    finished_at = models.DateTimeField(null=True, blank=True, editable=False) 

    # Relación de versiones anteriores y siguientes
    previous_version = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='next_versions'
    )

    def __str__(self):
        return self.version

    #evitar que se cambie el estado de un DQModel ya finalizado.
    def save(self, *args, **kwargs):
        # Obtener el estado anterior si el objeto ya existe
        if self.pk:
            previous = DQModel.objects.get(pk=self.pk)
            previous_status = previous.status
        else:
            previous_status = None

        # Si el estado cambia de 'draft' a 'finished' y finished_at no está asignado
        if previous_status == 'draft' and self.status == 'finished' and not self.finished_at:
            self.finished_at = timezone.now()

        super().save(*args, **kwargs)

    def clean(self):
        # Validación para asegurar que no se puede modificar un DQModel finalizado
        if self.pk:
            existing = DQModel.objects.get(pk=self.pk)
            if existing.status == 'finished' and self.status != 'finished':
                raise ValidationError("No se puede cambiar el estado de un DQModel finalizado.")


# DIMENSIONS, FACTORS, METRICS and METHODS preset
class DQDimensionBase(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Ej. "Accuracy"
    semantic = models.TextField()  # Descripción general de la dimensión.

    def __str__(self):
        return self.name


class DQFactorBase(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Ej. "Completeness"
    semantic = models.TextField()  # Descripción general del factor.

    facetOf = models.ForeignKey(DQDimensionBase, on_delete=models.CASCADE, related_name='factors', null=True, blank=True)

    def __str__(self):
        return self.name


class DQMetricBase(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Ej. "Mean Absolute Error"
    purpose = models.TextField()  # Objetivo de la métrica.
    granularity = models.CharField(max_length=100)  # Granularidad de los datos.
    resultDomain = models.CharField(max_length=100)  # Dominio de resultados.

    measures = models.ForeignKey(DQFactorBase, on_delete=models.CASCADE, related_name='metrics', null=True, blank=True)

    def __str__(self):
        return self.name


class DQMethodBase(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Ej. "Regression Analysis"
    inputDataType = models.CharField(max_length=100)  # Tipo de dato de entrada.
    outputDataType = models.CharField(max_length=100)  # Tipo de dato de salida.
    algorithm = models.TextField()  # Descripción del algoritmo.

    implements = models.ForeignKey(DQMetricBase, on_delete=models.CASCADE, related_name='methods', null=True, blank=True)

    def __str__(self):
        return self.name


# Modelos de asociación para mantener las relaciones jerárquicas específicas de cada DQModel.
class DQModelDimension(models.Model):
    dq_model = models.ForeignKey(DQModel, on_delete=models.CASCADE, related_name='model_dimensions')
    dimension_base = models.ForeignKey(DQDimensionBase, on_delete=models.CASCADE, related_name='model_dimensions')
    
    
    context_components = models.JSONField(default=list, blank=True)
    """
        "context_components": {
            "userType": [],
            "otherData": [],
            "dqMetadata": [5],
            "taskAtHand": [],
            "businessRule": [],
            "dataFiltering": [4, 3],
            "dqRequirement": [],
            "otherMetadata": [],
            "applicationDomain": [1],
            "systemRequirement": []
        }
    """
    dq_problems = models.JSONField(default=list, blank=True)
    

    def __str__(self):
        return f"{self.dimension_base.name} en {self.dq_model.version}"


class DQModelFactor(models.Model):
    dq_model = models.ForeignKey(DQModel, on_delete=models.CASCADE, related_name='model_factors')
    factor_base = models.ForeignKey(DQFactorBase, on_delete=models.CASCADE, related_name='model_factors')
    dimension = models.ForeignKey(
        DQModelDimension, 
        on_delete=models.CASCADE, 
        null=True,
        related_name='factors',
        editable=False  
    )
    
    context_components = models.JSONField(default=list, blank=True)
    
    dq_problems = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"{self.factor_base.name} en {self.dq_model.version} bajo {self.dimension.dimension_base.name if self.dimension else 'sin dimensión'}"
    """
    def clean(self):
        super().clean()
        if self.factor_base.facetOf:
            try:
                self.dimension = DQModelDimension.objects.get(
                    dq_model=self.dq_model,
                    dimension_base=self.factor_base.facetOf
                )
            except DQModelDimension.DoesNotExist:
                raise ValidationError(
                    f"No existe una dimensión en el modelo {self.dq_model.version} "
                    f"para el factor base {self.factor_base.name} "
                    f"(debería estar asociado a {self.factor_base.facetOf.name})"
                )
    """
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class DQModelMetric(models.Model):
    dq_model = models.ForeignKey(DQModel, on_delete=models.CASCADE, related_name='model_metrics')
    metric_base = models.ForeignKey(DQMetricBase, on_delete=models.CASCADE, related_name='model_metrics')
    factor = models.ForeignKey(
        DQModelFactor, 
        on_delete=models.CASCADE, 
        related_name='metrics',
        editable=False  # Hacemos el campo no editable
    )
    
    context_components = models.JSONField(default=list, blank=True)
        
    
    def __str__(self):
        return f"{self.metric_base.name} en {self.dq_model.version} bajo {self.factor.factor_base.name}"

    def clean(self):
        super().clean()
        if self.metric_base.measures:
            try:
                self.factor = DQModelFactor.objects.get(
                    dq_model=self.dq_model,
                    factor_base=self.metric_base.measures
                )
            except DQModelFactor.DoesNotExist:
                raise ValidationError(
                    f"No existe un factor en el modelo {self.dq_model.version} "
                    f"para la métrica base {self.metric_base.name} "
                    f"(debería estar asociado a {self.metric_base.measures.name})"
                )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class DQModelMethod(models.Model):
    dq_model = models.ForeignKey(DQModel, on_delete=models.CASCADE, related_name='model_methods')
    method_base = models.ForeignKey(DQMethodBase, on_delete=models.CASCADE, related_name='model_methods')
    metric = models.ForeignKey(
        DQModelMetric, 
        on_delete=models.CASCADE, 
        related_name='methods',
        editable=False  # Hacemos el campo no editable
    )
    
    context_components = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"{self.method_base.name} en {self.dq_model.version} bajo {self.metric.metric_base.name}"

    def clean(self):
        super().clean()
        if self.method_base.implements:
            try:
                self.metric = DQModelMetric.objects.get(
                    dq_model=self.dq_model,
                    metric_base=self.method_base.implements
                )
            except DQModelMetric.DoesNotExist:
                raise ValidationError(
                    f"No existe una métrica en el modelo {self.dq_model.version} "
                    f"para el método base {self.method_base.name} "
                    f"(debería estar asociado a {self.method_base.implements.name})"
                )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class AppliedDQMethod(models.Model):
    name = models.CharField(max_length=100)
    
    appliedTo = JSONField() # Almacena tabla y columna con sus identificadores en un objeto JSON o lista de objetos JSON
    # appliedTo = models.CharField(max_length=100)  # Atributos del esquema de datos a los que se aplica el método.
    associatedTo = models.ForeignKey(DQModelMethod, on_delete=models.CASCADE, related_name='%(class)s_applied_methods')  # Método DQ al que está asociado.
    
    algorithm = models.TextField(default="", blank=False)  #implementation

    class Meta:
        abstract = True

    def __str__(self):
        return f"METH{self.associatedTo.id}-{self.appliedTo}"


class MeasurementDQMethod(AppliedDQMethod):
    pass


class AggregationDQMethod(AppliedDQMethod):
    pass


# PRIORITIZED DQ PROBLEMS
# Enumerado para los tipos de prioridad
class PriorityType(models.TextChoices):
    HIGH = 'High', 'High'
    MEDIUM = 'Medium', 'Medium'
    LOW = 'Low', 'Low'

class PrioritizedDqProblem(models.Model):
    dq_model = models.ForeignKey(DQModel, related_name='prioritized_problems', on_delete=models.CASCADE)
    description = models.CharField(max_length=100)
    
    priority = models.IntegerField(default=-1)  # Prioridad numerica
    priority_type = models.CharField(max_length=6, choices=PriorityType.choices, default=PriorityType.MEDIUM)

    date = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)  # Fecha de creacion automatica
    
    is_selected = models.BooleanField(default=False) # Se agrego al DQ Model

    def __str__(self):
        return f"DQ Problem: {self.description} - Priority {self.priority_type}"

    class Meta:
        unique_together = ('dq_model', 'description')  # Asegura que no haya duplicados de problemas dentro de un DQModel
        


# EXECUTION ---------------------------

class DQModelExecution(models.Model):
    execution_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    #dq_model = models.ForeignKey(DQModel, on_delete=models.CASCADE, related_name='executions')
    dq_model_id = models.IntegerField()  # Cambiado de ForeignKey a IntegerField
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, default='in_progress')  # in_progress/completed/failed
    
    class Meta:
        db_table = 'dq_modelexecution'  # Opcional: personaliza nombre de tabla
        managed = True 
    
    @property
    def dq_model(self):
        """Acceso al modelo relacionado en la base 'default'"""
        from dqmodel.models import DQModel
        return DQModel.objects.using('default').get(pk=self.dq_model_id)
    

class DQMethodExecutionResult(models.Model):
    execution = models.ForeignKey(DQModelExecution, on_delete=models.CASCADE, related_name='method_results')

    # applied method id 
    content_type = models.ForeignKey(
        'contenttypes.ContentType',
        on_delete=models.CASCADE,
        db_constraint=False  # para evitar problemas entre bases de datos
    )
    object_id = models.PositiveIntegerField()
    applied_method = GenericForeignKey('content_type', 'object_id') 
    
    executed_at = models.DateTimeField(auto_now_add=True)

    dq_value = models.JSONField(default=dict)
    #result_type = models.CharField(
    #    max_length=20, 
    #    default='single',
    #    choices=[('single', 'Single'), ('multiple', 'Multiple')]
    #)
    result_type = models.CharField(max_length=20, default='single')  # 'single' (aggregated) o 'multiple'
    details = models.JSONField(default=dict)
    
    # Campos para DQ assessment
    assessment_thresholds = models.JSONField(default=list, blank=True)  # Almacena los umbrales definidos
    #assessment_score = models.CharField(max_length=100, null=True, blank=True)  # Cambiado de evaluation_score
    assessed_at = models.DateTimeField(null=True, blank=True)  # Cambiado de evaluated_at
    #is_passing = models.BooleanField(null=True, blank=True)
    
    class Meta:
        db_table = 'dq_method_execution_result'  # Opcional
        managed = True
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['execution']),
        ]
        
    @property
    def resolved_applied_method(self):
        """Resuelve el método aplicado desde la base correcta"""
        model_class = self.content_type.model_class()
        return model_class.objects.using('default').get(pk=self.object_id)
    
    def assess(self, thresholds=None):
        """
        Evalúa el resultado contra los umbrales proporcionados o los almacenados
        """
        if thresholds:
            self.assessment_thresholds = thresholds
        
        if not self.assessment_thresholds:
            raise ValueError("No assessment thresholds defined")
        
        value = self.dq_value
        self.assessed_at = timezone.now()
        
        for threshold in self.assessment_thresholds:
            if threshold['min'] <= value <= threshold['max']:
                self.assessment_score = threshold['name']
                #self.is_passing = threshold.get('is_passing', True)
                self.save()
                return True
        
        self.assessment_score = 'Not Assessed'
        #self.is_passing = False
        self.save()
        return False


class ExecutionTableResult(models.Model):
    """Resultados a nivel de tabla"""
    #id = models.AutoField(primary_key=True)
    execution_result = models.ForeignKey(
        'DQMethodExecutionResult', 
        on_delete=models.CASCADE,
        related_name='table_results'
    )
    table_id = models.IntegerField()
    table_name = models.CharField(max_length=255)
    
    #dq_value = models.JSONField()  
    dq_value = models.FloatField(null=True, blank=True)
    
    executed_at = models.DateTimeField(auto_now_add=True)
    
    assessment_score = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['table_id']),
            models.Index(fields=['execution_result']),
        ]
        
    # Función para evaluar el resultado contra los thresholds
    def assess_result(self):
        thresholds = self.execution_result.assessment_thresholds
        value = self.dq_value

        if thresholds is None or value is None:
            self.assessment_score = None
            return

        for threshold in thresholds:
            if threshold['min'] <= value <= threshold['max']:
                self.assessment_score = threshold['name']
                break
        else:
            self.assessment_score = 'Not Assessed'

        self.save()


class ExecutionColumnResult(models.Model):
    """Resultados a nivel de columna"""
    #id = models.AutoField(primary_key=True)
    execution_result = models.ForeignKey(
        'DQMethodExecutionResult',
        on_delete=models.CASCADE,
        related_name='column_results'
    )
    table_id = models.IntegerField()
    table_name = models.CharField(max_length=255)
    column_id = models.IntegerField()
    column_name = models.CharField(max_length=255)
    
    #dq_value = models.JSONField()  
    dq_value = models.FloatField(null=True, blank=True)
    
    executed_at = models.DateTimeField(auto_now_add=True)
    
    
    assessment_score = models.CharField(max_length=100, null=True, blank=True)

    # Función para evaluar el resultado contra los thresholds
    def assess_result(self):
        thresholds = self.execution_result.assessment_thresholds
        value = self.dq_value

        if thresholds is None or value is None:
            self.assessment_score = None
            return

        for threshold in thresholds:
            if threshold['min'] <= value <= threshold['max']:
                self.assessment_score = threshold['name']
                break
        else:
            self.assessment_score = 'Not Assessed'

        self.save()


    class Meta:
        indexes = [
            models.Index(fields=['column_id']),
            models.Index(fields=['table_id', 'column_id']),
        ]

class ExecutionRowResult(models.Model):
    """Resultados a nivel de fila"""
    #id = models.AutoField(primary_key=True)
    execution_result = models.ForeignKey(
        'DQMethodExecutionResult',
        on_delete=models.CASCADE,
        related_name='row_results'
    )
    applied_method_id = models.IntegerField()  # ID del método aplicado
    table_id = models.IntegerField()
    table_name = models.CharField(max_length=255)
    column_id = models.IntegerField(null=True, blank=True)
    column_name = models.CharField(max_length=255, blank=True)
    row_id = models.CharField(max_length=255)  # ID original de la fila
    
    #dq_value = models.JSONField()
    dq_value = models.FloatField(null=True, blank=True)
    
    executed_at = models.DateTimeField(auto_now_add=True)
    
    assessment_score = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['row_id']),
            models.Index(fields=['table_id', 'row_id']),
            models.Index(fields=['applied_method_id']),
        ]
        
    # Función para evaluar el resultado contra los thresholds
    def assess_result(self):
        thresholds = self.execution_result.assessment_thresholds
        value = self.dq_value

        if thresholds is None or value is None:
            self.assessment_score = None
            return

        for threshold in thresholds:
            if threshold['min'] <= value <= threshold['max']:
                self.assessment_score = threshold['name']
                break
        else:
            self.assessment_score = 'Not Assessed'

        self.save()
