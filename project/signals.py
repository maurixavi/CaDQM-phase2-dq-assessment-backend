import logging
import traceback
import requests

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.db import transaction
from django.conf import settings

from dqmodel.models import DQMethodExecutionResult, DQModel, DQModelExecution
from .models import PrioritizedDQProblem, Project, ProjectStage

logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# STAGES INITIALIZATION
# ---------------------------------------------------------
@receiver(post_save, sender=Project)
def initialize_project_stages(sender, instance, created, **kwargs):
    """
    Señal post_save que inicializa las etapas (stages) del proyecto cuando se crea.
    """
    if created:
        instance.initialize_stages()


# ---------------------------------------------------------
# TRACK PREVIOUS dqmodel_version TO DETECT CHANGES
# ---------------------------------------------------------

# Diccionario para almacenar el estado anterior del dqmodel_version
_previous_dqmodel_version = {}

@receiver(pre_save, sender=Project)
def store_previous_dqmodel_version(sender, instance, **kwargs):
    """
    Señal pre_save para guardar la versión anterior del dqmodel asociado al Project
    """
    if instance.pk:
        try:
            previous = Project.objects.get(pk=instance.pk)
            _previous_dqmodel_version[instance.pk] = previous.dqmodel_version
        except Project.DoesNotExist:
            _previous_dqmodel_version[instance.pk] = None
    else:
        _previous_dqmodel_version[instance.pk] = None


# ---------------------------------------------------------
# UPDATE STAGE 4 WHEN DQModel STATUS CHANGES
# ---------------------------------------------------------
@receiver(post_save, sender=Project)
def update_project_on_dqmodel_assignment(sender, instance, created, **kwargs):
    """
    Señal post_save que actualiza el estado y etapa del Project si se asigna o cambia
    dqmodel_version
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
                    return  # Otros estados no gestionados

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
    Señal post_save que sincroniza el estado del proyecto (ST4) según el estado del DQModel.
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
        return

    # Actualizar el Project sin disparar señales nuevamente
    Project.objects.filter(pk=project.pk).update(stage=new_stage, status=new_status)
    
    # Actualizar ProjectStage correspondiente
    stage_obj = project.get_stage(new_stage)
    if stage_obj:
        stage_obj.stage = stage
        stage_obj.status = stage_status
        stage_obj.save()


# ---------------------------------------------------------
# UPDATE STAGE 5 BASED ON EXECUTIONS OF DQModel
# ---------------------------------------------------------
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


# ---------------------------------------------------------
# UPDATE STAGE 6 BASED ON ASSESS_AT FIELD of DQMethodExecutionResult in DQModelExecution
# ---------------------------------------------------------
@receiver(post_save, sender=DQMethodExecutionResult)
def update_stage6_on_assessment(sender, instance, **kwargs):
    """
    Actualiza ST6 del proyecto si al menos un método del DQModelExecution ha sido evaluado (assessed).
    Si hay al menos un method con assessed_at → ST6 = IN_PROGRESS.
    """
    execution = instance.execution
    dq_model_id = execution.dq_model_id

    try:
        project = Project.objects.get(dqmodel_version_id=dq_model_id)
    except Project.DoesNotExist:
        logger.warning(f"[ST6 Update] No se encontró un Project asociado a dq_model_id={dq_model_id}")
        return

    try:
        # Verifica si hay al menos un método evaluado para esta ejecución
        assessed_exists = DQMethodExecutionResult.objects.using('metadata_db') \
            .filter(execution=execution, assessed_at__isnull=False).exists()

        if assessed_exists:
            stage6 = project.get_stage('ST6')
            if stage6 and stage6.status != ProjectStage.Status.IN_PROGRESS:
                logger.info(f"[ST6 Update] Actualizando ST6 para el proyecto '{project.name}' a IN_PROGRESS")
                stage6.status = ProjectStage.Status.IN_PROGRESS
                stage6.save()
            else:
                logger.debug(f"[ST6 Update] ST6 ya está en estado IN_PROGRESS o no existe.")
    except Exception as e:
        logger.error(f"[ST6 Update] Error al actualizar ST6 para dq_model_id={dq_model_id}: {str(e)}", exc_info=True)


@receiver(post_save, sender=DQMethodExecutionResult)
def update_stage6_on_assessment_done(sender, instance, **kwargs):
    """
    Actualiza el estado del ST6 del proyecto relacionado con la ejecución de métodos:
    - TO_DO: si ningún método fue evaluado.
    - IN_PROGRESS: si al menos uno fue evaluado.
    - DONE: si todos los métodos fueron evaluado.
    """
    execution = instance.execution
    dq_model_id = execution.dq_model_id

    try:
        project = Project.objects.get(dqmodel_version_id=dq_model_id)
    except Project.DoesNotExist:
        logger.warning(f"[ST6 Update] No se encontró un Project asociado al dq_model_id={dq_model_id}")
        return

    method_qs = execution.method_results.using('metadata_db')
    
    total = method_qs.count()
    assessed = method_qs.filter(assessed_at__isnull=False).count()

    if total == 0:
        return  # Nada que evaluar

    if assessed == 0:
        new_status = ProjectStage.Status.TO_DO
    elif assessed < total:
        new_status = ProjectStage.Status.IN_PROGRESS
    else:
        new_status = ProjectStage.Status.DONE

    stage6 = project.get_stage('ST6')
    if stage6 and stage6.status != new_status:
        logger.info(f"[ST6 Update] Actualizando ST6 del proyecto '{project.name}' a estado '{new_status}'")
        stage6.status = new_status
        stage6.save()


# ---------------------------------------------------------
# PRIORITIZED DQ PROBLEMS INITIALIZATION
# ---------------------------------------------------------
@receiver(post_save, sender=Project)
def initialize_prioritized_problems(sender, instance, created, **kwargs):
    """
    Señal post_save que inicializa los problemas priorizados cuando se crea un nuevo Project.
    Ejecuta la inicialización al final de la transacción con on_commit.
    """
    if created:
        # Retrasar la inicialización hasta que la transacción se complete
        transaction.on_commit(lambda: _initialize_prioritized_problems(instance, created))


def _initialize_prioritized_problems(instance, created):
    """
    Inicializa los problemas priorizados para un proyecto.
    Llama al endpoint de problemas de calidad para el proyecto y los guarda como PrioritizedDQProblem.
    """
    if created:
        # Construir la URL del endpoint usando el ID del proyecto
        endpoint_path = f'/api/projects/{instance.id}/dq-problems/'
        url = f'{settings.BASE_URL}{endpoint_path}'
        
        try:
            response = requests.get(url)
            response.raise_for_status()  
            dq_problems = response.json()
            dq_problem_ids = [problem['id'] for problem in dq_problems]
            
            # Crear un PrioritizedDQProblem para cada dq_problem_id
            for dq_problem_id in dq_problem_ids:
                PrioritizedDQProblem.objects.create(
                    dq_problem_id=dq_problem_id,
                    priority='Medium',      # Prioridad por defecto
                    is_selected=False,      # No seleccionado por defecto
                    project_id=instance.id  # Asocia el problema priorizado con el proyecto recién creado
                )
        
        except requests.RequestException as e:
            logger.error(f"[PrioritizedDQProblem] Error al obtener los problemas de calidad: {e}")
