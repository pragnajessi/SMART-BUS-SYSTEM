/**
 * Dashboard Service
 * Handles all dashboard statistics API calls
 */

class DashboardService {
  /**
   * Get dashboard statistics
   */
  async getDashboardStats() {
    try {
      console.log('📊 Fetching dashboard statistics...');
      const response = await apiService.get('/dashboard/stats');
      return response;
    } catch (error) {
      console.error('❌ Error fetching dashboard stats:', error);
      throw error;
    }
  }

  /**
   * Get user statistics
   */
  async getUserStats() {
    try {
      console.log('👥 Fetching user statistics...');
      const response = await apiService.get('/dashboard/user-stats');
      return response;
    } catch (error) {
      console.error('❌ Error fetching user stats:', error);
      throw error;
    }
  }

  /**
   * Get booking statistics
   */
  async getBookingStats() {
    try {
      console.log('📦 Fetching booking statistics...');
      const response = await apiService.get('/dashboard/booking-stats');
      return response;
    } catch (error) {
      console.error('❌ Error fetching booking stats:', error);
      throw error;
    }
  }

  /**
   * Get payment statistics
   */
  async getPaymentStats() {
    try {
      console.log('💳 Fetching payment statistics...');
      const response = await apiService.get('/dashboard/payment-stats');
      return response;
    } catch (error) {
      console.error('❌ Error fetching payment stats:', error);
      throw error;
    }
  }

  /**
   * Get bus statistics
   */
  async getBusStats() {
    try {
      console.log('🚌 Fetching bus statistics...');
      const response = await apiService.get('/dashboard/bus-stats');
      return response;
    } catch (error) {
      console.error('❌ Error fetching bus stats:', error);
      throw error;
    }
  }

  /**
   * Get real-time dashboard data
   */
  async getRealtimeDashboardData() {
    try {
      console.log('⚡ Fetching real-time dashboard data...');
      const response = await apiService.get('/dashboard/realtime');
      return response;
    } catch (error) {
      console.error('❌ Error fetching realtime data:', error);
      throw error;
    }
  }

  /**
   * Get daily dashboard summary
   */
  async getDailySummary(date = null) {
    try {
      const dateStr = date ? `?date=${date}` : '';
      console.log('📅 Fetching daily summary...');
      const response = await apiService.get(`/dashboard/daily-summary${dateStr}`);
      return response;
    } catch (error) {
      console.error('❌ Error fetching daily summary:', error);
      throw error;
    }
  }
}

// Create and export singleton instance
const dashboardService = new DashboardService();
