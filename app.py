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


        # Add Vaccinations table to maintain Vaccine records
        cursor.execute('''
            CREATE TABLE vaccinations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                registration_id INTEGER NOT NULL,
                owner_name TEXT NOT NULL,
                pet_name TEXT NOT NULL,
                veterinarian TEXT NOT NULL,
                vaccination_details TEXT NOT NULL,
                vaccination_date TEXT NOT NULL,
                FOREIGN KEY (registration_id) REFERENCES registrations(id) ON DELETE CASCADE
            )
        ''')


        def get_db_connection():
            #Create database connection with foreign keys enabled
            conn = sqlite3.connect(DB_FILE)
            conn.execute("PRAGMA foreign_keys = ON")
            conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            return conn

        def dict_from_row(row):
            #Convert sqlite3.Row to dictionary
            if row is None:
                return None
            return dict(row)

        def error_response(message, status_code=400):
            #Return standardized error response
            return jsonify({"error": message}), status_code
        
        

        @app.route('/api/registrations', methods=['POST'])
        def create_registration():
            """Create a new pet registration"""
            try:
                data = request.get_json()
                
                if not data:
                    return error_response("Invalid JSON data", 400)
                
                # Validate required fields
                if not data.get('owner_name') or data.get('owner_name').strip() == '':
                    return error_response("owner_name is required and cannot be empty", 400)
                if not data.get('owner_phone'):
                    return error_response("owner_phone is required", 400)
                if not data.get('pet_name'):
                    return error_response("pet_name is required", 400)
                if not data.get('pet_type'):
                    return error_response("pet_type is required", 400)
                if 'pet_age' not in data:
                    return error_response("pet_age is required", 400)
                
                conn = get_db_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO registrations 
                    (owner_name, owner_phone, pet_name, pet_type, pet_age)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    data['owner_name'],
                    data['owner_phone'],
                    data['pet_name'],
                    data['pet_type'],
                    data['pet_age']
                ))
                
                conn.commit()
                registration_id = cursor.lastrowid
                conn.close()
                
                return jsonify({
                    "id": registration_id,
                    "owner_name": data['owner_name'],
                    "pet_name": data['pet_name'],
                    "message": "Registration created successfully"
                }), 201
            
            except Exception as e:
                return error_response(f"Database error: {str(e)}", 500)
            
        #Read API Registrations
            @app.route('/api/registrations', methods=['GET'])
            def get_all_registrations():
                #Retrieve all pet registrations
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    
                    cursor.execute('SELECT * FROM registrations ORDER BY id')
                    registrations = cursor.fetchall()
                    conn.close()
                    
                    return jsonify([dict_from_row(row) for row in registrations]), 200
                
                except Exception as e:
                    return error_response(f"Database error: {str(e)}", 500)
                

                #Read single record operation for registrations
                @app.route('/api/registrations/<int:id>', methods=['GET'])
                def get_registration(id):
                    #Retrieve a specific registration by ID
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        
                        cursor.execute('SELECT * FROM registrations WHERE id = ?', (id,))
                        registration = cursor.fetchone()
                        conn.close()
                        
                        if not registration:
                            return error_response(f"Registration with id {id} not found", 404)
                        
                        return jsonify(dict_from_row(registration)), 200
                    
                    except Exception as e:
                        return error_response(f"Database error: {str(e)}", 500)
                #Update operation API for registrations
                @app.route('/api/registrations/<int:id>', methods=['PUT'])
                def update_registration(id):
                    #Update an existing registration
                    try:
                        data = request.get_json()
                        
                        if not data:
                            return error_response("Invalid JSON data", 400)
                        
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        
                        # Check if registration exists
                        cursor.execute('SELECT * FROM registrations WHERE id = ?', (id,))
                        if not cursor.fetchone():
                            return error_response(f"Registration with id {id} not found", 404)
                        
                        # Update fields (only if provided)
                        updates = []
                        values = []
                        
                        if 'owner_name' in data:
                            if data['owner_name'].strip() == '':
                                return error_response("owner_name cannot be empty", 400)
                            updates.append('owner_name = ?')
                            values.append(data['owner_name'])
                        if 'owner_phone' in data:
                            updates.append('owner_phone = ?')
                            values.append(data['owner_phone'])
                        if 'pet_name' in data:
                            updates.append('pet_name = ?')
                            values.append(data['pet_name'])
                        if 'pet_type' in data:
                            updates.append('pet_type = ?')
                            values.append(data['pet_type'])
                        if 'pet_age' in data:
                            updates.append('pet_age = ?')
                            values.append(data['pet_age'])
                        
                        if not updates:
                            return error_response("No fields to update", 400)
                        
                        values.append(id)
                        query = f"UPDATE registrations SET {', '.join(updates)} WHERE id = ?"
                        cursor.execute(query, values)
                        conn.commit()
                        conn.close()
                        
                        return jsonify({"message": "Registration updated successfully", "id": id}), 200
                    
                    except Exception as e:
                        return error_response(f"Database error: {str(e)}", 500)
                    

                    #Delete record operation API for registrations
                    @app.route('/api/registrations/<int:id>', methods=['DELETE'])
                    def delete_registration(id):
                        #Delete a registration and all associated records (cascade)
                        try:
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            
                            # Check if registration exists
                            cursor.execute('SELECT * FROM registrations WHERE id = ?', (id,))
                            if not cursor.fetchone():
                                return error_response(f"Registration with id {id} not found", 404)
                            
                            # Delete registration (cascade delete handles related records)
                            cursor.execute('DELETE FROM registrations WHERE id = ?', (id,))
                            conn.commit()
                            conn.close()
                            
                            return jsonify({"message": "Registration deleted successfully"}), 200
                        
                        except Exception as e:
                            return error_response(f"Database error: {str(e)}", 500)
                        

