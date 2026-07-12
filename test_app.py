import unittest
import json
import sqlite3
import os
import app as vet_app

class VetClinicApiTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test database and client"""
        vet_app.app.config['TESTING'] = True
        vet_app.DB_FILE = "test_vet_clinic.db"
        self.app = vet_app.app.test_client()
        
        # Create test database tables
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
        """Clean up test database"""
        if os.path.exists("test_vet_clinic.db"):
            os.remove("test_vet_clinic.db")

    # COMMIT 57: Registration endpoint tests
    def test_post_registration_creates_new_client(self):
        """Test POST /api/registrations creates new registration"""
        reg_data = {
            "owner_name": "John Doe",
            "owner_phone": "555-1234",
            "pet_name": "Max",
            "pet_type": "Dog",
            "pet_age": 3
        }
        response = self.app.post('/api/registrations', 
                                data=json.dumps(reg_data), 
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode())
        self.assertEqual(data['owner_name'], 'John Doe')
        self.assertEqual(data['pet_name'], 'Max')

    def test_get_all_registrations(self):
        """Test GET /api/registrations retrieves all registrations"""
        # Create a registration first
        reg_data = {"owner_name": "Jane", "owner_phone": "555-5678", "pet_name": "Bella", "pet_type": "Cat", "pet_age": 2}
        self.app.post('/api/registrations', data=json.dumps(reg_data), content_type='application/json')
        
        response = self.app.get('/api/registrations')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertGreater(len(data), 0)

    def test_get_registration_by_id(self):
        """Test GET /api/registrations/<id> retrieves specific registration"""
        reg_data = {"owner_name": "Tom", "owner_phone": "555-9999", "pet_name": "Rex", "pet_type": "Dog", "pet_age": 5}
        post_response = self.app.post('/api/registrations', data=json.dumps(reg_data), content_type='application/json')
        reg_id = json.loads(post_response.data.decode())['id']
        
        response = self.app.get(f'/api/registrations/{reg_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertEqual(data['pet_name'], 'Rex')

    def test_put_registration_updates_record(self):
        """Test PUT /api/registrations/<id> updates registration"""
        reg_data = {"owner_name": "Alice", "owner_phone": "555-0000", "pet_name": "Daisy", "pet_type": "Dog", "pet_age": 4}
        post_response = self.app.post('/api/registrations', data=json.dumps(reg_data), content_type='application/json')
        reg_id = json.loads(post_response.data.decode())['id']
        
        update_data = {"owner_name": "Alice Smith", "pet_age": 5}
        response = self.app.put(f'/api/registrations/{reg_id}', data=json.dumps(update_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_delete_registration_removes_record(self):
        """Test DELETE /api/registrations/<id> deletes registration"""
        reg_data = {"owner_name": "Bob", "owner_phone": "555-1111", "pet_name": "Buddy", "pet_type": "Dog", "pet_age": 6}
        post_response = self.app.post('/api/registrations', data=json.dumps(reg_data), content_type='application/json')
        reg_id = json.loads(post_response.data.decode())['id']
        
        response = self.app.delete(f'/api/registrations/{reg_id}')
        self.assertEqual(response.status_code, 200)
        
        # Verify deletion
        get_response = self.app.get(f'/api/registrations/{reg_id}')
        self.assertEqual(get_response.status_code, 404)

    # COMMIT 58: Appointment endpoint tests
    def test_post_appointment_creates_new_appointment(self):
        """Test POST /api/appointments creates appointment"""
        # Create registration first
        reg_data = {"owner_name": "Carol", "owner_phone": "555-2222", "pet_name": "Molly", "pet_type": "Cat", "pet_age": 3}
        reg_response = self.app.post('/api/registrations', data=json.dumps(reg_data), content_type='application/json')
        reg_id = json.loads(reg_response.data.decode())['id']
        
        # Create appointment
        apt_data = {
            "registration_id": reg_id,
            "owner_name": "Carol",
            "pet_name": "Molly",
            "pet_type": "Cat",
            "appointment_date": "2026-07-20",
            "appointment_time": "10:00",
            "veterinarian": "Dr. Sarah Jenkins",
            "reason": "Annual checkup"
        }
        response = self.app.post('/api/appointments', data=json.dumps(apt_data), content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode())
        self.assertEqual(data['registration_id'], reg_id)

    def test_get_all_appointments(self):
        """Test GET /api/appointments retrieves all appointments"""
        response = self.app.get('/api/appointments')
        self.assertEqual(response.status_code, 200)

    def test_get_appointment_by_id(self):
        """Test GET /api/appointments/<id> retrieves specific appointment"""
        # Setup: create registration and appointment
        reg_data = {"owner_name": "Dave", "owner_phone": "555-3333", "pet_name": "Charlie", "pet_type": "Dog", "pet_age": 2}
        reg_response = self.app.post('/api/registrations', data=json.dumps(reg_data), content_type='application/json')
        reg_id = json.loads(reg_response.data.decode())['id']
        
        apt_data = {
            "registration_id": reg_id,
            "owner_name": "Dave",
            "pet_name": "Charlie",
            "pet_type": "Dog",
            "appointment_date": "2026-07-22",
            "appointment_time": "14:30",
            "veterinarian": "Dr. Alex Carter",
            "reason": "Vaccination"
        }
        apt_response = self.app.post('/api/appointments', data=json.dumps(apt_data), content_type='application/json')
        apt_id = json.loads(apt_response.data.decode())['id']
        
        response = self.app.get(f'/api/appointments/{apt_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertEqual(data['pet_name'], 'Charlie')

    def test_delete_appointment(self):
        """Test DELETE /api/appointments/<id>"""
        # Setup
        reg_data = {"owner_name": "Eve", "owner_phone": "555-4444", "pet_name": "Ethan", "pet_type": "Dog", "pet_age": 1}
        reg_response = self.app.post('/api/registrations', data=json.dumps(reg_data), content_type='application/json')
        reg_id = json.loads(reg_response.data.decode())['id']
        
        apt_data = {
            "registration_id": reg_id,
            "owner_name": "Eve",
            "pet_name": "Ethan",
            "pet_type": "Dog",
            "appointment_date": "2026-08-01",
            "appointment_time": "09:00",
            "veterinarian": "Dr. Emily Ross",
            "reason": "Check-up"
        }
        apt_response = self.app.post('/api/appointments', data=json.dumps(apt_data), content_type='application/json')
        apt_id = json.loads(apt_response.data.decode())['id']
        
        response = self.app.delete(f'/api/appointments/{apt_id}')
        self.assertEqual(response.status_code, 200)

    # COMMIT 59: Consolidated clinical report pipeline test
    def test_consolidated_clinical_report_pipeline(self):
        """Test consolidated clinical report with health status evaluation"""
        # Create registration
        reg = {"owner_name": "Vidya", "owner_phone": "999", "pet_name": "Sunnyy", "pet_type": "Dog", "pet_age": 4}
        reg_response = self.app.post('/api/registrations', data=json.dumps(reg), content_type='application/json')
        reg_id = json.loads(reg_response.data.decode())['id']
        
        # Add medication with symptoms
        med = {
            "registration_id": reg_id, 
            "owner_name": "Vidya", 
            "pet_name": "Sunnyy", 
            "veterinarian": "Dr. Sarah Jenkins", 
            "medication_details": "Paracetamol", 
            "frequency": "once a day", 
            "symptoms": "High fever"
        }
        self.app.post('/api/medications', data=json.dumps(med), content_type='application/json')
        
        # Get clinical history
        response = self.app.get(f'/api/treatments/history?registration_id={reg_id}')
        data = json.loads(response.data.decode())
        
        # Confirms urgent symptoms trigger red status
        self.assertEqual(response.status_code, 200)
        self.assertIn('Needs Attention', data['status'])

if __name__ == '__main__':
    unittest.main()