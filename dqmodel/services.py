from datetime import timezone
import uuid
from .models import (
    DQMethodExecutionResult,
    DQModelExecution,
    ExecutionColumnResult,
    ExecutionRowResult,
    ExecutionTableResult,
    MeasurementDQMethod,
    AggregationDQMethod,
)
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

class DQExecutionResultService:
    
    @staticmethod
    @transaction.atomic(using='metadata_db')
    def get_or_create_execution(dq_model_id):
        """Obtiene o crea una ejecución activa en metadata_db"""
        # First try to get an existing in_progress execution
        execution = DQModelExecution.objects.using('metadata_db').filter(
            dq_model_id=dq_model_id,
            status='in_progress'
        ).first()
        
        if execution:
            return execution, False
        
        # If no in_progress execution exists, create a new one
        execution = DQModelExecution.objects.using('metadata_db').create(
            dq_model_id=dq_model_id,
            status='in_progress',
            execution_id=uuid.uuid4()
        )
        return execution, True

    @staticmethod
    @transaction.atomic(using='metadata_db')
    def get_or_create_execution__(dq_model_id):
        """Obtiene o crea una ejecución activa en metadata_db"""
        execution, created = DQModelExecution.objects.using('metadata_db').get_or_create(
            dq_model_id=dq_model_id,
            status='in_progress',
            defaults={'execution_id': uuid.uuid4()}
        )
        return execution
      
    @staticmethod
    def _get_content_type_for_model(model, using='default'):
        """Obtiene el ContentType usando la base de datos especificada"""
        return ContentType.objects.db_manager(using).get_for_model(model)
    

    @staticmethod
    @transaction.atomic(using='metadata_db')
    def save_execution_result(dq_model_id, applied_method, result_value, execution_details, result_type=None):
        """
        Versión que:
        1. Para resultados únicos: guarda solo el valor en dq_value
        2. Para resultados múltiples: guarda en dq_value la estructura completa con rows
        3. Mantiene metadata en details
        4. Guarda filas individuales en ExecutionRowResult
        """
        #execution = DQExecutionResultService.get_or_create_execution(dq_model_id)
        execution, created = DQExecutionResultService.get_or_create_execution(dq_model_id)
        content_type = ContentType.objects.db_manager('default').get_for_model(applied_method)
        
        # Determinar tipo de resultado si no se proporcionó
        if result_type is None:
            if isinstance(result_value, dict) and 'rows' in result_value:
                result_type = 'multiple'
            elif isinstance(result_value, list):
                result_type = 'multiple'
            else:
                result_type = 'single'
        
        # Preparar datos comunes
        applied_to = applied_method.appliedTo or []
        tables_info = []
        columns_info = []
        
        for item in applied_to:
            if isinstance(item, dict):
                if 'table_id' in item:
                    tables_info.append({
                        'table_id': item['table_id'],
                        'table_name': item.get('table_name', '')
                    })
                if 'column_id' in item:
                    columns_info.append({
                        'column_id': item['column_id'],
                        'column_name': item.get('column_name', ''),
                        'data_type': item.get('data_type', '')
                    })
        
        # Eliminar duplicados
        tables_info = [dict(t) for t in {tuple(d.items()) for d in tables_info}]
        columns_info = [dict(c) for c in {tuple(d.items()) for d in columns_info}]

        if result_type == 'single':
            # Caso 1: Resultado único
            value = result_value.get('value') if isinstance(result_value, dict) else result_value
            
            # Guardar en tabla principal
            result = DQMethodExecutionResult.objects.using('metadata_db').create(
                execution=execution,
                content_type=content_type,
                object_id=applied_method.id,
                result_type=result_type,
                dq_value=value,  # Solo el valor numérico
                details={
                    **execution_details,
                    'applied_to': applied_to,
                    'columns': execution_details.get('columns', [])
                }
            )
            
            # Opcional: Guardar en tablas específicas
            if tables_info:
                if columns_info:
                    for col in columns_info:
                        ExecutionColumnResult.objects.using('metadata_db').create(
                            execution_result=result,
                            table_id=tables_info[0]['table_id'],
                            table_name=tables_info[0]['table_name'],
                            column_id=col['column_id'],
                            column_name=col['column_name'],
                            #dq_value={'value': value}
                            dq_value=value
                        )
                else:
                    for table in tables_info:
                        ExecutionTableResult.objects.using('metadata_db').create(
                            execution_result=result,
                            table_id=table['table_id'],
                            table_name=table['table_name'],
                            #dq_value={'value': value}
                            dq_value=value
                        )
        
        else:
            # Caso 2: Resultados múltiples
            rows = result_value.get('rows', []) if isinstance(result_value, dict) else result_value
            
            # Obtener la columna DQ (viene de la vista)
            dq_column = result_value.get('dq_column') or execution_details.get('dq_column')
        
            # Estructura completa para dq_value
            dq_value_data = {
                'type': 'multiple',
                'rows': [
                    {
                        'row_id': str(row.get('row_id', row.get('id', f'unknown_{i}'))),
                        'dq_value': row.get(dq_column) if dq_column else row.get('dq_value', row.get('value'))
                        #'dq_value': row.get('dq_value', row.get('value'))
                    }
                    for i, row in enumerate(rows)
                ],
                'tables': tables_info,
                'columns': columns_info,
                'total_rows': len(rows),
                'execution_columns': execution_details.get('columns', [])
            }
            
            # Guardar registro principal
            result = DQMethodExecutionResult.objects.using('metadata_db').create(
                execution=execution,
                content_type=content_type,
                object_id=applied_method.id,
                result_type=result_type,
                dq_value=dq_value_data,  # Estructura completa con rows
                details={
                    **execution_details,
                    'applied_to': applied_to
                }
            )
            
            # Guardar cada fila como registro separado en ExecutionRowResult
            for row in dq_value_data['rows']:
                ExecutionRowResult.objects.using('metadata_db').create(
                    execution_result=result,
                    applied_method_id=applied_method.id,
                    table_id=tables_info[0]['table_id'] if tables_info else 0,
                    table_name=tables_info[0]['table_name'] if tables_info else '',
                    column_id=columns_info[0]['column_id'] if columns_info else 0,
                    column_name=columns_info[0]['column_name'] if columns_info else '',
                    row_id=row['row_id'],
                    dq_value=row['dq_value']
                )
        
        return result
      

    
    @staticmethod
    def _check_completion(execution):
        """Verifica finalización usando metadata_db"""
        # Nota: Count directo desde default no funciona, necesitamos conteo eficiente
        from .models import MeasurementDQMethod, AggregationDQMethod
        
        # Conteo optimizado para multi-DB
        total_methods = (
            MeasurementDQMethod.objects.using('default')
            .filter(associatedTo__metric__factor__dq_model=execution.dq_model)
            .count()
        ) + (
            AggregationDQMethod.objects.using('default')
            .filter(associatedTo__metric__factor__dq_model=execution.dq_model)
            .count()
        )
        
        completed_methods = execution.method_results.using('metadata_db').count()
        
        if total_methods == completed_methods:
            execution.status = 'completed'
            execution.completed_at = timezone.now()
            execution.save(using='metadata_db')