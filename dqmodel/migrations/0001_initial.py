# dqmodel/migrations/0001_initial.py
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone

#python manage.py migrate dqmodel 0001

class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='DQModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('version', models.CharField(blank=True, max_length=20, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('finished', 'Finished')], default='draft', max_length=10)),
                ('finished_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('previous_version', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='next_versions', to='dqmodel.dqmodel')),
            ],
        ),

        migrations.CreateModel(
            name='DQDimensionBase',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('semantic', models.TextField()),
                ('is_disabled', models.BooleanField(default=False)),
            ],
        ),

        migrations.CreateModel(
            name='DQFactorBase',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('semantic', models.TextField()),
                ('is_disabled', models.BooleanField(default=False)),
                ('facetOf', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='factors', to='dqmodel.dqdimensionbase')),
            ],
        ),

        migrations.CreateModel(
            name='DQMetricBase',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('purpose', models.TextField()),
                ('granularity', models.CharField(max_length=100)),
                ('resultDomain', models.CharField(max_length=100)),
                ('is_disabled', models.BooleanField(default=False)),
                ('measures', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='metrics', to='dqmodel.dqfactorbase')),
            ],
        ),

        migrations.CreateModel(
            name='DQMethodBase',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('inputDataType', models.CharField(max_length=100)),
                ('outputDataType', models.CharField(max_length=100)),
                ('algorithm', models.TextField()),
                ('is_disabled', models.BooleanField(default=False)),
                ('implements', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='methods', to='dqmodel.dqmetricbase')),
            ],
        ),

        migrations.CreateModel(
            name='DQModelDimension',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('context_components', models.JSONField(blank=True, default=list)),
                ('dq_problems', models.JSONField(blank=True, default=list)),
                ('dq_model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='model_dimensions', to='dqmodel.dqmodel')),
                ('dimension_base', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='model_dimensions', to='dqmodel.dqdimensionbase')),
            ],
        ),

        migrations.CreateModel(
            name='DQModelFactor',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('context_components', models.JSONField(blank=True, default=list)),
                ('dq_problems', models.JSONField(blank=True, default=list)),
                ('dimension', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='factors', to='dqmodel.dqmodeldimension')),
                ('dq_model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='model_factors', to='dqmodel.dqmodel')),
                ('factor_base', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='model_factors', to='dqmodel.dqfactorbase')),
            ],
        ),

        migrations.CreateModel(
            name='DQModelMetric',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('context_components', models.JSONField(blank=True, default=list)),
                ('dq_model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='model_metrics', to='dqmodel.dqmodel')),
                ('metric_base', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='model_metrics', to='dqmodel.dqmetricbase')),
                ('factor', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='metrics', to='dqmodel.dqmodelfactor')),
            ],
        ),

        migrations.CreateModel(
            name='DQModelMethod',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('context_components', models.JSONField(blank=True, default=list)),
                ('dq_model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='model_methods', to='dqmodel.dqmodel')),
                ('method_base', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='model_methods', to='dqmodel.dqmethodbase')),
                ('metric', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='methods', to='dqmodel.dqmodelmetric')),
            ],
        ),

        migrations.CreateModel(
            name='MeasurementDQMethod',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('algorithm', models.TextField()),
                ('appliedTo', models.JSONField()),
                ('associatedTo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='measurementdqmethod_applied_methods', to='dqmodel.dqmodelmethod')),
            ],
            options={'abstract': False},
        ),

        migrations.CreateModel(
            name='AggregationDQMethod',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('algorithm', models.TextField()),
                ('appliedTo', models.JSONField()),
                ('associatedTo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aggregationdqmethod_applied_methods', to='dqmodel.dqmodelmethod')),
            ],
            options={'abstract': False},
        ),
    ]
