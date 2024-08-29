import os
from typing import Any
from groq import Groq
import json

import database

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def human_query_to_sql(human_query: str):
    #1.1 Paso-> obtenemos el esquema de la base de datos
    database_schema = database.get_schema()

    #Agregamos el system message para que el LLM sepa que es lo que queremos hacer
    system_message = f"""
    Given the following schema, write a SQL query that retrieves the requested information.
    Important: Return the SQL query inside a JSON structure with the key 'sql_query'.
    <example>
    {{
        "sql_query": "SELECT * FROM users WHERE age > 18;"
        "original_query": "Show me all users older than 18 years old."
    }}
    </example>
    <schema>
    {database_schema}
    </schema>
    """
    
    user_message = human_query
    
    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        #response_format={"type": "json_object"}, #Parseo usado por openAI
        messages=[{
            "role": "system",
            "content": system_message,
        }, {
            "role": "user",
            "content": user_message,
        }],
        max_tokens=1024,
    )
    
    sql_query = response.choices[0].message.content
    print("Raw response:", sql_query)
    sql_query = extraer_json(sql_query)
    # if '```' in sql_query:
    #     sql_query = sql_query.split('```json\n')[1].split('\n```\n')[0]
    #     sql_query = sql_query.strip('```')
    print("JSON response:", sql_query)
    return sql_query

async def build_answer(result: list[dict[str, Any]], human_query: str)-> str | None:
    
    system_message = f"""
    Given a users question and the SQL rows response from the database from which the user wants to get the answer,
    write a response to the user's question.
    <user_question>
    {human_query}
    </user_question>
    <sql_response>
    ${result}
    </sql_response>
    """
    
    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[{
            "role": "system",
            "content": system_message,
        }],
        max_tokens=1024,
    )
    
    return response.choices[0].message.content

def extraer_json(texto):
    # Encuentra la posición del primer '{' y del último '}'
    inicio_json = texto.find('{')
    fin_json = texto.rfind('}')

    # Extrae la parte del JSON
    if inicio_json != -1 and fin_json != -1:
        json_str = texto[inicio_json:fin_json + 1]
        try:
            # Intenta cargar el JSON para asegurar que es válido
            json_data = json.loads(json_str)
            return json_data
        except json.JSONDecodeError:
            return "Error: JSON no válido."
    else:
        return "Error: No se encontró un JSON en el texto."