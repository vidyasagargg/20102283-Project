
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