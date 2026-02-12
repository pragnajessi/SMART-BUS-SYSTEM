const ADMIN_API_BASE_URL = 'http://localhost:5000/api/admin';
const GPS_API_BASE_URL = 'http://localhost:5000/api/gps';
const PAYMENT_API_BASE_URL = 'http://localhost:5000/api/payments';

// ========== ADMIN API CALLS ==========

async function fetchAdminDashboard() {
    try {
        const response = await fetch(`${ADMIN_API_BASE_URL}/dashboard`, {
            headers: {
                'X-User-Id': localStorage.getItem('admin_id') || '1'
            }
        });
        return await response.json();
    } catch (error) {
        console.error('Fetch dashboard error:', error);
        throw error;
    }
}

async function fetchAllBuses(page = 1, perPage = 10) {
    try {
        const response = await fetch(
            `${ADMIN_API_BASE_URL}/buses/manage?page=${page}&per_page=${perPage}`,
            {
                headers: {
                    'X-User-Id': localStorage.getItem('admin_id') || '1'
                }
            }
        );
        return await response.json();
    } catch (error) {
        console.error('Fetch buses error:', error);
        throw error;
    }
}

async function updateBusStatus(busId, status) {
    try {
        const response = await fetch(`${ADMIN_API_BASE_URL}/buses/${busId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-User-Id': localStorage.getItem('admin_id') || '1'
            },
            body: JSON.stringify({ status })
        });
        return await response.json();
    } catch (error) {
        console.error('Update bus status error:', error);
        throw error;
    }
}

async function fetchAllUsers(page = 1, perPage = 10) {
    try {
        const response = await fetch(
            `${ADMIN_API_BASE_URL}/users/manage?page=${page}&per_page=${perPage}`,
            {
                headers: {
                    'X-User-Id': localStorage.getItem('admin_id') || '1'
                }
            }
        );
        return await response.json();
    } catch (error) {
        console.error('Fetch users error:', error);
        throw error;
    }
}

async function fetchAllPayments(page = 1, perPage = 10, status = null) {
    try {
        let url = `${ADMIN_API_BASE_URL}/payments/manage?page=${page}&per_page=${perPage}`;
        if (status) url += `&status=${status}`;
        
        const response = await fetch(url, {
            headers: {
                'X-User-Id': localStorage.getItem('admin_id') || '1'
            }
        });
        return await response.json();
    } catch (error) {
        console.error('Fetch payments error:', error);
        throw error;
    }
}

async function fetchRevenueAnalytics(days = 30) {
    try {
        const response = await fetch(`${ADMIN_API_BASE_URL}/analytics/revenue?days=${days}`, {
            headers: {
                'X-User-Id': localStorage.getItem('admin_id') || '1'
            }
        });
        return await response.json();
    } catch (error) {
        console.error('Fetch revenue analytics error:', error);
        throw error;
    }
}

async function fetchBookingAnalytics(days = 30) {
    try {
        const response = await fetch(`${ADMIN_API_BASE_URL}/analytics/bookings?days=${days}`, {
            headers: {
                'X-User-Id': localStorage.getItem('admin_id') || '1'
            }
        });
        return await response.json();
    } catch (error) {
        console.error('Fetch booking analytics error:', error);
        throw error;
    }
}

async function generateDailyReport() {
    try {
        const response = await fetch(`${ADMIN_API_BASE_URL}/reports/daily`, {
            method: 'POST',
            headers: {
                'X-User-Id': localStorage.getItem('admin_id') || '1'
            }
        });
        return await response.json();
    } catch (error) {
        console.error('Generate report error:', error);
        throw error;
    }
}

async function fetchAdminLogs(page = 1, perPage = 20) {
    try {
        const response = await fetch(
            `${ADMIN_API_BASE_URL}/logs?page=${page}&per_page=${perPage}`,
            {
                headers: {
                    'X-User-Id': localStorage.getItem('admin_id') || '1'
                }
            }
        );
        return await response.json();
    } catch (error) {
        console.error('Fetch logs error:', error);
        throw error;
    }
}

// ========== GPS API CALLS ==========

async function fetchAllActiveBuses() {
    try {
        const response = await fetch(`${GPS_API_BASE_URL}/buses/active/locations`);
        return await response.json();
    } catch (error) {
        console.error('Fetch active buses error:', error);
        throw error;
    }
}

async function fetchGPSHistory(busId, limit = 100) {
    try {
        const response = await fetch(`${GPS_API_BASE_URL}/buses/${busId}/history?limit=${limit}`);
        return await response.json();
    } catch (error) {
        console.error('Fetch GPS history error:', error);
        throw error;
    }
}

// ========== PAYMENT API CALLS ==========

async function fetchPaymentWithWallet(userId) {
    try {
        const response = await fetch(`${PAYMENT_API_BASE_URL}/wallet/balance/${userId}`);
        return await response.json();
    } catch (error) {
        console.error('Fetch wallet error:', error);
        throw error;
    }
}