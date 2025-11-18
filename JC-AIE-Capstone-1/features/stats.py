import pandas as pd
from sqlalchemy import text

def stats(engine, table_name):
    try:
        # 1numeric print
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_schema = DATABASE()
                    AND table_name = :tbl
                """),
                {"tbl": table_name}
            )
            columns_info = result.fetchall()

        numeric_cols = [
            col for col, dtype in columns_info
            if any(num in dtype.upper() for num in ["INT", "DECIMAL", "FLOAT", "DOUBLE", "REAL"])
        ]

        if not numeric_cols:
            print("\nNo numeric columns available for statistics.")
            return

        print("\nAvailable numeric columns:")
        for col in numeric_cols:
            print("-", col)

        selected = input("\nEnter column to analyze: ").strip()

        if selected not in numeric_cols:
            print("Invalid column.")
            return

        # query
        with engine.connect() as conn:
            result = conn.execute(
                text(f"""
                    SELECT 
                        COUNT({selected}) AS count_val,
                        MIN({selected}) AS min_val,
                        MAX({selected}) AS max_val,
                        SUM({selected}) AS sum_val,
                        AVG({selected}) AS avg_val,
                        STDDEV({selected}) AS std_val   -- STDDEV added
                    FROM {table_name}
                """)
            )
            count_val, min_val, max_val, sum_val, avg_val, std_val = result.fetchone()

        # Show Statistics
        print(f"\n Statistics for column: {selected}")
        print(f"Non-null count: {count_val}")
        print(f"Minimum: {min_val}")
        print(f"Maximum: {max_val}")
        print(f"Sum: {sum_val:,}")
        print(f"Mean: {avg_val:.2f}")
        print(f"Standard Deviation: {std_val:.2f}")

    except Exception as e:
        print(f"Error while calculating statistics: {e}")
