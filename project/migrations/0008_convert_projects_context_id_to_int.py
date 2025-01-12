from django.db import migrations, models

def convert_fk_to_integer(apps, schema_editor):
    # Obtén el modelo Project
    Project = apps.get_model('project', 'Project')
    
    # Recorre todos los registros y copia los datos del antiguo campo FK al nuevo campo IntegerField
    for project in Project.objects.all():
        if project.context_version_id is not None:
            project.context_version_temp = project.context_version_id
        project.save()

class Migration(migrations.Migration):

    dependencies = [
        ('project', '0007_update_projects_status_values_2'),  # Cambia por la dependencia real
    ]

    operations = [
        # Crear un campo temporal como IntegerField
        migrations.AddField(
            model_name='project',
            name='context_version_temp',
            field=models.IntegerField(null=True, blank=True),
        ),
        
        # Ejecutar la conversión de datos
        # migrations.RunPython(convert_fk_to_integer),
        
        # Eliminar el campo antiguo (clave foránea)
        migrations.RemoveField(
            model_name='project',
            name='context_version',
        ),
        
        # Renombrar el campo temporal al nombre original
        migrations.RenameField(
            model_name='project',
            old_name='context_version_temp',
            new_name='context_version',
        ),
    ]
