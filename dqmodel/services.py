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
    def save_execution_result___(dq_model_id, applied_method, result_value, execution_details, result_type=None):
        """
        Versión que guarda resultados en ambas tablas:
        - DQMethodExecutionResult: Un registro por fila (para granularidad)
        - ExecutionRowResult: Registros detallados por fila
        """
        execution = DQExecutionResultService.get_or_create_execution(dq_model_id)
        content_type = ContentType.objects.db_manager('default').get_for_model(applied_method)
        
        # Determinar tipo de resultado si no se proporcionó
        if result_type is None:
            result_type = 'multiple' if (isinstance(result_value, (list, dict)) and 
                                       ('rows' in result_value or isinstance(result_value, list))) else 'single'
        
        applied_to = applied_method.appliedTo or []
        first_item = applied_to[0] if applied_to else {}

        if result_type == 'single':
            # 1. Resultado único - guardamos solo el valor en DQMethodExecutionResult
            value = result_value.get('value') if isinstance(result_value, dict) else result_value
            
            result = DQMethodExecutionResult.objects.using('metadata_db').create(
                execution=execution,
                content_type=content_type,
                object_id=applied_method.id,
                result_type=result_type,
                dq_value=value,  # Solo el valor numérico
                details=execution_details
            )

            # Opcional: Guardar en tablas específicas
            if 'table_id' in first_item:
                if 'column_id' in first_item:
                    ExecutionColumnResult.objects.using('metadata_db').create(
                        execution_result=result,
                        table_id=first_item.get('table_id'),
                        table_name=first_item.get('table_name', ''),
                        column_id=first_item.get('column_id'),
                        column_name=first_item.get('column_name', ''),
                        dq_value={'value': value}
                    )
                else:
                    ExecutionTableResult.objects.using('metadata_db').create(
                        execution_result=result,
                        table_id=first_item.get('table_id'),
                        table_name=first_item.get('table_name', ''),
                        dq_value={'value': value}
                    )

        else:
            # 2. Resultados múltiples - guardamos un registro por fila en AMBAS tablas
            rows = result_value.get('rows', []) if isinstance(result_value, dict) else result_value
            base_metadata = {
                'applied_to': applied_to,
                'total_rows': len(rows),
                'columns': execution_details.get('columns', [])
            }

            # Primero creamos el registro "padre" (opcional, para mantener relación)
            parent_result = DQMethodExecutionResult.objects.using('metadata_db').create(
                execution=execution,
                content_type=content_type,
                object_id=applied_method.id,
                result_type='parent',
                dq_value=base_metadata,
                details={**execution_details, 'is_parent_record': True}
            )

            # Luego creamos un registro en DQMethodExecutionResult POR CADA FILA
            for row in rows:
                row_id = str(row.get('row_id', row.get('id', 'unknown')))
                row_value = row.get('dq_value', row.get('value'))
                
                # Registro en DQMethodExecutionResult (por fila)
                row_result = DQMethodExecutionResult.objects.using('metadata_db').create(
                    execution=execution,
                    content_type=content_type,
                    object_id=applied_method.id,
                    result_type='multiple',
                    dq_value=row_value,  # Solo el valor de esta fila
                    details={
                        'row_id': row_id,
                        'parent_result_id': str(parent_result.id),
                        **{k: v for k, v in row.items() 
                          if k not in ('dq_value', 'value', 'row_id', 'id')}
                    }
                )

                # Registro en ExecutionRowResult (detalle completo)
                ExecutionRowResult.objects.using('metadata_db').create(
                    execution_result=row_result,  # Relación directa
                    parent_result=parent_result,  # Relación al padre
                    applied_method_id=applied_method.id,
                    table_id=first_item.get('table_id', 0),
                    table_name=first_item.get('table_name', ''),
                    column_id=first_item.get('column_id', 0),
                    column_name=first_item.get('column_name', ''),
                    row_id=row_id,
                    dq_value={
                        'value': row_value,
                        'row_data': {k: v for k, v in row.items() 
                                     if k not in ('dq_value', 'value', 'row_id', 'id')}
                    }
                )

            result = parent_result

        return result
    
    
    @staticmethod
    def save_execution_result_DISENOANTERIOR(dq_model_id, applied_method, result_value, execution_details, result_type=None):
        try:
            print("=== INICIO GUARDADO DE RESULTADOS ===")
            
            # 1. Validación inicial
            if not dq_model_id or not applied_method:
                raise ValueError("Se requieren dq_model_id y applied_method")

            # 2. Obtener metadata de tablas/columnas
            applied_to = applied_method.appliedTo or []
            tables_info = []
            columns_info = []
            
            for item in applied_to:
                if isinstance(item, dict):
                    if 'table_id' in item:
                        tables_info.append({
                            'table_id': item['table_id'],
                            'table_name': item.get('table_name', 'unknown')
                        })
                    if 'column_id' in item:
                        columns_info.append({
                            'column_id': item['column_id'],
                            'column_name': item.get('column_name', 'unknown'),
                            'data_type': item.get('data_type', '')
                        })

            # Eliminar duplicados
            tables_info = [dict(t) for t in {tuple(d.items()) for d in tables_info}]
            columns_info = [dict(c) for c in {tuple(d.items()) for d in columns_info}]

            # 3. Determinar tipo de resultado
            if result_type is None:
                if isinstance(result_value, dict) and 'rows' in result_value:
                    result_type = 'multiple'
                    rows = result_value['rows']
                elif isinstance(result_value, list):
                    result_type = 'multiple'
                    rows = result_value
                else:
                    result_type = 'single'
            else:
                rows = result_value.get('rows', []) if isinstance(result_value, dict) else result_value

            print(f"Tipo de resultado: {result_type}")
            print(f"Tablas afectadas: {len(tables_info)}")
            print(f"Columnas afectadas: {len(columns_info)}")

            # 4. Obtener ejecución y content type
            execution = DQExecutionResultService.get_or_create_execution(dq_model_id)
            content_type = ContentType.objects.db_manager('default').get_for_model(applied_method)

            # 5. Manejar resultado único
            if result_type == 'single':
                value = result_value.get('value') if isinstance(result_value, dict) else result_value
                
                if value is None:
                    raise ValueError("El resultado único no puede ser nulo")

                # Guardar en tabla principal
                result = DQMethodExecutionResult.objects.using('metadata_db').create(
                    execution=execution,
                    content_type=content_type,
                    object_id=applied_method.id,
                    result_type=result_type,
                    dq_value=value,
                    details={
                        **execution_details,
                        'applied_to': applied_to,
                        'tables': tables_info,
                        'columns': columns_info
                    }
                )
                print(f"Resultado único guardado (ID: {result.id})")

                # Guardar en ExecutionColumnResult si hay columnas
                if columns_info:
                    for col in columns_info:
                        ExecutionColumnResult.objects.using('metadata_db').create(
                            execution_result=result,
                            table_id=tables_info[0]['table_id'] if tables_info else 0,
                            table_name=tables_info[0]['table_name'] if tables_info else 'unknown',
                            column_id=col['column_id'],
                            column_name=col['column_name'],
                            dq_value={'value': value}
                        )
                    print(f"Guardados {len(columns_info)} registros en ExecutionColumnResult")
                else:
                    print("Advertencia: No hay información de columnas para guardar en ExecutionColumnResult")

                return result

            # 6. Manejar resultados múltiples
            with transaction.atomic(using='metadata_db'):
                # Crear registro padre
                parent_result = DQMethodExecutionResult.objects.using('metadata_db').create(
                    execution=execution,
                    content_type=content_type,
                    object_id=applied_method.id,
                    result_type='parent',
                    dq_value={
                        'type': 'multiple',
                        'total_rows': len(rows),
                        'tables': tables_info,
                        'columns': columns_info
                    },
                    details={
                        **execution_details,
                        'applied_to': applied_to
                    }
                )
                print(f"Registro padre creado (ID: {parent_result.id})")

                # Procesar cada fila en transacciones independientes
                for i, row in enumerate(rows):
                    try:
                        with transaction.atomic(using='metadata_db'):
                            row_id = str(row.get('row_id', f'auto_{i}'))
                            row_value = row.get('dq_value', row.get('value'))
                            
                            if row_value is None:
                                print(f"Fila {i} sin valor - omitiendo")
                                continue

                            # Crear registro en DQMethodExecutionResult
                            row_result = DQMethodExecutionResult.objects.using('metadata_db').create(
                                execution=execution,
                                content_type=content_type,
                                object_id=applied_method.id,
                                result_type='row',
                                dq_value=row_value,
                                details={
                                    'row_id': row_id,
                                    'parent_id': str(parent_result.id),
                                    **{k: v for k, v in row.items() 
                                    if k not in ('dq_value', 'value', 'row_id', 'id')}
                                }
                            )

                            # Crear registro en ExecutionRowResult
                            ExecutionRowResult.objects.using('metadata_db').create(
                                execution_result=row_result,
                                applied_method_id=applied_method.id,
                                table_id=tables_info[0]['table_id'] if tables_info else 0,
                                table_name=tables_info[0]['table_name'] if tables_info else 'unknown',
                                column_id=columns_info[0]['column_id'] if columns_info else 0,
                                column_name=columns_info[0]['column_name'] if columns_info else 'unknown',
                                row_id=row_id,
                                dq_value={
                                    'value': row_value,
                                    'row_data': {k: v for k, v in row.items() 
                                                if k not in ('dq_value', 'value', 'row_id', 'id')}
                                }
                            )
                            print(f"Fila {i} guardada correctamente (ID: {row_result.id})")

                    except Exception as e:
                        print(f"ERROR al guardar fila {i}: {str(e)}")
                        continue

            return parent_result

        except Exception as e:
            print(f"ERROR CRÍTICO: {str(e)}")
            raise
    
    @staticmethod
    def save_execution_result_intento2jueves_faltancolumnas(dq_model_id, applied_method, result_value, execution_details, result_type=None):
        try:
            print("=== INICIANDO GUARDADO DE RESULTADOS ===")
            
            # 1. Validación inicial
            if not dq_model_id or not applied_method:
                raise ValueError("IDs de modelo y método son requeridos")
            
            # 2. Obtener metadata de tablas/columnas
            applied_to = applied_method.appliedTo or []
            table_data = next((item for item in applied_to if isinstance(item, dict) and 'table_id' in item), None)
            column_data = next((item for item in applied_to if isinstance(item, dict) and 'column_id' in item), None)

            if not table_data:
                print("ADVERTENCIA: No se encontró metadata de tabla")
                table_data = {'table_id': 0, 'table_name': 'unknown'}
            
            if not column_data:
                print("ADVERTENCIA: No se encontró metadata de columna")
                column_data = {'column_id': 0, 'column_name': 'unknown'}

            # 3. Determinar tipo de resultado
            if result_type is None:
                if isinstance(result_value, dict) and 'rows' in result_value:
                    result_type = 'multiple'
                    rows = result_value['rows']
                elif isinstance(result_value, list):
                    result_type = 'multiple'
                    rows = result_value
                else:
                    result_type = 'single'
            else:
                rows = result_value.get('rows', []) if isinstance(result_value, dict) else result_value

            print(f"Tipo de resultado: {result_type} | Filas a procesar: {len(rows) if result_type == 'multiple' else 1}")

            # 4. Obtener ejecución y content type
            execution = DQExecutionResultService.get_or_create_execution(dq_model_id)
            content_type = ContentType.objects.db_manager('default').get_for_model(applied_method)

            # 5. Manejar resultado único
            if result_type == 'single':
                value = result_value.get('value') if isinstance(result_value, dict) else result_value
                result = DQMethodExecutionResult.objects.using('metadata_db').create(
                    execution=execution,
                    content_type=content_type,
                    object_id=applied_method.id,
                    result_type=result_type,
                    dq_value=value,
                    details=execution_details
                )
                print(f"Resultado único guardado (ID: {result.id})")
                return result

            # 6. Manejar resultados múltiples
            with transaction.atomic(using='metadata_db'):
                # Crear registro padre
                parent_result = DQMethodExecutionResult.objects.using('metadata_db').create(
                    execution=execution,
                    content_type=content_type,
                    object_id=applied_method.id,
                    result_type='parent',
                    dq_value={'total_rows': len(rows)},
                    details={
                        **execution_details,
                        'table_data': table_data,
                        'column_data': column_data
                    }
                )
                print(f"Registro padre creado (ID: {parent_result.id})")

                # Procesar cada fila en transacciones independientes
                for i, row in enumerate(rows):
                    try:
                        with transaction.atomic(using='metadata_db'):
                            row_id = str(row.get('row_id', f'auto_{i}'))
                            row_value = row.get('dq_value', row.get('value'))
                            
                            if row_value is None:
                                print(f"Fila {i} sin valor - omitiendo")
                                continue

                            # Crear registro en DQMethodExecutionResult
                            row_result = DQMethodExecutionResult.objects.using('metadata_db').create(
                                execution=execution,
                                content_type=content_type,
                                object_id=applied_method.id,
                                result_type='row',
                                dq_value=row_value,
                                details={
                                    'row_id': row_id,
                                    'parent_id': str(parent_result.id),
                                    **{k: v for k, v in row.items() 
                                    if k not in ('dq_value', 'value', 'row_id', 'id')}
                                }
                            )

                            # Crear registro en ExecutionRowResult
                            ExecutionRowResult.objects.using('metadata_db').create(
                                execution_result=row_result,
                                applied_method_id=applied_method.id,
                                table_id=table_data['table_id'],
                                table_name=table_data.get('table_name', 'unknown'),
                                column_id=column_data['column_id'],
                                column_name=column_data.get('column_name', 'unknown'),
                                row_id=row_id,
                                dq_value={'value': row_value}
                            )
                            print(f"Fila {i} guardada correctamente (ID: {row_result.id})")

                    except Exception as e:
                        print(f"ERROR al guardar fila {i}: {str(e)}")
                        continue

            return parent_result

        except Exception as e:
            print(f"ERROR CRÍTICO: {str(e)}")
            raise
    
    @staticmethod
    @transaction.atomic(using='metadata_db')
    def save_execution_result_intento1jueves(dq_model_id, applied_method, result_value, execution_details, result_type=None):
        try:
            print("Iniciando guardado de resultados...")
            
            # Validación básica
            if not dq_model_id or not applied_method:
                raise ValueError("Parámetros requeridos faltantes")

            execution = DQExecutionResultService.get_or_create_execution(dq_model_id)
            content_type = ContentType.objects.db_manager('default').get_for_model(applied_method)

            # Determinar tipo y extraer rows
            if isinstance(result_value, dict) and 'rows' in result_value:
                rows = result_value['rows']
                result_type = 'multiple'
            elif isinstance(result_value, list):
                rows = result_value
                result_type = 'multiple'
            else:
                result_type = 'single'

            print(f"Tipo: {result_type}, Filas: {len(rows) if result_type == 'multiple' else 1}")

            # Extraer metadata de tablas/columnas
            applied_to = applied_method.appliedTo or []
            table_data = next((item for item in applied_to if isinstance(item, dict) and 'table_id' in item), {})
            column_data = next((item for item in applied_to if isinstance(item, dict) and 'column_id' in item), {})

            if result_type == 'single':
                value = result_value.get('value') if isinstance(result_value, dict) else result_value
                return DQMethodExecutionResult.objects.using('metadata_db').create(
                    execution=execution,
                    content_type=content_type,
                    object_id=applied_method.id,
                    result_type=result_type,
                    dq_value=value,
                    details=execution_details
                )

            # Resultados múltiples
            parent_result = DQMethodExecutionResult.objects.using('metadata_db').create(
                execution=execution,
                content_type=content_type,
                object_id=applied_method.id,
                result_type='parent',
                dq_value={'total_rows': len(rows)},
                details={
                    **execution_details,
                    'table_data': table_data,
                    'column_data': column_data
                }
            )

            for i, row in enumerate(rows):
                try:
                    row_id = str(row.get('row_id', f'auto_{i}'))
                    row_value = row.get('dq_value', row.get('value'))
                    
                    if row_value is None:
                        print(f"Fila {i} sin valor - omitiendo")
                        continue

                    # Crear registro en DQMethodExecutionResult
                    row_result = DQMethodExecutionResult.objects.using('metadata_db').create(
                        execution=execution,
                        content_type=content_type,
                        object_id=applied_method.id,
                        result_type='row',
                        dq_value=row_value,
                        details={
                            'row_id': row_id,
                            'parent_id': str(parent_result.id),
                            **{k: v for k, v in row.items() 
                            if k not in ('dq_value', 'value', 'row_id', 'id')}
                        }
                    )

                    # Crear registro en ExecutionRowResult con todos los campos requeridos
                    ExecutionRowResult.objects.using('metadata_db').create(
                        execution_result=row_result,
                        applied_method_id=applied_method.id,
                        table_id=table_data.get('table_id', 0),  # Valor por defecto 0
                        table_name=table_data.get('table_name', 'unknown'),
                        column_id=column_data.get('column_id', 0),  # Valor por defecto 0
                        column_name=column_data.get('column_name', 'unknown'),
                        row_id=row_id,
                        dq_value={'value': row_value}  # Estructura mínima requerida
                    )

                    print(f"Fila {i} guardada correctamente")

                except Exception as e:
                    print(f"Error grave en fila {i}: {str(e)}")
                    # Continuar con las siguientes filas a pesar del error
                    continue

            return parent_result

        except Exception as e:
            print(f"ERROR CRÍTICO: {str(e)}")
            raise
    
    @staticmethod
    @transaction.atomic(using='metadata_db')
    def save_execution_result3(dq_model_id, applied_method, result_value, execution_details, result_type=None):
        """
        Versión corregida con manejo robusto de la variable rows
        """
        try:
            print("Iniciando guardado de resultados...")
            
            # Validación básica
            if not dq_model_id or not applied_method:
                raise ValueError("Parámetros requeridos faltantes")

            # Obtener ejecución
            execution = DQExecutionResultService.get_or_create_execution(dq_model_id)
            print(f"Ejecución obtenida: {execution.execution_id}")

            # Obtener ContentType
            content_type = ContentType.objects.db_manager('default').get_for_model(applied_method)
            print(f"ContentType obtenido: {content_type}")

            # Determinar tipo de resultado y extraer rows
            rows = []
            if result_type is None:
                if isinstance(result_value, dict) and 'rows' in result_value:
                    result_type = 'multiple'
                    rows = result_value['rows']
                elif isinstance(result_value, list):
                    result_type = 'multiple'
                    rows = result_value
                else:
                    result_type = 'single'
            else:
                # Si el tipo fue especificado, extraer rows según corresponda
                if result_type == 'multiple':
                    rows = result_value['rows'] if isinstance(result_value, dict) else result_value

            print(f"Tipo de resultado: {result_type}, Número de filas: {len(rows)}")

            if result_type == 'single':
                print("Procesando resultado único...")
                value = result_value.get('value') if isinstance(result_value, dict) else result_value
                
                result = DQMethodExecutionResult.objects.using('metadata_db').create(
                    execution=execution,
                    content_type=content_type,
                    object_id=applied_method.id,
                    result_type=result_type,
                    dq_value=value,
                    details=execution_details
                )
                print(f"Resultado único guardado con ID: {result.id}")
                return result

            else:  # Resultados múltiples
                if not rows:
                    raise ValueError("No se encontraron filas para resultados múltiples")

                print(f"Procesando {len(rows)} filas...")
                
                # Registrar metadata en un padre
                parent_result = DQMethodExecutionResult.objects.using('metadata_db').create(
                    execution=execution,
                    content_type=content_type,
                    object_id=applied_method.id,
                    result_type='parent',
                    dq_value={
                        'total_rows': len(rows),
                        'type': 'multiple'
                    },
                    details=execution_details
                )
                print(f"Registro padre creado: {parent_result.id}")

                # Procesar cada fila
                for i, row in enumerate(rows[:1000]):  # Límite por seguridad
                    try:
                        row_id = str(row.get('row_id', row.get('id', f'auto_{i}')))
                        row_value = row.get('dq_value', row.get('value'))
                        
                        if row_value is None:
                            print(f"Advertencia: Fila {i} sin valor")
                            continue

                        # Registrar en DQMethodExecutionResult
                        row_result = DQMethodExecutionResult.objects.using('metadata_db').create(
                            execution=execution,
                            content_type=content_type,
                            object_id=applied_method.id,
                            result_type='row',
                            dq_value=row_value,
                            details={
                                'row_id': row_id,
                                'parent_id': str(parent_result.id),
                                **{k: v for k, v in row.items() 
                                if k not in ('dq_value', 'value', 'row_id', 'id')}
                            }
                        )

                        # Registrar en ExecutionRowResult
                        ExecutionRowResult.objects.using('metadata_db').create(
                            execution_result=row_result,
                            #parent_result=parent_result,
                            applied_method_id=applied_method.id,
                            row_id=row_id,
                            dq_value={
                                'value': row_value,
                                'row_data': {k: v for k, v in row.items() 
                                            if k not in ('dq_value', 'value', 'row_id', 'id')}
                            }
                        )

                    except Exception as e:
                        print(f"Error guardando fila {i}: {str(e)}")
                        continue

                print("Proceso completado exitosamente")
                return parent_result

        except Exception as e:
            print(f"ERROR CRÍTICO: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    @transaction.atomic(using='metadata_db')
    def save_execution_result_este(dq_model_id, applied_method, result_value, execution_details, result_type=None):
        """
        Versión que:
        1. Para resultados únicos: guarda solo el valor en dq_value
        2. Para resultados múltiples: guarda en dq_value la estructura completa con rows
        3. Mantiene metadata en details
        4. Guarda filas individuales en ExecutionRowResult
        5. Verifica si la ejecución está completa después de guardar cada resultado
        """
        # Obtener o crear ejecución
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
                            dq_value={'value': value}
                        )
                else:
                    for table in tables_info:
                        ExecutionTableResult.objects.using('metadata_db').create(
                            execution_result=result,
                            table_id=table['table_id'],
                            table_name=table['table_name'],
                            dq_value={'value': value}
                        )
        
        else:
            # Caso 2: Resultados múltiples
            rows = result_value.get('rows', []) if isinstance(result_value, dict) else result_value
            
            # Estructura completa para dq_value
            dq_value_data = {
                'type': 'multiple',
                'rows': [
                    {
                        'row_id': str(row.get('row_id', row.get('id', f'unknown_{i}'))),
                        'dq_value': row.get('dq_value', row.get('value'))
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
        
        # Verificar si la ejecución está completa después de guardar este resultado
        DQExecutionResultService._check_completion(execution)
        
        return result

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
            
            # Estructura completa para dq_value
            dq_value_data = {
                'type': 'multiple',
                'rows': [
                    {
                        'row_id': str(row.get('row_id', row.get('id', f'unknown_{i}'))),
                        'dq_value': row.get('dq_value', row.get('value'))
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
    @transaction.atomic(using='metadata_db')
    def save_execution_result_noseporquemnof(dq_model_id, applied_method, result_value, execution_details, result_type=None):
        """
        Versión que:
        1. Para resultados únicos: guarda solo el valor en dq_value
        2. Para resultados múltiples: guarda en dq_value la estructura completa con rows
        3. Mantiene metadata en details
        4. Guarda filas individuales en ExecutionRowResult
        """
        execution = DQExecutionResultService.get_or_create_execution(dq_model_id)
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
                            dq_value={'value': value}
                        )
                else:
                    for table in tables_info:
                        ExecutionTableResult.objects.using('metadata_db').create(
                            execution_result=result,
                            table_id=table['table_id'],
                            table_name=table['table_name'],
                            dq_value={'value': value}
                        )
        
        else:
            # Caso 2: Resultados múltiples
            rows = result_value.get('rows', []) if isinstance(result_value, dict) else result_value
            
            # Estructura completa para dq_value
            dq_value_data = {
                #'type': 'multiple',
                'dq_values': [
                    {
                        'row_id': str(row.get('row_id', row.get('id', f'unknown_{i}'))),
                        'dq_value': row.get('dq_value', row.get('value'))
                    }
                    for i, row in enumerate(rows)
                ],
                #'tables': tables_info,
                #'columns': columns_info,
                'total_rows': len(rows),
                #'execution_columns': execution_details.get('columns', [])
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
                    'applied_to': applied_to,
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
    @transaction.atomic(using='metadata_db')
    def save_execution_result0000000(dq_model_id, applied_method, result_value, execution_details, result_type=None):
        """
        Versión optimizada que:
        1. Para resultados únicos: guarda solo el valor en dq_value
        2. Para resultados múltiples: guarda cada fila como registro separado
        """
        execution = DQExecutionResultService.get_or_create_execution(dq_model_id)
        content_type = ContentType.objects.db_manager('default').get_for_model(applied_method)
        
        # Determinar tipo de resultado si no se proporcionó
        if result_type is None:
            result_type = 'multiple' if (isinstance(result_value, (list, dict))) else 'single'
        
        # Preparar datos comunes
        applied_to = applied_method.appliedTo or []
        first_item = applied_to[0] if applied_to else {}
        
        if result_type == 'single':
            # Caso 1: Resultado único - guardamos solo el valor
            value = result_value.get('value') if isinstance(result_value, dict) else result_value
            
            # Guardar en tabla principal
            result = DQMethodExecutionResult.objects.using('metadata_db').create(
                execution=execution,
                content_type=content_type,
                object_id=applied_method.id,
                result_type=result_type,
                dq_value=value,  # Solo el valor, no el JSON completo
                details=execution_details
            )
            
            # Opcional: Guardar en tablas específicas (para compatibilidad)
            if 'table_id' in first_item:
                if 'column_id' in first_item:
                    # Nivel columna
                    ExecutionColumnResult.objects.using('metadata_db').create(
                        execution_result=result,
                        table_id=first_item.get('table_id'),
                        table_name=first_item.get('table_name', ''),
                        column_id=first_item.get('column_id'),
                        column_name=first_item.get('column_name', ''),
                        dq_value={'value': value}
                    )
                else:
                    # Nivel tabla
                    ExecutionTableResult.objects.using('metadata_db').create(
                        execution_result=result,
                        table_id=first_item.get('table_id'),
                        table_name=first_item.get('table_name', ''),
                        dq_value={'value': value}
                    )
            
        else:
            # Caso 2: Resultados múltiples
            rows = result_value.get('rows', []) if isinstance(result_value, dict) else result_value
            
            # Guardar registro principal (con metadata pero sin rows)
            result = DQMethodExecutionResult.objects.using('metadata_db').create(
                execution=execution,
                content_type=content_type,
                object_id=applied_method.id,
                result_type=result_type,
                dq_value={  # Metadata sin las filas
                    'total_rows': len(rows),
                },
                details={  # Metadata sin las filas
                    'applied_to': applied_to,
                    'total_rows': len(rows),
                    'columns': execution_details.get('columns', [])
                },
                #details=execution_details
            )
            
            # Guardar cada fila como registro separado
            for row in rows:
                row_id = str(row.get('row_id', row.get('id', 'unknown')))
                row_value = row.get('dq_value', row.get('value'))
                
                ExecutionRowResult.objects.using('metadata_db').create(
                    execution_result=result,
                    applied_method_id=applied_method.id,
                    table_id=first_item.get('table_id', 0),
                    table_name=first_item.get('table_name', ''),
                    column_id=first_item.get('column_id', 0),
                    column_name=first_item.get('column_name', ''),
                    row_id=row_id,
                    dq_value=row_value
                    #{ 
                        #'value': row_value,
                        #'row_data': {k: v for k, v in row.items() 
                        #            if k not in ('dq_value', 'value', 'row_id', 'id')}
                    #}
                )
        
        return result


    @staticmethod
    @transaction.atomic(using='metadata_db')
    def save_execution_result_intento1FuncionaMaso(dq_model_id, applied_method, result_value, execution_details, result_type=None):
        """
        Versión optimizada que:
        1. Para resultados únicos: guarda solo el valor en dq_value
        2. Para resultados múltiples: guarda cada fila como registro separado
        """
        execution = DQExecutionResultService.get_or_create_execution(dq_model_id)
        content_type = ContentType.objects.db_manager('default').get_for_model(applied_method)
        
        # Determinar tipo de resultado si no se proporcionó
        if result_type is None:
            result_type = 'multiple' if (isinstance(result_value, (list, dict))) else 'single'
        
        # Preparar datos comunes
        applied_to = applied_method.appliedTo or []
        first_item = applied_to[0] if applied_to else {}
        
        if result_type == 'single':
            # Caso 1: Resultado único - guardamos solo el valor
            value = result_value.get('value') if isinstance(result_value, dict) else result_value
            
            # Guardar en tabla principal
            result = DQMethodExecutionResult.objects.using('metadata_db').create(
                execution=execution,
                content_type=content_type,
                object_id=applied_method.id,
                result_type=result_type,
                dq_value=value,  # Solo el valor, no el JSON completo
                details=execution_details
            )
            
            # Opcional: Guardar en tablas específicas (para compatibilidad)
            if 'table_id' in first_item:
                if 'column_id' in first_item:
                    # Nivel columna
                    ExecutionColumnResult.objects.using('metadata_db').create(
                        execution_result=result,
                        table_id=first_item.get('table_id'),
                        table_name=first_item.get('table_name', ''),
                        column_id=first_item.get('column_id'),
                        column_name=first_item.get('column_name', ''),
                        dq_value={'value': value}
                    )
                else:
                    # Nivel tabla
                    ExecutionTableResult.objects.using('metadata_db').create(
                        execution_result=result,
                        table_id=first_item.get('table_id'),
                        table_name=first_item.get('table_name', ''),
                        dq_value={'value': value}
                    )
            
        else:
            # Caso 2: Resultados múltiples
            rows = result_value.get('rows', []) if isinstance(result_value, dict) else result_value
            
            # Guardar registro principal (con metadata pero sin rows)
            result = DQMethodExecutionResult.objects.using('metadata_db').create(
                execution=execution,
                content_type=content_type,
                object_id=applied_method.id,
                result_type=result_type,
                dq_value={  # Metadata sin las filas
                    'applied_to': applied_to,
                    'total_rows': len(rows),
                    'columns': execution_details.get('columns', [])
                },
                details=execution_details
            )
            
            # Guardar cada fila como registro separado
            for row in rows:
                row_id = str(row.get('row_id', row.get('id', 'unknown')))
                row_value = row.get('dq_value', row.get('value'))
                
                ExecutionRowResult.objects.using('metadata_db').create(
                    execution_result=result,
                    applied_method_id=applied_method.id,
                    table_id=first_item.get('table_id', 0),
                    table_name=first_item.get('table_name', ''),
                    column_id=first_item.get('column_id', 0),
                    column_name=first_item.get('column_name', ''),
                    row_id=row_id,
                    dq_value={
                        'value': row_value,
                        'row_data': {k: v for k, v in row.items() 
                                    if k not in ('dq_value', 'value', 'row_id', 'id')}
                    }
                )
        
        return result

  
    @staticmethod
    @transaction.atomic(using='metadata_db')
    def save_execution_result_RESPALDO10abr(dq_model_id, applied_method, result_value, execution_details, result_type=None):
        """
        Versión unificada que:
        1. Guarda en DQMethodExecutionResult (como antes)
        2. Opcionalmente guarda en tablas específicas
        """
        execution = DQExecutionResultService.get_or_create_execution(dq_model_id)
        content_type = ContentType.objects.db_manager('default').get_for_model(applied_method)
        
        # 1. Determinar el tipo de resultado si no se proporcionó
        if result_type is None:
            if isinstance(result_value, dict) and 'rows' in result_value:
                result_type = 'multiple'
            elif isinstance(result_value, list):
                result_type = 'multiple'
            else:
                result_type = 'single'
        
        # 2. Preparar datos para DQMethodExecutionResult (formato antiguo)
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

        # Estructura compatible con versión anterior
        stored_value = {
            'type': result_type,
            'tables': tables_info,
            'columns': columns_info,
            'execution_columns': execution_details.get('columns', []),
            'applied_to': applied_to
        }
        
        if result_type == 'multiple':
            rows = result_value.get('rows', []) if isinstance(result_value, dict) else result_value
            stored_value.update({
                'rows': rows,
                'dq_column': result_value.get('dq_column'),
                'total_rows': len(rows)
            })
        else:
            stored_value['value'] = result_value.get('value') if isinstance(result_value, dict) else result_value
        
        # 3. Guardar en tabla principal (siempre)
        result = DQMethodExecutionResult.objects.using('metadata_db').create(
            execution=execution,
            content_type=content_type,
            object_id=applied_method.id,
            result_type=result_type,
            dq_value=stored_value,  # Estructura compatible
            details=execution_details
        )
        
        # 4. Guardar en tablas específicas (opcional)
        try:
            first_item = applied_to[0] if applied_to else {}
            
            if result_type == 'multiple':
                # Guardar en ExecutionRowResult
                rows = result_value.get('rows', []) if isinstance(result_value, dict) else result_value
                for row in rows[:10000]:  # Límite por seguridad
                    ExecutionRowResult.objects.using('metadata_db').create(
                        execution_result=result,
                        applied_method_id=applied_method.id,
                        table_id=first_item.get('table_id', 0),
                        table_name=first_item.get('table_name', ''),
                        column_id=first_item.get('column_id', 0),
                        column_name=first_item.get('column_name', ''),
                        row_id=str(row.get('row_id', row.get('id', 'unknown'))),
                        dq_value={
                            'value': row.get('dq_value'),
                            'row_data': {k: v for k, v in row.items() if k != 'dq_value'}
                        }
                    )
            else:
                # Guardar en ExecutionColumnResult o ExecutionTableResult
                value = result_value.get('value') if isinstance(result_value, dict) else result_value
                
                if columns_info:  # Si hay columnas, es a nivel de columna
                    for col in columns_info:
                        ExecutionColumnResult.objects.using('metadata_db').create(
                            execution_result=result,
                            table_id=first_item.get('table_id', 0),
                            table_name=first_item.get('table_name', ''),
                            column_id=col['column_id'],
                            column_name=col['column_name'],
                            dq_value={'value': value}
                        )
                elif tables_info:  # Si no hay columnas pero sí tablas, es a nivel de tabla
                    for table in tables_info:
                        ExecutionTableResult.objects.using('metadata_db').create(
                            execution_result=result,
                            table_id=table['table_id'],
                            table_name=table['table_name'],
                            dq_value={'value': value}
                        )
        except Exception as e:
            print(f"Warning: No se pudieron guardar resultados en tablas específicas: {str(e)}")
            # No hacemos rollback porque el resultado principal sí se guardó
        
        return result
  
  
  
    @staticmethod
    @transaction.atomic(using='metadata_db')
    def save_execution_result0(dq_model_id, applied_method, result_value, execution_details):
        execution = DQExecutionResultService.get_or_create_execution(dq_model_id)
        content_type = ContentType.objects.get_for_model(applied_method)
        
        # Determinar tipo de resultado
        result_type = 'multiple' if isinstance(result_value, list) or ('rows' in result_value) else 'single'
        
        # Guardar en tabla principal
        result = DQMethodExecutionResult.objects.using('metadata_db').create(
            execution=execution,
            content_type=content_type,
            object_id=applied_method.id,
            result_type=result_type,
            dq_value=result_value,
            details=execution_details
        )
        
        # Guardar en tablas específicas
        applied_to = applied_method.appliedTo or []
        first_item = applied_to[0] if applied_to else {}
        
        if result_type == 'multiple':
            # Guardar resultados por fila
            rows = result_value.get('rows', []) if isinstance(result_value, dict) else result_value
            for row in rows[:10000]:  # Límite por seguridad
                ExecutionRowResult.objects.using('metadata_db').create(
                    execution_result=result,
                    applied_method_id=applied_method.id,
                    table_id=first_item.get('table_id'),
                    table_name=first_item.get('table_name', ''),
                    column_id=first_item.get('column_id'),
                    column_name=first_item.get('column_name', ''),
                    row_id=str(row.get('row_id', row.get('id', 'unknown'))),
                    dq_value={
                        'value': row.get('dq_value'),
                        'row_data': {k: v for k, v in row.items() if k != 'dq_value'}
                    }
                )
        else:
            # Resultado único (columna o tabla)
            value = result_value.get('value') if isinstance(result_value, dict) else result_value
            
            if 'column_id' in first_item:
                # Guardar resultado por columna
                ExecutionColumnResult.objects.using('metadata_db').create(
                    execution_result=result,
                    table_id=first_item.get('table_id'),
                    table_name=first_item.get('table_name', ''),
                    column_id=first_item.get('column_id'),
                    column_name=first_item.get('column_name', ''),
                    dq_value={'value': value}
                )
            else:
                # Guardar resultado por tabla
                ExecutionTableResult.objects.using('metadata_db').create(
                    execution_result=result,
                    table_id=first_item.get('table_id'),
                    table_name=first_item.get('table_name', ''),
                    dq_value={'value': value}
                )
        
        return result
      
    @staticmethod
    @transaction.atomic(using='metadata_db')
    def save_execution_result_RESPALDO_FUNCIONA_4abril2359(dq_model_id, applied_method, result_value, execution_details, result_type='single'):
        execution = DQExecutionResultService.get_or_create_execution(dq_model_id)
        content_type = ContentType.objects.db_manager('default').get_for_model(applied_method)
        
        # Extraer información de tablas y columnas
        applied_to = applied_method.appliedTo
        tables_info = []
        columns_info = []
        
        if applied_to and isinstance(applied_to, list):
            for item in applied_to:
                if 'table_id' in item and 'column_id' in item:
                    tables_info.append({
                        'table_id': item['table_id'],
                        'table_name': item.get('table_name', '')
                    })
                    columns_info.append({
                        'column_id': item['column_id'],
                        'column_name': item.get('column_name', ''),
                        'data_type': item.get('data_type', '')
                    })
        
        # Eliminar duplicados
        tables_info = [dict(t) for t in {tuple(d.items()) for d in tables_info}]
        columns_info = [dict(c) for c in {tuple(d.items()) for d in columns_info}]

        # Estructura de datos mejorada
        stored_value = {
            'type': result_type,
            'tables': tables_info,
            'columns': columns_info,
            'execution_columns': execution_details.get('columns', []),  # Columnas devueltas por la consulta
            'applied_to': applied_to  # Estructura original completa
        }

        if result_type == 'multiple':
            stored_value.update({
                'rows': result_value.get('rows', []) if isinstance(result_value, dict) else result_value,
                'dq_column': result_value.get('dq_column') if isinstance(result_value, dict) else None,
                'total_rows': len(result_value.get('rows', [])) if isinstance(result_value, dict) else len(result_value)
            })
        else:
            stored_value['value'] = result_value.get('value') if isinstance(result_value, dict) else result_value

        # Guardar resultado
        result = DQMethodExecutionResult.objects.using('metadata_db').create(
            execution=execution,
            content_type=content_type,
            object_id=applied_method.id,
            dq_value=stored_value,
            result_type=result_type,
            details={
                'execution_time': float(execution_details.get('query_time_seconds', 0)),
                'rows_affected': execution_details.get('rows_affected', 0),
                'total_records': execution_details.get('total_records', 0),
                'query': execution_details.get('query', ''),
                'applied_to': applied_to  # Guardar también en details por compatibilidad
            }
        )
        return result
  
    @staticmethod
    @transaction.atomic(using='metadata_db')
    def save_execution_result_BACKUP1656(dq_model_id, applied_method, result_value, execution_details, result_type='single'):
        execution = DQExecutionResultService.get_or_create_execution(dq_model_id)
        content_type = ContentType.objects.db_manager('default').get_for_model(applied_method)
        
        # Determinar estructura según tipo
        if result_type == 'multiple':
            stored_value = {
                'type': 'multiple',
                'rows': result_value,
                'columns': execution_details.get('columns', []),
                'total_rows': len(result_value)
            }
        else:
            stored_value = {
                'type': 'single',
                'value': result_value
            }

        result = DQMethodExecutionResult.objects.using('metadata_db').create(
            execution=execution,
            content_type=content_type,
            object_id=applied_method.id,
            dq_value=stored_value,
            result_type=result_type,
            details={
                'execution_time': float(execution_details.get('query_time_seconds', 0)),
                'rows_affected': execution_details.get('rows_affected'),
                'total_records': execution_details.get('total_records'),
                'query': execution_details.get('query')
            }
        )
        return result
      

    @staticmethod
    @transaction.atomic(using='metadata_db')
    def save_execution_result_SINROWS(dq_model_id, applied_method, result_value, execution_details):
        """
        Guarda el resultado en metadata_db con más detalles
        """
        execution = DQExecutionResultService.get_or_create_execution(dq_model_id)
        
        content_type = ContentType.objects.db_manager('default').get_for_model(applied_method)
        
        result = DQMethodExecutionResult.objects.using('metadata_db').create(
            execution=execution,
            content_type=content_type,
            object_id=applied_method.id,
            #dq_value=result_value,
            dq_value=result_value,  
            details={
                #'execution_time': execution_details.get('query_time_seconds'),
                'execution_time': float(execution_details.get('query_time_seconds', 0)),
                'rows_affected': execution_details.get('rows_affected'),
                'columns': execution_details.get('columns'),
                #'sample_data': execution_details.get('sample_data', []),
                'full_query': execution_details.get('query')
            }
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