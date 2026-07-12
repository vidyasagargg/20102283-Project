// ============================================================================
// PAWS & CLAWS VET CLINIC - FRONTEND APPLICATION
// ============================================================================

const API_BASE_URL = "http://localhost:5000/api";

let currentTab = 'registrations';
let editingRegistrationId = null;
let editingAppointmentId = null;
let editingMedicationId = null;
let editingVaccinationId = null;
let currentPatientRegistrationId = null;

// API HELPER FUNCTIONS
async function createApiCall(method, endpoint, data = null) {
    try {
        const options = {
            method: method,
            headers: { 'Content-Type': 'application/json' }
        };
        
        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(API_BASE_URL + endpoint, options);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error(`API Error [${method} ${endpoint}]:`, error);
        throw error;
    }
}

function showError(message, elementId = null) {
    console.error(message);
    if (elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = `❌ ${message}`;
            element.style.color = 'red';
            setTimeout(() => { element.textContent = ''; }, 3000);
        }
    } else {
        alert(`Error: ${message}`);
    }
}

function showSuccess(message, elementId = null) {
    console.log(message);
    if (elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = `✅ ${message}`;
            element.style.color = 'green';
            setTimeout(() => { element.textContent = ''; }, 3000);
        }
    }
}


// TAB SWITCHING
function switchTab(tabName) {
    document.getElementById('sectionRegistrations').style.display = 'none';
    document.getElementById('sectionAppointments').style.display = 'none';
    document.getElementById('sectionTreatments').style.display = 'none';
    
    switch(tabName) {
        case 'registrations':
            document.getElementById('sectionRegistrations').style.display = 'block';
            currentTab = 'registrations';
            fetchRegistrations();
            break;
        case 'appointments':
            document.getElementById('sectionAppointments').style.display = 'block';
            currentTab = 'appointments';
            break;
        case 'treatments':
            document.getElementById('sectionTreatments').style.display = 'block';
            currentTab = 'treatments';
            break;
    }
    
    document.getElementById('tabBtnRegistrations').style.fontWeight = tabName === 'registrations' ? 'bold' : 'normal';
    document.getElementById('tabBtnAppointments').style.fontWeight = tabName === 'appointments' ? 'bold' : 'normal';
    document.getElementById('tabBtnTreatments').style.fontWeight = tabName === 'treatments' ? 'bold' : 'normal';
}

window.addEventListener('load', function() {
    switchTab('registrations');
    populateVeterinarianDropdown();
});

// REGISTRATION FORM HANDLING
document.getElementById('registrationForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const regId = document.getElementById('regId').value;
    const ownerName = document.getElementById('regOwnerName').value;
    const ownerPhone = document.getElementById('regOwnerPhone').value;
    const petName = document.getElementById('regPetName').value;
    const petType = document.getElementById('regPetType').value;
    const petAge = parseInt(document.getElementById('regPetAge').value);
    
    if (!ownerName.trim()) {
        showError('Owner name is required');
        return;
    }
    if (!petAge || petAge < 0) {
        showError('Valid pet age is required');
        return;
    }
    
    try {
        const data = {
            owner_name: ownerName,
            owner_phone: ownerPhone,
            pet_name: petName,
            pet_type: petType,
            pet_age: petAge
        };
        
        if (regId) {
            await createApiCall('PUT', `/registrations/${regId}`, data);
            showSuccess('Registration updated successfully!');
            document.getElementById('regCancelBtn').style.display = 'none';
            document.getElementById('regSubmitBtn').textContent = 'Register Client';
        } else {
            await createApiCall('POST', '/registrations', data);
            showSuccess('Registration created successfully!');
        }
        
        clearRegistrationForm();
        fetchRegistrations();
    } catch (error) {
        showError(`Failed to save registration: ${error.message}`);
    }
});

async function fetchRegistrations() {
    try {
        const registrations = await createApiCall('GET', '/registrations');
        const tbody = document.getElementById('registrationsBody');
        tbody.innerHTML = '';
        
        if (!registrations || registrations.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">No registrations found</td></tr>';
            return;
        }
        
        registrations.forEach(reg => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${reg.id}</td>
                <td>${reg.owner_name}</td>
                <td>${reg.owner_phone}</td>
                <td>${reg.pet_name}</td>
                <td>${reg.pet_type}</td>
                <td>
                    <button onclick="editRegistration(${reg.id})" style="margin-right: 5px;">✏️ Edit</button>
                    <button onclick="deleteRegistration(${reg.id})" style="margin-right: 5px;">🗑️ Delete</button>
                    <button onclick="showMedicalCardReport(${reg.id})">📋 Medical Card</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        showError(`Failed to load registrations: ${error.message}`);
    }
}

async function editRegistration(id) {
    try {
        const registration = await createApiCall('GET', `/registrations/${id}`);
        
        document.getElementById('regId').value = registration.id;
        document.getElementById('regOwnerName').value = registration.owner_name;
        document.getElementById('regOwnerPhone').value = registration.owner_phone;
        document.getElementById('regPetName').value = registration.pet_name;
        document.getElementById('regPetType').value = registration.pet_type;
        document.getElementById('regPetAge').value = registration.pet_age;
        
        document.getElementById('regCancelBtn').style.display = 'inline-block';
        document.getElementById('regSubmitBtn').textContent = 'Update Registration';
        
        editingRegistrationId = id;
        document.getElementById('registrationForm').scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
        showError(`Failed to load registration: ${error.message}`);
    }
}

async function deleteRegistration(id) {
    if (!confirm('Are you sure you want to delete this registration and all associated records?')) {
        return;
    }
    
    try {
        await createApiCall('DELETE', `/registrations/${id}`);
        showSuccess('Registration deleted successfully!');
        fetchRegistrations();
    } catch (error) {
        showError(`Failed to delete registration: ${error.message}`);
    }
}

// APPOINTMENT FORM HANDLING
async function verifyAndPopulateRegistration() {
    const regId = document.getElementById('appRegId').value;
    const feedback = document.getElementById('validationFeedback');
    const submitBtn = document.getElementById('appSubmitBtn');
    
    if (!regId) {
        feedback.textContent = '';
        submitBtn.disabled = true;
        return;
    }
    
    try {
        const registration = await createApiCall('GET', `/registrations/${regId}`);
        
        document.getElementById('appOwnerName').value = registration.owner_name;
        document.getElementById('appPetName').value = registration.pet_name;
        document.getElementById('appPetType').value = registration.pet_type;
        
        feedback.textContent = '✅ Registration found!';
        feedback.style.color = 'green';
        submitBtn.disabled = false;
    } catch (error) {
        document.getElementById('appOwnerName').value = '';
        document.getElementById('appPetName').value = '';
        document.getElementById('appPetType').value = '';
        
        feedback.textContent = '❌ Registration not found';
        feedback.style.color = 'red';
        submitBtn.disabled = true;
    }
}

document.getElementById('appointmentForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const appId = document.getElementById('appId').value;
    const regId = document.getElementById('appRegId').value;
    const ownerName = document.getElementById('appOwnerName').value;
    const petName = document.getElementById('appPetName').value;
    const petType = document.getElementById('appPetType').value;
    const appDate = document.getElementById('appDate').value;
    const appTime = document.getElementById('appTime').value;
    const vet = document.getElementById('appVet').value;
    const reason = document.getElementById('appReason').value;
    
    if (!regId) {
        showError('Registration ID is required');
        return;
    }
    if (!appDate) {
        showError('Appointment date is required');
        return;
    }
    if (!appTime) {
        showError('Appointment time is required');
        return;
    }
    if (!vet) {
        showError('Veterinarian is required');
        return;
    }
    
    try {
        const data = {
            registration_id: parseInt(regId),
            owner_name: ownerName,
            pet_name: petName,
            pet_type: petType,
            appointment_date: appDate,
            appointment_time: appTime,
            veterinarian: vet,
            reason: reason
        };
        
        if (appId) {
            await createApiCall('PUT', `/appointments/${appId}`, data);
            showSuccess('Appointment updated successfully!', 'appointmentSuccessMessage');
            document.getElementById('appCancelBtn').style.display = 'none';
            document.getElementById('appSubmitBtn').textContent = 'Save Appointment';
        } else {
            await createApiCall('POST', '/appointments', data);
            showSuccess('Appointment created successfully!', 'appointmentSuccessMessage');
        }
        
        clearAppointmentForm();
        fetchAppointments();
    } catch (error) {
        showError(`Failed to save appointment: ${error.message}`);
    }
});

async function fetchAppointments() {
    try {
        const appointments = await createApiCall('GET', '/appointments');
        const tbody = document.getElementById('appointmentsBody');
        tbody.innerHTML = '';
        
        if (!appointments || appointments.length === 0) {
            tbody.innerHTML = '<tr><td colspan="10" style="text-align: center;">No appointments found</td></tr>';
            return;
        }
        
        appointments.forEach(apt => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${apt.id}</td>
                <td>${apt.registration_id}</td>
                <td>${apt.owner_name}</td>
                <td>${apt.pet_name}</td>
                <td>${apt.pet_type}</td>
                <td>${apt.appointment_date}</td>
                <td>${apt.appointment_time}</td>
                <td>${apt.veterinarian}</td>
                <td>${apt.reason}</td>
                <td>
                    <button onclick="editAppointment(${apt.id})" style="margin-right: 5px;">✏️ Edit</button>
                    <button onclick="deleteAppointment(${apt.id})">🗑️ Delete</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        showError(`Failed to load appointments: ${error.message}`);
    }
}

function toggleAppointmentsLog() {
    const container = document.getElementById('appointmentsLogContainer');
    const btn = document.getElementById('viewAllAppsBtn');
    
    if (container.style.display === 'none') {
        container.style.display = 'block';
        btn.textContent = 'Hide appointments';
        fetchAppointments();
    } else {
        container.style.display = 'none';
        btn.textContent = 'View all appointments';
    }
}

async function editAppointment(id) {
    try {
        const appointment = await createApiCall('GET', `/appointments/${id}`);
        
        document.getElementById('appId').value = appointment.id;
        document.getElementById('appRegId').value = appointment.registration_id;
        document.getElementById('appOwnerName').value = appointment.owner_name;
        document.getElementById('appPetName').value = appointment.pet_name;
        document.getElementById('appPetType').value = appointment.pet_type;
        document.getElementById('appDate').value = appointment.appointment_date;
        document.getElementById('appTime').value = appointment.appointment_time;
        document.getElementById('appVet').value = appointment.veterinarian;
        document.getElementById('appReason').value = appointment.reason;
        
        document.getElementById('appCancelBtn').style.display = 'inline-block';
        document.getElementById('appSubmitBtn').textContent = 'Update Appointment';
        
        document.getElementById('appointmentForm').scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
        showError(`Failed to load appointment: ${error.message}`);
    }
}

async function deleteAppointment(id) {
    if (!confirm('Are you sure you want to delete this appointment?')) {
        return;
    }
    
    try {
        await createApiCall('DELETE', `/appointments/${id}`);
        showSuccess('Appointment deleted successfully!');
        fetchAppointments();
    } catch (error) {
        showError(`Failed to delete appointment: ${error.message}`);
    }
}

// TREATMENT/MEDICATION/VACCINATION HANDLING
async function verifyAndPopulateConsultation() {
    const regId = document.getElementById('treatRegId').value;
    const feedback = document.getElementById('treatmentFeedback');
    const medBtn = document.getElementById('medSubmitBtn');
    const vacBtn = document.getElementById('vacSubmitBtn');
    
    if (!regId) {
        feedback.textContent = '';
        medBtn.disabled = true;
        vacBtn.disabled = true;
        return;
    }
    
    try {
        const registration = await createApiCall('GET', `/registrations/${regId}`);
        
        document.getElementById('treatOwnerName').value = registration.owner_name;
        document.getElementById('treatPetName').value = registration.pet_name;
        
        const appointments = await createApiCall('GET', `/appointments?registration_id=${regId}`);
        if (appointments && appointments.length > 0) {
            const latestApt = appointments[appointments.length - 1];
            document.getElementById('treatVet').value = latestApt.veterinarian;
        } else {
            document.getElementById('treatVet').value = 'Not assigned';
        }
        
        currentPatientRegistrationId = regId;
        
        feedback.textContent = '✅ Patient found!';
        feedback.style.color = 'green';
        medBtn.disabled = false;
        vacBtn.disabled = false;
        
        fetchMedicationsForPatient(regId);
        fetchVaccinationsForPatient(regId);
    } catch (error) {
        document.getElementById('treatOwnerName').value = '';
        document.getElementById('treatPetName').value = '';
        document.getElementById('treatVet').value = '';
        
        feedback.textContent = '❌ Patient not found';
        feedback.style.color = 'red';
        medBtn.disabled = true;
        vacBtn.disabled = true;
        
        currentPatientRegistrationId = null;
    }
}

function resetPatientContext() {
    document.getElementById('treatRegId').value = '';
    document.getElementById('treatOwnerName').value = '';
    document.getElementById('treatPetName').value = '';
    document.getElementById('treatVet').value = '';
    document.getElementById('treatmentFeedback').textContent = '';
    document.getElementById('medSubmitBtn').disabled = true;
    document.getElementById('vacSubmitBtn').disabled = true;
    document.getElementById('medicationsBody').innerHTML = '';
    document.getElementById('vaccinationsBody').innerHTML = '';
    currentPatientRegistrationId = null;
}

function checkClinicalSafetyRules() {
    const medDetails = document.getElementById('treatMeds').value.toLowerCase();
    const warningMsg = document.getElementById('safetyWarningMessage');
    const submitBtn = document.getElementById('medSubmitBtn');
    
    if (!medDetails.trim()) {
        submitBtn.disabled = true;
        warningMsg.textContent = '';
        return;
    }
    
    const highRiskKeywords = ['overdose', 'poison', 'toxic', 'critical'];
    const hasHighRisk = highRiskKeywords.some(keyword => medDetails.includes(keyword));
    
    if (hasHighRisk) {
        warningMsg.textContent = '⚠️ WARNING: High-risk medication detected. Verify veterinarian approval.';
        warningMsg.style.color = 'red';
    } else {
        warningMsg.textContent = '';
    }
    
    submitBtn.disabled = false;
}


document.getElementById('medicationForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const medId = document.getElementById('medId').value;
    const regId = currentPatientRegistrationId;
    const ownerName = document.getElementById('treatOwnerName').value;
    const petName = document.getElementById('treatPetName').value;
    const vet = document.getElementById('treatVet').value;
    const medDetails = document.getElementById('treatMeds').value;
    const frequency = document.getElementById('treatFreq').value;
    const symptoms = document.getElementById('treatSymptoms').value;
    
    if (!regId) {
        showError('Please select a patient first');
        return;
    }
    if (!medDetails.trim()) {
        showError('Medication details are required');
        return;
    }
    if (!frequency) {
        showError('Frequency is required');
        return;
    }
    
    try {
        const data = {
            registration_id: parseInt(regId),
            owner_name: ownerName,
            pet_name: petName,
            veterinarian: vet,
            medication_details: medDetails,
            frequency: frequency,
            symptoms: symptoms
        };
        
        if (medId) {
            await createApiCall('PUT', `/medications/${medId}`, data);
            showSuccess('Medication updated successfully!');
            document.getElementById('medCancelBtn').style.display = 'none';
            document.getElementById('medSubmitBtn').textContent = 'Append Medicine Entry';
        } else {
            await createApiCall('POST', '/medications', data);
            showSuccess('Medication recorded successfully!');
        }
        
        clearMedicationFormOnly();
        fetchMedicationsForPatient(regId);
    } catch (error) {
        showError(`Failed to save medication: ${error.message}`);
    }
});

async function fetchMedicationsForPatient(regId) {
    try {
        const medications = await createApiCall('GET', `/medications?registration_id=${regId}`);
        const tbody = document.getElementById('medicationsBody');
        tbody.innerHTML = '';
        
        if (!medications || medications.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">No medications recorded</td></tr>';
            return;
        }
        
        medications.forEach(med => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${med.id}</td>
                <td>${med.pet_name}</td>
                <td>${med.medication_details}</td>
                <td>${med.frequency}</td>
                <td>
                    <button onclick="editMedication(${med.id})" style="margin-right: 5px;">✏️ Edit</button>
                    <button onclick="deleteMedication(${med.id})">🗑️ Delete</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        showError(`Failed to load medications: ${error.message}`);
    }
}

async function editMedication(id) {
    try {
        const medication = await createApiCall('GET', `/medications/${id}`);
        
        document.getElementById('medId').value = medication.id;
        document.getElementById('treatMeds').value = medication.medication_details;
        document.getElementById('treatFreq').value = medication.frequency;
        document.getElementById('treatSymptoms').value = medication.symptoms || '';
        
        document.getElementById('medCancelBtn').style.display = 'inline-block';
        document.getElementById('medSubmitBtn').textContent = 'Update Medicine Entry';
        
        document.getElementById('medicationForm').scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
        showError(`Failed to load medication: ${error.message}`);
    }
}

async function deleteMedication(id) {
    if (!confirm('Are you sure you want to delete this medication record?')) {
        return;
    }
    
    try {
        await createApiCall('DELETE', `/medications/${id}`);
        showSuccess('Medication deleted successfully!');
        if (currentPatientRegistrationId) {
            fetchMedicationsForPatient(currentPatientRegistrationId);
        }
    } catch (error) {
        showError(`Failed to delete medication: ${error.message}`);
    }
}

document.getElementById('vaccinationForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const vacId = document.getElementById('vacId').value;
    const regId = currentPatientRegistrationId;
    const ownerName = document.getElementById('treatOwnerName').value;
    const petName = document.getElementById('treatPetName').value;
    const vet = document.getElementById('treatVet').value;
    const vacDetails = document.getElementById('treatVacs').value;
    const vacDate = document.getElementById('treatVacDate').value;
    
    if (!regId) {
        showError('Please select a patient first');
        return;
    }
    if (!vacDetails.trim()) {
        showError('Vaccination details are required');
        return;
    }
    if (!vacDate) {
        showError('Vaccination date is required');
        return;
    }
    
    try {
        const data = {
            registration_id: parseInt(regId),
            owner_name: ownerName,
            pet_name: petName,
            veterinarian: vet,
            vaccination_details: vacDetails,
            vaccination_date: vacDate
        };
        
        if (vacId) {
            await createApiCall('PUT', `/vaccinations/${vacId}`, data);
            showSuccess('Vaccination updated successfully!');
            document.getElementById('vacCancelBtn').style.display = 'none';
            document.getElementById('vacSubmitBtn').textContent = 'Append Vaccination Entry';
        } else {
            await createApiCall('POST', '/vaccinations', data);
            showSuccess('Vaccination recorded successfully!');
        }
        
        clearVaccinationFormOnly();
        fetchVaccinationsForPatient(regId);
    } catch (error) {
        showError(`Failed to save vaccination: ${error.message}`);
    }
});

async function fetchVaccinationsForPatient(regId) {
    try {
        const vaccinations = await createApiCall('GET', `/vaccinations?registration_id=${regId}`);
        const tbody = document.getElementById('vaccinationsBody');
        tbody.innerHTML = '';
        
        if (!vaccinations || vaccinations.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align: center;">No vaccinations recorded</td></tr>';
            return;
        }
        
        vaccinations.forEach(vac => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${vac.id}</td>
                <td>${vac.pet_name}</td>
                <td>${vac.vaccination_details}</td>
                <td>
                    <button onclick="editVaccination(${vac.id})" style="margin-right: 5px;">✏️ Edit</button>
                    <button onclick="deleteVaccination(${vac.id})">🗑️ Delete</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        showError(`Failed to load vaccinations: ${error.message}`);
    }
}

async function editVaccination(id) {
    try {
        const vaccination = await createApiCall('GET', `/vaccinations/${id}`);
        
        document.getElementById('vacId').value = vaccination.id;
        document.getElementById('treatVacs').value = vaccination.vaccination_details;
        document.getElementById('treatVacDate').value = vaccination.vaccination_date;
        
        document.getElementById('vacCancelBtn').style.display = 'inline-block';
        document.getElementById('vacSubmitBtn').textContent = 'Update Vaccination Entry';
        
        document.getElementById('vaccinationForm').scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
        showError(`Failed to load vaccination: ${error.message}`);
    }
}

async function deleteVaccination(id) {
    if (!confirm('Are you sure you want to delete this vaccination record?')) {
        return;
    }
    
    try {
        await createApiCall('DELETE', `/vaccinations/${id}`);
        showSuccess('Vaccination deleted successfully!');
        if (currentPatientRegistrationId) {
            fetchVaccinationsForPatient(currentPatientRegistrationId);
        }
    } catch (error) {
        showError(`Failed to delete vaccination: ${error.message}`);
    }
}

// CLINICAL REPORTING
function evaluateHealthStatus(medications, vaccinations) {
    if (!medications || medications.length === 0) {
        if (!vaccinations || vaccinations.length === 0) {
            return {
                status: '🟢 Healthy',
                recommendation: 'Schedule routine check-up',
                color: 'green'
            };
        }
        return {
            status: '🟢 Healthy',
            recommendation: 'Vaccinations up to date',
            color: 'green'
        };
    }
    
    const urgentKeywords = ['fever', 'poison', 'severe', 'emergency', 'critical'];
    for (let med of medications) {
        if (med.symptoms) {
            const symptomsLower = med.symptoms.toLowerCase();
            if (urgentKeywords.some(kw => symptomsLower.includes(kw))) {
                return {
                    status: '🔴 Needs Attention',
                    recommendation: 'Immediate veterinary consultation recommended',
                    color: 'red'
                };
            }
        }
    }
    
    return {
        status: '🟡 In Treatment',
        recommendation: 'Continue current medication regimen',
        color: 'orange'
    };
}

async function showMedicalCardReport(regId) {
    try {
        const history = await createApiCall('GET', `/treatments/history?registration_id=${regId}`);
        
        const reg = history.registration;
        const medications = history.medications || [];
        const vaccinations = history.vaccinations || [];
        
        const healthStatus = evaluateHealthStatus(medications, vaccinations);
        
        document.getElementById('reportMetaText').textContent = 
            `${reg.pet_name} (${reg.pet_type}, Age: ${reg.pet_age}) - Owner: ${reg.owner_name}`;
        
        document.getElementById('reportStatusBadge').textContent = healthStatus.status;
        document.getElementById('reportStatusBadge').style.color = healthStatus.color;
        
        document.getElementById('reportRecommendationText').textContent = healthStatus.recommendation;
        
        const historyBody = document.getElementById('historyBody');
        historyBody.innerHTML = '';
        
        if (history.appointments && history.appointments.length > 0) {
            history.appointments.forEach(apt => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${apt.id}</td>
                    <td>Appointment</td>
                    <td>${apt.veterinarian}</td>
                    <td>${apt.appointment_date} ${apt.appointment_time}: ${apt.reason}</td>
                    <td>-</td>
                `;
                historyBody.appendChild(row);
            });
        }
        
        medications.forEach(med => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${med.id}</td>
                <td>Medication</td>
                <td>${med.veterinarian}</td>
                <td>${med.medication_details} (${med.frequency})</td>
                <td>${med.symptoms || '-'}</td>
            `;
            historyBody.appendChild(row);
        });
        
        vaccinations.forEach(vac => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${vac.id}</td>
                <td>Vaccination</td>
                <td>${vac.veterinarian}</td>
                <td>${vac.vaccination_details} (${vac.vaccination_date})</td>
                <td>-</td>
            `;
            historyBody.appendChild(row);
        });
        
        document.getElementById('petHistorySection').style.display = 'block';
        document.getElementById('petHistorySection').scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
        showError(`Failed to load medical card: ${error.message}`);
    }
}

// FORM CLEARING FUNCTIONS
function clearRegistrationForm() {
    document.getElementById('registrationForm').reset();
    document.getElementById('regId').value = '';
    document.getElementById('regCancelBtn').style.display = 'none';
    document.getElementById('regSubmitBtn').textContent = 'Register Client';
    editingRegistrationId = null;
}

function clearAppointmentForm() {
    document.getElementById('appointmentForm').reset();
    document.getElementById('appId').value = '';
    document.getElementById('appCancelBtn').style.display = 'none';
    document.getElementById('appSubmitBtn').textContent = 'Save Appointment';
    document.getElementById('validationFeedback').textContent = '';
    editingAppointmentId = null;
}

function clearMedicationFormOnly() {
    document.getElementById('medicationForm').reset();
    document.getElementById('medId').value = '';
    document.getElementById('medCancelBtn').style.display = 'none';
    document.getElementById('medSubmitBtn').textContent = 'Append Medicine Entry';
    document.getElementById('safetyWarningMessage').textContent = '';
    editingMedicationId = null;
}

function clearVaccinationFormOnly() {
    document.getElementById('vaccinationForm').reset();
    document.getElementById('vacId').value = '';
    document.getElementById('vacCancelBtn').style.display = 'none';
    document.getElementById('vacSubmitBtn').textContent = 'Append Vaccination Entry';
    editingVaccinationId = null;
}

function populateVeterinarianDropdown() {
    const vetSelect = document.getElementById('appVet');
    const vets = [
        'Dr. Sarah Jenkins',
        'Dr. Alex Carter',
        'Dr. Emily Ross'
    ];
    
    vets.forEach(vet => {
        const option = document.createElement('option');
        option.value = vet;
        option.textContent = vet;
        vetSelect.appendChild(option);
    });
}