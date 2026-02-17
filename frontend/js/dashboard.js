/**
 * Dashboard Manager
 * Handles dashboard statistics and displays
 */

class DashboardManager {
    constructor() {
        this.stats = {};
    }

    /**
     * Load dashboard statistics
     */
    async loadStats() {
        try {
            console.log('📊 Loading dashboard statistics...');
            
            const response = await apiService.getDashboardStats();
            this.stats = response;
            
            console.log('✅ Dashboard stats loaded');
            return this.stats;
        } catch (error) {
            console.error('❌ Failed to load stats:', error.message);
            throw error;
        }
    }

    /**
     * Get specific stat
     */
    getStat(key) {
        return this.stats[key] || 0;
    }

    /**
     * Get all stats
     */
    getAllStats() {
        return this.stats;
    }

    /**
     * Format stats for display
     */
    getFormattedStats() {
        return {
            totalUsers: this.stats.total_users || 0,
            totalBuses: this.stats.total_buses || 0,
            activeBuses: this.stats.active_buses || 0,
            totalBookings: this.stats.total_bookings || 0,
            confirmedBookings: this.stats.confirmed_bookings || 0,
            totalRevenue: `₹${(this.stats.total_revenue || 0).toFixed(2)}`,
            passengers: this.stats.user_stats?.passengers || 0,
            completedPayments: this.stats.payment_stats?.completed || 0
        };
    }
}

// Create global instance
const dashboardManager = new DashboardManager();