document.addEventListener('DOMContentLoaded', () => {
    loadAppointments();
    loadRegistrations();
    loadVeterinarians();
    
    document.getElementById('appointmentForm').addEventListener('submit', handleAppointmentSubmit);
    document.getElementById('registrationForm').addEventListener('submit', handleRegistrationSubmit);
    document.getElementById('medicationForm').addEventListener('submit', handleMedicationSubmit);
    document.getElementById('vaccinationForm').addEventListener('submit', handleVaccinationSubmit);
});

function switchTab(tabName) {
    document.getElementById('sectionRegistrations').style.display = tabName === 'registrations' ? 'block' : 'none';
    document.getElementById('sectionAppointments').style.display = tabName === 'appointments' ? 'block' : 'none';
    document.getElementById('sectionTreatments').style.display = tabName === 'treatments' ? 'block' : 'none';
}

// TAB 1 - registrations
function toggleRegistrationsLog() {
    const container = document.getElementById('registrationsLogContainer');
    const btn = document.getElementById('viewAllRegsBtn');
    if (container.style.display === 'none') {
        container.style.display = 'block';
        btn.innerText = "Hide records log";
        loadRegistrations();
    } else {
        container.style.display = 'none';
        btn.innerText = "View all records";
    }
}

//SEARCH FIELD
async function searchRegistrationById() {
    const searchId = document.getElementById('regSearchId').value;
    const container = document.getElementById('registrationsLogContainer');
    const tbody = document.getElementById('registrationsBody');
    if (!searchId) { alert("Please enter a valid target Registration ID to run lookups!"); return; }

    const response = await fetch(`/api/registrations/${searchId}`);
    if (response.status === 404) {
        alert("❌ Registration ID profile index not found inside data tables!");
        return;
    }
    const reg = await response.json();
    container.style.display = 'block';
    document.getElementById('viewAllRegsBtn').innerText = "View all records"; // Reset baseline toggle string
    
    tbody.innerHTML = '';
    const tr = document.createElement('tr');
    tr.innerHTML = `<td><b>${reg.id}</b></td><td>${reg.owner_name}</td><td>${reg.owner_phone}</td><td>${reg.pet_name}</td><td>${reg.pet_type}</td>
        <td><button onclick="loadPetHistory(${reg.id})">🔎 History</button><button onclick="populateRegistrationEdit(${reg.id}, '${reg.owner_name}', '${reg.owner_phone}', '${reg.pet_name}', '${reg.pet_type}', ${reg.pet_age})">Edit</button><button onclick="deleteRegistration(${reg.id})">Delete</button></td>`;
    tbody.appendChild(tr);
}

function toggleAppointmentsLog() {
    const container = document.getElementById('appointmentsLogContainer');
    const btn = document.getElementById('viewAllAppsBtn');
    if (container.style.display === 'none') {
        container.style.display = 'block';
        btn.innerText = "Hide appointments log";
        loadAppointments();
    } else {
        container.style.display = 'none';
        btn.innerText = "View all appointments";
    }
}

async function loadVeterinarians() {
    const response = await fetch('/api/veterinarians');
    const vets = await response.json();
    const dropdown = document.getElementById('appVet');
    dropdown.innerHTML = '<option value="">-- Select Vet --</option>';
    vets.forEach(v => {
        const opt = document.createElement('option');
        opt.value = v.name; opt.textContent = `${v.name} (${v.specialty})`;
        dropdown.appendChild(opt);
    });
}

async function verifyAndPopulateRegistration() {
    const regId = document.getElementById('appRegId').value;
    const feedback = document.getElementById('validationFeedback');
    if (!regId) { resetAppFields(); feedback.innerText = ""; return; }

    const response = await fetch(`/api/registrations/${regId}/latest_consultation`);
    if (response.status === 404) {
        feedback.style.color = "red"; feedback.innerText = "❌ ID Not Registered!";
        resetAppFields(); return;
    }
    const data = await response.json();
    feedback.style.color = "green"; feedback.innerText = `✔️ Profile Verified (${data.pet_name})`;
    document.getElementById('appOwnerName').value = data.owner_name;
    document.getElementById('appPetName').value = data.pet_name;
    document.getElementById('appPetType').value = data.pet_type;
}

function resetAppFields() {
    document.getElementById('appOwnerName').value = '';
    document.getElementById('appPetName').value = '';
    document.getElementById('appPetType').value = '';
}

async function verifyAndPopulateConsultation() {
    const regId = document.getElementById('treatRegId').value;
    const feedback = document.getElementById('treatmentFeedback');
    const medBtn = document.getElementById('medSubmitBtn');
    const vacBtn = document.getElementById('vacSubmitBtn');
    if (!regId) { resetPatientContextFields(); feedback.innerText = ""; clearLogGridsOnly(); return; }

    const response = await fetch(`/api/registrations/${regId}/latest_consultation`);
    if (response.status === 404) {
        feedback.style.color = "red"; feedback.innerText = "❌ Registration Profile ID not found in records!";
        medBtn.disabled = true; vacBtn.disabled = true; resetPatientContextFields(); clearLogGridsOnly(); return;
    }
    const data = await response.json();
    document.getElementById('treatOwnerName').value = data.owner_name;
    document.getElementById('treatPetName').value = data.pet_name;
    document.getElementById('treatVet').value = data.consulted_doctor;

    if (data.consulted_doctor === "No prior appointment consultation found") {
        feedback.style.color = "orange"; feedback.innerText = "⚠️ Missing active consultation record! Please schedule an appointment checkup first.";
        medBtn.disabled = true; vacBtn.disabled = true; clearLogGridsOnly();
    } else {
        feedback.style.color = "green"; feedback.innerText = `✔️ Patient & Consultation Verified (Attending: ${data.consulted_doctor})`;
        medBtn.disabled = false; vacBtn.disabled = false;
        loadScopedMedications(regId); loadScopedVaccinations(regId);
    }
}

function resetPatientContextFields() {
    document.getElementById('treatOwnerName').value = '';
    document.getElementById('treatPetName').value = '';
    document.getElementById('treatVet').value = '';
}

function clearLogGridsOnly() {
    document.getElementById('medicationsBody').innerHTML = '';
    document.getElementById('vaccinationsBody').innerHTML = '';
}

function resetPatientContext() {
    document.getElementById('treatRegId').value = '';
    document.getElementById('treatmentFeedback').innerText = '';
    resetPatientContextFields(); clearMedicationFormOnly(); clearVaccinationFormOnly(); clearLogGridsOnly();
    document.getElementById('medSubmitBtn').disabled = true; document.getElementById('vacSubmitBtn').disabled = true;
}


// --- MEDICATION CRUD Operations ---

async function handleMedicationSubmit(e) {
    e.preventDefault();
    const id = document.getElementById('medId').value;
    const activeRegId = document.getElementById('treatRegId').value;
    const payload = {
        registration_id: parseInt(activeRegId),
        owner_name: document.getElementById('treatOwnerName').value,
        pet_name: document.getElementById('treatPetName').value,
        veterinarian: document.getElementById('treatVet').value,
        medication_details: document.getElementById('treatMeds').value,
        frequency: document.getElementById('treatFreq').value,
        symptoms: document.getElementById('treatSymptoms').value
    };

    let method = id ? 'PUT' : 'POST'; let url = id ? `/api/medications/${id}` : '/api/medications';
    const res = await fetch(url, { method: method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    if (res.ok) { clearMedicationFormOnly(); loadScopedMedications(activeRegId); }
}

function clearMedicationFormOnly() {
    document.getElementById('medId').value = ''; document.getElementById('treatMeds').value = ''; document.getElementById('treatFreq').value = '';
    document.getElementById('treatSymptoms').value = ''; document.getElementById('safetyWarningMessage').innerText = '';
    document.getElementById('medSubmitBtn').innerText = "Append Medicine Entry"; document.getElementById('medCancelBtn').style.display = "none";
}

async function loadScopedMedications(regId) {
    if (!regId) return;
    const response = await fetch(`/api/medications?registration_id=${regId}`);
    const data = await response.json();
    const tbody = document.getElementById('medicationsBody'); tbody.innerHTML = '';
    data.forEach(m => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${m.id}</td><td>${m.pet_name}</td><td><b>${m.medication_details}</b></td><td><code>${m.frequency}</code></td>
            <td><button onclick="populateMedicationEdit(${m.id}, '${m.medication_details}', '${m.frequency}', '${m.symptoms || ''}')">Edit</button><button onclick="deleteMedication(${m.id})">X</button></td>`;
        tbody.appendChild(tr);
    });
}

function populateMedicationEdit(id, details, frequency, symptoms) {
    document.getElementById('medId').value = id; document.getElementById('treatMeds').value = details; 
    document.getElementById('treatFreq').value = frequency; document.getElementById('treatSymptoms').value = symptoms;
    document.getElementById('medSubmitBtn').innerText = "Update Medicine"; document.getElementById('medCancelBtn').style.display = "inline-block";
}

async function deleteMedication(id) {
    const activeRegId = document.getElementById('treatRegId').value;
    if (confirm("Delete prescription record?")) { await fetch(`/api/medications/${id}`, { method: 'DELETE' }); loadScopedMedications(activeRegId); }
}


// --- VACCINATION CRUD Operations ---

async function handleVaccinationSubmit(e) {
    e.preventDefault();
    const id = document.getElementById('vacId').value;
    const activeRegId = document.getElementById('treatRegId').value;
    const payload = {
        registration_id: parseInt(activeRegId), owner_name: document.getElementById('treatOwnerName').value,
        pet_name: document.getElementById('treatPetName').value, veterinarian: document.getElementById('treatVet').value,
        vaccination_details: document.getElementById('treatVacs').value, vaccination_date: document.getElementById('treatVacDate').value
    };

    let method = id ? 'PUT' : 'POST'; let url = id ? `/api/vaccinations/${id}` : '/api/vaccinations';
    const res = await fetch(url, { method: method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    if (res.ok) { clearVaccinationFormOnly(); loadScopedVaccinations(activeRegId); }
}

function clearVaccinationFormOnly() {
    document.getElementById('vacId').value = ''; document.getElementById('treatVacs').value = ''; document.getElementById('treatVacDate').value = '';
    document.getElementById('vacSubmitBtn').innerText = "Append Vaccination Entry"; document.getElementById('vacCancelBtn').style.display = "none";
}

async function loadScopedVaccinations(regId) {
    if (!regId) return;
    const response = await fetch(`/api/vaccinations?registration_id=${regId}`);
    const data = await response.json();
    const tbody = document.getElementById('vaccinationsBody'); tbody.innerHTML = '';
    data.forEach(v => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${v.id}</td><td>${v.pet_name}</td><td><b>${v.vaccination_details}</b></td>
            <td><button onclick="populateVaccinationEdit(${v.id}, '${v.vaccination_details}', '${v.vaccination_date}')">Edit</button><button onclick="deleteVaccination(${v.id})">X</button></td>`;
        tbody.appendChild(tr);
    });
}

function populateVaccinationEdit(id, details, date) {
    document.getElementById('vacId').value = id; document.getElementById('treatVacs').value = details; document.getElementById('treatVacDate').value = date;
    document.getElementById('vacSubmitBtn').innerText = "Update Vaccine"; document.getElementById('vacCancelBtn').style.display = "inline-block";
}

async function deleteVaccination(id) {
    const activeRegId = document.getElementById('treatRegId').value;
    if (confirm("Delete vaccination log entry?")) { await fetch(`/api/vaccinations/${id}`, { method: 'DELETE' }); loadScopedVaccinations(activeRegId); }
}


// --- APPOINTMENTS & REGISTRATIONS ---

async function checkClinicalSafetyRules() {
    const meds = document.getElementById('treatMeds').value;
    const warningDiv = document.getElementById('safetyWarningMessage');
    const res = await fetch('/api/treatments/validate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ medications: meds }) });
    const data = await res.json(); warningDiv.innerText = data.status === "warning" ? data.message : "";
}

async function loadAppointments() {
    const response = await fetch('/api/appointments'); const data = await response.json();
    const tbody = document.getElementById('appointmentsBody'); tbody.innerHTML = '';
    data.forEach(app => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${app.id}</td><td>${app.registration_id}</td><td>${app.owner_name}</td><td>${app.pet_name}</td><td>${app.pet_type}</td><td>${app.appointment_date}</td><td>${app.appointment_time}</td><td>${app.veterinarian}</td><td>${app.reason}</td>
            <td><button onclick="populateAppointmentEdit(${app.id}, ${app.registration_id}, '${app.owner_name}', '${app.pet_name}', '${app.pet_type}', '${app.appointment_date}', '${app.appointment_time}', '${app.veterinarian}', '${app.reason}')">Edit</button><button onclick="deleteAppointment(${app.id})">Cancel</button></td>`;
        tbody.appendChild(tr);
    });
}

function populateAppointmentEdit(id, regId, owner, pet, type, date, time, vet, reason) {
    switchTab('appointments'); document.getElementById('appointmentsLogContainer').style.display = 'block'; document.getElementById('viewAllAppsBtn').innerText = "Hide appointments log";
    document.getElementById('appId').value = id; document.getElementById('appRegId').value = regId; document.getElementById('appRegId').readOnly = true;
    document.getElementById('appOwnerName').value = owner; document.getElementById('appPetName').value = pet; document.getElementById('appPetType').value = type;
    document.getElementById('appDate').value = date; document.getElementById('appTime').value = time; document.getElementById('appVet').value = vet; document.getElementById('appReason').value = reason;
    document.getElementById('validationFeedback').innerText = ""; document.getElementById('appSubmitBtn').innerText = "Update Appointment"; document.getElementById('appCancelBtn').style.display = "inline-block";
}

async function handleAppointmentSubmit(e) {
    e.preventDefault(); const id = document.getElementById('appId').value;
    const payload = {
        registration_id: parseInt(document.getElementById('appRegId').value), owner_name: document.getElementById('appOwnerName').value,
        pet_name: document.getElementById('appPetName').value, pet_type: document.getElementById('appPetType').value,
        appointment_date: document.getElementById('appDate').value, appointment_time: document.getElementById('appTime').value,
        veterinarian: document.getElementById('appVet').value, reason: document.getElementById('appReason').value
    };
    let method = id ? 'PUT' : 'POST'; let url = id ? `/api/appointments/${id}` : '/api/appointments';
    const res = await fetch(url, { method: method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    if (res.ok) {
        clearAppointmentForm(); const alertSpan = document.getElementById('appointmentSuccessMessage');
        alertSpan.innerText = "Appointment scheduled"; setTimeout(() => { alertSpan.innerText = ""; }, 4000); loadAppointments();
    }
}

function clearAppointmentForm() {
    document.getElementById('appId').value = ''; document.getElementById('appRegId').value = ''; document.getElementById('appRegId').readOnly = false;
    document.getElementById('validationFeedback').innerText = ''; document.getElementById('appointmentForm').reset();
    document.getElementById('appSubmitBtn').innerText = "Save Appointment"; document.getElementById('appCancelBtn').style.display = "none";
}

async function loadRegistrations() {
    const response = await fetch('/api/registrations'); const data = await response.json();
    const tbody = document.getElementById('registrationsBody'); tbody.innerHTML = '';
    data.forEach(reg => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td><b>${reg.id}</b></td><td>${reg.owner_name}</td><td>${reg.owner_phone}</td><td>${reg.pet_name}</td><td>${reg.pet_type}</td>
            <td><button onclick="loadPetHistory(${reg.id})">🔎 History</button><button onclick="populateRegistrationEdit(${reg.id}, '${reg.owner_name}', '${reg.owner_phone}', '${reg.pet_name}', '${reg.pet_type}', ${reg.pet_age})">Edit</button><button onclick="deleteRegistration(${reg.id})">Delete</button></td>`;
        tbody.appendChild(tr);
    });
}

function populateRegistrationEdit(id, owner, phone, pet, type, age) {
    // Reveal container to easily see changes during edit sessions
    document.getElementById('registrationsLogContainer').style.display = 'block';
    document.getElementById('viewAllRegsBtn').innerText = "Hide records log";

    document.getElementById('regId').value = id; document.getElementById('regOwnerName').value = owner; document.getElementById('regOwnerPhone').value = phone;
    document.getElementById('regPetName').value = pet; document.getElementById('regPetType').value = type; document.getElementById('regPetAge').value = age;
    document.getElementById('regSubmitBtn').innerText = "Update Profile"; document.getElementById('regCancelBtn').style.display = "inline-block";
}

// ENHANCED: Captures and alerts unique serial registry keys dynamically
async function handleRegistrationSubmit(e) {
    e.preventDefault(); const id = document.getElementById('regId').value;
    const payload = {
        owner_name: document.getElementById('regOwnerName').value, owner_phone: document.getElementById('regOwnerPhone').value,
        pet_name: document.getElementById('regPetName').value, pet_type: document.getElementById('regPetType').value,
        pet_age: parseInt(document.getElementById('regPetAge').value)
    };
    let method = id ? 'PUT' : 'POST'; let url = id ? `/api/registrations/${id}` : '/api/registrations';
    const res = await fetch(url, { method: method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    if (res.ok) {
        const data = await res.json();
        clearRegistrationForm();
        loadRegistrations();
        loadAppointments();
        
        // Success confirmation banner
        if (method === 'POST') {
            const alertSpan = document.getElementById('registrationSuccessMessage');
            alertSpan.innerText = `Record created successfully with registration ID "${data.id}"`;
            setTimeout(() => { alertSpan.innerText = ""; }, 5000);
        }
    }
}

function clearRegistrationForm() {
    document.getElementById('regId').value = ''; document.getElementById('registrationForm').reset();
    document.getElementById('regSubmitBtn').innerText = "Register Client"; document.getElementById('regCancelBtn').style.display = "none";
}

async function deleteRegistration(id) {
    if (confirm("Delete client profile? Doing so will clear all associated records!")) {
        await fetch(`/api/registrations/${id}`, { method: 'DELETE' }); loadRegistrations(); loadAppointments();
        if (document.getElementById('treatRegId').value == id) { resetPatientContext(); }
    }
}

async function loadPetHistory(regId) {
    const response = await fetch(`/api/treatments/history?registration_id=${regId}`);
    const data = await response.json();
    
    const p = data.profile;
    document.getElementById('historyTitle').innerText = `📋 Complete Clinical Medical Card for: ${p.pet_name}`;
    
    document.getElementById('reportMetaText').innerText = `Species: ${p.pet_type} | Age: ${p.pet_age} Years Old | Registered Owner ID: ${p.id} (${p.owner_name})`;
    document.getElementById('reportStatusBadge').innerText = data.status;
    document.getElementById('reportRecommendationText').innerText = data.recommendation;
    
    const tbody = document.getElementById('historyBody');
    tbody.innerHTML = '';
    if (data.ledger.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:gray;">No clinical treatment history records found.</td></tr>`;
    } else {
        data.ledger.forEach(h => {
            const tr = document.createElement('tr');
            let color = h.entry_type === 'Medication' ? 'blue' : 'purple';
            tr.innerHTML = `<td>${h.id}</td><td><b style="color:${color};">${h.entry_type}</b></td><td>${h.veterinarian}</td><td>${h.details}</td><td>${h.symptoms || 'N/A'}</td>`;
            tbody.appendChild(tr);
        });
    }
    document.getElementById('petHistorySection').style.display = 'block';
    window.scrollTo(0, 0);
}