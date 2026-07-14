import unittest
import json
import sqlite3
import os
from datetime import datetime, timedelta
import app as vet_app

class VetClinicApiTestCase(unittest.TestCase):
    def setUp(self):
        """Initialise test configuration and establish a clean sandboxed database schema."""
        vet_app.app.config['TESTING'] = True
        vet_app.DB_FILE = "test_vet_clinic.db"
        self.app = vet_app.app.test_client()
        
        with sqlite3.connect(vet_app.DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS registrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    owner_name TEXT NOT NULL, owner_phone TEXT NOT NULL,
                    pet_name TEXT NOT NULL, pet_type TEXT NOT NULL, pet_age INTEGER NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS appointments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    registration_id INTEGER NOT NULL,
                    owner_name TEXT NOT NULL, pet_name TEXT NOT NULL, pet_type TEXT NOT NULL,
                    appointment_date TEXT NOT NULL, appointment_time TEXT NOT NULL,
                    veterinarian TEXT NOT NULL, reason TEXT NOT NULL,
                    FOREIGN KEY (registration_id) REFERENCES registrations(id) ON DELETE CASCADE
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS medications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    registration_id INTEGER NOT NULL,
                    owner_name TEXT NOT NULL, pet_name TEXT NOT NULL,
                    veterinarian TEXT NOT NULL, medication_details TEXT NOT NULL, frequency TEXT NOT NULL, symptoms TEXT,
                    FOREIGN KEY (registration_id) REFERENCES registrations(id) ON DELETE CASCADE
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vaccinations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    registration_id INTEGER NOT NULL,
                    owner_name TEXT NOT NULL, pet_name TEXT NOT NULL,
                    veterinarian TEXT NOT NULL, vaccination_details TEXT NOT NULL, vaccination_date TEXT NOT NULL,
                    FOREIGN KEY (registration_id) REFERENCES registrations(id) ON DELETE CASCADE
                )
            ''')
            conn.commit()

    def tearDown(self):
        """Dismantle database links and permanently delete the sandboxed storage file."""
        if os.path.exists("test_vet_clinic.db"):
            os.remove("test_vet_clinic.db")

    # =====================================================================
    # TEST CASE 1: Client Registration CRUD Operations
    # =====================================================================
    def test_registration_crud_lifecycle(self):
        """Verify Create, Read, Update, and Delete endpoints for client profiles."""
        # A. Test Create (POST)
        payload = {"owner_name": "Vidya", "owner_phone": "0871112222", "pet_name": "Sunnyy", "pet_type": "Dog", "pet_age": 5}
        res_create = self.app.post('/api/registrations', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res_create.status_code, 201)
        
        # B. Test Read (GET)
        res_get = self.app.get('/api/registrations')
        data_get = json.loads(res_get.data.decode())
        self.assertEqual(len(data_get), 1)
        self.assertEqual(data_get[0]['pet_name'], "Sunnyy")
        
        # C. Test Update (PUT)
        updated_payload = {"owner_name": "Vidya", "owner_phone": "0871112222", "pet_name": "Sunnyy", "pet_type": "Dog", "pet_age": 6}
        res_update = self.app.put('/api/registrations/1', data=json.dumps(updated_payload), content_type='application/json')
        self.assertEqual(res_update.status_code, 200)
        
        # D. Test Delete (DELETE)
        res_delete = self.app.delete('/api/registrations/1')
        self.assertEqual(res_delete.status_code, 200)

    # =====================================================================
    # TEST CASE 2: Appointment Creation & Relational Validation
    # =====================================================================
    def test_appointment_validation(self):
        """Verify appointment scheduling constraints map perfectly to existing registration contexts."""
        # Setup active mock registration parent
        reg = {"owner_name": "Kris", "owner_phone": "12345", "pet_name": "Kutta", "pet_type": "Dog", "pet_age": 3}
        self.app.post('/api/registrations', data=json.dumps(reg), content_type='application/json')
        
        # A. Try scheduling an appointment under an invalid registration key (Should fail)
        bad_app = {"registration_id": 999, "owner_name": "Unknown", "pet_name": "Ghost", "pet_type": "Cat", "appointment_date": "2026-07-20", "appointment_time": "12:00", "veterinarian": "Dr. Sarah Jenkins", "reason": "Checkup"}
        res_bad = self.app.post('/api/appointments', data=json.dumps(bad_app), content_type='application/json')
        self.assertEqual(res_bad.status_code, 400)
        
        # B. Schedule an appointment under a valid key (Should succeed)
        good_app = {"registration_id": 1, "owner_name": "Kris", "pet_name": "Kutta", "pet_type": "Dog", "appointment_date": "2026-07-20", "appointment_time": "12:00", "veterinarian": "Dr. Sarah Jenkins", "reason": "Routine Checkup"}
        res_good = self.app.post('/api/appointments', data=json.dumps(good_app), content_type='application/json')
        self.assertEqual(res_good.status_code, 201)

    # =====================================================================
    # TEST CASE 3: Scoped Subsystem Record Isolation
    # =====================================================================
    def test_context_scoped_data_isolation(self):
        """Ensure medications endpoints isolate logs explicitly by active patient ID parameter queries."""
        # Register Pet 1 and Pet 2
        self.app.post('/api/registrations', data=json.dumps({"owner_name": "A", "owner_phone": "1", "pet_name": "Kutta", "pet_type": "Dog", "pet_age": 2}), content_type='application/json')
        self.app.post('/api/registrations', data=json.dumps({"owner_name": "B", "owner_phone": "2", "pet_name": "Sunnyy", "pet_type": "Dog", "pet_age": 4}), content_type='application/json')
        
        # Log a prescription ONLY for Patient 1
        med_p1 = {"registration_id": 1, "owner_name": "A", "pet_name": "Kutta", "veterinarian": "Dr. Jenkins", "medication_details": "Amo", "frequency": "once a day", "symptoms": ""}
        self.app.post('/api/medications', data=json.dumps(med_p1), content_type='application/json')
        
        # Query medications for Patient 1 explicitly
        res_p1 = self.app.get('/api/medications?registration_id=1')
        data_p1 = json.loads(res_p1.data.decode())
        self.assertEqual(len(data_p1), 1)
        
        # Query medications for Patient 2 explicitly (Must return empty array)
        res_p2 = self.app.get('/api/medications?registration_id=2')
        data_p2 = json.loads(res_p2.data.decode())
        self.assertEqual(len(data_p2), 0)

    # =====================================================================
    # TEST CASE 4: Health Monitoring Rule 1 — Awaiting Evaluation
    # =====================================================================
    def test_rule_engine_awaiting_evaluation(self):
        """Verify that a brand-new registration with empty history generates 'Awaiting Evaluation' status."""
        self.app.post('/api/registrations', data=json.dumps({"owner_name": "Maddy", "owner_phone": "555", "pet_name": "jonhy", "pet_type": "Dog", "pet_age": 4}), content_type='application/json')
        
        response = self.app.get('/api/treatments/history?registration_id=1')
        data = json.loads(response.data.decode())
        self.assertEqual(data['status'], "⚪ Awaiting Evaluation")
        self.assertIn("New patient profile", data['recommendation'])

    # =====================================================================
    # TEST CASE 5: Health Monitoring Rule 2 — Active Symptoms Priority
    # =====================================================================
    def test_rule_engine_symptoms_priority(self):
        """Verify that active symptoms immediately trigger high-priority 'Needs Attention' status."""
        self.app.post('/api/registrations', data=json.dumps({"owner_name": "Vidya", "owner_phone": "999", "pet_name": "Sunnyy", "pet_type": "Dog", "pet_age": 4}), content_type='application/json')
        
        # Inject active symptoms context
        med = {"registration_id": 1, "owner_name": "Vidya", "pet_name": "Sunnyy", "veterinarian": "Dr. Sarah Jenkins", "medication_details": "Paracetamol", "frequency": "once a day", "symptoms": "fever and food poison"}
        self.app.post('/api/medications', data=json.dumps(med), content_type='application/json')
        
        response = self.app.get('/api/treatments/history?registration_id=1')
        data = json.loads(response.data.decode())
        self.assertEqual(data['status'], "🔴 Needs Attention")
        self.assertIn("Book an immediate check-up", data['recommendation'])

    # =====================================================================
    # TEST CASE 6: Health Monitoring Rule 3 — Vaccination Overdue
    # =====================================================================
    def test_rule_engine_vaccination_overdue(self):
        """Verify that asymptomatic pets with outdated boosters trigger 'Vaccination Due' status."""
        self.app.post('/api/registrations', data=json.dumps({"owner_name": "Vidya", "owner_phone": "444", "pet_name": "Sunnyy", "pet_type": "Dog", "pet_age": 5}), content_type='application/json')
        
        # Add a medication entry with NO active symptoms
        med = {"registration_id": 1, "owner_name": "Vidya", "pet_name": "Sunnyy", "veterinarian": "Dr. Jenkins", "medication_details": "Vitamins", "frequency": "once a day", "symptoms": ""}
        self.app.post('/api/medications', data=json.dumps(med), content_type='application/json')
        
        # Add an old vaccine record (older than 365 days relative to July 13, 2026)
        vac = {"registration_id": 1, "owner_name": "Vidya", "pet_name": "Sunnyy", "veterinarian": "Dr. Jenkins", "vaccination_details": "Rabies", "vaccination_date": "2025-05-10"}
        self.app.post('/api/vaccinations', data=json.dumps(vac), content_type='application/json')
        
        response = self.app.get('/api/treatments/history?registration_id=1')
        data = json.loads(response.data.decode())
        self.assertEqual(data['status'], "🟡 Vaccination Due")
        self.assertIn("Schedule a routine vaccination", data['recommendation'])

    # =====================================================================
    # TEST CASE 7: Health Monitoring Rule 4 — Healthy Baseline
    # =====================================================================
    def test_rule_engine_healthy_baseline(self):
        """Verify that asymptomatic pets with current boosters evaluate to 'Healthy' status."""
        self.app.post('/api/registrations', data=json.dumps({"owner_name": "Kris", "owner_phone": "222", "pet_name": "Kutta", "pet_type": "Dog", "pet_age": 3}), content_type='application/json')
        
        # Add asymptomatic medication
        med = {"registration_id": 1, "owner_name": "Kris", "pet_name": "Kutta", "veterinarian": "Dr. Jenkins", "medication_details": "Vitamins", "frequency": "once a day", "symptoms": ""}
        self.app.post('/api/medications', data=json.dumps(med), content_type='application/json')
        
        # Add a current vaccine record (within 365 days of July 13, 2026)
        vac = {"registration_id": 1, "owner_name": "Kris", "pet_name": "Kutta", "veterinarian": "Dr. Jenkins", "vaccination_details": "Core", "vaccination_date": "2026-06-15"}
        self.app.post('/api/vaccinations', data=json.dumps(vac), content_type='application/json')
        
        response = self.app.get('/api/treatments/history?registration_id=1')
        data = json.loads(response.data.decode())
        self.assertEqual(data['status'], "🟢 Healthy")
        self.assertIn("Continue regular care", data['recommendation'])

if __name__ == '__main__':
    unittest.main()