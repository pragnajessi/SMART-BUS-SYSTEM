const API_BASE_URL = 'http://localhost:5000/api';

// ========== AUTHENTICATION API ==========
async function registerUser(userData) {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        });
        return await response.json();
    } catch (error) {
        console.error('Registration error:', error);
        throw error;
    }
}

async function loginUser(email, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        return await response.json();
    } catch (error) {
        console.error('Login error:', error);
        throw error;
    }
}

// ========== BUS API ==========
async function fetchBuses() {
    try {
        const response = await fetch(`${API_BASE_URL}/buses`);
        return await response.json();
    } catch (error) {
        console.error('Fetch buses error:', error);
        throw error;
    }
}

async function createBus(busData) {
    try {
        const response = await fetch(`${API_BASE_URL}/buses`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(busData)
        });
        return await response.json();
    } catch (error) {
        console.error('Create bus error:', error);
        throw error;
    }
}

async function updateBusLocation(busId, latitude, longitude) {
    try {
        const response = await fetch(`${API_BASE_URL}/buses/${busId}/update-location`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ latitude, longitude })
        });
        return await response.json();
    } catch (error) {
        console.error('Update location error:', error);
        throw error;
    }
}

// ========== SEAT API ==========
async function fetchSeats(busId) {
    try {
        const response = await fetch(`${API_BASE_URL}/buses/${busId}/seats`);
        return await response.json();
    } catch (error) {
        console.error('Fetch seats error:', error);
        throw error;
    }
}

async function reserveSeat(seatId, userId) {
    try {
        const response = await fetch(`${API_BASE_URL}/seats/${seatId}/reserve`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId })
        });
        return await response.json();
    } catch (error) {
        console.error('Reserve seat error:', error);
        throw error;
    }
}

async function cancelReservation(seatId) {
    try {
        const response = await fetch(`${API_BASE_URL}/seats/${seatId}/cancel`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        return await response.json();
    } catch (error) {
        console.error('Cancel reservation error:', error);
        throw error;
    }
}

// ========== ANNOUNCEMENTS API ==========
async function fetchAnnouncements(busId) {
    try {
        const response = await fetch(`${API_BASE_URL}/buses/${busId}/announcements`);
        return await response.json();
    } catch (error) {
        console.error('Fetch announcements error:', error);
        throw error;
    }
}

async function createAnnouncement(busId, announcementData) {
    try {
        const response = await fetch(`${API_BASE_URL}/buses/${busId}/announcements`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(announcementData)
        });
        return await response.json();
    } catch (error) {
        console.error('Create announcement error:', error);
        throw error;
    }
}

// ========== WAKE-UP ALERTS API ==========
async function createWakeupAlert(alertData) {
    try {
        const response = await fetch(`${API_BASE_URL}/wakeup-alerts`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(alertData)
        });
        return await response.json();
    } catch (error) {
        console.error('Create alert error:', error);
        throw error;
    }
}

async function fetchUserWakeupAlerts(userId) {
    try {
        const response = await fetch(`${API_BASE_URL}/users/${userId}/wakeup-alerts`);
        return await response.json();
    } catch (error) {
        console.error('Fetch alerts error:', error);
        throw error;
    }
}

// ========== EMERGENCY API ==========
async function reportEmergency(emergencyData) {
    try {
        const response = await fetch(`${API_BASE_URL}/emergencies`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(emergencyData)
        });
        return await response.json();
    } catch (error) {
        console.error('Report emergency error:', error);
        throw error;
    }
}

async function fetchEmergencies() {
    try {
        const response = await fetch(`${API_BASE_URL}/emergencies`);
        return await response.json();
    } catch (error) {
        console.error('Fetch emergencies error:', error);
        throw error;
    }
}

async function resolveEmergency(emergencyId) {
    try {
        const response = await fetch(`${API_BASE_URL}/emergencies/${emergencyId}/resolve`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        return await response.json();
    } catch (error) {
        console.error('Resolve emergency error:', error);
        throw error;
    }
}

// ========== LOST & FOUND API ==========
async function reportLostItem(itemData) {
    try {
        const response = await fetch(`${API_BASE_URL}/lost-items`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(itemData)
        });
        return await response.json();
    } catch (error) {
        console.error('Report lost item error:', error);
        throw error;
    }
}

async function fetchLostItems(status = 'lost') {
    try {
        const response = await fetch(`${API_BASE_URL}/lost-items?status=${status}`);
        return await response.json();
    } catch (error) {
        console.error('Fetch lost items error:', error);
        throw error;
    }
}

async function markItemFound(itemId, workerId, location) {
    try {
        const response = await fetch(`${API_BASE_URL}/lost-items/${itemId}/mark-found`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ worker_id: workerId, location_found: location })
        });
        return await response.json();
    } catch (error) {
        console.error('Mark item found error:', error);
        throw error;
    }
}

async function claimLostItem(itemId) {
    try {
        const response = await fetch(`${API_BASE_URL}/lost-items/${itemId}/claim`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        return await response.json();
    } catch (error) {
        console.error('Claim item error:', error);
        throw error;
    }
}