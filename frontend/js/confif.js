/**
 * API Configuration
 * Centralized API endpoint configuration
 */

const API_CONFIG = {
    // Base URL - Change this for production
    BASE_URL: 'http://localhost:5000/api',
    
    // Timeouts
    TIMEOUT: 5000,
    
    // API Endpoints
    ENDPOINTS: {
        // Authentication
        AUTH: {
            REGISTER: '/auth/register',
            LOGIN: '/auth/login'
        },
        
        // Buses
        BUSES: {
            GET_ALL: '/buses',
            CREATE: '/buses',
            GET_SEATS: '/buses/:busId/seats',
            UPDATE_LOCATION: '/buses/:busId/update-location',
            GET_ANNOUNCEMENTS: '/buses/:busId/announcements'
        },
        
        // Seats
        SEATS: {
            RESERVE: '/seats/:seatId/reserve',
            CANCEL: '/seats/:seatId/cancel'
        },
        
        // Bookings
        BOOKINGS: {
            CREATE: '/bookings',
            GET: '/bookings/:bookingId',
            CONFIRM: '/bookings/:bookingId/confirm',
            CANCEL: '/bookings/:bookingId/cancel'
        },
        
        // Payments
        PAYMENTS: {
            CREATE: '/payments'
        },
        
        // Wallet
        WALLET: {
            GET_BALANCE: '/wallet/:userId',
            ADD_MONEY: '/wallet/:userId/add-money',
            GET_TRANSACTIONS: '/wallet/:userId/transactions'
        },
        
        // GPS
        GPS: {
            LOG: '/gps/buses/:busId/log',
            GET_LATEST: '/gps/buses/:busId/latest',
            GET_HISTORY: '/gps/buses/:busId/history',
            GET_ALL_ACTIVE: '/gps/buses/active/locations'
        },
        
        // Statistics
        STATISTICS: {
            DASHBOARD: '/statistics/dashboard',
            REVENUE: '/statistics/revenue',
            ROUTES: '/statistics/routes'
        },
        
        // Emergencies
        EMERGENCIES: {
            REPORT: '/emergencies',
            GET_ACTIVE: '/emergencies',
            RESOLVE: '/emergencies/:emergencyId/resolve'
        },
        
        // Lost & Found
        LOST_FOUND: {
            REPORT: '/lost-items',
            GET_ALL: '/lost-items',
            MARK_FOUND: '/lost-items/:itemId/mark-found',
            CLAIM: '/lost-items/:itemId/claim'
        },
        
        // Alerts
        ALERTS: {
            CREATE: '/wakeup-alerts',
            GET_USER: '/users/:userId/wakeup-alerts'
        }
    }
};

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = API_CONFIG;
}
/**
 * Configuration File
 */

const config = {
  // API Configuration
  apiUrl: 'http://localhost:5000/api',
  // apiUrl: 'https://your-production-api.com/api', // For production
  
  // Application Settings
  appName: 'Smart Bus System',
  appVersion: '1.0.0',
  
  // Feature Flags
  features: {
    locationTracking: true,
    voiceAnnouncements: true,
    paymentIntegration: true,
    adminDashboard: true,
  },

  // Timeout settings
  requestTimeout: 30000, // 30 seconds

  // Logging
  debug: true, // Set to false in production
};

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
  module.exports = config;
}
