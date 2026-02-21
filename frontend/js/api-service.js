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
     * Generic HTTP request method with timeout
     */
    async request(method, endpoint, data = null, headers = {}) {
        const url = `${this.baseURL}${endpoint}`;

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
                ...headers
            },
            signal: controller.signal
        };

        // Add auth token
        if (this.authToken) {
            options.headers['Authorization'] = `Bearer ${this.authToken}`;
        }

        // Add body
        if (data) {
            options.body = JSON.stringify(data);
        }

        try {
            console.log(`📡 API Request: ${method} ${url}`);

            const response = await fetch(url, options);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(
                    errorData.error ||
                    errorData.message ||
                    `HTTP ${response.status}`
                );
            }

            const result = await response.json();
            console.log(`✅ API Response: ${endpoint}`, result);
            return result;
        } catch (error) {
            if (error.name === 'AbortError') {
                throw new Error('Request timeout');
            }
            console.error(`❌ API Error [${method} ${endpoint}]:`, error.message);
            throw error;
        } finally {
            clearTimeout(timeoutId);
        }
    }

    // ==================== BASIC METHODS ====================

    async get(endpoint, params = null) {
        let url = endpoint;
        if (params) {
            const queryString = new URLSearchParams(params).toString();
            url += `?${queryString}`;
        }
        return this.request('GET', url);
    }

    async post(endpoint, data) {
        return this.request('POST', endpoint, data);
    }

    async put(endpoint, data) {
        return this.request('PUT', endpoint, data);
    }

    async delete(endpoint) {
        return this.request('DELETE', endpoint);
    }

    async patch(endpoint, data) {
        return this.request('PATCH', endpoint, data);
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

    // ==================== AUTH ====================

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
        return this.get(this.endpoints.BUSES.GET_ALL, {
            page,
            per_page: perPage
        });
    }

    async createBus(busData) {
        return this.post(this.endpoints.BUSES.CREATE, busData);
    }

    async getBusSeats(busId) {
        const endpoint = this.getEndpoint(
            this.endpoints.BUSES.GET_SEATS,
            { busId }
        );
        return this.get(endpoint);
    }

    async updateBusLocation(busId, latitude, longitude) {
        const endpoint = this.getEndpoint(
            this.endpoints.BUSES.UPDATE_LOCATION,
            { busId }
        );
        return this.post(endpoint, { latitude, longitude });
    }

    async getBusAnnouncements(busId) {
        const endpoint = this.getEndpoint(
            this.endpoints.BUSES.GET_ANNOUNCEMENTS,
            { busId }
        );
        return this.get(endpoint);
    }

    // ==================== BOOKINGS ====================

    async createBooking(bookingData) {
        return this.post(this.endpoints.BOOKINGS.CREATE, bookingData);
    }

    async getBooking(bookingId) {
        const endpoint = this.getEndpoint(
            this.endpoints.BOOKINGS.GET,
            { bookingId }
        );
        return this.get(endpoint);
    }

    async confirmBooking(bookingId) {
        const endpoint = this.getEndpoint(
            this.endpoints.BOOKINGS.CONFIRM,
            { bookingId }
        );
        return this.post(endpoint, {});
    }

    async cancelBooking(bookingId, reason = null) {
        const endpoint = this.getEndpoint(
            this.endpoints.BOOKINGS.CANCEL,
            { bookingId }
        );
        return this.post(endpoint, { reason });
    }

    // ==================== STATISTICS ====================

    async getDashboardStats() {
        return this.get(this.endpoints.STATISTICS.DASHBOARD);
    }
}

// ✅ Single global instance
const apiService = new APIService();
