# project/signals.py
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from dqmodel.models import DQModel, DQModelExecution
from .models import PrioritizedDQProblem, Project, ProjectStage
from django.conf import settings
import requests
from django.db import transaction

import logging
import traceback


logger = logging.getLogger(__name__)

@receiver(post_save, sender=Project)
def initialize_project_stages(sender, instance, created, **kwargs):
    if created:
        instance.initialize_stages()


# Diccionario para almacenar el estado anterior de dqmodel_version por Project.pk
_previous_dqmodel_version = {}

@receiver(pre_save, sender=Project)
def store_previous_dqmodel_version(sender, instance, **kwargs):
    """
    Señal pre_save para almacenar la versión anterior de dqmodel_version.
    """
    if instance.pk:
        try:
            previous = Project.objects.get(pk=instance.pk)
            _previous_dqmodel_version[instance.pk] = previous.dqmodel_version
        except Project.DoesNotExist:
            _previous_dqmodel_version[instance.pk] = None
    else:
        _previous_dqmodel_version[instance.pk] = None

@receiver(post_save, sender=Project)
def update_project_on_dqmodel_assignment(sender, instance, created, **kwargs):
    """
    Señal post_save para actualizar stage y status al asignar o cambiar dqmodel_version.
    """
    if instance.pk:
        previous_dqmodel = _previous_dqmodel_version.get(instance.pk)
        current_dqmodel = instance.dqmodel_version

        # Si es una creación o dqmodel_version ha cambiado
        if created or previous_dqmodel != current_dqmodel:
            if current_dqmodel:
                if current_dqmodel.status == 'draft':
                    new_stage = 'ST4'
                    new_status = 'in_progress'
                    stage = ProjectStage.Stage.ST4
                    stage_status = ProjectStage.Status.IN_PROGRESS
                elif current_dqmodel.status == 'finished':
                    new_stage = 'ST4'
                    new_status = 'done'
                    stage = ProjectStage.Stage.ST4
                    stage_status = ProjectStage.Status.DONE
                else:
                    # Manejar otros estados si existen
                    return

                # Actualizar el Project sin disparar señales nuevamente
                Project.objects.filter(pk=instance.pk).update(stage=new_stage, status=new_status)
                
                # Actualizar ProjectStage correspondiente
                stage_obj = instance.get_stage(new_stage)
                if stage_obj:
                    stage_obj.stage = stage
                    stage_obj.status = stage_status
                    stage_obj.save()

    # Limpiar el diccionario después de procesar
    if instance.pk in _previous_dqmodel_version:
        del _previous_dqmodel_version[instance.pk]

@receiver(post_save, sender=DQModel)
def update_project_stage_and_status(sender, instance, created, **kwargs):
    """
    Señal post_save para actualizar stage y status del Project cuando DQModel cambia de estado.
    """
    try:
        project = Project.objects.get(dqmodel_version=instance)
    except Project.DoesNotExist:
        # No hay Project asociado; no hacer nada
        return

    # Definir las actualizaciones basadas en el estado actual de DQModel
    if instance.status == 'draft':
        new_stage = 'ST4'
        new_status = 'in_progress'
        stage = ProjectStage.Stage.ST4
        stage_status = ProjectStage.Status.IN_PROGRESS
    elif instance.status == 'finished':
        new_stage = 'ST4'
        new_status = 'done'
        stage = ProjectStage.Stage.ST4
        stage_status = ProjectStage.Status.DONE
    else:
        # Manejar otros estados si existen
        return

    # Actualizar el Project sin disparar señales nuevamente
    Project.objects.filter(pk=project.pk).update(stage=new_stage, status=new_status)
    
    # Actualizar ProjectStage correspondiente
    stage_obj = project.get_stage(new_stage)
    if stage_obj:
        stage_obj.stage = stage
        stage_obj.status = stage_status
        stage_obj.save()


@receiver(post_save, sender=DQModelExecution)
def update_stage5_on_execution(sender, instance, **kwargs):
    """
    Actualiza ST5 del proyecto según las ejecuciones del DQModel.
    Si hay al menos una ejecución completada → ST5 = DONE.
    Si no hay completadas pero hay alguna activa → ST5 = IN_PROGRESS.
    """
    dq_model_id = instance.dq_model_id

    try:
        project = Project.objects.get(dqmodel_version_id=dq_model_id)
    except Project.DoesNotExist:
        logger.warning(f"[ST5 Update] No se encontró un Project asociado a dq_model_id={dq_model_id}")
        return

    try:
        executions = DQModelExecution.objects.using('metadata_db').filter(dq_model_id=dq_model_id)

        has_completed = executions.filter(completed_at__isnull=False).exists()
        has_active = executions.filter(completed_at__isnull=True).exists()

        new_status = None
        if has_completed:
            new_status = ProjectStage.Status.DONE
        elif has_active:
            new_status = ProjectStage.Status.IN_PROGRESS

        if new_status:
            stage5 = project.get_stage('ST5')
            if stage5 and stage5.status != new_status:
                logger.info(f"[ST5 Update] Actualizando ST5 para el proyecto '{project.name}' a estado '{new_status}'")
                stage5.status = new_status
                stage5.save()
            else:
                logger.debug(f"[ST5 Update] ST5 ya está en estado '{new_status}' o no existe.")
    except Exception as e:
        logger.error(f"[ST5 Update] Error al actualizar ST5 para dq_model_id={dq_model_id}: {str(e)}", exc_info=True)


# --------------
# DQ PROBLEMS
# --------------
@receiver(post_save, sender=Project)
def initialize_prioritized_problems(sender, instance, created, **kwargs):
    """
    Señal que se activa después de guardar un proyecto.
    Si el proyecto se acaba de crear, inicializa los problemas priorizados.
    """
    if created:
        # Retrasar la inicialización hasta que la transacción se complete
        transaction.on_commit(lambda: _initialize_prioritized_problems(instance, created))


"""
transaction.on_commit: Retrasa la ejecución de _initialize_prioritized_problems hasta que la transacción de base de datos se complete con éxito.

_initialize_prioritized_problems: Realiza la inicialización de los problemas priorizados.
"""

def _initialize_prioritized_problems(instance, created):
    """
    Función que inicializa los problemas priorizados para un proyecto.
    """
    if created:
        # Construir la URL del endpoint usando el ID del proyecto
        endpoint_path = f'/api/projects/{instance.id}/dq-problems/'
        url = f'{settings.BASE_URL}{endpoint_path}'
        
        try:
            # Hacer una solicitud GET al endpoint
            response = requests.get(url)
            response.raise_for_status()  # Lanza una excepción si la solicitud no fue exitosa
            
            # Obtener los datos JSON
            dq_problems = response.json()
            
            # Extraer los IDs de los problemas
            dq_problem_ids = [problem['id'] for problem in dq_problems]
            
            # Crear un PrioritizedDQProblem para cada dq_problem_id
            for dq_problem_id in dq_problem_ids:
                PrioritizedDQProblem.objects.create(
                    dq_problem_id=dq_problem_id,
                    priority='Medium',  # Prioridad por defecto
                    is_selected=False,  # No seleccionado por defecto
                    project_id=instance.id  # Asocia el problema priorizado con el proyecto recién creado
                )
        
        except requests.RequestException as e:
            # Manejar errores de solicitud
            print(f"Error al obtener los problemas de calidad: {e}")
