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
                        

                        #API for create appointment
                        @app.route('/api/appointments', methods=['POST'])
                        def create_appointment():
                            #Create a new appointment
                            try:
                                data = request.get_json()
                                
                                if not data:
                                    return error_response("Invalid JSON data", 400)
                                
                                # Validate required fields
                                required_fields = ['registration_id', 'owner_name', 'pet_name', 'pet_type',
                                                'appointment_date', 'appointment_time', 'veterinarian', 'reason']
                                for field in required_fields:
                                    if not data.get(field):
                                        return error_response(f"{field} is required", 400)
                                
                                conn = get_db_connection()
                                cursor = conn.cursor()
                                
                                # Verify registration exists
                                cursor.execute('SELECT * FROM registrations WHERE id = ?', (data['registration_id'],))
                                if not cursor.fetchone():
                                    return error_response(f"Registration with id {data['registration_id']} not found", 404)
                                
                                cursor.execute('''
                                    INSERT INTO appointments 
                                    (registration_id, owner_name, pet_name, pet_type, appointment_date, 
                                    appointment_time, veterinarian, reason)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (
                                    data['registration_id'],
                                    data['owner_name'],
                                    data['pet_name'],
                                    data['pet_type'],
                                    data['appointment_date'],
                                    data['appointment_time'],
                                    data['veterinarian'],
                                    data['reason']
                                ))
                                
                                conn.commit()
                                appointment_id = cursor.lastrowid
                                conn.close()
                                
                                return jsonify({
                                    "id": appointment_id,
                                    "registration_id": data['registration_id'],
                                    "appointment_date": data['appointment_date'],
                                    "message": "Appointment created successfully"
                                }), 201
                            
                            except Exception as e:
                                return error_response(f"Database error: {str(e)}", 500)
                            
                            #API for reading all the appointments at once
                            @app.route('/api/appointments', methods=['GET'])
                            def get_all_appointments():
                                #Retrieve all appointments
                                try:
                                    conn = get_db_connection()
                                    cursor = conn.cursor()
                                    
                                    cursor.execute('''
                                        SELECT a.* FROM appointments a
                                        ORDER BY a.appointment_date, a.appointment_time
                                    ''')
                                    appointments = cursor.fetchall()
                                    conn.close()
                                    
                                    return jsonify([dict_from_row(row) for row in appointments]), 200
                                
                                except Exception as e:
                                    return error_response(f"Database error: {str(e)}", 500)
                                

                                #Read API for single record
                                @app.route('/api/appointments/<int:id>', methods=['GET'])
                                def get_appointment(id):
                                    #Retrieve a specific appointment by ID
                                    try:
                                        conn = get_db_connection()
                                        cursor = conn.cursor()
                                        
                                        cursor.execute('SELECT * FROM appointments WHERE id = ?', (id,))
                                        appointment = cursor.fetchone()
                                        conn.close()
                                        
                                        if not appointment:
                                            return error_response(f"Appointment with id {id} not found", 404)
                                        
                                        return jsonify(dict_from_row(appointment)), 200
                                    
                                    except Exception as e:
                                        return error_response(f"Database error: {str(e)}", 500)
                                    
                                    
                                    #Update operation API for appointments
                                    @app.route('/api/appointments/<int:id>', methods=['PUT'])
                                    def update_appointment(id):
                                        #Update an existing appointment
                                        try:
                                            data = request.get_json()
                                            
                                            if not data:
                                                return error_response("Invalid JSON data", 400)
                                            
                                            conn = get_db_connection()
                                            cursor = conn.cursor()
                                            
                                            # Check if appointment exists
                                            cursor.execute('SELECT * FROM appointments WHERE id = ?', (id,))
                                            if not cursor.fetchone():
                                                return error_response(f"Appointment with id {id} not found", 404)
                                            
                                            # Update fields
                                            updates = []
                                            values = []
                                            
                                            if 'appointment_date' in data:
                                                updates.append('appointment_date = ?')
                                                values.append(data['appointment_date'])
                                            if 'appointment_time' in data:
                                                updates.append('appointment_time = ?')
                                                values.append(data['appointment_time'])
                                            if 'reason' in data:
                                                updates.append('reason = ?')
                                                values.append(data['reason'])
                                            
                                            if not updates:
                                                return error_response("No fields to update", 400)
                                            
                                            values.append(id)
                                            query = f"UPDATE appointments SET {', '.join(updates)} WHERE id = ?"
                                            cursor.execute(query, values)
                                            conn.commit()
                                            conn.close()
                                            
                                            return jsonify({"message": "Appointment updated successfully"}), 200
                                        
                                        except Exception as e:
                                            return error_response(f"Database error: {str(e)}", 500)


                                    #Delate operation API for appointments
                                    @app.route('/api/appointments/<int:id>', methods=['DELETE'])
                                    def delete_appointment(id):
                                        #Delete an appointment
                                        try:
                                            conn = get_db_connection()
                                            cursor = conn.cursor()
                                            
                                            # Check if appointment exists
                                            cursor.execute('SELECT * FROM appointments WHERE id = ?', (id,))
                                            if not cursor.fetchone():
                                                return error_response(f"Appointment with id {id} not found", 404)
                                            
                                            cursor.execute('DELETE FROM appointments WHERE id = ?', (id,))
                                            conn.commit()
                                            conn.close()
                                            
                                            return jsonify({"message": "Appointment deleted successfully"}), 200
                                        
                                        except Exception as e:
                                            return error_response(f"Database error: {str(e)}", 500)
                                        


                                        #Create medication records
                                        @app.route('/api/medications', methods=['POST'])
                                        def create_medication():
                                            #Create a new medication record
                                            try:
                                                data = request.get_json()
                                                
                                                if not data:
                                                    return error_response("Invalid JSON data", 400)
                                                
                                                required_fields = ['registration_id', 'owner_name', 'pet_name', 'veterinarian',
                                                                'medication_details', 'frequency']
                                                for field in required_fields:
                                                    if not data.get(field):
                                                        return error_response(f"{field} is required", 400)
                                                
                                                conn = get_db_connection()
                                                cursor = conn.cursor()
                                                
                                                # Verify registration exists
                                                cursor.execute('SELECT * FROM registrations WHERE id = ?', (data['registration_id'],))
                                                if not cursor.fetchone():
                                                    return error_response(f"Registration with id {data['registration_id']} not found", 404)
                                                
                                                cursor.execute('''
                                                    INSERT INTO medications 
                                                    (registration_id, owner_name, pet_name, veterinarian, medication_details, frequency, symptoms)
                                                    VALUES (?, ?, ?, ?, ?, ?, ?)
                                                ''', (
                                                    data['registration_id'],
                                                    data['owner_name'],
                                                    data['pet_name'],
                                                    data['veterinarian'],
                                                    data['medication_details'],
                                                    data['frequency'],
                                                    data.get('symptoms', '')
                                                ))
                                                
                                                conn.commit()
                                                medication_id = cursor.lastrowid
                                                conn.close()
                                                
                                                return jsonify({
                                                    "id": medication_id,
                                                    "message": "Medication recorded successfully"
                                                }), 201
                                            
                                            except Exception as e:
                                                return error_response(f"Database error: {str(e)}", 500)
                                            

                                            #Read operation for medication
                                            @app.route('/api/medications', methods=['GET'])
                                            def get_all_medications():
                                                #Retrieve all medications
                                                try:
                                                    conn = get_db_connection()
                                                    cursor = conn.cursor()
                                                    
                                                    # Check for registration_id query parameter
                                                    registration_id = request.args.get('registration_id')
                                                    
                                                    if registration_id:
                                                        cursor.execute('SELECT * FROM medications WHERE registration_id = ?', (registration_id,))
                                                    else:
                                                        cursor.execute('SELECT * FROM medications ORDER BY id')
                                                    
                                                    medications = cursor.fetchall()
                                                    conn.close()
                                                    
                                                    return jsonify([dict_from_row(row) for row in medications]), 200
                                                
                                                except Exception as e:
                                                    return error_response(f"Database error: {str(e)}", 500)


                                            @app.route('/api/medications/<int:id>', methods=['GET'])
                                            def get_medication(id):
                                                #Retrieve a specific medication by ID"""
                                                try:
                                                    conn = get_db_connection()
                                                    cursor = conn.cursor()
                                                    
                                                    cursor.execute('SELECT * FROM medications WHERE id = ?', (id,))
                                                    medication = cursor.fetchone()
                                                    conn.close()
                                                    
                                                    if not medication:
                                                        return error_response(f"Medication with id {id} not found", 404)
                                                    
                                                    return jsonify(dict_from_row(medication)), 200
                                                
                                                except Exception as e:
                                                    return error_response(f"Database error: {str(e)}", 500)
                                            



    



                                    

                        



