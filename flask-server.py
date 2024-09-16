from flask import Flask, request, jsonify
import sqlite3
import json
# import gspread
# from google.oauth2.service_account import Credentials

app = Flask(__name__)

# SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
# SERVICE_ACCOUNT_FILE = 'first/credentials.json'

# # Authorizing using the credentials provided in the JSON file
# creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
# client = gspread.authorize(creds)


def get_db_connection():
    conn = sqlite3.connect('database.db') 
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/create', methods=['POST'])
def create_table():
    data = request.get_json()
    columns = data['columns']
    sheet_name = data['sheetName']

    # Check if the table already exists
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{sheet_name}';")
    table_exists = cursor.fetchone()

    if not table_exists:
        # Create table if it doesn't exist
        columns_with_types = ', '.join([f"{col} TEXT" for col in columns])
        sql = f"CREATE TABLE {sheet_name} (id INTEGER PRIMARY KEY AUTOINCREMENT);"
        cursor.execute(sql)
        conn.commit()
        message = "Table created successfully!"
        print(f"Table '{sheet_name}' created with only a primary key in SQLite.")
    else:
        # If table exists, check for new columns and add them
        existing_columns_query = f"PRAGMA table_info({sheet_name});"
        existing_columns = [row[1] for row in cursor.execute(existing_columns_query).fetchall()]
        
        new_columns = set(columns) - set(existing_columns)
        
        for column in new_columns:
            alter_sql = f"ALTER TABLE {sheet_name} ADD COLUMN {column} TEXT;"
            print(alter_sql)
            cursor.execute(alter_sql)
        
        conn.commit()
        message = "Table updated with new columns!"

    conn.close()
    
    return jsonify({"message": message}), 200

@app.route('/syncc', methods=['POST'])
def sync_data():
    data = request.get_json()
    print(json.dumps(data, indent=4))
    action = data['action']
    sheet_name = data['sheetName']

    conn = get_db_connection()

    if action == 'insert':
        pk = data['pk']
        # columns = ', '.join(data['attr'])
        # values_placeholder = ', '.join(['?'] * len(data['attr']))
        sql = f"INSERT INTO {sheet_name} (id) VALUES (?)"
        # sql = f"INSERT INTO {sheet_name} ({columns}) VALUES ({values_placeholder});"
        conn.execute(sql, [pk])
       
    elif action == 'update':
        pk = data['pk']
        try:
            updated_value = data['updatedvalue']
        except Exception as e:
            updated_value=""
        sql = f"UPDATE {sheet_name} SET {data['attr']}=? WHERE id=?;"
        conn.execute(sql, (updated_value, pk))
       
    elif action == 'delete':
        pk = data['pk']
        sql = f"DELETE FROM {sheet_name} WHERE id=?;"
        conn.execute(sql, (pk,))
       
    conn.commit()
    conn.close()

    return jsonify({"message": "Data synced successfully!"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080,debug=True)