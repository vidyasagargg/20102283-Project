import sqlite3
import os

DB_FILE = "vet_clinic.db"

def seed_database():
    if not os.path.exists(DB_FILE):
        print(f"⚠️ Error: '{DB_FILE}' not found. Please run 'python3 app.py' first to initialize the database tables.")
        return

    print("🚀 Connecting to database and enabling foreign key constraints...")
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    try:
        # Clear existing rows from previous sessions to maintain clean serial IDs
        print("🧹 Clearing old data to ensure pristine seeding IDs (1, 2, 3)...")
        cursor.execute("DELETE FROM vaccinations;")
        cursor.execute("DELETE FROM medications;")
        cursor.execute("DELETE FROM appointments;")
        cursor.execute("DELETE FROM registrations;")
        
        # Reset SQLite sequence counters for autoincrement keys
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('registrations', 'appointments', 'medications', 'vaccinations');")
        conn.commit()

        print("📝 Seeding Scenario 1: 🟢 Healthy Pet Profile (Kutta)...")
        # 1. Registration (Generates ID: 1)
        cursor.execute('''
            INSERT INTO registrations (id, owner_name, owner_phone, pet_name, pet_type, pet_age)
            VALUES (1, 'Kris', '+353 87 111 2222', 'Kutta', 'Dog', 3);
        ''')
        # 2. Appointment
        cursor.execute('''
            INSERT INTO appointments (registration_id, owner_name, pet_name, pet_type, appointment_date, appointment_time, veterinarian, reason)
            VALUES (1, 'Kris', 'Kutta', 'Dog', '2026-06-15', '10:00', 'Dr. Sarah Jenkins', 'Annual wellness exam and preventative care');
        ''')
        # 3. Medication
        cursor.execute('''
            INSERT INTO medications (registration_id, owner_name, pet_name, veterinarian, medication_details, frequency, symptoms)
            VALUES (1, 'Kris', 'Kutta', 'Dr. Sarah Jenkins', 'Joint Health Vitamins', 'once a day', '');
        ''')
        # 4. Vaccination
        cursor.execute('''
            INSERT INTO vaccinations (registration_id, owner_name, pet_name, veterinarian, vaccination_details, vaccination_date)
            VALUES (1, 'Kris', 'Kutta', 'Dr. Sarah Jenkins', 'DHPP Canine Core Vaccine', '2026-06-15');
        ''')


        print("📝 Seeding Scenario 2: 🟡 Vaccination Overdue Profile (Sunnyy)...")
        # 1. Registration (Generates ID: 2)
        cursor.execute('''
            INSERT INTO registrations (id, owner_name, owner_phone, pet_name, pet_type, pet_age)
            VALUES (2, 'Vidya', '+353 87 333 4444', 'Sunnyy', 'Dog', 5);
        ''')
        # 2. Appointment
        cursor.execute('''
            INSERT INTO appointments (registration_id, owner_name, pet_name, pet_type, appointment_date, appointment_time, veterinarian, reason)
            VALUES (2, 'Vidya', 'Sunnyy', 'Dog', '2025-05-10', '14:30', 'Dr. Alex Carter', 'Routine claw trim');
        ''')
        # 3. Medication
        cursor.execute('''
            INSERT INTO medications (registration_id, owner_name, pet_name, veterinarian, medication_details, frequency, symptoms)
            VALUES (2, 'Vidya', 'Sunnyy', 'Dr. Alex Carter', 'Soothing Skin Ointment', 'twice a day', '');
        ''')
        # 4. Vaccination
        cursor.execute('''
            INSERT INTO vaccinations (registration_id, owner_name, pet_name, veterinarian, vaccination_details, vaccination_date)
            VALUES (2, 'Vidya', 'Sunnyy', 'Dr. Alex Carter', 'Rabies Booster Batch #A4', '2025-05-10');
        ''')


        print("📝 Seeding Scenario 3: 🔴 Needs Attention Profile (Fluffy)...")
        # 1. Registration (Generates ID: 3)
        cursor.execute('''
            INSERT INTO registrations (id, owner_name, owner_phone, pet_name, pet_type, pet_age)
            VALUES (3, 'Alice Smith', '+353 87 555 6666', 'Fluffy', 'Cat', 2);
        ''')
        # 2. Appointment
        cursor.execute('''
            INSERT INTO appointments (registration_id, owner_name, pet_name, pet_type, appointment_date, appointment_time, veterinarian, reason)
            VALUES (3, 'Alice Smith', 'Fluffy', 'Cat', '2026-07-12', '11:15', 'Dr. Emily Ross', 'Emergency checkup for severe loss of appetite');
        ''')
        # 3. Medication
        cursor.execute('''
            INSERT INTO medications (registration_id, owner_name, pet_name, veterinarian, medication_details, frequency, symptoms)
            VALUES (3, 'Alice Smith', 'Fluffy', 'Dr. Emily Ross', 'Anti-emetic liquid suspension', 'thrice a day', 'fever and food poison');
        ''')
        # 4. Vaccination
        cursor.execute('''
            INSERT INTO vaccinations (registration_id, owner_name, pet_name, veterinarian, vaccination_details, vaccination_date)
            VALUES (3, 'Alice Smith', 'Fluffy', 'Dr. Emily Ross', 'Feline Leukemia Core Booster', '2026-07-12');
        ''')

        conn.commit()
        print("✨ Database successfully seeded with all mock scenarios!")

    except sqlite3.Error as e:
        conn.rollback()
        print(f"❌ Database error encountered during transaction execution loop: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    seed_database()