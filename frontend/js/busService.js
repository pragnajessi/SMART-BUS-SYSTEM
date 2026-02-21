/**
 * Bus Service
 * Handles all bus-related API calls
 */

class BusService {
  /**
   * Get next stop based on current location
   */
  async getNextStop(latitude, longitude, busId = null) {
    try {
      console.log('🛑 Fetching next stop...');
      const response = await apiService.post('/next-stop', {
        latitude,
        longitude,
        busId,
      });
      return response;
    } catch (error) {
      console.error('❌ Error fetching next stop:', error);
      throw error;
    }
  }

  /**
   * Get bus route information
   */
  async getBusRoute(busId) {
    try {
      console.log(`🗺️ Fetching route for bus ${busId}...`);
      const response = await apiService.get(`/bus/${busId}/route`);
      return response;
    } catch (error) {
      console.error('❌ Error fetching bus route:', error);
      throw error;
    }
  }

  /**
   * Update bus location
   */
  async updateBusLocation(busId, latitude, longitude) {
    try {
      console.log(`📍 Updating location for bus ${busId}...`);
      const response = await apiService.put(`/bus/${busId}/location`, {
        latitude,
        longitude,
        timestamp: new Date().toISOString(),
      });
      return response;
    } catch (error) {
      console.error('❌ Error updating bus location:', error);
      throw error;
    }
  }

  /**
   * Get all stops for a route
   */
  async getRouteStops(routeId) {
    try {
      console.log(`🛑 Fetching stops for route ${routeId}...`);
      const response = await apiService.get(`/route/${routeId}/stops`);
      return response;
    } catch (error) {
      console.error('❌ Error fetching route stops:', error);
      throw error;
    }
  }

  /**
   * Get bus details
   */
  async getBusDetails(busId) {
    try {
      console.log(`🚌 Fetching details for bus ${busId}...`);
      const response = await apiService.get(`/bus/${busId}`);
      return response;
    } catch (error) {
      console.error('❌ Error fetching bus details:', error);
      throw error;
    }
  }

  /**
   * Get all active buses
   */
  async getActiveBuses() {
    try {
      console.log('🚌 Fetching active buses...');
      const response = await apiService.get('/buses/active');
      return response;
    } catch (error) {
      console.error('❌ Error fetching active buses:', error);
      throw error;
    }
  }

  /**
   * Get bus tracking data
   */
  async getBusTracking(busId) {
    try {
      console.log(`📍 Fetching tracking data for bus ${busId}...`);
      const response = await apiService.get(`/bus/${busId}/tracking`);
      return response;
    } catch (error) {
      console.error('❌ Error fetching bus tracking:', error);
      throw error;
    }
  }

  /**
   * Start tracking bus
   */
  async startTracking(busId) {
    try {
      console.log(`▶️ Starting tracking for bus ${busId}...`);
      const response = await apiService.post(`/bus/${busId}/tracking/start`, {
        timestamp: new Date().toISOString(),
      });
      return response;
    } catch (error) {
      console.error('❌ Error starting tracking:', error);
      throw error;
    }
  }

  /**
   * Stop tracking bus
   */
  async stopTracking(busId) {
    try {
      console.log(`⏹️ Stopping tracking for bus ${busId}...`);
      const response = await apiService.post(`/bus/${busId}/tracking/stop`, {
        timestamp: new Date().toISOString(),
      });
      return response;
    } catch (error) {
      console.error('❌ Error stopping tracking:', error);
      throw error;
    }
  }
}

// Create and export singleton instance
const busService = new BusService();
