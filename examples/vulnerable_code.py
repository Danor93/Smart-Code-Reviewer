# Example: Code with security vulnerabilities (for testing purposes only!)

import os
import sqlite3
import hashlib

# SECURITY ISSUE: Hardcoded credentials
DATABASE_PASSWORD = "admin123"
API_KEY = "sk-1234567890abcdef"
SECRET_TOKEN = "super_secret_token_2023"

def connect_to_database():
    """Connect to database with hardcoded credentials"""
    # SECURITY ISSUE: Hardcoded connection string
    connection_string = "postgresql://admin:password123@localhost:5432/mydb"
    return connection_string

def authenticate_user(username, password):
    """Authenticate user - VULNERABLE VERSION"""
    
    # SECURITY ISSUE: SQL Injection vulnerability
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    
    # SECURITY ISSUE: Using MD5 for password hashing
    hashed_password = hashlib.md5(password.encode()).hexdigest()
    
    # SECURITY ISSUE: No input validation
    if username and password:
        return True
    return False

def get_user_data(user_id):
    """Get user data - VULNERABLE VERSION"""
    
    # SECURITY ISSUE: SQL Injection through string formatting
    sql = f"SELECT * FROM users WHERE id = {user_id}"
    
    # SECURITY ISSUE: No sanitization of user input
    conn = sqlite3.connect('users.db')
    cursor = conn.execute(sql)
    
    return cursor.fetchall()

def upload_file(filename, content):
    """File upload function - VULNERABLE VERSION"""
    
    # SECURITY ISSUE: No file type validation
    # SECURITY ISSUE: Path traversal vulnerability
    file_path = f"/uploads/{filename}"
    
    # SECURITY ISSUE: No size limits
    with open(file_path, 'w') as f:
        f.write(content)
    
    # SECURITY ISSUE: Executing user-provided filename
    os.system(f"chmod 777 {file_path}")

def generate_session_token():
    """Generate session token - VULNERABLE VERSION"""
    
    # SECURITY ISSUE: Predictable token generation
    import time
    timestamp = str(int(time.time()))
    
    # SECURITY ISSUE: Weak randomization
    import random
    random.seed(123)  # Fixed seed!
    random_part = str(random.randint(1000, 9999))
    
    return timestamp + random_part

def log_user_activity(user_id, activity):
    """Log user activity - VULNERABLE VERSION"""
    
    # SECURITY ISSUE: Logging sensitive information
    log_entry = f"User {user_id} performed: {activity} at {time.time()}"
    
    # SECURITY ISSUE: No access controls on log files
    with open("/var/log/user_activity.log", "a") as log_file:
        log_file.write(log_entry + "\n")

def validate_email(email):
    """Email validation - VULNERABLE VERSION"""
    
    # SECURITY ISSUE: Regex that's vulnerable to ReDoS
    import re
    pattern = r"^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$"
    
    # SECURITY ISSUE: No input length limits (potential DoS)
    return re.match(pattern, email) is not None

def deserialize_data(data):
    """Deserialize user data - VULNERABLE VERSION"""
    
    # SECURITY ISSUE: Using pickle to deserialize untrusted data
    import pickle
    return pickle.loads(data)

# SECURITY ISSUE: Debug mode enabled in production
DEBUG = True

if __name__ == "__main__":
    # SECURITY ISSUE: Exposing sensitive information in logs
    print(f"Starting application with API key: {API_KEY}")
    print(f"Database password: {DATABASE_PASSWORD}")
    
    # SECURITY ISSUE: No error handling - information disclosure
    try:
        user_data = get_user_data("1 OR 1=1")  # SQL injection example
        print(user_data)
    except Exception as e:
        print(f"Full error details: {e}")  # Exposes internal details
