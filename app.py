import sqlite3
import os
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)
DB_FILE = "vet_clinic.db"

def get_db_connection():
    """Helper to connect to SQLite and explicitly enforce foreign key constraints."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Table 1: Client Registrations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_name TEXT NOT NULL,
                owner_phone TEXT NOT NULL,
                pet_name TEXT NOT NULL,
                pet_type TEXT NOT NULL,
                pet_age INTEGER NOT NULL
            )
        ''')
        
        # Table 2: Veterinarians Directory
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS veterinarians (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                specialty TEXT NOT NULL
            )
        ''')
        
        # Table 3: Appointment Scheduling
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
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

        # Table 4: Medications Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medications (
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

        # Table 5: Vaccinations Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vaccinations (
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
        
        # Seed clinic doctors if database is empty
        cursor.execute("SELECT COUNT(*) FROM veterinarians")
        if cursor.fetchone()[0] == 0:
            cursor.executemany('''
                INSERT INTO veterinarians (name, specialty) VALUES (?, ?)
            ''', [
                ("Dr. Sarah Jenkins", "General Medicine (Cats & Dogs)"),
                ("Dr. Alex Carter", "Soft Tissue Surgery (Exotics)"),
                ("Dr. Emily Ross", "Avian & Small Mammal Diagnostics")
            ])
            
        conn.commit()

# =====================================================================
# --- UTILITY ENDPOINTS ---
# =====================================================================

@app.route('/api/veterinarians', methods=['GET'])
def get_veterinarians():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM veterinarians")
        rows = cursor.fetchall()
    return jsonify([dict(row) for row in rows]), 200

@app.route('/api/registrations/<int:reg_id>/latest_consultation', methods=['GET'])
def get_latest_consultation(reg_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT owner_name, pet_name, pet_type, pet_age FROM registrations WHERE id = ?", (reg_id,))
        profile = cursor.fetchone()
        if not profile:
            return jsonify({"error": "Profile registration ID not found."}), 404
            
        cursor.execute('''
            SELECT veterinarian FROM appointments 
            WHERE registration_id = ? 
            ORDER BY appointment_date DESC, appointment_time DESC LIMIT 1
        ''', (reg_id,))
        appointment = cursor.fetchone()
        
        result = dict(profile)
        result['consulted_doctor'] = appointment['veterinarian'] if appointment else "No prior appointment consultation found"
        return jsonify(result), 200

@app.route('/api/treatments/validate', methods=['POST'])
def validate_treatment_rules():
    data = request.get_json()
    meds = data.get('medications', '').lower()
    if "steroid" in meds:
        return jsonify({
            "status": "warning", 
            "message": "⚠️ Clinical Warning: Evaluate patient immune metrics before dispensing corticosteroids."
        }), 200
    return jsonify({"status": "clear", "message": "✔️ Medication parameters verified clear."}), 200

# =====================================================================
# --- REGISTRATION CRUD ENDPOINTS ---
# =====================================================================

@app.route('/api/registrations', methods=['POST'])
def create_registration():
    data = request.get_json()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO registrations (owner_name, owner_phone, pet_name, pet_type, pet_age) VALUES (?, ?, ?, ?, ?)
        ''', (data['owner_name'], data['owner_phone'], data['pet_name'], data['pet_type'], data['pet_age']))
        conn.commit()
    return jsonify({"message": "Profile registered successfully!"}), 201

@app.route('/api/registrations', methods=['GET'])
def get_registrations():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM registrations")
        rows = cursor.fetchall()
    return jsonify([dict(row) for row in rows]), 200

@app.route('/api/registrations/<int:reg_id>', methods=['PUT'])
def update_registration(reg_id):
    data = request.get_json()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE registrations 
            SET owner_name = ?, owner_phone = ?, pet_name = ?, pet_type = ?, pet_age = ? 
            WHERE id = ?
        ''', (data['owner_name'], data['owner_phone'], data['pet_name'], data['pet_type'], data['pet_age'], reg_id))
        conn.commit()
    return jsonify({"message": "Registration updated successfully."}), 200

@app.route('/api/registrations/<int:reg_id>', methods=['DELETE'])
def delete_registration(reg_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM registrations WHERE id = ?", (reg_id,))
        conn.commit()
    return jsonify({"message": "Profile removed."}), 200

# =====================================================================
# --- APPOINTMENT CRUD ENDPOINTS ---
# =====================================================================

@app.route('/api/appointments', methods=['POST'])
def create_appointment():
    data = request.get_json()
    reg_id = data.get('registration_id')
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM registrations WHERE id = ?", (reg_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Invalid Registration ID."}), 400

        cursor.execute('''
            INSERT INTO appointments (registration_id, owner_name, pet_name, pet_type, appointment_date, appointment_time, veterinarian, reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (reg_id, data['owner_name'], data['pet_name'], data['pet_type'], data['appointment_date'], data['appointment_time'], data['veterinarian'], data['reason']))
        conn.commit()
    return jsonify({"message": "Appointment created!"}), 201

@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM appointments")
        rows = cursor.fetchall()
    return jsonify([dict(row) for row in rows]), 200

@app.route('/api/appointments/<int:app_id>', methods=['PUT'])
def update_appointment(app_id):
    data = request.get_json()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE appointments 
            SET appointment_date = ?, appointment_time = ?, veterinarian = ?, reason = ? 
            WHERE id = ?
        ''', (data['appointment_date'], data['appointment_time'], data['veterinarian'], data['reason'], app_id))
        conn.commit()
    return jsonify({"message": "Appointment edited successfully."}), 200

@app.route('/api/appointments/<int:app_id>', methods=['DELETE'])
def delete_appointment(app_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM appointments WHERE id = ?", (app_id,))
        conn.commit()
    return jsonify({"message": "Appointment deleted."}), 200

# =====================================================================
# --- MEDICATIONS CRUD ---
# =====================================================================

@app.route('/api/medications', methods=['POST'])
def create_medication():
    data = request.get_json()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO medications (registration_id, owner_name, pet_name, veterinarian, medication_details, frequency, symptoms)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (data['registration_id'], data['owner_name'], data['pet_name'], data['veterinarian'], data['medication_details'], data['frequency'], data['symptoms']))
        conn.commit()
    return jsonify({"message": "Medication prescription appended successfully!"}), 201

@app.route('/api/medications', methods=['GET'])
def get_medications():
    reg_id = request.args.get('registration_id')
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if reg_id:
            cursor.execute("SELECT * FROM medications WHERE registration_id = ?", (reg_id,))
        else:
            cursor.execute("SELECT * FROM medications")
        rows = cursor.fetchall()
    return jsonify([dict(row) for row in rows]), 200

@app.route('/api/medications/<int:med_id>', methods=['PUT'])
def update_medication(med_id):
    data = request.get_json()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE medications 
            SET medication_details = ?, frequency = ?, symptoms = ? 
            WHERE id = ?
        ''', (data['medication_details'], data['frequency'], data['symptoms'], med_id))
        conn.commit()
    return jsonify({"message": "Medication log modified successfully."}), 200

@app.route('/api/medications/<int:med_id>', methods=['DELETE'])
def delete_medication(med_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM medications WHERE id = ?", (med_id,))
        conn.commit()
    return jsonify({"message": "Medication prescription deleted."}), 200

# =====================================================================
# --- VACCINATIONS CRUD ---
# =====================================================================

@app.route('/api/vaccinations', methods=['POST'])
def create_vaccination():
    data = request.get_json()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO vaccinations (registration_id, owner_name, pet_name, veterinarian, vaccination_details, vaccination_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['registration_id'], data['owner_name'], data['pet_name'], data['veterinarian'], data['vaccination_details'], data['vaccination_date']))
        conn.commit()
    return jsonify({"message": "Vaccination log appended entry successfully!"}), 201

@app.route('/api/vaccinations', methods=['GET'])
def get_vaccinations():
    reg_id = request.args.get('registration_id')
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if reg_id:
            cursor.execute("SELECT * FROM vaccinations WHERE registration_id = ?", (reg_id,))
        else:
            cursor.execute("SELECT * FROM vaccinations")
        rows = cursor.fetchall()
    return jsonify([dict(row) for row in rows]), 200

@app.route('/api/vaccinations/<int:vac_id>', methods=['PUT'])
def update_vaccination(vac_id):
    data = request.get_json()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE vaccinations 
            SET vaccination_details = ?, vaccination_date = ? 
            WHERE id = ?
        ''', (data['vaccination_details'], data['vaccination_date'], vac_id))
        conn.commit()
    return jsonify({"message": "Vaccination record modified successfully."}), 200

@app.route('/api/vaccinations/<int:vac_id>', methods=['DELETE'])
def delete_vaccination(vac_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM vaccinations WHERE id = ?", (vac_id,))
        conn.commit()
    return jsonify({"message": "Vaccination entry deleted."}), 200

# =====================================================================
# --- HEALTH REPORT ENGINE WITH NEW PATIENT SAFEGUARDS ---
# =====================================================================

@app.route('/api/treatments/history', methods=['GET'])
def get_treatment_history():
    reg_id = request.args.get('registration_id')
    if not reg_id:
        return jsonify({"error": "Missing profile parameter."}), 400
        
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Fetch Demographic Data
        cursor.execute("SELECT id, owner_name, pet_name, pet_type, pet_age FROM registrations WHERE id = ?", (reg_id,))
        reg_row = cursor.fetchone()
        if not reg_row:
            return jsonify({"error": "Profile not found."}), 404
        profile = dict(reg_row)
        
        # 2. Fetch Aggregated Clinical Ledger
        cursor.execute('''
            SELECT id, 'Medication' AS entry_type, veterinarian, (medication_details || ' [' || frequency || ']') AS details, symptoms FROM medications WHERE registration_id = ?
            UNION ALL
            SELECT id, 'Vaccination' AS entry_type, veterinarian, (vaccination_details || ' [Administered: ' || vaccination_date || ']') AS details, NULL AS symptoms FROM vaccinations WHERE registration_id = ?
            ORDER BY id DESC
        ''', (reg_id, reg_id))
        ledger_rows = cursor.fetchall()
        ledger = [dict(r) for r in ledger_rows]
        
        # 3. Analyze Health Metrics via Clean Rule-Based If Conditions
        has_symptoms = any(bool(r['symptoms'] and r['symptoms'].strip()) for r in ledger if r['entry_type'] == 'Medication')
        
        cursor.execute("SELECT vaccination_date FROM vaccinations WHERE registration_id = ? ORDER BY id DESC LIMIT 1", (reg_id,))
        last_vac = cursor.fetchone()
        
        is_overdue = False
        current_date = datetime(2026, 7, 13)
        
        if not last_vac:
            is_overdue = True
        else:
            try:
                v_date = datetime.strptime(last_vac['vaccination_date'], "%Y-%m-%d")
                if (current_date - v_date).days > 365:
                    is_overdue = True
            except:
                pass
                
        # FIXED HIERARCHY: Added an initial safeguard to prevent false-positives on new registrations
        if not ledger:
            status = "⚪ Awaiting Evaluation"
            recommendation = "New patient profile detected with no treatment logs. Please schedule an initial appointment consultation checkup."
        elif has_symptoms:
            status = "🔴 Needs Attention"
            recommendation = "Book an immediate check-up to treat active clinical symptoms."
        elif is_overdue:
            status = "🟡 Vaccination Due"
            recommendation = "Schedule a routine vaccination booster appointment."
        else:
            status = "🟢 Healthy"
            recommendation = "Continue regular care and preventative maintenance."
            
        return jsonify({
            "profile": profile,
            "status": status,
            "recommendation": recommendation,
            "ledger": ledger
        }), 200

@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', debug=True, port=8080)