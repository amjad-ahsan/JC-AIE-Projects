import pandas as pd
from sqlalchemy import text


# C Create

def add_crud(engine, table_name):
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

        rows = result.fetchall()
        columns = []

        for row in rows:
            column_name = row[0]
            data_type = row[1]
            columns.append((column_name, data_type))

        return columns



def c_crud_loop(columns):
    values = {}

    for name, dtype in columns:
        user_input = input(f"Enter {name} ({dtype}): ")

        type_checker = dtype.upper()

        if "INT" in type_checker and "TINYINT(1)" not in type_checker: #Interger
            val = int(user_input) if user_input else None

        elif any(x in type_checker for x in ["DOUBLE", "FLOAT", "DECIMAL"]): # Float
            val = float(user_input) if user_input else None

        elif "BOOL" in type_checker or "TINYINT(1)" in type_checker:
            val = int(user_input) if user_input else None   # 0 and 1

        else:
            val = user_input if user_input else None # Else

        values[name] = val

    return values


def c_commit(engine, table_name, values):
    columns = ", ".join(values.keys())
    placeholders = ", ".join([f":{col}" for col in values.keys()])

    query = text(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})")

    with engine.connect() as conn:
        conn.execute(query, values)
        conn.commit()

    print("\n Row inserted successfully\n")


def create_c(engine, table_name):
    columns = add_crud(engine, table_name)

    if not columns:
        print("Table not found or no columns detected.")
        return

    print(f"\n Adding new row to table: {table_name}")
    print("Leave input empty to insert NULL.\n")

    values = c_crud_loop(columns)
    c_commit(engine, table_name, values)

# R Read

def read_r(engine, table_name):
    try:
        print("\n READ OPTIONS")
        print("1 Show all rows")
        print("2 Filter WHERE column = value")
        print("3 Show first N rows (LIMIT)")

        choice = input("Enter choice (1-3): ").strip()

        with engine.connect() as conn:

            # Show all
            if choice == "1":

                query = f"SELECT * FROM {table_name}"

                result = conn.execute(text(query))
                rows = result.fetchall()
                df = pd.DataFrame(rows, columns=result.keys())
                print(f"\nTotal rows: {len(df)}")
                print(df)
                return df

            # filtered
            elif choice == "2":
                col = input("Column name: ").strip()
                val = input(f"Value for {col}: ").strip()

                if col == "":
                    print(" Column cannot be empty")
                    return

                query = f"SELECT * FROM {table_name} WHERE {col} = :value"

                params = {"value": val}
                result = conn.execute(text(query), params)
                rows = result.fetchall()
                df = pd.DataFrame(rows, columns=result.keys())
                print(f"\nFound {len(df)} rows")
                print(df)
                return df

            elif choice == "3":
                limit = int(input("How many rows? ").strip())
                
                query = f"SELECT * FROM {table_name} LIMIT :limit"

                params = {"limit": limit}
                result = conn.execute(text(query), params)
                rows = result.fetchall()
                df = pd.DataFrame(rows, columns=result.keys())
                print(df)
                return df

            else:
                print(" Invalid choice")

    except Exception as e:
        print(f" Error while reading: {e}")



# U update

def update_u(engine, table_name):
    try:
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
            columns = [row[0] for row in result.fetchall()]

        if not columns:
            print("Could not retrieve table structure.")
            return

        print("\nUPDATE OPTIONS")
        print("1 Update a single column")
        print("2 Update multiple columns")#Columns not Rows
        choice = input("Enter choice (1-2): ").strip()

        print("\nAvailable columns:", columns)

        with engine.connect() as conn:

            # ONE rows FOR ALL columns
            if choice == "1":
                target_col = input("Enter Column to Update: ").strip()
                if target_col not in columns:
                    print("Invalid column name.")
                    return

                new_val = input(f"New value for {target_col}: ").strip()

                cond_col = input("Enter Condition Column(WHERE): ").strip()
                if cond_col not in columns:
                    print("Invalid condition column.")
                    return

                cond_val = input(f"Value for {cond_col}: ").strip()

                result = conn.execute(
                    text(f"""
                        UPDATE {table_name}
                        SET {target_col} = :new_val
                        WHERE {cond_col} = :cond_val
                    """),
                    {"new_val": new_val, "cond_val": cond_val}
                )
                conn.commit()

                print(f"\nUpdated {result.rowcount} row(s).")

                # Preview
                preview = conn.execute(
                    text(f"SELECT * FROM {table_name} WHERE {target_col} = :new_val"),
                    {"new_val": new_val}
                )
                df = pd.DataFrame(preview.fetchall(), columns=preview.keys())
                print("\nPreview after update:")
                print(df.head() if not df.empty else "No rows match the updated value.")

            # ALL rows FOR ONE COLUMN
            elif choice == "2":
                print("\nEnter columns to update (press ENTER without column to finish):")

                set_clauses = []
                params = {}

                while True:
                    col = input("Enter Column to Update: ").strip()
                    if not col:
                        break
                    if col not in columns:
                        print("Invalid column name, try again.")
                        continue
                    val = input(f"New value for {col}: ")
                    set_clauses.append(f"{col} = :{col}")
                    params[col] = val

                if not set_clauses:
                    print("No update columns provided.")
                    return

                cond_col = input("Enter Condition Column(WHERE): ").strip()
                if cond_col not in columns:
                    print("Invalid condition column.")
                    return

                cond_val = input(f"Value for {cond_col}: ").strip()
                params["cond_val"] = cond_val

                query = f"""
                    UPDATE {table_name}
                    SET {', '.join(set_clauses)}
                    WHERE {cond_col} = :cond_val
                """

                result = conn.execute(text(query), params)
                conn.commit()

                print(f"\nUpdated {result.rowcount} row(s).")

                # Preview
                first_updated_col = list(params.keys())[0]  
                preview_val = params[first_updated_col]

                preview = conn.execute(
                    text(f"SELECT * FROM {table_name} WHERE {first_updated_col} = :preview_val"),
                    {"preview_val": preview_val}
                )
                df = pd.DataFrame(preview.fetchall(), columns=preview.keys())
                print("\nPreview after update:")
                print(df.head() if not df.empty else "No rows match the updated values.")

            else:
                print("Invalid choice.")

    except Exception as e:
        print(f"Error while updating: {e}")



# D Delete

def delete_d(engine, table_name):
    try:
        print("\n DELETE OPTIONS")
        print("1 Delete rows WHERE column = value")
        print("2 Delete ALL rows (TRUNCATE)")
        print("3 DROP table (cannot be undone)")

        choice = input("Enter choice (1-3): ").strip()

        with engine.connect() as conn:

            # delete where
            if choice == "1":
                cond_col = input("Enter Column Condition/WHERE: ").strip()
                cond_val = input(f"Value for {cond_col}: ").strip()

                confirm = input(
                    f" Confirm delete rows where {cond_col} = '{cond_val}'? (y/n): "
                ).strip().lower()

                if confirm != "y":
                    print(" Deletion cancelled.")
                    return

                result = conn.execute(
                    text(f"""
                        DELETE FROM {table_name}
                        WHERE {cond_col} = :cond_val
                    """),
                    {"cond_val": cond_val}
                )
                conn.commit()

                print(f"\n Deleted {result.rowcount} row(s).")


            # All remove
            elif choice == "2":
                confirm = input(
                    f" Confirm remove ALL rows from '{table_name}'? (y/n): "
                ).strip().lower()

                if confirm != "y":
                    print(" Deletion cancelled.")
                    return

                conn.execute(text(f"TRUNCATE TABLE {table_name}"))
                conn.commit()

                print(f"\nAll rows deleted from table '{table_name}'.")


            # DROP TABLE
            elif choice == "3":
                confirm = input(
                    f" CONFIRM DROP TABLE '{table_name}' forever? (y/n): "
                ).strip().lower()

                if confirm != "y":
                    print(" Deletion cancelled.")
                    return

                conn.execute(text(f"DROP TABLE {table_name}"))
                conn.commit()

                print(f"\n Table '{table_name}' dropped successfully.")
                return "TABLE_DROPPED"   # so main.py


            else:
                print(" Invalid choice.")

    except Exception as e:
        print(f" Error while deleting: {e}")



