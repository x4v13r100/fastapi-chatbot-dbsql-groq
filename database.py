import os
from typing import Any
from typing_extensions import LiteralString
from sqlalchemy import QueuePool, create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

# Configuración de la base de datos para MySQL
DB_USERNAME = os.getenv("DB_USERNAME", "default_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "default_password")
DB_HOST = os.getenv("HOST", "localhost")
DB_NAME = os.getenv("DB_DATABASE", "default_db")

DB_URI = f"mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
#Con postgres
#DB_URI = os.getenv("DATABASE_URI", "default")

engine = create_engine(DB_URI, poolclass=QueuePool, pool_size=5, max_overflow=0)
Session = sessionmaker(bind=engine)

#1.2 Paso-> Funcion que nos permite obtener el esquema de la base de datos
def get_schema()-> LiteralString:
    engine = create_engine(
        DB_URI
    )
    inspector = inspect(engine)
    #table_names = inspector.get_table_names()
    table_names = ['l_pal_polins', 'l_pal_cortes']
    
    def get_column_details(table_name)-> list[str]:
        columns = inspector.get_columns(table_name)
        return[f"{col['name']} {col['type']}" for col in columns]

    schema_info = []
    for table_name in table_names:
        table_info = [f"Table:{table_name}"]
        table_info.append("Columns:")
        table_info.extend(f" - {column}" for column in get_column_details(table_name))
        schema_info.append("\n".join(table_info))
    
    engine.dispose()
    return "\n\n".join(schema_info)

async def query(sql_query: str)-> list[dict[str, Any]]:
    print("sql_query", sql_query)
    try:
        with Session() as session:
            statement = text(sql_query)
            result = session.execute(statement)
            return [dict(row._mapping) for row in result]
    except Exception as e:
        logger.error(f"Database query error: {e}")
        raise HTTPException(status_code=500, detail="Database query failed")

def cleanup()-> None:
    engine.dispose()