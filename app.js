
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


// ============================================================================
// TAB SWITCHING
// ============================================================================

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