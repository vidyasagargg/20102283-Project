import unittest
import json
import sqlite3
import os
import app as vet_app

class VetClinicApiTestCase(unittest.TestCase):
    def setUp(self):
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
        if os.path.exists("test_vet_clinic.db"):
            os.remove("test_vet_clinic.db")

    def test_consolidated_clinical_report_pipeline(self):
        reg = {"owner_name": "Vidya", "owner_phone": "999", "pet_name": "Sunnyy", "pet_type": "Dog", "pet_age": 4}
        self.app.post('/api/registrations', data=json.dumps(reg), content_type='application/json')
        
        med = {
            "registration_id": 1, "owner_name": "Vidya", "pet_name": "Sunnyy", 
            "veterinarian": "Dr. Sarah Jenkins", "medication_details": "Paracetamol", 
            "frequency": "once a day", "symptoms": "High fever"
        }
        self.app.post('/api/medications', data=json.dumps(med), content_type='application/json')
        
        response = self.app.get('/api/treatments/history?registration_id=1')
        data = json.loads(response.data.decode())
        
        # Confirms symptoms evaluate immediately to High Priority Red status
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], "🔴 Needs Attention")

if __name__ == '__main__':
    unittest.main()