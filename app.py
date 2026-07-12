#Need to update code logic for backend application here

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
import time
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    DEBUG = False
    TESTING = False
    JSON_SORT_KEYS = False

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    DB_FILE = "test_vet_clinic.db"

class ProductionConfig(Config):
    DEBUG = False

DB_FILE = "vet_clinic.db"

# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def create_app(config_name='development'):
    app = Flask(__name__)
    config_dict = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig
    }
    app.config.from_object(config_dict.get(config_name, DevelopmentConfig))
    CORS(app)
    return app

app = create_app()

# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================

def get_db_connection():
    """Create database connection with optimizations"""
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("PRAGMA cache_size = -64000")
    conn.row_factory = sqlite3.Row
    return conn

def dict_from_row(row):
    """Convert sqlite3.Row to dictionary"""
    if row is None:
        return None
    return dict(row)

def error_response(message, status_code=400):
    """Return standardized error response"""
    return jsonify({
        "error": message,
        "status": status_code,
        "timestamp": datetime.now().isoformat()
    }), status_code

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_owner_name(name):
    if not name or len(name.strip()) == 0:
        return False, "Owner name cannot be empty"
    if len(name) > 100:
        return False, "Owner name must be less than 100 characters"
    return True, ""

def validate_phone(phone):
    if not phone or len(phone.strip()) == 0:
        return False, "Phone number cannot be empty"
    return True, ""

def validate_pet_name(name):
    if not name or len(name.strip()) == 0:
        return False, "Pet name cannot be empty"
    if len(name) > 100:
        return False, "Pet name must be less than 100 characters"
    return True, ""

def validate_appointment_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True, ""
    except ValueError:
        return False, "Date must be in ISO format (YYYY-MM-DD)"

def validate_appointment_time(time_str):
    try:
        datetime.strptime(time_str, '%H:%M')
        return True, ""
    except ValueError:
        return False, "Time must be in HH:MM format"

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_db():
    """Initialize database with all required tables"""
    if not os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        
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
        
        conn.commit()
        conn.close()
        print("✓ Database initialized successfully")

# ============================================================================
# LOGGING MIDDLEWARE
# ============================================================================

@app.before_request
def log_request():
    """Log incoming requests"""
    request.start_time = time.time()
    print(f"\n→ [{request.method}] {request.path}")

@app.after_request
def log_response(response):
    """Log response and timing"""
    if hasattr(request, 'start_time'):
        elapsed = time.time() - request.start_time
        print(f"← [{response.status_code}] ({elapsed:.3f}s)")
    return response

# ============================================================================
# REGISTRATION ENDPOINTS
# ============================================================================

@app.route('/api/registrations', methods=['POST'])
def create_registration():
    """
    Create a new pet registration
    Request JSON: owner_name, owner_phone, pet_name, pet_type, pet_age
    Returns: 201 Created with registration details
    """
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Invalid JSON data", 400)
        
        is_valid, msg = validate_owner_name(data.get('owner_name', ''))
        if not is_valid:
            return error_response(msg, 400)
        
        is_valid, msg = validate_phone(data.get('owner_phone', ''))
        if not is_valid:
            return error_response(msg, 400)
        
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

@app.route('/api/registrations', methods=['GET'])
def get_all_registrations():
    """Retrieve all pet registrations. Returns: 200 OK with array of registrations"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM registrations ORDER BY id')
        registrations = cursor.fetchall()
        conn.close()
        
        return jsonify([dict_from_row(row) for row in registrations]), 200
    
    except Exception as e:
        return error_response(f"Database error: {str(e)}", 500)

@app.route('/api/registrations/<int:id>', methods=['GET'])
def get_registration(id):
    """Retrieve a specific registration by ID. Returns: 200 OK or 404 Not Found"""
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

@app.route('/api/registrations/<int:id>', methods=['PUT'])
def update_registration(id):
    """Update an existing registration. Returns: 200 OK or 404 Not Found"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Invalid JSON data", 400)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM registrations WHERE id = ?', (id,))
        if not cursor.fetchone():
            return error_response(f"Registration with id {id} not found", 404)
        
        updates = []
        values = []
        
        if 'owner_name' in data:
            is_valid, msg = validate_owner_name(data['owner_name'])
            if not is_valid:
                return error_response(msg, 400)
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

@app.route('/api/registrations/<int:id>', methods=['DELETE'])
def delete_registration(id):
    """Delete a registration and all cascading records. Returns: 200 OK or 404 Not Found"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('BEGIN TRANSACTION')
        
        cursor.execute('SELECT * FROM registrations WHERE id = ?', (id,))
        if not cursor.fetchone():
            conn.rollback()
            return error_response(f"Registration with id {id} not found", 404)
        
        cursor.execute('DELETE FROM appointments WHERE registration_id = ?', (id,))
        cursor.execute('DELETE FROM medications WHERE registration_id = ?', (id,))
        cursor.execute('DELETE FROM vaccinations WHERE registration_id = ?', (id,))
        cursor.execute('DELETE FROM registrations WHERE id = ?', (id,))
        
        conn.commit()
        
        return jsonify({"message": "Registration and all related records deleted successfully"}), 200
    
    except Exception as e:
        if conn:
            conn.rollback()
        return error_response(f"Database error: {str(e)}", 500)
    finally:
        if conn:
            conn.close()

# ============================================================================
# APPOINTMENTS ENDPOINTS
# ============================================================================

@app.route('/api/appointments', methods=['POST'])
def create_appointment():
    """Create a new appointment. Returns: 201 Created"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Invalid JSON data", 400)
        
        required_fields = ['registration_id', 'owner_name', 'pet_name', 'pet_type',
                          'appointment_date', 'appointment_time', 'veterinarian', 'reason']
        for field in required_fields:
            if not data.get(field):
                return error_response(f"{field} is required", 400)
        
        is_valid, msg = validate_appointment_date(data['appointment_date'])
        if not is_valid:
            return error_response(msg, 400)
        
        is_valid, msg = validate_appointment_time(data['appointment_time'])
        if not is_valid:
            return error_response(msg, 400)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
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

@app.route('/api/appointments', methods=['GET'])
def get_all_appointments():
    """Retrieve all appointments. Returns: 200 OK"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM appointments
            ORDER BY appointment_date, appointment_time
        ''')
        appointments = cursor.fetchall()
        conn.close()
        
        return jsonify([dict_from_row(row) for row in appointments]), 200
    
    except Exception as e:
        return error_response(f"Database error: {str(e)}", 500)

@app.route('/api/appointments/<int:id>', methods=['GET'])
def get_appointment(id):
    """Retrieve a specific appointment. Returns: 200 OK or 404 Not Found"""
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

@app.route('/api/appointments/<int:id>', methods=['PUT'])
def update_appointment(id):
    """Update an appointment. Returns: 200 OK or 404 Not Found"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Invalid JSON data", 400)
        
        if 'appointment_date' in data:
            is_valid, msg = validate_appointment_date(data['appointment_date'])
            if not is_valid:
                return error_response(msg, 400)
        
        if 'appointment_time' in data:
            is_valid, msg = validate_appointment_time(data['appointment_time'])
            if not is_valid:
                return error_response(msg, 400)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM appointments WHERE id = ?', (id,))
        if not cursor.fetchone():
            return error_response(f"Appointment with id {id} not found", 404)
        
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

@app.route('/api/appointments/<int:id>', methods=['DELETE'])
def delete_appointment(id):
    """Delete an appointment. Returns: 200 OK or 404 Not Found"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM appointments WHERE id = ?', (id,))
        if not cursor.fetchone():
            return error_response(f"Appointment with id {id} not found", 404)
        
        cursor.execute('DELETE FROM appointments WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Appointment deleted successfully"}), 200
    
    except Exception as e:
        return error_response(f"Database error: {str(e)}", 500)

# ============================================================================
# MEDICATIONS ENDPOINTS
# ============================================================================

@app.route('/api/medications', methods=['POST'])
def create_medication():
    """Create a new medication record. Returns: 201 Created"""
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
        
        return jsonify({"id": medication_id, "message": "Medication recorded successfully"}), 201
    
    except Exception as e:
        return error_response(f"Database error: {str(e)}", 500)

@app.route('/api/medications', methods=['GET'])
def get_all_medications():
    """Retrieve medications. Supports query parameter: registration_id. Returns: 200 OK"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
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
    """Retrieve a specific medication. Returns: 200 OK or 404 Not Found"""
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

@app.route('/api/medications/<int:id>', methods=['PUT'])
def update_medication(id):
    """Update a medication record. Returns: 200 OK or 404 Not Found"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Invalid JSON data", 400)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM medications WHERE id = ?', (id,))
        if not cursor.fetchone():
            return error_response(f"Medication with id {id} not found", 404)
        
        updates = []
        values = []
        
        if 'medication_details' in data:
            if not data['medication_details'].strip():
                return error_response("medication_details cannot be empty", 400)
            updates.append('medication_details = ?')
            values.append(data['medication_details'])
        if 'frequency' in data:
            updates.append('frequency = ?')
            values.append(data['frequency'])
        if 'symptoms' in data:
            updates.append('symptoms = ?')
            values.append(data['symptoms'])
        
        if not updates:
            return error_response("No fields to update", 400)
        
        values.append(id)
        query = f"UPDATE medications SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Medication updated successfully"}), 200
    
    except Exception as e:
        return error_response(f"Database error: {str(e)}", 500)

@app.route('/api/medications/<int:id>', methods=['DELETE'])
def delete_medication(id):
    """Delete a medication record. Returns: 200 OK or 404 Not Found"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM medications WHERE id = ?', (id,))
        if not cursor.fetchone():
            return error_response(f"Medication with id {id} not found", 404)
        
        cursor.execute('DELETE FROM medications WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Medication deleted successfully"}), 200
    
    except Exception as e:
        return error_response(f"Database error: {str(e)}", 500)

# ============================================================================
# VACCINATIONS ENDPOINTS
# ============================================================================

@app.route('/api/vaccinations', methods=['POST'])
def create_vaccination():
    """Create a new vaccination record. Returns: 201 Created"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Invalid JSON data", 400)
        
        required_fields = ['registration_id', 'owner_name', 'pet_name', 'veterinarian',
                          'vaccination_details', 'vaccination_date']
        for field in required_fields:
            if not data.get(field):
                return error_response(f"{field} is required", 400)
        
        is_valid, msg = validate_appointment_date(data['vaccination_date'])
        if not is_valid:
            return error_response(msg, 400)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM registrations WHERE id = ?', (data['registration_id'],))
        if not cursor.fetchone():
            return error_response(f"Registration with id {data['registration_id']} not found", 404)
        
        cursor.execute('''
            INSERT INTO vaccinations 
            (registration_id, owner_name, pet_name, veterinarian, vaccination_details, vaccination_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['registration_id'],
            data['owner_name'],
            data['pet_name'],
            data['veterinarian'],
            data['vaccination_details'],
            data['vaccination_date']
        ))
        
        conn.commit()
        vaccination_id = cursor.lastrowid
        conn.close()
        
        return jsonify({"id": vaccination_id, "message": "Vaccination recorded successfully"}), 201
    
    except Exception as e:
        return error_response(f"Database error: {str(e)}", 500)

@app.route('/api/vaccinations', methods=['GET'])
def get_all_vaccinations():
    """Retrieve vaccinations. Supports query parameter: registration_id. Returns: 200 OK"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        registration_id = request.args.get('registration_id')
        
        if registration_id:
            cursor.execute('SELECT * FROM vaccinations WHERE registration_id = ? ORDER BY vaccination_date DESC', (registration_id,))
        else:
            cursor.execute('SELECT * FROM vaccinations ORDER BY vaccination_date DESC')
        
        vaccinations = cursor.fetchall()
        conn.close()
        
        return jsonify([dict_from_row(row) for row in vaccinations]), 200
    
    except Exception as e:
        return error_response(f"Database error: {str(e)}", 500)

@app.route('/api/vaccinations/<int:id>', methods=['GET'])
def get_vaccination(id):
    """Retrieve a specific vaccination. Returns: 200 OK or 404 Not Found"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM vaccinations WHERE id = ?', (id,))
        vaccination = cursor.fetchone()
        conn.close()
        
        if not vaccination:
            return error_response(f"Vaccination with id {id} not found", 404)
        
        return jsonify(dict_from_row(vaccination)), 200
    
    except Exception as e:
        return error_response(f"Database error: {str(e)}", 500)

@app.route('/api/vaccinations/<int:id>', methods=['PUT'])
def update_vaccination(id):
    """Update a vaccination record. Returns: 200 OK or 404 Not Found"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Invalid JSON data", 400)
        
        if 'vaccination_date' in data:
            is_valid, msg = validate_appointment_date(data['vaccination_date'])
            if not is_valid:
                return error_response(msg, 400)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM vaccinations WHERE id = ?', (id,))
        if not cursor.fetchone():
            return error_response(f"Vaccination with id {id} not found", 404)
        
        updates = []
        values = []
        
        if 'vaccination_details' in data:
            updates.append('vaccination_details = ?')
            values.append(data['vaccination_details'])
        if 'vaccination_date' in data:
            updates.append('vaccination_date = ?')
            values.append(data['vaccination_date'])
        
        if not updates:
            return error_response("No fields to update", 400)
        
        values.append(id)
        query = f"UPDATE vaccinations SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Vaccination updated successfully"}), 200
    
    except Exception as e:
        return error_response(f"Database error: {str(e)}", 500)

@app.route('/api/vaccinations/<int:id>', methods=['DELETE'])
def delete_vaccination(id):
    """Delete a vaccination record. Returns: 200 OK or 404 Not Found"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM vaccinations WHERE id = ?', (id,))
        if not cursor.fetchone():
            return error_response(f"Vaccination with id {id} not found", 404)
        
        cursor.execute('DELETE FROM vaccinations WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Vaccination deleted successfully"}), 200
    
    except Exception as e:
        return error_response(f"Database error: {str(e)}", 500)

# ============================================================================
# CLINICAL REPORT ENDPOINT
# ============================================================================

def evaluate_health_status(medications, vaccinations):
    """Evaluate pet health status based on medical records"""
    if not medications and not vaccinations:
        return "🟢 Healthy", "Routine check-up recommended"
    
    urgent_symptoms = ['fever', 'poison', 'severe', 'emergency', 'urgent', 'critical']
    
    for med in medications:
        if med.get('symptoms'):
            symptoms_lower = med['symptoms'].lower()
            if any(keyword in symptoms_lower for keyword in urgent_symptoms):
                return "🔴 Needs Attention", "Immediate veterinary consultation recommended"
    
    if vaccinations:
        return "🟢 Healthy", "Vaccinations up to date"
    
    return "🟡 Vaccination Overdue", "Schedule vaccination appointment"

@app.route('/api/treatments/history', methods=['GET'])
def get_treatment_history():
    """
    Get consolidated clinical report for a pet
    Query parameter: registration_id (required)
    Returns: 200 OK with complete clinical history or 404 Not Found
    """
    try:
        registration_id = request.args.get('registration_id')
        
        if not registration_id:
            return error_response("registration_id query parameter is required", 400)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM registrations WHERE id = ?', (registration_id,))
        registration = cursor.fetchone()
        
        if not registration:
            return error_response(f"Registration with id {registration_id} not found", 404)
        
        reg = dict_from_row(registration)
        
        cursor.execute('SELECT * FROM appointments WHERE registration_id = ?', (registration_id,))
        appointments = [dict_from_row(row) for row in cursor.fetchall()]
        
        cursor.execute('SELECT * FROM medications WHERE registration_id = ?', (registration_id,))
        medications = [dict_from_row(row) for row in cursor.fetchall()]
        
        cursor.execute('SELECT * FROM vaccinations WHERE registration_id = ?', (registration_id,))
        vaccinations = [dict_from_row(row) for row in cursor.fetchall()]
        
        conn.close()
        
        status, recommendation = evaluate_health_status(medications, vaccinations)
        
        latest_vet = "Not assigned"
        if appointments:
            latest_vet = appointments[-1].get('veterinarian', 'Not assigned')
        
        return jsonify({
            "status": status,
            "recommendation": recommendation,
            "registration": reg,
            "appointments": appointments,
            "medications": medications,
            "vaccinations": vaccinations,
            "latest_veterinarian": latest_vet
        }), 200
    
    except Exception as e:
        return error_response(f"Database error: {str(e)}", 500)

# ============================================================================
# APPLICATION STARTUP
# ============================================================================

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)