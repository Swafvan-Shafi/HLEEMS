import pymysql
import os
import bcrypt
from dotenv import load_dotenv

load_dotenv()

try:
    print("Connecting to MySQL to fix passwords...")
    conn = pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'hleems_db')
    )
    
    # Generate proper hash
    hashed = bcrypt.hashpw(b"password123", bcrypt.gensalt()).decode('utf-8')
    
    with conn.cursor() as cursor:
        cursor.execute("UPDATE users SET password_hash = %s", (hashed,))
        conn.commit()
        
    print("Success! Passwords for all users have been permanently fixed to 'password123'")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals() and conn.open:
        conn.close()
