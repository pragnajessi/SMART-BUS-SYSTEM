/**
 * Authentication Manager
 * Handles user login, registration, and session management
 */

class AuthManager {
    constructor() {
        this.currentUser = this.loadUser();
        this.isAuthenticated = !!this.currentUser;
    }

    /**
     * Register new user
     */
    async register(userData) {
        try {
            console.log('📝 Registering user:', userData.email);
            
            const response = await apiService.register(userData);
            
            console.log('✅ Registration successful');
            return response;
        } catch (error) {
            console.error('❌ Registration failed:', error.message);
            throw error;
        }
    }

    /**
     * Login user
     */
    async login(email, password) {
        try {
            console.log('🔐 Logging in user:', email);
            
            const response = await apiService.login(email, password);
            
            // Store user data
            this.currentUser = {
                id: response.user_id,
                name: response.name,
                email: response.email,
                accountType: response.account_type
            };
            
            localStorage.setItem('userId', response.user_id);
            localStorage.setItem('userName', response.name);
            localStorage.setItem('userEmail', response.email);
            localStorage.setItem('accountType', response.account_type);
            localStorage.setItem('authToken', `user_${response.user_id}`);
            
            this.isAuthenticated = true;
            apiService.userId = response.user_id;
            apiService.authToken = `user_${response.user_id}`;
            
            console.log('✅ Login successful:', response.name);
            return response;
        } catch (error) {
            console.error('❌ Login failed:', error.message);
            throw error;
        }
    }

    /**
     * Logout user
     */
    logout() {
        try {
            console.log('👋 Logging out user');
            
            apiService.logout();
            this.currentUser = null;
            this.isAuthenticated = false;
            
            console.log('✅ Logout successful');
        } catch (error) {
            console.error('❌ Logout failed:', error.message);
        }
    }

    /**
     * Load user from local storage
     */
    loadUser() {
        try {
            const userId = localStorage.getItem('userId');
            const userName = localStorage.getItem('userName');
            const userEmail = localStorage.getItem('userEmail');
            const accountType = localStorage.getItem('accountType');

            if (userId) {
                return {
                    id: userId,
                    name: userName,
                    email: userEmail,
                    accountType: accountType
                };
            }
            return null;
        } catch (error) {
            console.error('Error loading user:', error);
            return null;
        }
    }

    /**
     * Get current user
     */
    getCurrentUser() {
        return this.currentUser;
    }

    /**
     * Check if user is authenticated
     */
    isLoggedIn() {
        return this.isAuthenticated && !!this.currentUser;
    }

    /**
     * Get user by role
     */
    isPassenger() {
        return this.currentUser?.accountType === 'passenger';
    }

    isDriver() {
        return this.currentUser?.accountType === 'driver';
    }

    isWorker() {
        return this.currentUser?.accountType === 'worker';
    }

    isAdmin() {
        return this.currentUser?.accountType === 'admin';
    }
}

// Create global instance
const authManager = new AuthManager();