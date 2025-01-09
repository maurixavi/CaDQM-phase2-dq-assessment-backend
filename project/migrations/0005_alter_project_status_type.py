from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('project', '0004_alter_project_dqmodel_version_alter_project_stage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='stage',
            field=models.CharField(
                max_length=3,  # Longitud máxima para etapas como 'ST1'
                choices=[('ST1', 'Stage 1'), ('ST2', 'Stage 2'), ('ST3', 'Stage 3'), ('ST4', 'Stage 4'), ('ST5', 'Stage 5'), ('ST6', 'Stage 6')],
                default='ST4'  # Por defecto en 'ST4'
            ),
        ),
    ]


