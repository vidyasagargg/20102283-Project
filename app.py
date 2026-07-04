#Need to update code logic for backend application here

from flask import Flask, jsonify, request
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True

DB_FILE = "vet_clinic.db"



def init_db():
    """Initialize database with all required tables"""
    if not os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Add Registrations table
        cursor.execute('''
            CREATE TABLE registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_name TEXT NOT NULL,
                owner_phone TEXT NOT NULL,
                pet_name TEXT NOT NULL,
                pet_type TEXT NOT NULL,
                pet_age INTEGER NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✓ Database initialized - Registrations table created")

# Call at startup
if __name__ == '__main__':
    init_db()
    app.run(debug=True)