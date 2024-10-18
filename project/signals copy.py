from django.db.models.signals import post_save
from django.dispatch import receiver
from dqmodel.models import DQModel
from .models import Project

@receiver(post_save, sender=DQModel)
def update_project_stage_and_status(sender, instance, created, **kwargs):
    """
    Actualiza el stage y status del Project asociado cuando un DQModel cambia su estado.
    """
    # Buscar el Project asociado a este DQModel
    try:
        project = Project.objects.get(dqmodel_version=instance)
    except Project.DoesNotExist:
        # Si no existe un Project asociado, no hacer nada
        return

    # Definir las actualizaciones basadas en el estado del DQModel
    if instance.status == 'draft':
        new_stage = 4
        new_status = 'in_progress'
    elif instance.status == 'finished':
        new_stage = 4
        new_status = 'done'
    else:
        # Opcional: Manejar otros estados si existen
        return

    # Actualizar el Project
    project.stage = new_stage
    project.status = new_status
    project.save()
