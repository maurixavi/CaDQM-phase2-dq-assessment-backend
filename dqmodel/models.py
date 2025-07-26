import uuid
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import JSONField  # Django 3.1 y versiones posteriores
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


# ---------------------------------------------------------------
# DQModel
# ---------------------------------------------------------------

class DQModel(models.Model):
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('finished', 'Finished'),
    ]
    
    name = models.CharField(max_length=100) 
    version = models.CharField(max_length=20, blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
    )
    finished_at = models.DateTimeField(null=True, blank=True, editable=False) 

    # Relación de versiones
    previous_version = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='next_versions'
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Asignar versión 1.0.0 por defecto si es la primera versión
        if self.previous_version is None and not self.version:
            self.version = "1.0.0"
            
        # Obtener el estado anterior si el objeto ya existe
        if self.pk:
            previous = DQModel.objects.get(pk=self.pk)
            previous_status = previous.status
        else:
            previous_status = None

        # Actualizar finished_at si el estado cambia de 'draft' a 'finished'
        if previous_status == 'draft' and self.status == 'finished' and not self.finished_at:
            self.finished_at = timezone.now()

        super().save(*args, **kwargs)

    def clean(self):
        # Validación: no se puede modificar un DQModel finalizado
        if self.pk:
            existing = DQModel.objects.get(pk=self.pk)
            if existing.status == 'finished' and self.status != 'finished':
                raise ValidationError("No se puede cambiar el estado de un DQModel finalizado.")


# ---------------------------------------------------------------
# Modelos Base para Dimensiones, Factores, Métricas y Métodos
# ---------------------------------------------------------------

class DQDimensionBase(models.Model):
    """
    Modelo base para dimensiones de calidad de datos.
    """
    name = models.CharField(max_length=100, unique=True) 
    semantic = models.TextField() 
    
    is_disabled = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class DQFactorBase(models.Model):
    """
    Modelo base para factores de calidad de datos.
    Representa características específicas dentro de una dimensión.
    """
    name = models.CharField(max_length=100, unique=True)
    semantic = models.TextField() 
    
    is_disabled = models.BooleanField(default=False)

    # Relación con dimension
    facetOf = models.ForeignKey(DQDimensionBase, on_delete=models.CASCADE, related_name='factors', null=True, blank=True)

    def __str__(self):
        return self.name


class DQMetricBase(models.Model):
    """
    Modelo base para métricas de calidad de datos.
    Define cómo medir un factor específico.
    """
    name = models.CharField(max_length=100, unique=True) 
    purpose = models.TextField() 
    granularity = models.CharField(max_length=100)  
    resultDomain = models.CharField(max_length=100) 
    
    is_disabled = models.BooleanField(default=False)

    # Relación con factor
    measures = models.ForeignKey(DQFactorBase, on_delete=models.CASCADE, related_name='metrics', null=True, blank=True)

    def __str__(self):
        return self.name


class DQMethodBase(models.Model):
    """
    Modelo base para métodos de calidad de datos.
    Implementación concreta de cómo calcular una métrica.
    """
    name = models.CharField(max_length=100, unique=True) 
    inputDataType = models.CharField(max_length=100) 
    outputDataType = models.CharField(max_length=100) 
    algorithm = models.TextField() 
    
    is_disabled = models.BooleanField(default=False)

    implements = models.ForeignKey(DQMetricBase, on_delete=models.CASCADE, related_name='methods', null=True, blank=True)

    def __str__(self):
        return self.name


# ---------------------------------------------------------------
# Asociación Artefactos Base al DQModel
# ---------------------------------------------------------------
class DQModelDimension(models.Model):
    """
    Asocia una dimensión base con un DQModel específico.
    """
    dq_model = models.ForeignKey(DQModel, on_delete=models.CASCADE, related_name='model_dimensions')
    dimension_base = models.ForeignKey(DQDimensionBase, on_delete=models.CASCADE, related_name='model_dimensions')
    
    # Componentes de Contexto asociados (Estructura Category:Id) 
    context_components = models.JSONField(default=list, blank=True)
    # Example:
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
    # Problemas de Calidad asociados (Estructura Id:Description) 
    dq_problems = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"{self.dimension_base.name} - {self.dq_model.name} v{self.dq_model.version}"


class DQModelFactor(models.Model):
    """
    Asocia un factor base con un DQModel específico.
    Relacionado con una dimensión del modelo.
    """
    dq_model = models.ForeignKey(DQModel, on_delete=models.CASCADE, related_name='model_factors')
    factor_base = models.ForeignKey(DQFactorBase, on_delete=models.CASCADE, related_name='model_factors')
    
    # Relacion con dimension en DQ Model
    dimension = models.ForeignKey(
        DQModelDimension, 
        on_delete=models.CASCADE, 
        null=True,
        related_name='factors',
        editable=False  
    )
    
    # Componentes de Contexto y Problemas de Calidad asociados 
    context_components = models.JSONField(default=list, blank=True)
    dq_problems = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"{self.factor_base.name} - {self.dq_model.name} v{self.dq_model.version} - facet Of {self.dimension.dimension_base.name if self.dimension else 'sin dimensión'}"

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class DQModelMetric(models.Model):
    """
    Asocia una métrica base con un DQModel específico.
    Relacionado con un factor del modelo.
    """
    dq_model = models.ForeignKey(DQModel, on_delete=models.CASCADE, related_name='model_metrics')
    metric_base = models.ForeignKey(DQMetricBase, on_delete=models.CASCADE, related_name='model_metrics')
    
    # Relacion con factor en DQ Model
    factor = models.ForeignKey(
        DQModelFactor, 
        on_delete=models.CASCADE, 
        related_name='metrics',
        editable=False 
    )
    
    # Componentes de Contexto asociados 
    context_components = models.JSONField(default=list, blank=True)
        
    def __str__(self):
        return f"{self.metric_base.name} - {self.dq_model.name} {self.dq_model.version} - measures {self.factor.factor_base.name}"

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
    """
    Asocia un método base con un DQModel específico.
    Relacionado con una métrica del modelo.
    """
    dq_model = models.ForeignKey(DQModel, on_delete=models.CASCADE, related_name='model_methods')
    method_base = models.ForeignKey(DQMethodBase, on_delete=models.CASCADE, related_name='model_methods')
    
    # Relacion con metrica en DQ Model
    metric = models.ForeignKey(
        DQModelMetric, 
        on_delete=models.CASCADE, 
        related_name='methods',
        editable=False  
    )
    
    # Componentes de Contexto asociados 
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


# ---------------------------------------------------------------
# Métodos Aplicados
# ---------------------------------------------------------------
class AppliedDQMethod(models.Model):
    """
    Clase abstracta que representa un método de calidad del DQ Model aplicado a un data at hand especifico.
    """
    name = models.CharField(max_length=100)
    algorithm = models.TextField(default="", blank=False)  
    
    # Identificadores y detalles de Table y Column del Data Schema del Data at Hand sobre los que se aplica el metodo
    appliedTo = JSONField() 
    
    # Método en DQ Model aplicado
    associatedTo = models.ForeignKey(
        DQModelMethod, 
        on_delete=models.CASCADE, 
        related_name='%(class)s_applied_methods'
    )
    
    class Meta:
        abstract = True

    def __str__(self):
        return f"METH{self.associatedTo.id}-{self.appliedTo}"

class MeasurementDQMethod(AppliedDQMethod):
    """Método de tipo Medición aplicado"""
    pass

class AggregationDQMethod(AppliedDQMethod):
    """Método de tipo Agregación aplicado"""
    pass


# ---------------------------------------------------------------
# DQ Metadata: Ejecución de DQ Models
# ---------------------------------------------------------------

class DQModelExecution(models.Model):
    """
    Registro de ejecución de un DQ Model.
    """
    execution_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # IntegerField en lugar de FK pues DB distintas
    dq_model_id = models.IntegerField()  
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, default='in_progress')  # in_progress/completed/failed
    
    class Meta:
        db_table = 'dq_modelexecution'
        managed = True 
    
    @property
    def dq_model(self):
        """Acceso al modelo relacionado en la base 'default'"""
        from dqmodel.models import DQModel
        return DQModel.objects.using('default').get(pk=self.dq_model_id)
    

class DQMethodExecutionResult(models.Model):
    """
    Resultados de la ejecución de un método de calidad aplicado.
    """
    # Id Ejecucion DQ Model asociado
    execution = models.ForeignKey(DQModelExecution, on_delete=models.CASCADE, related_name='method_results')

    # Campos para relación genérica con el método aplicado
    # Tipo del método aplicado (MeasurementDQMethod o AggregationDQMethod)
    content_type = models.ForeignKey(
        'contenttypes.ContentType',
        on_delete=models.CASCADE,
        db_constraint=False  # evitar problemas entre bases de datos
    )
    # Id del método aplicado
    object_id = models.PositiveIntegerField()
    applied_method = GenericForeignKey('content_type', 'object_id') 
    
    # DQ measurement
    executed_at = models.DateTimeField(auto_now_add=True)
    dq_value = models.JSONField(default=dict)
    result_type = models.CharField(max_length=20, default='single') # 'single' (ej: columna) o 'multiple' (ej: filas)
    details = models.JSONField(default=dict)
    
    # DQ assessment
    assessment_thresholds = models.JSONField(default=list, blank=True) 
    assessed_at = models.DateTimeField(null=True, blank=True) 
    
    class Meta:
        db_table = 'dq_method_execution_result' 
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
        Evalúa el resultado contra los umbrales definidos.
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
                self.save()
                return True
        
        self.assessment_score = 'Not Assessed'
        self.save()
        return False


class ExecutionTableResult(models.Model):
    """
    Resultados de ejecución a nivel de tabla.
    """
    # Id ejecucion metodo aplicado asociado
    execution_result = models.ForeignKey(
        'DQMethodExecutionResult', 
        on_delete=models.CASCADE,
        related_name='table_results'
    )
    table_id = models.IntegerField()
    table_name = models.CharField(max_length=255)
    
    # DQ measurement details
    executed_at = models.DateTimeField(auto_now_add=True)
    dq_value = models.FloatField(null=True, blank=True)
    
    # DQ assessment details
    assessment_score = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['table_id']),
            models.Index(fields=['execution_result']),
        ]
        
    def assess_result(self):
        """Evalúa el resultado contra los thresholds definidos"""
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
    """
    Resultados de ejecución a nivel de columna.
    """
    # Id ejecucion metodo aplicado asociado
    execution_result = models.ForeignKey(
        'DQMethodExecutionResult',
        on_delete=models.CASCADE,
        related_name='column_results'
    )
    table_id = models.IntegerField()
    table_name = models.CharField(max_length=255)
    column_id = models.IntegerField()
    column_name = models.CharField(max_length=255)
    
    # DQ measurement details
    executed_at = models.DateTimeField(auto_now_add=True)
    dq_value = models.FloatField(null=True, blank=True)
    
    # DQ assessment details
    assessment_score = models.CharField(max_length=100, null=True, blank=True)

    def assess_result(self):
        """Evalúa el resultado contra los thresholds definidos"""
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
    """
    Resultados de ejecución a nivel de fila.
    """
    # Id ejecucion metodo aplicado asociado
    execution_result = models.ForeignKey(
        'DQMethodExecutionResult',
        on_delete=models.CASCADE,
        related_name='row_results'
    )
    applied_method_id = models.IntegerField()
    table_id = models.IntegerField()
    table_name = models.CharField(max_length=255)
    column_id = models.IntegerField(null=True, blank=True)
    column_name = models.CharField(max_length=255, blank=True)
    row_id = models.CharField(max_length=255) 
    
    # DQ measurement details
    executed_at = models.DateTimeField(auto_now_add=True)
    dq_value = models.FloatField(null=True, blank=True)
    
    # DQ assessment details
    assessment_score = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['row_id']),
            models.Index(fields=['table_id', 'row_id']),
            models.Index(fields=['applied_method_id']),
        ]

    def assess_result(self):
        """Evalúa el resultado contra los thresholds definidos"""
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
