import os
import json
import logging
import llm
import database
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

class PostHumanQueryPayload(BaseModel):
    human_query: str

class PostHumanQueryResponse(BaseModel):
    result: list

#endpoint with actions gpt
@app.post(
    "/human_query",
    name="Human Query",
    operation_id="post_human_query",
    description="Get a natural language query, internally convert it to a SQL query, execute the query in the database ,and return the results"
)
async def human_query(payload: PostHumanQueryPayload) -> dict[str,str]:
    # payload.human_query = "Cuales fueron las ventas del mes pasado?"
    # select * from sales where date between '2024-07-01' and '2024-07-31'
    # payload.human_query = "Cuales fue la ultima compra del cliente Javier Mercado?"
    # select max(date) from sales where customer_id in (select id from customers where name like '%Javier Mercado%')
    # 1.Paso-> Para que el LLM sepa cuales son las tablas a consultar debe conocerse el esquema de la base de datos
    
    try:
        #transformamos la query a sql
        sql_query = await llm.human_query_to_sql(payload.human_query)
        if not sql_query:
            raise HTTPException(status_code=400, detail="Invalid query")
        try:
            result_dict = sql_query
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JSON: {str(e)}")
        
        result = await database.query(result_dict['sql_query'])
        #return {"result": result} #Devuelvo el resultado de la consulta en SQL rows
        
        answer = await llm.build_answer(result, payload.human_query) # Devuelvo el resultado en lenguaje natural
        if not answer:
            raise HTTPException(status_code=400, detail="Invalid query")
        
        return {"result": answer}
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error decoding JSON response from LLM")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")