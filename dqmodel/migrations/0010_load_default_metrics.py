from django.db import migrations

def load_default_metrics(apps, schema_editor):
    # Obtiene el modelo de las dimensiones desde el apps registry.
    DQFactorBase = apps.get_model('dqmodel', 'DQFactorBase')
    DQMetricBase = apps.get_model('dqmodel', 'DQMetricBase')

    # Crear las metricas asociadas a cada factor
    metrics_base = [ 
        {"name": "Real-world Matching Ratio", 
        "purpose": "Proportion of data matching real-world entities or states.", 
        "granularity": "Record or attribute", 
        "result_domain": "[0, 1]", 
        "factor": "Semantic Accuracy"},

        {"name": "Entity Accuracy Score", 
        "purpose": "Measure how accurate data is in representing specific entities.", 
        "granularity": "Entity", 
        "result_domain": "Numeric range", 
        "factor": "Semantic Accuracy"},

        {"name": "Syntax Error Rate", 
        "purpose": "Proportion of syntactic errors detected in the data.", 
        "granularity": "Attribute or record", 
        "result_domain": "[0, 1]", 
        "factor": "Syntactic Accuracy"},

        {"name": "Conformance Score", 
        "purpose": "Degree of data conformance with defined syntactic rules.", 
        "granularity": "Entire dataset", 
        "result_domain": "[0, 1]", 
        "factor": "Syntactic Accuracy"},

        {"name": "Detail Level Score", 
        "purpose": "Measures whether the level of detail in the data is appropriate for its purpose.", 
        "granularity": "Attribute", 
        "result_domain": "Boolean", 
        "factor": "Precision"},

        {"name": "Rounding Error Rate", 
        "purpose": "Proportion of errors caused by rounding in numeric values.", 
        "granularity": "Attribute or value", 
        "result_domain": "[0, 1]", 
        "factor": "Precision"},

        {"name": "Data Density Ratio", 
        "purpose": "Proportion of data entries present compared to the total possible.", 
        "granularity": "Dataset or table", 
        "result_domain": "[0, 1]", 
        "factor": "Density"},

        {"name": "Null Value Percentage", 
        "purpose": "Proportion of null values in the dataset.", 
        "granularity": "Dataset or column", 
        "result_domain": "[0, 1]", 
        "factor": "Density"},

        {"name": "Domain Coverage Ratio", 
        "purpose": "Extent to which the data covers the required domain.", 
        "granularity": "Dataset", 
        "result_domain": "[0, 1]", 
        "factor": "Coverage"},

        {"name": "Attribute Coverage Score", 
        "purpose": "Proportion of key attributes covered in the data.", 
        "granularity": "Attribute", 
        "result_domain": "[0, 1]", 
        "factor": "Coverage"},

        {"name": "Data Age", 
        "purpose": "Average time since the last update of the data.", 
        "granularity": "Record", 
        "result_domain": "Numeric range (in days, hours, etc.)", 
        "factor": "Currency"},

        {"name": "Update Frequency", 
        "purpose": "Frequency of updates made to the data.", 
        "granularity": "Dataset", 
        "result_domain": "Integer", 
        "factor": "Currency"},

        {"name": "Availability Delay", 
        "purpose": "Time from need to availability of data.", 
        "granularity": "Record", 
        "result_domain": "Numeric range", 
        "factor": "Timeliness"},

        {"name": "On-time Data Ratio", 
        "purpose": "Proportion of data available on time relative to the total.", 
        "granularity": "Dataset", 
        "result_domain": "[0, 1]", 
        "factor": "Timeliness"},

        {"name": "Change Rate", 
        "purpose": "Rate of change in the data over time.", 
        "granularity": "Attribute or record", 
        "result_domain": "[0, 1]", 
        "factor": "Volatility"},

        {"name": "Stability Index", 
        "purpose": "Index measuring data stability over a period.", 
        "granularity": "Dataset", 
        "result_domain": "Numeric range", 
        "factor": "Volatility"},

        {"name": "Range Conformance Ratio", 
        "purpose": "Proportion of values falling within the defined range.", 
        "granularity": "Attribute or value", 
        "result_domain": "[0, 1]", 
        "factor": "Domain Integrity"},

        {"name": "Outlier Percentage", 
        "purpose": "Proportion of values outside the defined range.", 
        "granularity": "Attribute or value", 
        "result_domain": "[0, 1]", 
        "factor": "Domain Integrity"},

        {"name": "Constraint Satisfaction Ratio", 
        "purpose": "Proportion of intra-relational constraints satisfied.", 
        "granularity": "Dataset", 
        "result_domain": "[0, 1]", 
        "factor": "Intra-relationship Integrity"},

        {"name": "Error Count", 
        "purpose": "Number of violations of intra-relational constraints.", 
        "granularity": "Dataset", 
        "result_domain": "Integer", 
        "factor": "Intra-relationship Integrity"},

        {"name": "Cross-dataset Consistency Ratio", 
        "purpose": "Proportion of inter-dataset relationships that are consistent.", 
        "granularity": "Multiple datasets", 
        "result_domain": "[0, 1]", 
        "factor": "Inter-relationship Integrity"},

        {"name": "Inter-dataset Error Count", 
        "purpose": "Number of inconsistencies between datasets.", 
        "granularity": "Dataset or record", 
        "result_domain": "Integer", 
        "factor": "Inter-relationship Integrity"},

        {"name": "Duplicate Entry Count", 
        "purpose": "Number of duplicate entries in the dataset.", 
        "granularity": "Dataset", 
        "result_domain": "Integer", 
        "factor": "No-duplication"},

        {"name": "Unique Entry Ratio", 
        "purpose": "Proportion of unique entries relative to the total.", 
        "granularity": "Dataset", 
        "result_domain": "[0, 1]", 
        "factor": "No-duplication"},

        {"name": "Contradiction Detection Count", 
        "purpose": "Number of contradictions detected in the data.", 
        "granularity": "Dataset or record", 
        "result_domain": "Integer", 
        "factor": "No-contradiction"},

        {"name": "Consistency Ratio", 
        "purpose": "Proportion of data free from contradictions relative to the total.", 
        "granularity": "Dataset", 
        "result_domain": "[0, 1]", 
        "factor": "No-contradiction"},
    ]



    
    # Crear los factores asociados a cada dimensión
    for metric in metrics_base:
        # Get factor id as measures fk for the metric
        try:
            factor = DQFactorBase.objects.get(name=metric['factor'] + " (preset)")
        except DQFactorBase.DoesNotExist:
            factor = None
        
        # Crear el factor y asociarlo a la dimensión mediante facetOf
        DQMetricBase.objects.create(
            name=metric['name'],
            purpose=metric['purpose'],
            granularity=metric['granularity'],
            resultDomain=metric['result_domain'],
            measures=factor
        )


class Migration(migrations.Migration):

    dependencies = [
        ('dqmodel', '0009_load_default_dimensions'),
    ]

    operations = [
        migrations.RunPython(load_default_metrics),
    ]
