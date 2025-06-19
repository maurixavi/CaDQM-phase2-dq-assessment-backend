from langchain_groq import ChatGroq
from langchain.schema import HumanMessage
import json
import logging
import json
import time
from datetime import datetime
import random
import time

# Configuración silenciosa (solo errores)
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Configuración de Groq
GROQ_API_KEY = "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"
#MODEL_NAME = "llama-3.3-70b-versatile"
MODEL_NAME = "llama-3.1-8b-instant" 
#MODEL_NAME = "llama3-8b-8192"
#MODEL_NAME = "llama3-70b-8192"

TEMPERATURE = 0.3
# Cliente LLM
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name=MODEL_NAME,
    temperature=TEMPERATURE
)

# Estructuras de datos para prompt
dimensions_and_factors = {
    "Accuracy": {
        "semantic": "Indicates that the data is correct and precise.",
        "factors": {
            "Semantic Accuracy": "The data correctly represents entities or states of the real world.",
            "Syntactic Accuracy": "The data is free from syntactic errors.",
            "Precision": "The data has an adequate level of detail."
        }
    },
    "Completeness": {
        "semantic": "Refers to the availability of all necessary data, ensuring that no important data is missing for analysis or decision-making.",
        "factors": {
            "Density": "The proportion of actual data entries compared to the total possible entries.",
            "Coverage": "The extent to which the data covers the required scope or domain."
        }
    },
    "Freshness": {
        "semantic": "Refers to the recency and update status of the data, indicating whether the data is current and up-to-date.",
        "factors": {
            "Currency": "Indicates how up-to-date the data is.",
            "Timeliness": "The data is available when needed.",
            "Volatility": "The rate at which the data changes over time."
        }
    },
    "Consistency": {
        "semantic": "Ensures that the data is coherent across different sources and over time, maintaining integrity and reliability.",
        "factors": {
            "Domain Integrity": "Data values conform to defined domain rules.",
            "Intra-relationship Integrity": "Ensures that data within a single dataset is consistent.",
            "Inter-relationship Integrity": "Ensures that data across multiple datasets is consistent."
        }
    },
    "Uniqueness": {
        "semantic": "Indicates that each data entry must be unique, with no duplicates present in the dataset.",
        "factors": {
            "No-duplication": "Ensures that there are no duplicate entries in the dataset.",
            "No-contradiction": "Ensures that there are no conflicting entries within the dataset."
        }
    }
}

# -------------------
# CASO DE ESTUDIO
#  -------------------
dq_problems = {
    1: "Missing values in required fields",
    2: "Inconsistent data formats",
    3: "Duplicated records",
    4: "Data out of range limits",
    5: "Unresolved data conflicts",
    6: "Incorrect categorization",
    7: "Non-standardized data",
    8: "Redundant entries",
    9: "Missing timestamps",
    10: "Inconsistent values across sources",
    11: "Nulls in key fields",
    12: "Invalid foreign keys",
    13: "Missing relationships",
    14: "Inconsistent units",
    15: "Data encoding errors",
    16: "Business rule violations"
}

dq_problems_en = {
    1: "Null values in required fields",
    2: "Inconsistent data formats",
    3: "Duplicated records",
    4: "Data out of range limits",
    5: "Unresolved data conflicts",
    6: "Incorrect categorization",
    7: "Non-standardized data",
    8: "Redundant entries",
    9: "Missing timestamps",
    10: "Inconsistent values across sources",
    11: "Nulls in key fields",
    12: "Invalid foreign keys",
    13: "Missing relationships",
    14: "Inconsistent units",
    15: "Data encoding errors",
    16: "Business rule violations"
}


dq_problems_es = {
    1: "Valores nulos en campos obligatorios",
    2: "Formatos de datos inconsistentes",
    3: "Registros duplicados",
    4: "Datos fuera de los límites establecidos",
    5: "Conflictos de datos no resueltos",
    6: "Categorización incorrecta",
    7: "Datos no estandarizados",
    8: "Entradas redundantes",
    9: "Tiempos faltantes",
    10: "Valores inconsistentes entre fuentes",
    11: "Nulos en campos clave",
    12: "Claves foráneas inválidas",
    13: "Relaciones faltantes",
    14: "Unidades inconsistentes",
    15: "Errores de codificación de datos",
    16: "Violación de reglas de negocio"
}

context_components_es = {
    "appDomain": [
        {"n": "Comercio electrónico de libros impresos y digitales; reseñas de clientes en Amazon", "id": 1}
    ],
    "bizRule": [
        {
            "s": "El campo 'score' debe estar entre 1 y 5",
            "id": 2,
            "sem": "Validación de rango de calificaciones"
        },
        {
            "s": "La combinacion (title, userId) debe ser unica.",
            "id": 3,
            "sem": "Evitar múltiples reseñas por usuario y libro"
        }
    ],
    "dataFilter": [
        {
            "s": "Incluir solo reseñas en inglés publicadas desde 2018",
            "id": 3,
            "desc": "Filtrar por idioma y fecha de publicación",
            "task": 11
        },
        {
            "s": "Excluir reseñas con menos de 20 caracteres",
            "id": 4,
            "desc": "Eliminar reseñas demasiado cortas",
            "task": 11
        }
    ],
    "dqMeta": [
        {
            "p": "/path/to/dqmetadata/1",
            "id": 5,
            "desc": "Metadata de calidad de datos",
            "meas": "Medición de completitud y precisión"
        }
    ],
    "dqReq": [
        {
            "s": "Latencia < 5 s para consultas interactivas",
            "id": 6,
            "desc": "Garantizar respuesta rápida en tiempo real"
        },
        {
            "s": "Métrica de completitud ≥ 95% para los campos obligatorios (title y reviewText)",
            "id": 7,
            "desc": "Asegurar integridad de datos"
        }
    ],
    "otherMeta": [
        {
            "p": "/path/to/othermetadata/1",
            "id": 8,
            "desc": "Metadata adicional",
            "auth": "Autor Desconocido",
            "lastUpd": 0
        }
    ],
    "task": [
        {
            "n": "Calcular sentiment scores",
            "id": 11,
            "purp": "Calcular puntuaciones de sentimiento para cada libro"
        },
        {
            "n": "Detectar y filtrar reseñas sospechosas",
            "id": 12,
            "purp": "Identificar 'review spam'"
        },
        {
            "n": "Generar ranking de calidad",
            "id": 13,
            "purp": "Clasificar la calidad de los contenidos textuales"
        }
    ],
    "userType": [
        {
            "n": "Analistas de marketing",
            "id": 12,
            "char": "Monitorean la reputación de títulos/editoriales"
        },
        {
            "n": "Científicos de datos",
            "id": 13,
            "char": "Entrenan modelos de recomendación"
        },
        {
            "n": "Investigadores académicos",
            "id": 14,
            "char": "Analizan sesgo lingüístico"
        }
    ]
}

context_components_en = {
    "appDomain": [
        {"n": "E-commerce of printed and digital books; customer reviews on Amazon", "id": 1}
    ],
    "bizRule": [
        {
            "s": "The 'overall' field must be between 1 and 5",
            "id": 2,
            "sem": "Rating range validation"
        },
        {
            "s": "Each combination (asin, reviewerID) must be unique",
            "id": 3,
            "sem": "Prevent multiple reviews per user and book"
        }
    ],
    "dataFilter": [
        {
            "s": "Include only English reviews published since 2018",
            "id": 3,
            "desc": "Filter by language and publication date",
            "task": 11
        },
        {
            "s": "Exclude reviews with fewer than 20 characters",
            "id": 4,
            "desc": "Remove excessively short reviews",
            "task": 11
        }
    ],
    "dqMeta": [
        {
            "p": "/path/to/dqmetadata/1",
            "id": 5,
            "desc": "Data quality metadata",
            "meas": "Completeness and accuracy measurement"
        }
    ],
    "dqReq": [
        {
            "s": "Latency < 5 s for interactive queries",
            "id": 6,
            "desc": "Ensure fast real-time response"
        },
        {
            "s": "Completeness metric ≥ 95% for mandatory fields (asin, overall, reviewText)",
            "id": 7,
            "desc": "Ensure data integrity"
        }
    ],
    "otherMeta": [
        {
            "p": "/path/to/othermetadata/1",
            "id": 8,
            "desc": "Additional metadata",
            "auth": "Unknown Author",
            "lastUpd": 0
        }
    ],
    "task": [
        {
            "n": "Calculate sentiment scores",
            "id": 11,
            "purp": "Compute sentiment scores for each book"
        },
        {
            "n": "Detect and filter suspicious reviews",
            "id": 12,
            "purp": "Identify 'review spam'"
        },
        {
            "n": "Generate quality ranking",
            "id": 13,
            "purp": "Rank the quality of textual content"
        }
    ],
    "userType": [
        {
            "n": "Marketing analysts",
            "id": 12,
            "char": "Monitor the reputation of titles/publishers"
        },
        {
            "n": "Data scientists",
            "id": 13,
            "char": "Train recommendation models"
        },
        {
            "n": "Academic researchers",
            "id": 14,
            "char": "Analyze linguistic bias"
        }
    ]
}


# -----------
# PROMPT
# -----------

DQ_RECOMMENDATION_PROMPT = """As a data quality expert, analyze these components and return ONLY a JSON object with:

1. The most relevant DQ dimension and factor
2. Choose ONLY THE STRONGEST supporting evidence and
3. A concise rationale

Available Dimensions and Factors:
{dimensions_and_factors}

Data Quality Problems:
{dq_problems}

System Context:
{context_components}

Return EXACTLY this JSON structure WITHOUT ANY OTHER TEXT OR COMMENTS:
{{
    "recommended_dimension": "dimension_name",
    "recommended_factor": "factor_name",
    "supported_by_problems": [problem_id1, problem_id2], 
    "supported_by_context": {{
        "appDomain": [ids],
        "bizRule": [ids],
        "dataFilter": [ids],
        "dqMeta": [ids],
        "dqReq": [ids],
        "otherData": [ids],
        "otherMeta": [ids],
        "sysReq": [ids],
        "task": [ids],
        "userType": [ids]
    }}, 
    "rationale": "Provide a clear, concise yet detailed explanation that links the selected problem descriptions and context component values to the recommended dimension and factor. Avoid using IDs or references like '(problem 1)'."
}}

IMPORTANT: 
- Return ONLY the JSON object, no explanations, headers, or any other text.
- "Try to avoid repeating previously recommended factors, and consider alternative factors if similarly supported."
- "Your goal is to recommend a DQ factor that is both well-supported AND not previously selected, to encourage coverage across dimensions."
"""


# UTILS
def expand_context_components(abbreviated: dict) -> dict:
    expanded = {}

    if "appDomain" in abbreviated:
        expanded["applicationDomain"] = [
            {"name": item["n"], "id": item["id"]} for item in abbreviated["appDomain"]
        ]
    if "bizRule" in abbreviated:
        expanded["businessRule"] = [
            {"statement": item["s"], "id": item["id"], "semantic": item["sem"]}
            for item in abbreviated["bizRule"]
        ]
    if "dataFilter" in abbreviated:
        expanded["dataFiltering"] = [
            {"statement": item["s"], "id": item["id"], "description": item["desc"], "taskAtHandId": item["task"]}
            for item in abbreviated["dataFilter"]
        ]
    if "dqMeta" in abbreviated:
        expanded["dqMetadata"] = [
            {"path": item["p"], "id": item["id"], "description": item["desc"], "measuredMetrics": item["meas"]}
            for item in abbreviated["dqMeta"]
        ]
    if "dqReq" in abbreviated:
        expanded["dqRequirement"] = [
            {"statement": item["s"], "id": item["id"], "description": item["desc"], "dataFilterIds": item["dataFilterIds"], "userTypeId": item["userTypeId"]}
            for item in abbreviated["dqReq"]
        ]
    if "otherData" in abbreviated:
        expanded["otherData"] = [
            {"path": item["p"], "id": item["id"], "description": item["desc"], "owner": item["own"]}
            for item in abbreviated["otherData"]
        ]
    if "otherMeta" in abbreviated:
        expanded["otherMetadata"] = [
            {"path": item["p"], "id": item["id"], "description": item["desc"], "author": item["auth"], "lastUpdated": item["lastUpd"]}
            for item in abbreviated["otherMeta"]
        ]
    if "sysReq" in abbreviated:
        expanded["systemRequirement"] = [
            {"statement": item["s"], "id": item["id"], "description": item["desc"]}
            for item in abbreviated["sysReq"]
        ]
    if "task" in abbreviated:
        expanded["taskAtHand"] = [
            {"name": item["n"], "id": item["id"], "purpose": item["purp"]}
            for item in abbreviated["task"]
        ]
    if "userType" in abbreviated:
        expanded["userType"] = [
            {"name": item["n"], "id": item["id"], "characteristics": item["char"]}
            for item in abbreviated["userType"]
        ]

    return expanded

def extract_json_from_response(response: str) -> str:
    """Extrae el primer bloque JSON válido de un string"""
    depth = 0
    start_idx = -1
    end_idx = -1

    for i, char in enumerate(response):
        if char == '{':
            if depth == 0:
                start_idx = i
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0 and start_idx != -1:
                end_idx = i + 1
                break

    if start_idx == -1 or end_idx == -1:
        raise ValueError("No se encontró JSON válido en la respuesta")

    return response[start_idx:end_idx]

def calculate_token_cost0(model_name, input_tokens, output_tokens):
    if model_name == "llama-3.3-70b-versatile":
        input_price_per_million = 0.59
        output_price_per_million = 0.79
    elif model_name == "llama-3.1-8b-instant":
        input_price_per_million = 0.05
        output_price_per_million = 0.08
    else:
        raise ValueError("Modelo no soportado")

    cost_input = (input_tokens / 1_000_000) * input_price_per_million
    cost_output = (output_tokens / 1_000_000) * output_price_per_million
    total_cost = cost_input + cost_output

    return {
        "input_cost_usd": round(cost_input, 6),
        "output_cost_usd": round(cost_output, 6),
        "total_cost_usd": round(total_cost, 6)
    }

def calculate_token_cost(model_name, input_tokens, output_tokens):
    model_name = model_name.lower()

    match model_name:
        case "llama-3.3-70b-versatile" | "llama3-70b-8192":
            input_price = 0.59 / 1_000_000
            output_price = 0.79 / 1_000_000

        case "llama-3.1-8b-instant" | "llama3-8b-8192":
            input_price = 0.05 / 1_000_000
            output_price = 0.08 / 1_000_000

        case _:
            raise ValueError(f"Modelo no reconocido para cálculo de costos: {model_name}")

    input_cost = input_tokens * input_price
    output_cost = output_tokens * output_price
    total_cost = input_cost + output_cost

    return {
        "input_cost_usd": round(input_cost, 6),
        "output_cost_usd": round(output_cost, 6),
        "total_cost_usd": round(total_cost, 6)
    }


def get_dq_recommendation(dimensions: dict, problems: dict, context: dict) -> dict:
    """Obtiene un DQ Factor sugerido"""
    try:
        #print(f"[Intento {attempt}] Generando recomendación...")

        prompt = DQ_RECOMMENDATION_PROMPT.format(
            dimensions_and_factors=json.dumps(dimensions, indent=2),
            dq_problems=json.dumps(problems, indent=2),
            context_components=json.dumps(context, indent=2)
        )

        response = llm.invoke([HumanMessage(content=prompt)])
        
        # Extraer toda la metadata de tokens
        token_usage = response.response_metadata.get('token_usage', {})
        usage_metadata = getattr(response, 'usage_metadata', {})
        
        # Unificar toda la información de tokens
        tokens_info = {
            "prompt_tokens": token_usage.get('prompt_tokens', 0),
            "completion_tokens": token_usage.get('completion_tokens', 0),
            "total_tokens": token_usage.get('total_tokens', 0),
            "input_tokens": usage_metadata.get('input_tokens', 0),
            "output_tokens": usage_metadata.get('output_tokens', 0),
            "total_tokens_alt": usage_metadata.get('total_tokens', 0),
            "prompt_time": token_usage.get('prompt_time', 0),
            "completion_time": token_usage.get('completion_time', 0),
            "total_time": token_usage.get('total_time', 0),
            "queue_time": token_usage.get('queue_time', 0)
        }
        
        json_str = extract_json_from_response(response.content)

        try:
            result = json.loads(json_str)
        except json.JSONDecodeError:
            lines = json_str.split('\n')
            cleaned = [line.split('//')[0].strip() for line in lines if line.strip() and not line.strip().startswith('//')]
            result = json.loads('\n'.join(cleaned))

        required_fields = [
            "recommended_dimension",
            "recommended_factor",
            "supported_by_problems",
            "supported_by_context",
            "rationale"
        ]
        if not all(field in result for field in required_fields):
            raise ValueError("Respuesta incompleta del modelo")
        
        # Añadir toda la información de tokens y metadata al resultado
        result.update({
            "tokens_used": tokens_info,
            "model_metadata": {
                "model_name": response.response_metadata.get('model_name'),
                "finish_reason": response.response_metadata.get('finish_reason')
            },
        })

        return result

    except Exception as e:
        #print(f"⚠️ Error en intento {attempt}: {e}")
        #if attempt < MAX_RETRIES:
        #    time.sleep(RETRY_BACKOFF ** attempt)
        #else:
        return {"error": str(e)}


NUM_GLOBAL_RUNS = 1  # Número de ejecuciones globales

if __name__ == "__main__":
    for run_id in range(1, NUM_GLOBAL_RUNS + 1):
        print(f"\n\n=== 🔁 EJECUCIÓN GLOBAL #{run_id} ===")
        
        # Copiamos las dimensiones y factores para no modificar el original
        remaining_dimensions = {
            k: {"semantic": v["semantic"], "factors": v["factors"].copy()}
            for k, v in dimensions_and_factors.items()
        }

        # Estructura para registrar el orden de recomendación de factores
        factor_order_tracking = {
            dimension: {factor: 0 for factor in factors["factors"].keys()}
            for dimension, factors in dimensions_and_factors.items()
        }

        # Métricas agregadas
        stats = {
            "total_recommendations": 0,
            "total_executions": 0,
            "total_tokens": {
                "prompt": 0,
                "completion": 0,
                "total": 0,
                "time": 0
            },
            "total_cost_usd": {
                "input_cost_usd": 0.0,
                "output_cost_usd": 0.0,
                "total_cost_usd": 0.0
            },
            "recommendations": [],
            "factor_recommendation_order": []  # Nuevo campo para registrar el orden
        }

        print("Iniciando generación de recomendaciones con tracking de tokens...\n")

        while True:
            remaining_factors = sum(len(d['factors']) for d in remaining_dimensions.values())
            if remaining_factors == 0:
                print("\n✅ Todos los factores han sido recomendados.")
                break

            print(f"\n🔍 Factores restantes: {remaining_factors}")
            print("=" * 50)

            # Variables para acumular métricas por recomendación
            rec_metrics = {
                "executions": 0,
                "tokens": {
                    "prompt": 0,
                    "completion": 0,
                    "total": 0,
                    "time": 0
                }
            }
            
            recommendation = None
            start_time = time.time()

            while not recommendation or "error" in recommendation:
                rec_metrics["executions"] += 1
                stats["total_executions"] += 1
                
                print(f"Ejecución {rec_metrics['executions']} para esta recomendación...")
                
                current_rec = get_dq_recommendation(
                    remaining_dimensions,
                    dq_problems_es, 
                    context_components_es
                )
                    
                # Si es exitosa, procesar tokens
                recommendation = current_rec
                tokens = recommendation.get("tokens_used", {})
                
                rec_metrics["tokens"]["prompt"] += tokens.get("prompt_tokens", 0)
                rec_metrics["tokens"]["completion"] += tokens.get("completion_tokens", 0)
                rec_metrics["tokens"]["total"] += tokens.get("total_tokens", 0)
                rec_metrics["tokens"]["time"] += tokens.get("total_time", 0)

            if not recommendation:
                continue

            # Actualizar estadísticas globales
            stats["total_recommendations"] += 1
            
            for token_type in ["prompt", "completion", "total"]:
                stats["total_tokens"][token_type] += rec_metrics["tokens"][token_type]
            stats["total_tokens"]["time"] += rec_metrics["tokens"]["time"]
            
            # Calcular costo para esta recomendación
            rec_cost = calculate_token_cost(
                model_name=MODEL_NAME,
                input_tokens=rec_metrics["tokens"]["prompt"],
                output_tokens=rec_metrics["tokens"]["completion"]
            )
            
            # Calcular promedios por recomendación
            recommendation.update({
                "executions_needed": rec_metrics["executions"],  
                "total_time": rec_metrics["tokens"]["time"] * rec_metrics["executions"],
                "token_cost_usd": rec_cost
            })
            
            # Acumular costos globales
            for k in ["input_cost_usd", "output_cost_usd", "total_cost_usd"]:
                stats["total_cost_usd"][k] += rec_cost[k]

            # Mostrar métricas
            print(f"\n⭐ Recomendación #{stats['total_recommendations']}")
            print(f"📊 Tokens: {rec_metrics['tokens']['prompt']} (prompt) + {rec_metrics['tokens']['completion']} (completion)")
            print(f"⏱️ Tiempo: {rec_metrics['tokens']['time']:.2f}s total")
            print(json.dumps({k:v for k,v in recommendation.items() if k not in ['tokens_used']}, indent=2))

            # Registrar el orden de recomendación
            dim = recommendation['recommended_dimension']
            factor = recommendation['recommended_factor']
            
            # Registrar el orden en que fue recomendado este factor
            recommendation_order = stats["total_recommendations"]
            factor_order_tracking[dim][factor] = recommendation_order
            stats["factor_recommendation_order"].append({
                "order": recommendation_order,
                "dimension": dim,
                "factor": factor,
                "timestamp": datetime.now().isoformat()
            })

            # Eliminar factor recomendado
            if dim in remaining_dimensions and factor in remaining_dimensions[dim]['factors']:
                del remaining_dimensions[dim]['factors'][factor]
                if not remaining_dimensions[dim]['factors']:
                    del remaining_dimensions[dim]

            stats["recommendations"].append(recommendation)

        # Resumen final con métricas de tokens
        print("\n" + "="*50)
        print("📊 Resumen final de métricas:")
        print(f"- Recomendaciones generadas: {stats['total_recommendations']}")
        print(f"- Ejecuciones totales: {stats['total_executions']}")
        print("\n🔍 Uso de tokens:")
        print(f"  Prompt: {stats['total_tokens']['prompt']} (avg {stats['total_tokens']['prompt']/stats['total_executions']:.1f}/ejecución)")
        print(f"  Completion: {stats['total_tokens']['completion']} (avg {stats['total_tokens']['completion']/stats['total_executions']:.1f}/ejecución)")
        print(f"  Total: {stats['total_tokens']['total']} tokens")
        print(f"\n⏱️ Tiempo total: {stats['total_tokens']['time']:.2f}s")
        print(f"  Avg: {stats['total_tokens']['time']/stats['total_executions']:.2f}s/ejecución")
        print(f"\n💰 Costo total estimado:")
        print(f"  - Input: ${stats['total_cost_usd']['input_cost_usd']:.6f}")
        print(f"  - Output: ${stats['total_cost_usd']['output_cost_usd']:.6f}")
        print(f"  - Total: ${stats['total_cost_usd']['total_cost_usd']:.6f}")

        # Mostrar orden de recomendación de factores
        print("\n📝 Orden de recomendación de factores:")
        for dim, factors in factor_order_tracking.items():
            print(f"\nDimensión: {dim}")
            for factor, order in factors.items():
                print(f"  - {factor}: {'No recomendado' if order == 0 else f'Recomendado #{order}'}")

        # Guardar resultados
        output = {
            **stats,
            "factor_recommendation_order_details": factor_order_tracking,  # Añadir el tracking detallado
            "average_metrics": {
                "executions_per_recommendation": stats["total_executions"] / stats["total_recommendations"],
                "tokens_per_recommendation": {
                    "prompt": stats["total_tokens"]["prompt"] / stats["total_recommendations"],
                    "completion": stats["total_tokens"]["completion"] / stats["total_recommendations"],
                    "total": stats["total_tokens"]["total"] / stats["total_recommendations"]
                },
                "time_per_recommendation": stats["total_tokens"]["time"] / stats["total_recommendations"]
            },
            "cost_summary_usd": {
                "input_cost_usd": round(stats["total_cost_usd"]["input_cost_usd"], 6),
                "output_cost_usd": round(stats["total_cost_usd"]["output_cost_usd"], 6),
                "total_cost_usd": round(stats["total_cost_usd"]["total_cost_usd"], 6)
            }
        }

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ai_eval_results/dq_factors_recommendations_{MODEL_NAME}_{timestamp}_temp{TEMPERATURE}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Resultados guardados en {filename}")


if __name__ != "__main__":

    # Copiamos las dimensiones y factores para no modificar el original
    remaining_dimensions = {
        k: {"semantic": v["semantic"], "factors": v["factors"].copy()}
        for k, v in dimensions_and_factors.items()
    }

    # Métricas agregadas
    stats = {
        "total_recommendations": 0,
        "total_executions": 0,
        "total_tokens": {
            "prompt": 0,
            "completion": 0,
            "total": 0,
            "time": 0
        },
        "total_cost_usd": {
            "input_cost_usd": 0.0,
            "output_cost_usd": 0.0,
            "total_cost_usd": 0.0
        },
        "recommendations": []
    }

    print("Iniciando generación de recomendaciones con tracking de tokens...\n")

    while True:
        remaining_factors = sum(len(d['factors']) for d in remaining_dimensions.values())
        if remaining_factors == 0:
            print("\n✅ Todos los factores han sido recomendados.")
            break

        print(f"\n🔍 Factores restantes: {remaining_factors}")
        print("=" * 50)

        # Variables para acumular métricas por recomendación
        rec_metrics = {
            "executions": 0,
            "tokens": {
                "prompt": 0,
                "completion": 0,
                "total": 0,
                "time": 0
            }
        }
        
        recommendation = None
        start_time = time.time()

        while not recommendation or "error" in recommendation:
            rec_metrics["executions"] += 1
            stats["total_executions"] += 1
            
            print(f"Ejecución {rec_metrics['executions']} para esta recomendación...")
            
            current_rec = get_dq_recommendation(
                remaining_dimensions,
                dq_problems_en, 
                context_components_en
            )
                
            # Si es exitosa, procesar tokens
            recommendation = current_rec
            tokens = recommendation.get("tokens_used", {})
            
            rec_metrics["tokens"]["prompt"] += tokens.get("prompt_tokens", 0)
            rec_metrics["tokens"]["completion"] += tokens.get("completion_tokens", 0)
            rec_metrics["tokens"]["total"] += tokens.get("total_tokens", 0)
            rec_metrics["tokens"]["time"] += tokens.get("total_time", 0)

        if not recommendation:
            continue

        # Actualizar estadísticas globales
        stats["total_recommendations"] += 1
        
        for token_type in ["prompt", "completion", "total"]:
            stats["total_tokens"][token_type] += rec_metrics["tokens"][token_type]
        stats["total_tokens"]["time"] += rec_metrics["tokens"]["time"]
        
        # Calcular costo para esta recomendación
        rec_cost = calculate_token_cost(
            model_name=MODEL_NAME,
            input_tokens=rec_metrics["tokens"]["prompt"],
            output_tokens=rec_metrics["tokens"]["completion"]
        )
        
        # Calcular promedios por recomendación
        recommendation.update({
            "executions_needed": rec_metrics["executions"],  
            #"avg_tokens_per_attempt": {
            #    "prompt": rec_metrics["tokens"]["prompt"] / rec_metrics["executions"],
            #    "completion": rec_metrics["tokens"]["completion"] / rec_metrics["executions"],
            #    "total": rec_metrics["tokens"]["total"] / rec_metrics["executions"]
            #},
            "total_time": rec_metrics["tokens"]["time"] * rec_metrics["executions"],
            #"avg_time_per_attempt": rec_metrics["tokens"]["time"] / rec_metrics["executions"]
            "token_cost_usd": rec_cost
        })
        
        # Acumular costos globales
        for k in ["input_cost_usd", "output_cost_usd", "total_cost_usd"]:
            stats["total_cost_usd"][k] += rec_cost[k]

        # Mostrar métricas
        print(f"\n⭐ Recomendación #{stats['total_recommendations']}")
        print(f"📊 Tokens: {rec_metrics['tokens']['prompt']} (prompt) + {rec_metrics['tokens']['completion']} (completion)")
        print(f"⏱️ Tiempo: {rec_metrics['tokens']['time']:.2f}s total")
        print(json.dumps({k:v for k,v in recommendation.items() if k not in ['tokens_used']}, indent=2))

        # Eliminar factor recomendado
        dim = recommendation['recommended_dimension']
        factor = recommendation['recommended_factor']
        if dim in remaining_dimensions and factor in remaining_dimensions[dim]['factors']:
            del remaining_dimensions[dim]['factors'][factor]
            if not remaining_dimensions[dim]['factors']:
                del remaining_dimensions[dim]

        stats["recommendations"].append(recommendation)

    # Resumen final con métricas de tokens
    print("\n" + "="*50)
    print("📊 Resumen final de métricas:")
    print(f"- Recomendaciones generadas: {stats['total_recommendations']}")
    print(f"- Ejecuciones totales: {stats['total_executions']}")
    print("\n🔍 Uso de tokens:")
    print(f"  Prompt: {stats['total_tokens']['prompt']} (avg {stats['total_tokens']['prompt']/stats['total_executions']:.1f}/ejecución)")
    print(f"  Completion: {stats['total_tokens']['completion']} (avg {stats['total_tokens']['completion']/stats['total_executions']:.1f}/ejecución)")
    print(f"  Total: {stats['total_tokens']['total']} tokens")
    print(f"\n⏱️ Tiempo total: {stats['total_tokens']['time']:.2f}s")
    print(f"  Avg: {stats['total_tokens']['time']/stats['total_executions']:.2f}s/ejecución")
    print(f"\n💰 Costo total estimado:")
    print(f"  - Input: ${stats['total_cost_usd']['input_cost_usd']:.6f}")
    print(f"  - Output: ${stats['total_cost_usd']['output_cost_usd']:.6f}")
    print(f"  - Total: ${stats['total_cost_usd']['total_cost_usd']:.6f}")

    # Guardar resultados
    output = {
        **stats,
        "average_metrics": {
            "executions_per_recommendation": stats["total_executions"] / stats["total_recommendations"],
            "tokens_per_recommendation": {
                "prompt": stats["total_tokens"]["prompt"] / stats["total_recommendations"],
                "completion": stats["total_tokens"]["completion"] / stats["total_recommendations"],
                "total": stats["total_tokens"]["total"] / stats["total_recommendations"]
            },
            "time_per_recommendation": stats["total_tokens"]["time"] / stats["total_recommendations"]
        },
        "cost_summary_usd": {
            "input_cost_usd": round(stats["total_cost_usd"]["input_cost_usd"], 6),
            "output_cost_usd": round(stats["total_cost_usd"]["output_cost_usd"], 6),
            "total_cost_usd": round(stats["total_cost_usd"]["total_cost_usd"], 6)
        }
    }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ai_eval_results/dq_factors_recommendations_{MODEL_NAME}_{timestamp}_temp{TEMPERATURE}_es.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Resultados guardados en {filename}")
