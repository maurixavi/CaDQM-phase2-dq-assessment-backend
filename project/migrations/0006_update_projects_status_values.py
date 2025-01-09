from django.db import migrations

def migrate_stage_values(apps, schema_editor):
    Project = apps.get_model('project', 'Project')
    # Aquí deberás mapear los valores antiguos (enteros) a los nuevos valores (strings)
    for project in Project.objects.all():
        if project.stage == "1":
            project.stage = 'ST1'
        elif project.stage == "2":
            project.stage = 'ST2'
        elif project.stage == "3":
            project.stage = 'ST3'
        elif project.stage == "4":
            project.stage = 'ST4'
        elif project.stage == "5":
            project.stage = 'ST5'
        elif project.stage == "6":
            project.stage = 'ST6'
        # Aquí podrías agregar más condiciones si es necesario
        project.save()

class Migration(migrations.Migration):

    dependencies = [
        ('project', '0005_alter_project_status_type'),
    ]

    operations = [
        migrations.RunPython(migrate_stage_values),
    ]


