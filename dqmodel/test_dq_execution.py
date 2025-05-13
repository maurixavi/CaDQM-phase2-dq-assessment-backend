import psycopg2
import json
from typing import Dict, List, Union
import sys
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    """Encoder personalizado para manejar objetos Decimal"""
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super().default(o)

def get_connection_params():
    """Parámetros de conexión específicos para tu caso"""
    return {
        'dbname': 'data_at_hand_v01',
        'user': 'postgres',
        'password': 'password',
        'host': 'localhost',
        'port': 5432,
        'connect_timeout': 5
    }

def test_connection():
    """Prueba básica de conexión con manejo detallado de errores"""
    params = get_connection_params()
    print("\nProbando conexión con estos parámetros:")
    print(f"- Host: {params['host']}")
    print(f"- Puerto: {params['port']}")
    print(f"- Base de datos: {params['dbname']}")
    print(f"- Usuario: {params['user']}")
    
    try:
        conn = psycopg2.connect(**params)
        cursor = conn.cursor()
        
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()[0]
        
        print("\n✅ ¡Conexión exitosa!")
        print(f"Versión de PostgreSQL: {db_version}")
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = [table[0] for table in cursor.fetchall()]
        
        print("\nTablas disponibles en la base de datos:")
        for table in tables:
            print(f"- {table}")
        
        return True
        
    except psycopg2.OperationalError as e:
        print("\n❌ Error de conexión:")
        print(f"Tipo: {type(e).__name__}")
        print(f"Mensaje: {str(e)}")
        return False
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {type(e).__name__}: {str(e)}")
        return False
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def execute_dq_method(method_type: str, applied_to: Union[Dict, List[Dict]], algorithm: str):
    """Función para ejecutar métodos de calidad de datos"""
    params = get_connection_params()
    
    try:
        conn = psycopg2.connect(**params)
        cursor = conn.cursor()
        
        if isinstance(applied_to, dict):
            tables = [applied_to]
        else:
            tables = applied_to
            
        results = []
        
        for table in tables:
            query = algorithm
            query = query.replace('{table}', table['table_name'])
            for col in table.get('columns', []):
                query = query.replace(f'{{{col}}}', col)
            
            cursor.execute(query)
            
            if method_type == 'aggregation':
                columns = [desc[0] for desc in cursor.description]
                row = cursor.fetchone()
                if row:
                    # Convertir Decimal a float para serialización
                    row_dict = {}
                    for idx, col_name in enumerate(columns):
                        value = row[idx]
                        if isinstance(value, Decimal):
                            value = float(value)
                        row_dict[col_name] = value
                    results.append(row_dict)
            elif method_type == 'measurement':
                columns = [desc[0] for desc in cursor.description]
                for row in cursor.fetchall():
                    # Convertir Decimal a float para serialización
                    row_dict = {}
                    for idx, col_name in enumerate(columns):
                        value = row[idx]
                        if isinstance(value, Decimal):
                            value = float(value)
                        row_dict[col_name] = value
                    results.append(row_dict)
        
        return {
            'status': 'success',
            'results': results,
            'tables_processed': len(tables)
        }
        
    except psycopg2.Error as e:
        return {
            'status': 'error',
            'error_type': type(e).__name__,
            'error_message': str(e),
            'query': query if 'query' in locals() else None
        }
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    if not test_connection():
        print("\nNo se puede continuar sin conexión a la base de datos.")
        sys.exit(1)
    
    # Ejemplo 1: Método de agregación (completitud)
    print("\nEjemplo 1: Método de agregación (completitud)")
    agg_result = execute_dq_method(
        method_type='aggregation',
        applied_to={
            'table_name': 'books_data',
            'columns': ['title', 'authors', 'publisher']
        },
        algorithm="""
            SELECT 
                COUNT(*) AS total,
                COUNT(title) AS with_title,
                COUNT(authors) AS with_authors,
                COUNT(publisher) AS with_publisher,
                ROUND(100.0 * COUNT(title) / COUNT(*), 2) AS title_completeness,
                ROUND(100.0 * COUNT(authors) / COUNT(*), 2) AS authors_completeness,
                ROUND(100.0 * COUNT(publisher) / COUNT(*), 2) AS publisher_completeness
            FROM {table}
        """
    )
    print(json.dumps(agg_result, indent=2, cls=DecimalEncoder))
    
    # Ejemplo 2: Método de medición (reviews)
    print("\nEjemplo 2: Método de medición (reviews)")
    meas_result = execute_dq_method(
        method_type='measurement',
        applied_to={
            'table_name': 'books_rating',
            'columns': ['review_score']
        },
        algorithm="""
            SELECT 
                id,
                title,
                review_score,
                CASE
                    WHEN review_score < 1 THEN 'INVALIDO (menor que 1)'
                    WHEN review_score > 5 THEN 'INVALIDO (mayor que 5)'
                    WHEN review_score < 2 THEN 'BAJO (posible outlier)'
                    WHEN review_score > 4.5 THEN 'ALTO (posible outlier)'
                    ELSE 'NORMAL'
                END AS score_category
            FROM {table}
            WHERE review_score < 2 OR review_score > 4.5 OR review_score < 1 OR review_score > 5
            ORDER BY review_score
            LIMIT 10
        """
    )
    print(json.dumps(meas_result, indent=2, cls=DecimalEncoder))