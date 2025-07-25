from django.db import models
from dqmodel.models import DQModel
from contextmodel.models import ContextModel
from django.core.exceptions import ValidationError
from django.db import models

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save


class User(AbstractUser):
    type = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)

    groups = models.ManyToManyField(
        Group, related_name="custom_user_groups", blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission, related_name="custom_user_permissions", blank=True
    )

    class Meta:
        db_table = "user"


# ---------------------------------------------------------------
# Data At Hand & Data Schema
# ---------------------------------------------------------------
#def validate_database_type(value):
#    """
#    Valida que el tipo de base de datos sea soportado.
#    Tipos soportados: postgresql, mysql, sqlite, oracle
#    """
#    supported_types = ['postgresql', 'mysql', 'sqlite', 'oracle']
#    if value not in supported_types:
#        raise ValidationError(f"Unsupported database type: {value}. Supported types are: {', '.join(supported_types)}")


import psycopg2

class DataAtHand(models.Model):
    """
    Modelo que representa una conexión a una base de datos.
    Almacena los parámetros de conexión y metadatos.
    """
    name = models.CharField(max_length=255, verbose_name="Database Name")
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Database Description"
    )
    date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Database Date",
        help_text="Fecha real cuando se creó la base de datos (no cuando se registró aquí)"
    )
    
    url_db = models.CharField(max_length=255, verbose_name="Database URL or Host")
    user_db = models.CharField(max_length=255, verbose_name="Database User")
    pass_db = models.CharField(max_length=255, verbose_name="Database Password")
    
    port = models.IntegerField(
        default=5432, # PostgreSQL default port 
        blank=True,
        null=True,
        verbose_name="Port"
    )
    
    DB_TYPES = (
        ('postgresql', 'PostgreSQL'),
        ('mysql', 'MySQL'),
        ('sqlite', 'SQLite'),
        ('oracle', 'Oracle'),
        ('mssql', 'SQL Server'),
        ('other', 'Other'), 
    )

    type = models.CharField(
        max_length=50,
        choices=DB_TYPES,
        default='postgresql',
        verbose_name="Database Type"
    )
    
    class Meta:
        db_table = "data_at_hand"

    def __str__(self):
        return f"{self.name} ({self.type})"

    def create_initial_schema(self):
        try:
            connection = psycopg2.connect(
                dbname=self.name,
                user=self.user_db,
                password=self.pass_db,
                host=self.url_db,
                port=self.port or 5432
            )
            schema = self.get_database_schema(connection)
            connection.close()

            data_schema = DataSchema.objects.create(
                data_at_hand=self,
                schema=schema
            )
        except Exception as e:
            print(f"⚠️ Error en create_initial_schema: {e}")
            DataSchema.objects.create(data_at_hand=self, schema={})

    def get_tables_info(self, connection):
        """
        Retrieve detailed information about tables in the database.
        """
        cursor = connection.cursor()
        cursor.execute("""
            SELECT 
                t.oid as table_id,
                t.relname as table_name,
                n.nspname as schema_name
            FROM 
                pg_class t
                JOIN pg_namespace n ON n.oid = t.relnamespace
            WHERE 
                t.relkind = 'r'
                AND n.nspname = 'public';
        """)
        tables = cursor.fetchall()
        return tables
    
    def get_database_schema(self, connection):
        """
        Retrieve database schema as a structured list of tables with columns.
        """
        try:
            tables = self.get_tables_info(connection)
            schema = []
            
            for table_info in tables:
                table_id = table_info[0]
                table_name = table_info[1]
                
                columns = self.get_table_columns_enhanced(connection, table_name)
                
                # Create structured table information
                table_data = {
                    "table_id": table_id,
                    "table_name": table_name,
                    "columns": columns
                }
                
                schema.append(table_data)

            return schema

        except Exception as e:
            raise e

    def get_table_columns_enhanced(self, connection, table_name):
        """
        Retrieve enhanced column information for a specific table.
        """
        cursor = connection.cursor()
        cursor.execute("""
            SELECT
                a.attnum as column_id,
                a.attname as column_name,
                format_type(a.atttypid, a.atttypmod) as data_type,
                a.attnotnull as is_required,
                CASE 
                    WHEN ct.contype = 'p' THEN TRUE 
                    ELSE FALSE 
                END as is_primary_key
            FROM
                pg_attribute a
                LEFT JOIN pg_constraint ct ON ct.conrelid = a.attrelid 
                    AND a.attnum = ANY(ct.conkey) AND ct.contype = 'p'
                JOIN pg_class c ON a.attrelid = c.oid
                JOIN pg_namespace n ON c.relnamespace = n.oid
            WHERE
                c.relname = %s
                AND a.attnum > 0
                AND NOT a.attisdropped
                AND n.nspname = 'public'
            ORDER BY a.attnum;
        """, (table_name,))
        
        columns = []
        for col in cursor.fetchall():
            columns.append({
                "column_id": col[0],
                "column_name": col[1],
                "data_type": col[2]
            })
        
        return columns



        
        
class DataSchema(models.Model):
    """
    Modelo que almacena el esquema de una base de datos.
    Relacionado 1:1 con DataAtHand.
    """
    data_at_hand = models.OneToOneField(
        DataAtHand,
        on_delete=models.CASCADE,
        related_name='data_schema'
    )
    
    schema = models.JSONField()  
    
    class Meta:
        db_table = "data_schema"
    
    def __str__(self):
        return f"Schema for {self.data_at_hand.name}"



# ---------------------------------------------------------------
# Project
# ---------------------------------------------------------------
class Project(models.Model):
    class Meta:
        #unique_together = ('context', 'dqmodel_version')
        db_table = "project"
    
    name = models.CharField(max_length=255)
    description = models.TextField() 
    created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now_add=True) 
    
    dqmodel_version = models.ForeignKey(
        DQModel, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects", null=True, blank=True)
    
    #context_version = models.IntegerField(null=True, blank=True) # DEFINICION ANTERIOR
    context = models.ForeignKey(
        "Context",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects",
    )
      
    data_at_hand = models.ForeignKey(DataAtHand, on_delete=models.CASCADE, null=True, blank=True)
    
    estimation = models.OneToOneField(
        "Estimation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="project",
    )

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Validación para campos que no deben cambiar una vez asignados
        if self.pk:
            original = Project.objects.get(pk=self.pk)
            # Solo validar si el campo no es null y está intentando cambiar
            #if original.dqmodel_version is not None and self.dqmodel_version != original.dqmodel_version:
            #    raise ValidationError("No se puede cambiar la version de DQ Model una vez asignado.")
            #if original.context is not None and self.context != original.context:
            #    raise ValidationError("No se puede cambiar la version de Contexto una vez asignado.")
        super().save(*args, **kwargs)
            
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
    
    def get_stage(self, stage_code):
        """Obtiene un stage específico"""
        return self.stages.filter(stage=stage_code).first()


class ProjectStage(models.Model):
    class Meta:
        db_table = "project_stage"
        unique_together = ('project', 'stage')
        ordering = ['stage']

    class Stage(models.TextChoices):
        ST1 = "ST1", _("ST1")
        ST2 = "ST2", _("ST2")
        ST3 = "ST3", _("ST3")
        ST4 = "ST4", _("ST4")  # Stage por defecto en Fase 2
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
    
    def __str__(self):
        return f"{self.project.name} - {self.get_stage_display()} ({self.get_status_display()})"


# ---------------------------------------------------------------
# Context
# ---------------------------------------------------------------
class Context(models.Model):
    class Meta:
        db_table = "context"

    name = models.CharField(max_length=255)
    version = models.CharField(max_length=50)
    previous_version = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="next_versions",
    )
    context_components = models.ManyToManyField(
        "ContextComponent", related_name="related_contexts"
    )


class ContextComponent(models.Model):
    class Meta:
        db_table = "context_component"

    project_stage = models.ForeignKey(
        "ProjectStage",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="context_components",
    )
    

class OtherData(ContextComponent):
    class Meta:
        db_table = "other_data"

    path = models.CharField(max_length=255)
    description = models.TextField()
    owner = models.CharField(max_length=255)


class DQMetadata(ContextComponent):
    class Meta:
        db_table = "dq_metadata"

    path = models.CharField(max_length=255)
    description = models.TextField()
    measurement = models.TextField()


class OtherMetadata(ContextComponent):
    class Meta:
        db_table = "other_metadata"

    path = models.CharField(max_length=255)
    description = models.TextField()
    author = models.CharField(max_length=255)
    last_update = models.DateTimeField(auto_now=True)


class TaskAtHand(ContextComponent):
    class Meta:
        db_table = "task_at_hand"

    name = models.CharField(max_length=255)
    purpose = models.TextField()
    other_data = models.ManyToManyField(
        OtherData, related_name="tasks_at_hand", blank=True
    )
    user_types = models.ManyToManyField(
        "UserType", related_name="tasks_at_hand", blank=True
    )
    system_requirements = models.ManyToManyField(
        "SystemRequirement", related_name="tasks_at_hand", blank=True
    )


class ApplicationDomain(ContextComponent):
    class Meta:
        db_table = "application_domain"

    description = models.TextField()


class BusinessRule(ContextComponent):
    class Meta:
        db_table = "business_rule"

    statement = models.TextField()
    semantic = models.TextField()


class DQRequirement(ContextComponent):
    class Meta:
        db_table = "dq_requirement"

    statement = models.TextField()
    description = models.TextField()
    data_filtering = models.ManyToManyField(
        "DataFiltering", related_name="dq_requirements", blank=True
    )
    user_type = models.ForeignKey(
        "UserType",
        on_delete=models.CASCADE,
        related_name="dq_requirements",
        null=True,
        blank=True,
    )


class DataFiltering(ContextComponent):
    class Meta:
        db_table = "data_filtering"

    statement = models.TextField()
    description = models.TextField()
    task_at_hand = models.ForeignKey(
        "TaskAtHand",
        on_delete=models.CASCADE,
        related_name="data_filterings",
        null=True,
        blank=True,
    )


class SystemRequirement(ContextComponent):
    class Meta:
        db_table = "system_requirement"

    statement = models.TextField()
    description = models.TextField()


class UserType(ContextComponent):
    class Meta:
        db_table = "user_type"

    name = models.CharField(max_length=255)
    characteristics = models.TextField()


class UserData(models.Model):
    class Meta:
        db_table = "user_data"

    name = models.CharField(max_length=255)
    description = models.TextField()
    user_type = models.ForeignKey(
        "UserType", on_delete=models.CASCADE, related_name="user_data"
    )



# ---------------------------------------------------------------
# DQ Problems
# ---------------------------------------------------------------
 
class QualityProblem(models.Model):
    class Meta:
        db_table = "quality_problem"

    description = models.TextField()
    date = models.DateField() # YYYY-MM-DD
    reviews = models.ManyToManyField("Review", related_name="related_quality_problems", blank=True)


class PriorityType(models.TextChoices):
    HIGH = 'High', 'High'
    MEDIUM = 'Medium', 'Medium'
    LOW = 'Low', 'Low'


class QualityProblemProject(models.Model):
    class Meta:
        db_table = "quality_problem_project"
        unique_together = ("quality_problem", "project")

    quality_problem = models.ForeignKey(
        QualityProblem,
        on_delete=models.CASCADE,
        related_name="problem_projects",
        #db_column="dq_problem_id"  
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="project_problems"
    )
    priority = models.CharField(max_length=10, choices=PriorityType.choices, default=PriorityType.MEDIUM)
    is_selected = models.BooleanField(default=False)



# PRIORITIZED DQ PROBLEMS

#class PrioritizedDQProblem(models.Model):
 #   dq_problem_id = models.IntegerField() 
    
 #   project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='prioritized_dq_problems', db_column='project_id')
#
#    priority = models.CharField(max_length=10, choices=PriorityType.choices, default=PriorityType.MEDIUM)
#    
#    is_selected = models.BooleanField(default=False)  # if added to DQ Model

#    def __str__(self):
#        return f"Prioritized DQ Problem {self.id} (Priority: {self.priority}, Selected: {self.is_selected})"


# ---------------------------------------------------------------
# Phase 1 only 
# ---------------------------------------------------------------
class Review(models.Model):
    class Meta:
        db_table = "review"

    type = models.CharField(max_length=50)
    created_at = models.DateField()
    data = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        UserData,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviews",
    )
    project = models.ForeignKey(
        "Project", on_delete=models.CASCADE, related_name="reviews",
        null=True,
        blank=True,
    )
    context_components = models.ManyToManyField(
        "ContextComponent", related_name="reviews", blank=True
    )
    quality_problems = models.ManyToManyField(
        "QualityProblem", related_name="related_reviews", blank=True
    )
    rejected_suggestions = models.TextField(blank=True, null=True)

class DataProfiling(models.Model):
    class Meta:
        db_table = "data_profiling"

    description = models.TextField()
    type = models.CharField(max_length=50)
    result = models.JSONField()
    date = models.DateTimeField()
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="data_profilings",
        null=True,
        blank=True,
    )
    context_components = models.ManyToManyField(
        "ContextComponent", related_name="data_profilings", blank=True
    )


class FileType(models.Model):
    class Meta:
        db_table = "file_type"

    type = models.TextField(blank=True, null=True)


class UploadedFile(models.Model):
    class Meta:
        db_table = "uploaded_file"

    file = models.FileField(upload_to="uploads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    analysis = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    review = models.ForeignKey(
        "Review", on_delete=models.CASCADE, related_name="uploaded_files"
    )

    file_type = models.ForeignKey(
        FileType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_files",
    )


class Estimation(models.Model):
    class Meta:
        db_table = "estimation"

    result = models.JSONField()
    manual_facts = models.JSONField(default=list, blank=True)
    date = models.DateField(auto_now_add=True)
