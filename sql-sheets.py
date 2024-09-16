import sqlite3
import gspread
from google.oauth2.service_account import Credentials


conn = sqlite3.connect('example.db')
cursor = conn.cursor()


SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'E:/Sheets-SQL/credentials.json'


creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

sheet_id = "13-saEPXm7p-wOqOByyDt1aVWaEzXRP8mKeyYcsLCkBw"
workbook = client.open_by_key(sheet_id)

def get_field_names(table_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    fields = [info[1] for info in cursor.fetchall()]
    return fields if fields else []


def list_tables():
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [table[0] for table in cursor.fetchall()]
    if tables:
        print("\n--- List of tables ---")
        for i, table in enumerate(tables, start=1):
            print(f"{i}. {table}")
    else:
        print("No tables found in the database.")
    return tables


def select_table():
    tables = list_tables()
    if not tables:
        print("Please create a table first.")
        return None
    choice = int(input("\nChoose a table number: ")) - 1
    if 0 <= choice < len(tables):
        return tables[choice]
    else:
        print("Invalid choice.")
        return None


def create_table():
    table_name = input("Enter the name for the new table: ")
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY
        )
    ''')
    conn.commit()
    print(f"Table '{table_name}' created with only a primary key in SQLite.")


    try:
        workbook.worksheet(table_name)
        print(f"Sheet '{table_name}' already exists in the workbook.")
    except gspread.WorksheetNotFound:
        workbook.add_worksheet(title=table_name, rows="100", cols="20")
        print(f"Sheet '{table_name}' created in the workbook.")


def add_column(table_name):
    display_table(table_name)
    field_name = input("Enter column name: ")
    field_type = input("Enter column type (TEXT, INTEGER, REAL, etc.) [Default: TEXT]: ") or "TEXT"
    try:
        cursor.execute(f'''
            ALTER TABLE {table_name}
            ADD COLUMN {field_name} {field_type}
        ''')
        conn.commit()
        print(f"Column '{field_name}' of type '{field_type}' added to table '{table_name}'.")

       
        sheet = workbook.worksheet(table_name)
        fields = get_field_names(table_name) 
        sheet.clear()  
        sheet.append_row(fields)  
        print(f"Google Sheet '{table_name}' headers updated with new column '{field_name}'.")

    except sqlite3.OperationalError as e:
        print(f"Error: {e}")



def insert_row(table_name):
    fields = get_field_names(table_name) 
    if not fields:
        print(f"Table '{table_name}' has no fields. Please add columns first.")
        return
    

    values = []
    for field in fields:
        value = input(f"Enter value for '{field}' (leave blank for NULL): ") or None
        values.append(value)
    
    placeholders = ', '.join(['?'] * len(fields))
    query = f'''
        INSERT INTO {table_name} ({', '.join(fields)})
        VALUES ({placeholders})
    '''
    
    try:
        cursor.execute(query, values)
        conn.commit()
        print(f"Inserted row with values {values} into '{table_name}'.")


        sheet = workbook.worksheet(table_name)
        sheet.append_row(values if values else [''] * len(fields)) 
        print(f"Row synced to Google Sheet '{table_name}'.")

    except sqlite3.IntegrityError as e:
        print(f"Error: {e}. Make sure the values are valid and the primary key is unique.")
    except gspread.APIError as e:
        print(f"Google Sheets API error: {e}")


def update_row(table_name):
    display_table(table_name)
    primary_key = input("Enter primary key (id) value: ")
    fields = get_field_names(table_name)
    if len(fields) <= 1:
        print(f"Table '{table_name}' only has a primary key. Add fields before updating.")
        return
    for i, field in enumerate(fields[1:], start=1):
        print(f"{i}. {field}")
    field_choice = int(input("Choose a field to update: ")) - 1
    field_name = fields[field_choice + 1] if 0 <= field_choice < len(fields) - 1 else None
    if field_name:
        new_value = input(f"Enter new value for '{field_name}' (leave blank to set NULL): ") or None
        cursor.execute(f'''
            UPDATE {table_name}
            SET {field_name} = ?
            WHERE id = ?
        ''', (new_value, primary_key))
        conn.commit()
        print(f"Field '{field_name}' updated for id {primary_key} in '{table_name}'.")

        # Update Google Sheets row
        sheet = workbook.worksheet(table_name)
        cell = sheet.find(str(primary_key))
        if cell:
            col_index = fields.index(field_name) + 1
            sheet.update_cell(cell.row, col_index, new_value if new_value is not None else '')

        print(f"Row updated in Google Sheet '{table_name}'.")



def delete_row(table_name):
    display_table(table_name) 
    primary_key = input("Enter primary key (id) value: ")
    confirmation = input(f"Are you sure you want to delete the row with id {primary_key}? (yes/no): ")

    if confirmation.lower() == 'yes':

        try:
            cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (primary_key,))
            conn.commit()
            print(f"Deleted row with id {primary_key} from SQLite table '{table_name}'.")
        except sqlite3.OperationalError as e:
            print(f"Error: {e}. Make sure the table exists and primary key is correct.")
            return


        try:
            sheet = workbook.worksheet(table_name)
            cell = sheet.find(str(primary_key))
            if cell:
                sheet.delete_rows(cell.row) 
                print(f"Deleted row with id {primary_key} from Google Sheet '{table_name}'.")
            else:
                print(f"Primary key {primary_key} not found in Google Sheet '{table_name}'.")
        except gspread.WorksheetNotFound:
            print(f"Sheet '{table_name}' not found in the workbook.")
        except gspread.APIError as e:
            print(f"Google Sheets API error: {e}")

    else:
        print("Deletion cancelled.")




def read_table(table_name):
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        if rows:
            print(f"\n--- Data in table '{table_name}' ---")
            fields = get_field_names(table_name)
            print(f"Fields: {fields}")
            for row in rows:
                print(row)


            sheet = workbook.worksheet(table_name)
            sheet.clear()
            sheet.append_row(fields)
            for row in rows:
                sheet.append_row(row)
        else:
            print(f"No data found in table '{table_name}'.")
    except sqlite3.OperationalError as e:
        print(f"Error: {e}. Make sure the table exists.")


def display_table(table_name):
    print(f"\n--- Current data in table '{table_name}' ---")
    read_table(table_name)

# Menu
def menu():
    while True:
        print("\n--- Main Menu ---")
        print("1. Create a new table")
        print("2. Select a table to perform operations")
        print("3. List all tables")
        print("4. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            create_table()

        elif choice == '2':
            table_name = select_table()
            if not table_name:
                continue

            while True:
                print(f"\n--- Operations on table '{table_name}' ---")
                print("1. Add column")
                print("2. Insert row (only primary key)")
                print("3. Update row")
                print("4. Delete row")
                print("5. Read entire table")
                print("6. Back to main menu")
                sub_choice = input("Choose an option: ")

                if sub_choice == '1':
                    add_column(table_name)

                elif sub_choice == '2':
                    insert_row(table_name)

                elif sub_choice == '3':
                    update_row(table_name)

                elif sub_choice == '4':
                    delete_row(table_name)

                elif sub_choice == '5':
                    read_table(table_name)

                elif sub_choice == '6':
                    break

                else:
                    print("Invalid choice. Try again.")

        elif choice == '3':
            list_tables()

        elif choice == '4':
            print("Exiting...")
            break

        else:
            print("Invalid choice. Try again.")

if __name__ == '__main__':
    menu()


conn.close()
