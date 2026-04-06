import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def run_sql_file(cursor, filename):
    with open(filename, 'r') as f:
        sql_file = f.read()
        
    # Split queries by semicolon, ignoring empty ones
    sql_commands = [cmd.strip() for cmd in sql_file.split(';') if cmd.strip()]
    
    for command in sql_commands:
        try:
            cursor.execute(command)
        except Exception as e:
            print(f"Command skipped or failed: {e}")

try:
    print("Connecting to MySQL...")
    # First, connect WITHOUT specifying a database, so we can create it
    conn = pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', '')
    )
    
    with conn.cursor() as cursor:
        print("Running schema.sql...")
        # Since the script is in "backend", path goes up one dir
        run_sql_file(cursor, '../database/schema.sql')
        conn.commit()
        
        print("Running seed.sql...")
        run_sql_file(cursor, '../database/seed.sql')
        conn.commit()
        
    print("Database setup complete! You can now start 'python app.py'")
    
except Exception as e:
    print(f"Error connecting to database: {e}")
finally:
    if 'conn' in locals() and conn.open:
        conn.close()
