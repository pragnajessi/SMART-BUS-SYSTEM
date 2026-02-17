/**
 * API Service Layer
 * Handles all HTTP requests to backend
 * Provides clean methods for frontend to call
 */

class APIService {
    constructor(config = API_CONFIG) {
        this.baseURL = config.BASE_URL;
        this.timeout = config.TIMEOUT;
        this.endpoints = config.ENDPOINTS;
        this.authToken = localStorage.getItem('authToken') || null;
        this.userId = localStorage.getItem('userId') || null;
    }

    /**
     * Generic HTTP request method
     */
    async request(method, endpoint, data = null, headers = {}) {
        try {
            const url = `${this.baseURL}${endpoint}`;
            
            const options = {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    ...headers
                }
            };

            // Add auth token if available
            if (this.authToken) {
                options.headers['Authorization'] = `Bearer ${this.authToken}`;
            }

            // Add request body for POST/PUT
            if (data) {
                options.body = JSON.stringify(data);
            }

            const response = await Promise.race([
                fetch(url, options),
                new Promise((_, reject) =>
                    setTimeout(() => reject(new Error('Request timeout')), this.timeout)
                )
            ]);

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || error.message || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API Error [${method} ${endpoint}]:`, error.message);
            throw error;
        }
    }

    /**
     * GET request
     */
    async get(endpoint, params = null) {
        let url = endpoint;
        if (params) {
            const queryString = new URLSearchParams(params).toString();
            url += `?${queryString}`;
        }
        return this.request('GET', url);
    }

    /**
     * POST request
     */
    async post(endpoint, data) {
        return this.request('POST', endpoint, data);
    }

    /**
     * PUT request
     */
    async put(endpoint, data) {
        return this.request('PUT', endpoint, data);
    }

    /**
     * Helper: Replace URL parameters
     */
    getEndpoint(template, params = {}) {
        let url = template;
        for (const [key, value] of Object.entries(params)) {
            url = url.replace(`:${key}`, value);
        }
        return url;
    }

    // ==================== AUTHENTICATION ====================

    async register(userData) {
        return this.post(this.endpoints.AUTH.REGISTER, userData);
    }

    async login(email, password) {
        return this.post(this.endpoints.AUTH.LOGIN, { email, password });
    }

    async logout() {
        localStorage.removeItem('authToken');
        localStorage.removeItem('userId');
        localStorage.removeItem('userName');
        this.authToken = null;
        this.userId = null;
    }

    // ==================== BUSES ====================

    async getAllBuses(page = 1, perPage = 10) {
        return this.get(this.endpoints.BUSES.GET_ALL, { page, per_page: perPage });
    }

    async createBus(busData) {
        return this.post(this.endpoints.BUSES.CREATE, busData);
    }

    async getBusSeats(busId) {
        const endpoint = this.getEndpoint(this.endpoints.BUSES.GET_SEATS, { busId });
        return this.get(endpoint);
    }

    async updateBusLocation(busId, latitude, longitude) {
        const endpoint = this.getEndpoint(this.endpoints.BUSES.UPDATE_LOCATION, { busId });
        return this.post(endpoint, { latitude, longitude });
    }

    async getBusAnnouncements(busId) {
        const endpoint = this.getEndpoint(this.endpoints.BUSES.GET_ANNOUNCEMENTS, { busId });
        return this.get(endpoint);
    }

    // ==================== SEATS ====================

    async reserveSeat(seatId, userId) {
        const endpoint = this.getEndpoint(this.endpoints.SEATS.RESERVE, { seatId });
        return this.post(endpoint, { user_id: userId });
    }

    async cancelSeatReservation(seatId) {
        const endpoint = this.getEndpoint(this.endpoints.SEATS.CANCEL, { seatId });
        return this.post(endpoint, {});
    }

    // ==================== BOOKINGS ====================

    async createBooking(bookingData) {
        return this.post(this.endpoints.BOOKINGS.CREATE, bookingData);
    }

    async getBooking(bookingId) {
        const endpoint = this.getEndpoint(this.endpoints.BOOKINGS.GET, { bookingId });
        return this.get(endpoint);
    }

    async confirmBooking(bookingId) {
        const endpoint = this.getEndpoint(this.endpoints.BOOKINGS.CONFIRM, { bookingId });
        return this.post(endpoint, {});
    }

    async cancelBooking(bookingId, reason = null) {
        const endpoint = this.getEndpoint(this.endpoints.BOOKINGS.CANCEL, { bookingId });
        return this.post(endpoint, { reason });
    }

    // ==================== PAYMENTS ====================

    async createPayment(paymentData) {
        return this.post(this.endpoints.PAYMENTS.CREATE, paymentData);
    }

    // ==================== WALLET ====================

    async getWalletBalance(userId) {
        const endpoint = this.getEndpoint(this.endpoints.WALLET.GET_BALANCE, { userId });
        return this.get(endpoint);
    }

    async addWalletMoney(userId, amount, description = null) {
        const endpoint = this.getEndpoint(this.endpoints.WALLET.ADD_MONEY, { userId });
        return this.post(endpoint, { amount, description });
    }

    async getWalletTransactions(userId, limit = 20) {
        const endpoint = this.getEndpoint(this.endpoints.WALLET.GET_TRANSACTIONS, { userId });
        return this.get(endpoint, { limit });
    }

    // ==================== GPS ====================

    async logGPS(busId, latitude, longitude, speed = 0, heading = 0) {
        const endpoint = this.getEndpoint(this.endpoints.GPS.LOG, { busId });
        return this.post(endpoint, { latitude, longitude, speed, heading });
    }

    async getLatestGPS(busId) {
        const endpoint = this.getEndpoint(this.endpoints.GPS.GET_LATEST, { busId });
        return this.get(endpoint);
    }

    async getGPSHistory(busId, hours = 24) {
        const endpoint = this.getEndpoint(this.endpoints.GPS.GET_HISTORY, { busId });
        return this.get(endpoint, { hours });
    }

    async getAllActiveGPS() {
        return this.get(this.endpoints.GPS.GET_ALL_ACTIVE);
    }

    // ==================== STATISTICS ====================

    async getDashboardStats() {
        return this.get(this.endpoints.STATISTICS.DASHBOARD);
    }

    async getRevenueStats(date = null) {
        return this.get(this.endpoints.STATISTICS.REVENUE, { date });
    }

    async getRouteStats() {
        return this.get(this.endpoints.STATISTICS.ROUTES);
    }

    // ==================== EMERGENCIES ====================

    async reportEmergency(emergencyData) {
        return this.post(this.endpoints.EMERGENCIES.REPORT, emergencyData);
    }

    async getActiveEmergencies() {
        return this.get(this.endpoints.EMERGENCIES.GET_ACTIVE);
    }

    async resolveEmergency(emergencyId) {
        const endpoint = this.getEndpoint(this.endpoints.EMERGENCIES.RESOLVE, { emergencyId });
        return this.post(endpoint, {});
    }

    // ==================== LOST & FOUND ====================

    async reportLostItem(itemData) {
        return this.post(this.endpoints.LOST_FOUND.REPORT, itemData);
    }

    async getLostItems(status = 'lost') {
        return this.get(this.endpoints.LOST_FOUND.GET_ALL, { status });
    }

    async markItemFound(itemId, workerId, location) {
        const endpoint = this.getEndpoint(this.endpoints.LOST_FOUND.MARK_FOUND, { itemId });
        return this.post(endpoint, { worker_id: workerId, location_found: location });
    }

    async claimLostItem(itemId) {
        const endpoint = this.getEndpoint(this.endpoints.LOST_FOUND.CLAIM, { itemId });
        return this.post(endpoint, {});
    }

    // ==================== ALERTS ====================

    async createWakeupAlert(alertData) {
        return this.post(this.endpoints.ALERTS.CREATE, alertData);
    }

    async getUserAlerts(userId) {
        const endpoint = this.getEndpoint(this.endpoints.ALERTS.GET_USER, { userId });
        return this.get(endpoint);
    }
}

// Create global instance
const apiService = new APIService();