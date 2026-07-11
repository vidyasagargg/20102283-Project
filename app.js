
const API_BASE_URL = "http://localhost:5000/api";

// Global state
let currentTab = 'registrations';
let editingRegistrationId = null;
let editingAppointmentId = null;
let editingMedicationId = null;
let editingVaccinationId = null;
let currentPatientRegistrationId = null;

// ============================================================================
// API HELPER FUNCTIONS
// ============================================================================

/**
 * Make API call with proper error handling
 * @param {string} method - HTTP method (GET, POST, PUT, DELETE)
 * @param {string} endpoint - API endpoint path (e.g., '/registrations')
 * @param {object} data - Request body data (for POST/PUT)
 * @returns {Promise} API response as JSON
 */
async function createApiCall(method, endpoint, data = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            }
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

/**
 * Display error message to user
 * @param {string} message - Error message
 * @param {string} elementId - Element to display error in
 */
function showError(message, elementId = null) {
    console.error(message);
    if (elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = `❌ ${message}`;
            element.style.color = 'red';
            setTimeout(() => {
                element.textContent = '';
            }, 3000);
        }
    } else {
        alert(`Error: ${message}`);
    }
}

/**
 * Display success message to user
 * @param {string} message - Success message
 * @param {string} elementId - Element to display success in
 */
function showSuccess(message, elementId = null) {
    console.log(message);
    if (elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = `✅ ${message}`;
            element.style.color = 'green';
            setTimeout(() => {
                element.textContent = '';
            }, 3000);
        }
    }
}


// TAB SWITCHING
/**
 * Switch between tabs
 * @param {string} tabName - Tab identifier: 'registrations', 'appointments', 'treatments'
 */
function switchTab(tabName) {
    // Hide all tabs
    document.getElementById('sectionRegistrations').style.display = 'none';
    document.getElementById('sectionAppointments').style.display = 'none';
    document.getElementById('sectionTreatments').style.display = 'none';
    
    // Show selected tab
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
    
    // Update button styles
    document.getElementById('tabBtnRegistrations').style.fontWeight = tabName === 'registrations' ? 'bold' : 'normal';
    document.getElementById('tabBtnAppointments').style.fontWeight = tabName === 'appointments' ? 'bold' : 'normal';
    document.getElementById('tabBtnTreatments').style.fontWeight = tabName === 'treatments' ? 'bold' : 'normal';
}

// Initialize on page load
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
    
    // Validation
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
        
        let response;
        if (regId) {
            // Update existing
            response = await createApiCall('PUT', `/registrations/${regId}`, data);
            showSuccess('Registration updated successfully!');
            editingRegistrationId = null;
            document.getElementById('regCancelBtn').style.display = 'none';
            document.getElementById('regSubmitBtn').textContent = 'Register Client';
        } else {
            // Create new
            response = await createApiCall('POST', '/registrations', data);
            showSuccess('Registration created successfully!');
        }
        
        clearRegistrationForm();
        fetchRegistrations();
    } catch (error) {
        showError(`Failed to save registration: ${error.message}`);
    }
});

/**
 * Fetch all registrations from API and display in table
 */
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

/**
 * Load registration for editing
 * @param {number} id - Registration ID
 */
async function editRegistration(id) {
    try {
        const registration = await createApiCall('GET', `/registrations/${id}`);
        
        document.getElementById('regId').value = registration.id;
        document.getElementById('regOwnerName').value = registration.owner_name;
        document.getElementById('regOwnerPhone').value = registration.owner_phone;
        document.getElementById('regPetName').value = registration.pet_name;
        document.getElementById('regPetType').value = registration.pet_type;
        document.getElementById('regPetAge').value = registration.pet_age;
        
        // Show cancel button, change submit text
        document.getElementById('regCancelBtn').style.display = 'inline-block';
        document.getElementById('regSubmitBtn').textContent = 'Update Registration';
        
        editingRegistrationId = id;
        
        // Scroll to form
        document.getElementById('registrationForm').scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
        showError(`Failed to load registration: ${error.message}`);
    }
}

/**
 * Delete a registration with confirmation
 * @param {number} id - Registration ID
 */
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

/**
 * Verify registration exists and auto-populate appointment form
 */
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
    
    // Validation
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
        
        let response;
        if (appId) {
            response = await createApiCall('PUT', `/appointments/${appId}`, data);
            showSuccess('Appointment updated successfully!', 'appointmentSuccessMessage');
            document.getElementById('appCancelBtn').style.display = 'none';
            document.getElementById('appSubmitBtn').textContent = 'Save Appointment';
        } else {
            response = await createApiCall('POST', '/appointments', data);
            showSuccess('Appointment created successfully!', 'appointmentSuccessMessage');
        }
        
        clearAppointmentForm();
        fetchAppointments();
    } catch (error) {
        showError(`Failed to save appointment: ${error.message}`);
    }
});

/**
 * Fetch all appointments from API and display in table
 */
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

/**
 * Toggle appointments log display
 */
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

/**
 * Load appointment for editing
 * @param {number} id - Appointment ID
 */
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

/**
 * Delete an appointment with confirmation
 * @param {number} id - Appointment ID
 */
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