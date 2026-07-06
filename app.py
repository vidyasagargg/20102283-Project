#Need to update code logic for backend application here

from flask import Flask, jsonify, request
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True

DB_FILE = "vet_clinic.db"



def init_db():
    #Initialize database with all required tables
    if not os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        conn.execute("PRAGMA foreign_keys = ON")
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
        
        # Add Appointments table
        cursor.execute('''
            CREATE TABLE appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                registration_id INTEGER NOT NULL,
                owner_name TEXT NOT NULL,
                pet_name TEXT NOT NULL,
                pet_type TEXT NOT NULL,
                appointment_date TEXT NOT NULL,
                appointment_time TEXT NOT NULL,
                veterinarian TEXT NOT NULL,
                reason TEXT NOT NULL,
                FOREIGN KEY (registration_id) REFERENCES registrations(id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✓ Database initialized - Appointments table created")

        # Add Medication table
        cursor.execute('''
            CREATE TABLE medications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                registration_id INTEGER NOT NULL,
                owner_name TEXT NOT NULL,
                pet_name TEXT NOT NULL,
                veterinarian TEXT NOT NULL,
                medication_details TEXT NOT NULL,
                frequency TEXT NOT NULL,
                symptoms TEXT,
                FOREIGN KEY (registration_id) REFERENCES registrations(id) ON DELETE CASCADE
            )
        ''')