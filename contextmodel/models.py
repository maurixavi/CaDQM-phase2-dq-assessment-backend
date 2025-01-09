from django.db import models
#from ..dataqualitymodel.models , DQDimension, DQFactor, DQMetric, DQMethod, MeasurementDQMethod, AggregationDQMethod
# from dataqualitymodel.models import DQModel
from dqmodel.models import DQModel

class ContextModel(models.Model):
    version = models.CharField(max_length=100) #The version that identifies the context model. Example: CTX_v1.0
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.version

class ApplicationDomain(models.Model):
    name = models.CharField(max_length=100)
    
    context_model = models.ForeignKey(ContextModel, on_delete=models.CASCADE, related_name='application_domains')

    def __str__(self):
        return f"appDom"

class BusinessRule(models.Model):
    statement = models.TextField()  # Business rule statement. e.g., ATB ∈ {“amika”, “vanco”, “genta”}
    semantic = models.TextField()  # Business rule description in natural language. e.g., The only drugs studied are three antibiotics. “amika”, “vanco”, OR “genta”
    context_model = models.ForeignKey(ContextModel, on_delete=models.CASCADE, related_name='business_rules')


    def __str__(self):
        return f"BR{self.id}"
  
class UserType(models.Model):
    name = models.CharField(max_length=100) # e.g., Collector
    characteristics = models.TextField() # The user type characteristics. e.g., Doctor
    context_model = models.ForeignKey(ContextModel, on_delete=models.CASCADE, related_name='user_types')

    def __str__(self):
        return f"UT{self.id}: {self.name}"

class TaskAtHand(models.Model):
    name = models.CharField(max_length=100) #e.g., Data Collection, Data Register, Data Analysis, etc.
    purpose = models.TextField() #e.g., Collect data to investigate drug effectiveness, Store data collected by doctors, Publish results obtained
    
    assignedTo = models.ManyToManyField(UserType, related_name='tasks_at_hand')  #The users types in charge of performing the task at hand.
    
    use = models.TextField(blank=True, null=True)  # Identifiers of other data involved in the task at hand.
		# use = models.ManyToManyField(OtherData, related_name='other_data') # Identifiers of other data involved in the task at hand. 
    context_model = models.ForeignKey(ContextModel, on_delete=models.CASCADE, related_name='tasks_at_hand')

		

    def __str__(self):
        return f"T{self.id}: {self.name}"


# REQUIREMENTS:
class DQRequirement(models.Model):
    statement = models.TextField() # e.g., 100% of tuples must satisfy non-null “date” attribute.

    description = models.TextField() #Information that complements the DQ requirement statement. e.g., The “date” attribute is associated with the dosage date
    
    imposed_by = models.ManyToManyField(UserType, related_name='dq_requirements')  # The users types that impose the DQ requirement.
    
    references = models.ManyToManyField('DataFiltering', related_name='referenced_by', blank=True)  # The identifiers of the data filtering requirements to which the DQ requirement refers. (e.g., N/A)
    context_model = models.ForeignKey(ContextModel, on_delete=models.CASCADE, related_name='dq_requirements')


    def __str__(self):
        return f"DF{self.id}"


class DataFiltering(models.Model):
    statement = models.TextField() #SELECT * FROM dosages WHERE Conc <> NULL

    description = models.TextField() # Information that complements the data filtering requirement statement. e.g., Select records that have data in the “Conc” column, which stores the drug concentration when the time of blood collection is unknown
    
    asigned_to = models.ManyToManyField(UserType, related_name='data_filtering_requirements')  # VA O NO VA??????????
    
    
    addressed_by = models.ForeignKey(TaskAtHand, on_delete=models.CASCADE, related_name='data_filtering_requirements') #The task at hand that addresses the data filtering requirement.
    context_model = models.ForeignKey(ContextModel, on_delete=models.CASCADE, related_name='data_filtering')


    def __str__(self):
        return f"DF{self.id}"

class SystemRequirement(models.Model):
    statement = models.TextField() #Have an Internet connection, Operating system Windows 10 or higher

    purpose = models.TextField() # ??? (distinto en la especificacion)   Download data collected by doctors
    
    imposed_by = models.ForeignKey(TaskAtHand, on_delete=models.CASCADE, related_name='system_requirements')  # The task at hand that imposes the system requirement.
    context_model = models.ForeignKey(ContextModel, on_delete=models.CASCADE, related_name='system_requirements')


    def __str__(self):
        return f"M{self.id}: {self.name}"
# end of REQUIREMENTS


# METADATA:
class DQMetadata(models.Model):
    path = models.TextField() #Path or website to the DQ metadata. 
    description = models.TextField() #DQ metadata description.
    describe = models.TextField()  # Identifier, URL, or website to the dataset described by the metadata.
    
    # The DQ model version that proposed the measurement whose result is the DQ metadata (if apply):
    measurement = models.ForeignKey(DQModel, on_delete=models.CASCADE, related_name='dq_metadata', blank=True, null=True)  # The DQ model version that proposed the measurement whose result is the DQ metadata (if applicable).
    context_model = models.ForeignKey(ContextModel, on_delete=models.CASCADE, related_name='dq_metadata', blank=True, null=True)




    def __str__(self):
        return f"DQM{self.id}"

class OtherMetadata(models.Model):
    path = models.TextField() # The path or website to the metadata.
    description = models.TextField() # Metadata description.
    author = models.TextField() # The author of the metadata using natural language or a URL.
    last_update = models.DateField() # The date of the last update.
    describe = models.TextField() # The identifier, URL, or website to the dataset described by the metadata.
    context_model = models.ForeignKey(ContextModel, on_delete=models.CASCADE, related_name='other_metadata')


    def __str__(self):
        return f"OM{self.id}"
      
# end of METADATA.


class OtherData(models.Model):
    path = models.TextField()  # The path to the database or website where the other data can be accessed.
    description = models.TextField()  # A brief description of the dataset.
    owner = models.TextField()  # The owner of the other data.
    context_model = models.ForeignKey(ContextModel, on_delete=models.CASCADE, related_name='other_data')


    def __str__(self):
        return f"OD{self.id}"


