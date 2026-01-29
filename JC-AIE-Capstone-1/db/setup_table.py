import pandas as pd
from sqlalchemy import text

def create_table_from_csv(engine, input_csv_path, table_name):
    try:
        # Check if table exists using INFORMATION_SCHEMA
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT TABLE_NAME 
                    FROM INFORMATION_SCHEMA.TABLES
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = :tbl
                """),
                {"tbl": table_name}
            )
            table_exists = result.scalar() is not None

        # table_exist
        if table_exists:
            print(f"Table '{table_name}' found in database — connecting . . . ")

            df = pd.read_sql(text(f"SELECT * FROM {table_name}"), engine)
            return df

        # incase table not exist
        print(f"Table '{table_name}' not found in database.")
        print("Creating new table...")

        df = pd.read_csv(input_csv_path)
        print(f"Loaded CSV: {len(df)} rows x {len(df.columns)} columns")

        create_choice = input(
            f"Would you like to create table '{table_name}' in the database? (y/n): "
        ).strip().lower()

        if create_choice != 'y':
            print("Table creation cancelled.")
            return None

        df.to_sql(
            name=table_name,
            con=engine,
            if_exists="replace",
            index=False
        )
        print(f"Table '{table_name}' created successfully.")
        return df

    except Exception as e:
        print(f"Error in create_table_from_csv: {e}")
        return None


def list_tables(engine):
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result]
            print("\nTables in database:", tables)
            return tables
    except Exception as e:
        print(f"Error listing tables: {e}")
        return []
