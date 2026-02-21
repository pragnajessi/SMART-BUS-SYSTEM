/**
 * Services Index
 * Centralized export of all services
 */

// All services are defined globally after loading:
// - apiService (from api-service.js)
// - busService (from busService.js)
// - dashboardService (from dashboardService.js)

// This file serves as documentation for available services
const services = {
  api: apiService,
  bus: busService,
  dashboard: dashboardService,
};

console.log('✅ All services loaded:', Object.keys(services));
