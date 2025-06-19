import json
import logging
import random
import time
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage
from decouple import config

# Configuración de logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Configuración de API y modelo
#GROQ_API_KEY = "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"
GROQ_API_KEY = config('GROQ_API_KEY')
print("GROQ_API_KEY:", GROQ_API_KEY)

MODEL_NAME = "llama-3.3-70b-versatile" #"llama-3.1-8b-instant" 


TEMPERATURE = 0.3

# Inicialización del cliente LLM
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name=MODEL_NAME,
    temperature=TEMPERATURE
)

MAX_RETRIES = 5
RETRY_BACKOFF = 2  # segundos

# ==============================================
# DATOS DE EJEMPLO - ESTRUCTURAS DE REFERENCIA
# 
# Estas estructuras muestran el formato esperado.
# En producción serán reemplazadas por datos reales.
# ==============================================
DIMENSIONS_AND_FACTORS = {
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

# Ejemplo de problemas (serán dinámicos en producción)
DQ_PROBLEMS_EXAMPLE = {
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

# =====================================================================
# COMPONENTES DE CONTEXTO (VERSIÓN ABREVIADA)
#
# Nota: Las claves y campos están abreviados para minimizar el uso de 
# tokens en las llamadas al LLM. En el código se expanden a su forma 
# completa mediante expand_context_components() antes de ser utilizados.
#
# Estructura abreviada vs completa:
#   - appDomain  → applicationDomain
#   - n          → name
#   - s          → statement
#   - p          → path
#   - etc...
# =====================================================================
# Ejemplo de contexto (estructura variable por caso de uso)
CONTEXT_COMPONENTS_EXAMPLE = {
    "appDomain": [
        {"n": "Digital Publishing and Book Recommendation", "id": 1}
    ],
    "bizRule": [
        {
            "s": "A rating must be associated with a valid user and a valid book",
            "id": 2,
            "sem": "Ensures referential integrity"
        }
    ],
    "dataFilter": [
        {
            "s": "Only consider reviews from users with more than 5 reviews",
            "id": 3,
            "desc": "Reduce noise from inactive users",
            "task": 11
        },
        {
            "s": "Exclude books with less than 10 ratings",
            "id": 4,
            "desc": "Focus on books with sufficient feedback",
            "task": 11
        }
    ],
    "dqMeta": [
        {
            "p": "/path/to/dqmetadata/ratings_dq.json",
            "id": 5,
            "desc": "DQ metrics for ratings",
            "meas": "Completeness, validity, uniqueness"
        }
    ],
    "dqReq": [
        {
            "s": "Rating values must be numeric and in the range 1-5",
            "id": 6,
            "desc": "Valid range for book ratings",
            "dataFilterIds": [3, 4],
            "userTypeId": 12
        }
    ],
    "otherData": [
        {
            "p": "/path/to/otherdata/book_covers.zip",
            "id": 7,
            "desc": "Images of book covers",
            "own": "Content department"
        }
    ],
    "otherMeta": [
        {
            "p": "/path/to/othermetadata/books_schema.json",
            "id": 8,
            "desc": "Schema definition for books",
            "auth": "Data engineering team",
            "lastUpd": 1713744000
        }
    ],
    "sysReq": [
        {
            "s": "System must handle large datasets efficiently (up to 3GB)",
            "id": 10,
            "desc": "Performance and scalability"
        }
    ],
    "task": [
        {
            "n": "Book Recommendation",
            "id": 11,
            "purp": "Recommend books based on ratings and metadata"
        }
    ],
    "userType": [
        {
            "n": "Reader",
            "id": 12,
            "char": "Users who rate and review books"
        },
        {
            "n": "System Administrator",
            "id": 13,
            "char": "Maintains database quality"
        },
        {
            "n": "Data Analyst",
            "id": 14,
            "char": "Explores data trends"
        }
    ]
}


# =================
# PROMPT TEMPLATES
# =================
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


# =================
# UTILS, HELPERS
# =================
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


def expand_context_components(abbreviated: dict) -> dict:
    """Expande los componentes de contexto abreviados a su forma completa"""
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


# ===========================
# ALGORITMO RECOMENDACIONES
# ===========================
def generate_ai_dq_factor_recommendation(dimensions: dict, problems: dict, context: dict) -> dict:
    """
    Obtiene recomendación de calidad de datos (DQ Dimension, DQ Factor) con manejo de errores y reintentos
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"Intento {attempt} - Generando recomendación...")
            prompt = DQ_RECOMMENDATION_PROMPT.format(
                dimensions_and_factors=json.dumps(dimensions, indent=2),
                dq_problems=json.dumps(problems, indent=2),
                context_components=json.dumps(context, indent=2)
            )
            
            # Obtener respuesta del modelo
            response = llm.invoke([HumanMessage(content=prompt)]).content
            
            # Procesar la respuesta
            json_str = extract_json_from_response(response)

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

            return result

        except Exception as e:
            logger.warning(f"Error en intento {attempt}: {str(e)}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF ** attempt)
            else:
                return {"error": str(e)}


# =============
# PUNTO DE ENTRADA
# =============
if __name__ == "__main__":
    recommendation = generate_ai_dq_factor_recommendation(
        DIMENSIONS_AND_FACTORS,
        DQ_PROBLEMS_EXAMPLE,
        CONTEXT_COMPONENTS_EXAMPLE
    )
    print(json.dumps(recommendation, indent=2, ensure_ascii=False))