import matplotlib.pyplot as plt
from sqlalchemy import text
import pandas as pd

def visual(engine, table_name):
    try:
        # Load entire table
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT * FROM {table_name}"))
            df = pd.DataFrame(result.fetchall(), columns=result.keys())

        if df.empty:
            print("\n No data available for visualization.")
            return
        
        numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
        categorical_cols = df.select_dtypes(include=["object"]).columns.tolist()

        print("\n VISUALIZATION OPTIONS")
        print("1 Histogram (numeric)")
        print("2 Bar plot (categorical)")
        print("3 Pie chart (categorical)")
        choice = input("Enter choice (1-3): ").strip()

        # Histogram
        if choice == "1":
            if not numeric_cols:
                print("\n No numeric columns available for histogram.")
                return

            print("\nNumeric columns:", numeric_cols)
            column = input("Select column for histogram: ").strip()

            if column not in numeric_cols:
                print(" Invalid column.")
                return

            df[column].plot(kind="hist", bins=20)
            plt.title(f"Histogram of {column}")
            plt.xlabel(column)
            plt.ylabel("Frequency")
            plt.show()

        # Bar
        elif choice == "2":
            if not categorical_cols:
                print("\n No categorical columns available for bar plot.")
                return

            print("\nCategorical columns:", categorical_cols)
            column = input("Select column for bar plot: ").strip()

            if column not in categorical_cols:
                print(" Invalid column.")
                return

            df[column].value_counts().plot(kind="bar")
            plt.title(f"Bar plot of {column}")
            plt.xlabel(column)
            plt.ylabel("Count")
            plt.show()

        # PIE
        elif choice == "3":
            if not categorical_cols:
                print("\n No categorical columns available for pie chart.")
                return

            print("\nCategorical columns:", categorical_cols)
            column = input("Select column for pie chart: ").strip()

            if column not in categorical_cols:
                print("\n Invalid column.")
                return

            df[column].value_counts().plot(kind="pie", autopct="%1.1f%%")
            plt.title(f"Pie chart of {column}")
            plt.ylabel("") 
            plt.show()

        else:
            print(" Invalid choice.")
            return


    except Exception as e:
        print(f" Error while generating visualization: {e}")

