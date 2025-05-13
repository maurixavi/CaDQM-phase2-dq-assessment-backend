import psycopg2
import json
from typing import Dict, List
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super().default(o)

def get_connection_params():
    return {
        'dbname': 'data_at_hand_v01',
        'user': 'postgres',
        'password': 'password',
        'host': 'localhost',
        'port': 5432,
        'connect_timeout': 5
    }

def execute_dq_method(method_config: Dict) -> Dict:
    """Ejecuta un método de calidad de datos"""
    params = get_connection_params()
    result = {
        "status": "success",
        "method": method_config["name"],
        "dimension": method_config["dimension"],
        "factor": method_config["factor"],
        "metric": method_config["metric"],
        "result_type": method_config["result_type"],
        "results": None,
        "query": ""
    }
    
    try:
        conn = psycopg2.connect(**params)
        cursor = conn.cursor()
        
        # Construir consulta
        query = method_config["algorithm"]
        result["query"] = query
        cursor.execute(query)
        
        # Procesar resultados
        if method_config["result_type"] == "boolean":
            rows = cursor.fetchall()
            result["results"] = [{"row_id": idx+1, "value": bool(row[0])} 
                               for idx, row in enumerate(rows[:10])]  # Limitamos a 10 filas
            
        elif method_config["result_type"] == "percentage":
            result["results"] = float(cursor.fetchone()[0])
            
        elif method_config["result_type"] == "count":
            result["results"] = cursor.fetchone()[0]
            
        elif method_config["result_type"] == "value":
            row = cursor.fetchone()
            result["results"] = row[0] if row else None
            
    except Exception as e:
        result.update({
            "status": "error",
            "error": str(e),
            "results": None
        })
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    
    return result

# Métodos específicos para tu base de libros
DQ_METHODS = [
    # 1. Completitud de descripciones (Completeness)
    {
        "name": "Descripciones no nulas",
        "description": "Porcentaje de libros con descripción no nula",
        "dimension": "Completeness",
        "factor": "Density",
        "metric": "Null Value Percentage",
        "result_type": "percentage",
        "algorithm": """
            SELECT 1 - (COUNT(*) FILTER (WHERE description IS NULL) * 1.0 / COUNT(*)) 
            FROM books_data
        """
    },
    
    # 2. Precios válidos (Accuracy)
    {
        "name": "Precios positivos",
        "description": "Verifica que los precios sean >= 0 (primeras 10 filas)",
        "dimension": "Accuracy",
        "factor": "Domain Integrity",
        "metric": "Value Validation",
        "result_type": "boolean",
        "algorithm": "SELECT price >= 0 FROM books_rating LIMIT 10"
    },
    
    # 3. Ratings en rango válido (Accuracy)
    {
        "name": "Ratings válidos",
        "description": "Porcentaje de ratings entre 1 y 5",
        "dimension": "Accuracy",
        "factor": "Domain Integrity",
        "metric": "Range Compliance",
        "result_type": "percentage",
        "algorithm": """
            SELECT COUNT(*) FILTER (WHERE review_score BETWEEN 1 AND 5) * 1.0 / COUNT(*)
            FROM books_rating
        """
    },
    
    # 4. Autores no nulos (Completeness)
    {
        "name": "Autores completos",
        "description": "Verifica que los autores no sean nulos (primeras 10 filas)",
        "dimension": "Completeness",
        "factor": "Density",
        "metric": "Null Value Check",
        "result_type": "boolean",
        "algorithm": "SELECT authors IS NOT NULL FROM books_data LIMIT 10"
    },
    
    # 5. Reviews recientes (Freshness)
    {
        "name": "Reviews últimos 3 meses",
        "description": "Conteo de reviews en últimos 3 meses",
        "dimension": "Freshness",
        "factor": "Currency",
        "metric": "Recent Items Count",
        "result_type": "count",
        "algorithm": """
            SELECT COUNT(*) FROM books_rating 
            WHERE to_timestamp(review_time) > CURRENT_DATE - INTERVAL '3 months'
        """
    },
    
    # 6. Consistencia entre tablas (Consistency)
    {
        "name": "Libros con reviews",
        "description": "Número de libros en books_data que tienen reviews",
        "dimension": "Consistency",
        "factor": "Inter-relationship Integrity",
        "metric": "Cross-table Validation",
        "result_type": "count",
        "algorithm": """
            SELECT COUNT(DISTINCT b.title)
            FROM books_data b
            JOIN books_rating r ON b.title = r.title
        """
    }
]

def main():
    """Función principal para ejecutar los métodos"""
    print("Ejecutando pruebas de calidad de datos...\n")
    results = []
    
    for method in DQ_METHODS:
        result = execute_dq_method(method)
        results.append(result)
        
        print(f"\nMétodo: {result['method']} ({result['dimension']})")
        print(f"Consulta: {result['query'][:100]}...")  # Mostramos solo el inicio de la consulta
        
        if result['status'] == 'success':
            if result['result_type'] == 'boolean':
                valid = sum(1 for r in result['results'] if r['value'])
                total = len(result['results'])
                print(f"Resultado: {valid}/{total} válidos ({valid/total:.0%})")
            else:
                print(f"Resultado: {result['results']}")
        else:
            print(f"Error: {result['error']}")
    
    # Exportar resultados
    with open("dq_test_results.json", "w") as f:
        json.dump(results, f, indent=2, cls=DecimalEncoder)
    print("\nPruebas completadas. Resultados guardados en dq_test_results.json")

if __name__ == "__main__":
    main()