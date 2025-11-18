###########################################
# Import os, Sys. Allows Python to find and import modules from the parent directory 
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

###########################################
# Imports function from different directory

# from db
from db.db import coc_db

#from setup_table
from db.setup_table import create_table_from_csv, list_tables

#from crud
from features.crud import create_c, read_r, update_u, delete_d

# from stats
from features.stats import stats

# from visual
from features.visual import visual

############################
#Non Essential
import pandas as pd
import numpy as np


##########################
# Main
def clear():
    os.system("cls" if os.name == "nt" else "clear")

def main():
    clear()
    engine = None
    table_con = None
    df_con = None

    while True:
        if engine is None:
            input_database = input('Enter database name to CREATE or CONNECT: ').strip()

            if not input_database:
                print("Database name cannot be empty. Please try again.\n")
                continue

            engine = coc_db(input_database)

            if not engine:
                print(f"FAILED TO CONNECT TO DATABASE: {input_database}")
                print("Please try again.\n")
                engine = None
                continue


        # For table
        if table_con is None:
            csv_path = input(r'Press ENTER or provide a CSV path: ').strip() #r to reverse '/' 
            table_name = input('Enter table name to CREATE or CONNECT to a table: ').strip()   

            df_con = create_table_from_csv(engine, csv_path, table_name)
            if df_con is not None:
                table_con = table_name

                print(f'\n Table Active: {table_con}')

                list_tables(engine)
                print("\n Sample data:")

                print(df_con.head(5))


    # main menu 
        print(f'\n Select the index Options Below for {table_con}')
        print('1. Create Row')
        print('2. Read Row')
        print('3. Update Table')
        print('4. Delete Table')
        print('5. Show Statistics')
        print('6. Show Visualization')
        print('7. Connect to a Databse')
        print('8. Exit')


# connection to choicesss
        choice = input('Enter your choice (1-8): ').strip()
        
        if choice == '1':
            create_c(engine, table_con)
            print(input('\nPress ENTER to continue . . . '))
        elif choice == '2':
            read_r(engine, table_con)
            print(input('\nPress ENTER to continue . . . '))
        elif choice == '3':
            update_u(engine, table_con)
            print(input('\nPress ENTER to continue . . . '))
        elif choice == '4':
            result = delete_d(engine, table_con)
            if result == "TABLE_DROPPED":
                table_con = None   # return to CSV selection step
            print(input('\nPress ENTER to continue . . . '))
        elif choice == '5':
            stats(engine, table_con)
            print(input('\nPress ENTER to continue . . . '))
        elif choice == '6':
            visual(engine, table_con)
            print(input('\nPress ENTER to continue . . . '))
        elif choice == '7':
            print("\nConnecting database...")
            engine = None
            table_con = None
            df_con = None
            continue 

        elif choice == '8':
            print("\nTerminating Program .. . .  .   .")
            break

        else:
            print("Invalid choice. Try again.")
        
if __name__ == "__main__":
    main()
