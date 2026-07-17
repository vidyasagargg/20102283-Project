# 20102283-Project
GITHUB Repository for Programming Project

Project Title: Paws & Claws Vet Clinic Management System

## What is this project?

This is basically a booking system for a vet clinic. Instead of using paper and pen to keep track of appointments, owner can book online and the vet can see all the appointments at one place. We also track medications and vaccinations for every pet.

I'm building this application for my Programming module assignment. The idea is to make it easier for small vet clinic to manage their day-to-day work without having to manually write everything down.

## How does it work?

The system has two main parts:

**Backend (the main logic):**
- Written in Python using Flask, a web framework
- Uses SQLite for the database, stores all the data
- Has endpoints/routes that handle creating, reading, updating, and deleting data
- Basically when someone submits a form, it saves it to the database

**Frontend (what you see on the screen UI):**
- Used HTML for the visual stuff
- Used JavaScript to make things interactive without page refresh
- Fetching data from the backend and displays it nicely

When you type something into the form, JavaScript sends it to Python, Python saves it to the database, and then JavaScript updates the page to show the new data.

## What features does it have?

1. **Register Pets** - Add owner details and the pets information
2. **Book Appointments** - Schedule a vet/Doctor appointment with a specific doctor
3. **Track Medications** - Keep notes on what meds a pet is taking
4. **Track Vaccinations** - Record when a pet gets vaccinated
5. **View Everything** - See all appointments, medications, and vaccination records in a table

## How to run this?

### What I need:
- Python 3.x installed
- Flask (`pip install flask`)
- SQLite comes built-in with Python

### Steps to run:

1. **First time setup:**
   ```
   python3 app.py
   ```
   This creates the database and starts the server. You should see something like "Running on http://127.0.0.1:5000"

2. **Open your browser:**
   Go to `http://localhost:5000` and you should see the vet clinic website
   MyLocalHost - 34.13.37.114

3. **Start using it:**
   - Click on "Register Pet" tab to add a new pet and pet owner
   - Click "Book Appointment" to schedule a vet/Doctor visit
   - Use the "Medications & Vaccines" tab to track pet health records

### To seed the database with test data:
```
python3 seed_db.py
```
This adds some dummy data for pets and appointments so you can test everything without entering data manually.

### To run tests:
```
python3 -m unittest test_app.py -v
```
This checks if everything is working correctly.

## Database Tables - What gets stored?

The system uses 5 main tables to organize data:

**registrations** - Stores pet owner and pet information
- owner name, phone, pet name, pet type, pet age

**appointments** - Books vet/Doctor visits
- date, time, which vet, why they're coming in

**medications** - Tracks medicine given to pets
- what medicine, how often to give it, any symptoms

**vaccinations** - Records vaccine shots given to pets
- vaccine name, date given

**veterinarians** - List of available vets
- their name, their specialty

## File Structure
.
├── app.py                 (Main Flask backend code)
├── seed_db.py            (Adds fake test data)
├── test_app.py           (Tests to check if things work)
├── vet_clinic.db         (Database - created when you run app.py)
└── static/
    ├── index.html        (The website page)
    └── app.js           (Makes the website interactive)


## How the data flows

1. User fills out a form in the browser
2. JavaScript catches the submit event
3. JavaScript sends the data to Python as JSON
4. Python receives it and saves to the database
5. Python sends back a success message
6. JavaScript updates the page to show the new data

It's all connected, so when you add something, it shows up immediately without refreshing the page.

## Some important things about this project

- **Validation:** Before saving to the database, we check that required fields aren't empty
- **Foreign Keys:** Appointments and medical records are linked to pet registrations, so if you delete a pet, all their records delete too
- **Error Handling:** The system tries to catch errors and show helpful messages
- **Simple UI:** Nothing too fancy, just functional. The point is for the vet clinic to actually use it, not to look pretty

## What could be improved?

Honestly there's a lot that could be better:
- We Can add user login, right now anyone can see and edit everything
- We Can add more filtering options, like show me all appointments this week
- We stored The database as a file, which isn't ideal for a real business
- We can send emails to remind people about appointments
- Better styling would make it nicer to look at

But for this project, we're supposed to do minimal UI.

## Testing

If you run the tests and everything passes, it means:
- Creating new records works
- Reading from database works
- Updating records works
- Deleting records works

All the basic scenarios that we'd expect from a database system.

## Known issues / Things that might not work

- The system doesn't have a login, so anyone can access everything
- Times are stored as text, not actual time objects
- No way to cancel an appointment (you have to delete it)
- If the database gets corrupted for some reason, there's no backup

## Why I built it this way

- **Flask** - It's simple and good for beginners. Easy to understand what's happening
- **SQLite** - File-based, so no need to set up a complicated database server
- **Vanilla JavaScript** - No fancy frameworks, just plain JS using fetch() to talk to the backend
- **Simple HTML** - Just tables and forms, nothing complex

The goal was to learn how to build a working web application from scratch, not to build something perfect for real use.

## Final thoughts

This project taught me how databases, backend servers, and frontend websites all work together. It's not the most prettiest thing, and it's definitely not production-ready, but it works. Getting an actual application running was way more satisfying than just learning theory.

Working but still learning how to make it better.


## References for the application building process.

This project is taken as reference from YOUTUBE - https://youtu.be/HZy2sSRZnxo?is=IN1B1GUw-Kj5JycQ

## Flask Application logic :
 This logic taken from reference of Flask tutorial blog - https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world

 And from Youtube - https://www.youtube.com/playlist?list=PL-osiE80TeTs4UjLw5MM6OjgkjFeUxCYH

 ## SQL Database Connection

 This logic is taken from reference - https://docs.python.org/3/library/sqlite3.html

 Creating Database tables taken reference and help from my friend.(Gurudev)

 I've taken CRUD operation reference from Gemini and Chatgpt.
 https://gemini.google.com/u/3/app/da3e9ae535ff18f7
 

 Rule based health engine is taken reference from realpython - https://realpython.com/python-conditional-statements/

 In Javascript, "Fetch API" logic taken reference from "Bro code" Youtube channel - https://youtu.be/37vxWr0WgQk?si=8FS2T2ji_ixe2EiR

 HTML logic is taken reference from - W3school - https://www.w3schools.com/html/html_forms.asp



