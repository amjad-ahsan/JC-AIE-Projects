from sqlalchemy import create_engine, text
import numpy as np
from dotenv import load_dotenv
import os

def coc_db(name_db=None):
    load_dotenv()

    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")
    host = os.getenv("MYSQL_HOST", "localhost")
    port = os.getenv("MYSQL_PORT", "3306")


    # Preventing empty nae 
    if not name_db or name_db.strip() == "":
        print("Database name cannot be empty.")
        return None
    
    try:
        prime_engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/")

        with prime_engine.connect() as conn:
            result = conn.execute(text
                        ("""
                        SELECT SCHEMA_NAME 
                        FROM INFORMATION_SCHEMA.SCHEMATA 
                        WHERE SCHEMA_NAME = :db
                        """),
                        {"db": name_db })
            exist = result.scalar() is not None

            if not exist:
                print(f'Database {name_db} does not exist --- creating new . . .')
                conn.execute(text(f"CREATE DATABASE {name_db}"))  
                conn.commit()
                print(f'Database {name_db} created successfully.')
            else:
                print(f"Database {name_db} already exists.")
        
        # Connecting Engine
        engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{name_db}")
        print(f"Connected to database '{name_db}'")
        return engine

    except Exception as e:
        print(f"Error: {e}")
        return None
    
    

#Complete