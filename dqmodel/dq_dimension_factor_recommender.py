from langchain_groq import ChatGroq
from langchain.schema import HumanMessage
import json
import logging

# Configuración silenciosa (solo errores)
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Configuración de Groq
GROQ_API_KEY = "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"
MODEL_NAME = "llama3-8b-8192"

# Cliente LLM
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name=MODEL_NAME,
    temperature=0.6
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

context_components = {
    "DB": "Transactional database",
    "ETL": "Data processing pipelines",
    "BI": "Business intelligence tools"
}

context_components_abbr = {
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

# Prompt Template mejorado
DQ_RECOMMENDATION_PROMPT0 = """As a data quality expert, analyze these components and return ONLY a JSON object with:

1. The most relevant DQ dimension and factor
2. Supporting evidence from problems and context
3. A concise rationale

Available Dimensions and Factors:
{dimensions_and_factors}

Data Quality Problems:
{dq_problems}

System Context:
{context_components}

Return EXACTLY this JSON structure (no other text):
{{
    "recommended_dimension": "dimension_name",
    "recommended_factor": "factor_name",
    "supported_by_problems": [problem_id1, problem_id2],
    "supported_by_context": ["context_component1", "context_component2"],
    "rationale": "Concise explanation linking problems (by mentioning problem description, no id) and context to the recommendation"
}}"""

DQ_RECOMMENDATION_PROMPT_bckp = """As a data quality expert, analyze these components and return ONLY a JSON object with:

1. The most relevant DQ dimension and factor
2. Choose ONLY THE STRONGEST supporting evidence (max 3 problems, 3 context elements) and
3. A concise rationale

Available Dimensions and Factors:
{dimensions_and_factors}

Data Quality Problems:
{dq_problems}

System Context:
{context_components}

Return EXACTLY this JSON structure (no other text):
{{
    "recommended_dimension": "dimension_name",
    "recommended_factor": "factor_name",
    "supported_by_problems": [problem_id1, problem_id2],  // Max 3
    "supported_by_context": [
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
    ],  // Max 5
    "rationale": "Concise explanation linking problems (by mentioning problem description, no id) and context to the recommendation"
}}"""

DQ_RECOMMENDATION_PROMPT__ = """As a data quality expert, analyze these components and return ONLY a JSON object with:

1. The most relevant DQ dimension and factor
2. Choose ONLY THE STRONGEST supporting evidence (max 3 problems, 3 context elements) and
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
    "supported_by_problems": [problem_id1, problem_id2],  // Max 3
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
    }},  // Max 5
    "rationale": "Concise explanation linking problems (by mentioning problem description, no id) and context to the recommendation"
}}

IMPORTANT: Return ONLY the JSON object, no explanations, headers, or any other text."""


DQ_RECOMMENDATION_PROMPT = """As a data quality expert, analyze these components and return ONLY a JSON object with:

1. The most relevant DQ dimension and factor
2. Choose ONLY THE STRONGEST supporting evidence (max 3 problems, 3 context elements) and
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
    "supported_by_problems": [problem_id1, problem_id2],  // Max 3
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
    }},  // Max 5
    "rationale": "Concise explanation linking problems (by mentioning problem description, no id) and context to the recommendation"
}}

IMPORTANT: 
- Return ONLY the JSON object, no explanations, headers, or any other text.
- "Try to avoid repeating previously recommended factors, and consider alternative factors if similarly supported."
- "Your goal is to recommend a DQ factor that is both well-supported AND not previously selected, to encourage coverage across dimensions."
"""

DQ_RECOMMENDATION_PROMPT = """As a data quality expert, analyze these components and return ONLY a JSON object with:

1. The most relevant DQ dimension and factor
2. Choose ONLY THE STRONGEST supporting evidence (max 3 problems, 3 context elements) and
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
    "supported_by_problems": [problem_id1, problem_id2],  // Max 3
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
    }},  // Max 5
    "rationale": "Provide a clear, concise yet detailed explanation that links the selected problem descriptions and context component values to the recommended dimension and factor. Avoid using IDs or references like '(problem 1)'."
}}

IMPORTANT: 
- Return ONLY the JSON object, no explanations, headers, or any other text.
- "Try to avoid repeating previously recommended factors, and consider alternative factors if similarly supported."
- "Your goal is to recommend a DQ factor that is both well-supported AND not previously selected, to encourage coverage across dimensions."
"""

# "rationale": "Concise explanation linking problems (by mentioning problem description, no id) and context to the recommendation"


DQ_RECOMMENDATION_PROMPTv2 = """As a data quality expert, analyze these components and return ONLY a JSON object with:

1. The most relevant DQ dimension and factor
2. Choose THE STRONGEST supporting evidence and
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


import random
import time

MAX_RETRIES = 5
RETRY_BACKOFF = 2  # segundos

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


def get_dq_recommendation(dimensions: dict, problems: dict, context: dict) -> dict:
    """Obtiene recomendación de calidad de datos con reintentos y entradas aleatorias para más diversidad"""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"[Intento {attempt}] Generando recomendación...")

            #shuffled_problems = dict(random.sample(list(problems.items()), len(problems)))
            #shuffled_context = shuffle_input_dict(context)

            prompt = DQ_RECOMMENDATION_PROMPT.format(
                dimensions_and_factors=json.dumps(dimensions, indent=2),
                dq_problems=json.dumps(problems, indent=2),
                context_components=json.dumps(context, indent=2)
            )

            response = llm.invoke([HumanMessage(content=prompt)]).content
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
            print(f"⚠️ Error en intento {attempt}: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF ** attempt)
            else:
                return {"error": str(e)}

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

def get_dq_recommendation2(dimensions: dict, problems: dict, context: dict) -> dict:
    """Obtiene recomendación de calidad de datos con reintentos y entradas aleatorias para más diversidad"""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"[Intento {attempt}] Generando recomendación...")

            prompt = DQ_RECOMMENDATION_PROMPT.format(
                dimensions_and_factors=json.dumps(dimensions, indent=2),
                dq_problems=json.dumps(problems, indent=2),
                context_components=json.dumps(context, indent=2)
            )

            response = llm.invoke([HumanMessage(content=prompt)]).content
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

            # Reemplazar el contexto abreviado con su versión expandida
            result["supported_by_context"] = expand_context_components(result["supported_by_context"])

            return result

        except Exception as e:
            print(f"⚠️ Error en intento {attempt}: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF ** attempt)
            else:
                return {"error": str(e)}



def shuffle_input_dict(d):
    """Devuelve una copia del diccionario con los elementos internos mezclados"""
    return {k: random.sample(v, len(v)) if isinstance(v, list) else v for k, v in d.items()}


def get_dq_recommendation0(dimensions: dict, problems: dict, context: dict) -> dict:
    """Obtiene recomendación de calidad de datos con reintentos y entradas aleatorias para más diversidad"""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"[Intento {attempt}] Generando recomendación...")

            # Aleatorizar problemas y componentes de contexto para diversidad
            shuffled_problems = dict(random.sample(list(problems.items()), len(problems)))
            shuffled_context = shuffle_input_dict(context)

            prompt = DQ_RECOMMENDATION_PROMPT.format(
                dimensions_and_factors=json.dumps(dimensions, indent=2),
                dq_problems=json.dumps(shuffled_problems, indent=2),
                context_components=json.dumps(shuffled_context, indent=2)
            )

            response = llm.invoke([HumanMessage(content=prompt)]).content

            # Extraer JSON manualmente (robusto)
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

            json_str = response[start_idx:end_idx]

            # Intentar parsear
            try:
                result = json.loads(json_str)
            except json.JSONDecodeError:
                lines = json_str.split('\n')
                cleaned = []
                for line in lines:
                    if '//' in line:
                        line = line.split('//')[0]
                    if line.strip():
                        cleaned.append(line)
                cleaned_json = '\n'.join(cleaned)
                result = json.loads(cleaned_json)

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
            print(f"⚠️ Error en intento {attempt}: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF ** attempt)
            else:
                return {"error": str(e)}



if __name__ == "__main__":
    # Ejecutar y mostrar solo el resultado
    recommendation = get_dq_recommendation(
        dimensions_and_factors,
        dq_problems,
        context_components_abbr
    )
    
    # Salida limpia en JSON
    print(json.dumps(recommendation, indent=2, ensure_ascii=False))