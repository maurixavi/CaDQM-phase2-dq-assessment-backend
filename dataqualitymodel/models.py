from django.db import models
from django.utils import timezone
#from project.models import Project 


class DQModel(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('finished', 'Finished'),
    ]
    
    version = models.CharField(max_length=100) #The version that identifies the DQ model.
    created_at = models.DateTimeField(auto_now_add=True) 
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
    )
    finished_at = models.DateTimeField(null=True, blank=True)
    #context_version = models.ForeignKey(ContextModel, on_delete=models.CASCADE, null=True, blank=True) 
    #project_in = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='dq_models')
    #project = models.ForeignKey('project.Project', on_delete=models.CASCADE, null=True, blank=True, related_name='dq_models')


    def __str__(self):
        return self.version
    
    def save(self, *args, **kwargs):
        if self.status == 'finished' and not self.finished_at:
            self.finished_at = timezone.now()
        super().save(*args, **kwargs)

class DQDimension(models.Model):
    name = models.CharField(max_length=100)
    semantic = models.TextField() #The type of DQ problem the DQ dimension addresses.
    dIn = models.ForeignKey(DQModel, on_delete=models.CASCADE, related_name='dimensions') #The DQ model versions to which it belongs.

    def __str__(self):
        return f"D{self.id}: {self.name}"

class DQFactor(models.Model):
    name = models.CharField(max_length=100)
    semantic = models.TextField() #The DQ factor semantic, more specific than the one recorded for the corresponding DQ dimension.
    facetOf = models.ForeignKey(DQDimension, on_delete=models.CASCADE, related_name='factors') #The DQ dimension to which it refers
    #The DQ model versions to which it belongs:
    fIn = models.ForeignKey(DQModel, on_delete=models.CASCADE, related_name='factors') #The DQ model versions to which it belongs.

    def __str__(self):
        return f"F{self.id}: {self.name}"

class DQMetric(models.Model):
    name = models.CharField(max_length=100)
    purpose = models.TextField() #The measurement objective.
    granularity = models.CharField(max_length=100) #The data granularity to which the measure is associated, and is strongly dependent on the data model (e.g. in the relational model, it could be table, attribute, tuple or value). 
    resultDomain = models.CharField(max_length=100)
    
    measures = models.ForeignKey(DQFactor, on_delete=models.CASCADE, related_name='metrics') #The DQ factor that it measures.
   
    mIn = models.ForeignKey(DQModel, on_delete=models.CASCADE, related_name='metrics') #The DQ model versions to which it belongs.

    def __str__(self):
        return f"M{self.id}: {self.name}"

class DQMethod(models.Model):
    name = models.CharField(max_length=100)
    inputDataType = models.CharField(max_length=100) #Data type expected as input parameters.
    outputDataType = models.CharField(max_length=100) #Data type expected as output parameters.
    
    algorithm = models.TextField()
    
    implements = models.ForeignKey(DQMetric, on_delete=models.CASCADE, related_name='methods') #The DQ metric that it implements.

    mtIn = models.ForeignKey(DQModel, on_delete=models.CASCADE, related_name='methods') #The DQ model versions to which it belongs.

    def __str__(self):
        return f"METH{self.id}: {self.name}"

class AppliedDQMethod(models.Model):
    name = models.CharField(max_length=100)
    # type = models.CharField(max_length=100) #Applied method type (measurement OR aggregation).
    
    appliedTo = models.CharField(max_length=100) #Data schema attributes on which the method is applied.
    
    associatedTo = models.ForeignKey(DQMethod, on_delete=models.CASCADE, related_name='%(class)s_applied_methods')  #The DQ method to which it is associated.

    # associatedTo = models.ForeignKey(DQMethod, on_delete=models.CASCADE, related_name='applied_methods')
    
    class Meta:
        abstract = True
    
    def __str__(self):
        return f"METH{self.associatedTo.id}-{self.appliedTo}"

class MeasurementDQMethod(AppliedDQMethod):
    pass

class AggregationDQMethod(AppliedDQMethod):
    pass