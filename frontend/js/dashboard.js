/**
 * Dashboard Manager
 * Handles dashboard statistics, location tracking, and voice announcements
 */

class DashboardManager {
    constructor() {
        this.stats = {};
        this.tracking = {
            isActive: false,
            currentLocation: null,
            nextStop: null,
            watchId: null
        };
        this.voiceSettings = {
            enabled: false,
            rate: 0.9,
            pitch: 1,
            volume: 1
        };
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

    // ============================================
    // LOCATION TRACKING METHODS
    // ============================================

    startTracking(onLocationUpdate, onError) {
        if (!navigator.geolocation) {
            const error = 'Geolocation is not supported by your browser';
            onError?.(error);
            return false;
        }

        try {
            console.log('🗺️ Starting location tracking...');

            this.tracking.watchId = navigator.geolocation.watchPosition(
                (position) => {
                    const { latitude, longitude, accuracy } = position.coords;

                    this.tracking.currentLocation = {
                        latitude,
                        longitude,
                        accuracy,
                        timestamp: new Date()
                    };

                    console.log(`📍 Location updated: ${latitude}, ${longitude}`);
                    onLocationUpdate?.(this.tracking.currentLocation);

                    // Fetch next stop
                    this.fetchNextStop(latitude, longitude);
                },
                (error) => {
                    console.error('❌ Geolocation error:', error.message);
                    onError?.(error.message);
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 0
                }
            );

            this.tracking.isActive = true;
            return true;
        } catch (error) {
            console.error('❌ Error starting tracking:', error);
            onError?.(error.message);
            return false;
        }
    }

    stopTracking() {
        if (this.tracking.watchId !== null) {
            navigator.geolocation.clearWatch(this.tracking.watchId);
            this.tracking.watchId = null;
        }

        this.tracking.isActive = false;
        this.stopVoiceAnnouncements();

        console.log('⏹️ Location tracking stopped');
        return true;
    }

    getCurrentLocation() {
        return this.tracking.currentLocation;
    }

    isTracking() {
        return this.tracking.isActive;
    }

    // ============================================
    // NEXT STOP METHODS
    // ============================================

    async fetchNextStop(latitude, longitude) {
        try {
            const busInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');

            const response = await fetch('/api/next-stop', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    latitude,
                    longitude,
                    busId: busInfo?.busId || null
                })
            });

            if (!response.ok) {
                throw new Error('Failed to fetch next stop');
            }

            const data = await response.json();
            this.tracking.nextStop = data.nextStop;

            console.log('🛑 Next stop updated:', data.nextStop?.name);

            if (this.voiceSettings.enabled) {
                this.playVoiceAnnouncement(data.nextStop);
            }

            return data.nextStop;
        } catch (error) {
            console.error('❌ Error fetching next stop:', error);
            throw error;
        }
    }

    getNextStop() {
        return this.tracking.nextStop;
    }

    // ============================================
    // VOICE ANNOUNCEMENT METHODS
    // ============================================

    enableVoiceAnnouncements() {
        if (!this.tracking.isActive) {
            console.warn('⚠️ Cannot enable voice announcements - tracking not active');
            return false;
        }

        this.voiceSettings.enabled = true;
        console.log('🔊 Voice announcements enabled');

        if (this.tracking.nextStop) {
            this.playVoiceAnnouncement(this.tracking.nextStop);
        }

        return true;
    }

    stopVoiceAnnouncements() {
        window.speechSynthesis.cancel();
        this.voiceSettings.enabled = false;
        console.log('🔇 Voice announcements disabled');
        return true;
    }

    toggleVoiceAnnouncements() {
        return this.voiceSettings.enabled
            ? this.stopVoiceAnnouncements()
            : this.enableVoiceAnnouncements();
    }

    playVoiceAnnouncement(stop) {
        if (!stop) {
            console.warn('⚠️ No stop information to announce');
            return false;
        }

        try {
            const text = `Next stop: ${stop.name}. Distance: ${Number(stop.distance || 0).toFixed(2)} kilometers`;
            const utterance = new SpeechSynthesisUtterance(text);

            utterance.rate = this.voiceSettings.rate;
            utterance.pitch = this.voiceSettings.pitch;
            utterance.volume = this.voiceSettings.volume;

            utterance.onstart = () => console.log('🔊 Speaking:', text);
            utterance.onend = () => console.log('✅ Speech ended');
            utterance.onerror = (event) => console.error('❌ Speech error:', event.error);

            window.speechSynthesis.speak(utterance);
            return true;
        } catch (error) {
            console.error('❌ Error playing voice announcement:', error);
            return false;
        }
    }

    setVoiceSettings(settings) {
        this.voiceSettings = {
            ...this.voiceSettings,
            ...settings
        };
        console.log('🔊 Voice settings updated:', this.voiceSettings);
    }

    getVoiceSettings() {
        return { ...this.voiceSettings };
    }

    // ============================================
    // UTILITY METHODS
    // ============================================

    getDashboardState() {
        return {
            stats: this.getFormattedStats(),
            tracking: {
                isActive: this.tracking.isActive,
                currentLocation: this.tracking.currentLocation,
                nextStop: this.tracking.nextStop
            },
            voice: {
                enabled: this.voiceSettings.enabled
            }
        };
    }

    reset() {
        this.stopTracking();
        this.tracking = {
            isActive: false,
            currentLocation: null,
            nextStop: null,
            watchId: null
        };
        console.log('🔄 Dashboard manager reset');
    }
}

// ✅ Create single global instance
const dashboardManager = new DashboardManager();
/**
 * Dashboard with Location Tracking & Voice Announcements
 */

class Dashboard {
  constructor() {
    this.stats = {};
    this.tracking = {
      isActive: false,
      currentLocation: null,
      nextStop: null,
      watchId: null
    };
    this.voiceSettings = {
      enabled: false,
      rate: 0.9,
      pitch: 1,
      volume: 1
    };
  }

  /**
   * Initialize dashboard
   */
  async init() {
    try {
      console.log('📊 Initializing dashboard...');
      await this.loadStats();
      this.setupEventListeners();
      console.log('✅ Dashboard initialized');
    } catch (error) {
      console.error('❌ Failed to initialize dashboard:', error);
    }
  }

  /**
   * Load dashboard statistics using service
   */
  async loadStats() {
    try {
      console.log('📊 Loading dashboard statistics...');
      const response = await dashboardService.getDashboardStats();
      this.stats = response;
      this.updateStatsDisplay();
      console.log('✅ Dashboard stats loaded');
      return this.stats;
    } catch (error) {
      console.error('❌ Failed to load stats:', error);
      throw error;
    }
  }

  /**
   * Update stats display on page
   */
  updateStatsDisplay() {
    const stats = this.getFormattedStats();
    
    // Update DOM elements
    if (document.getElementById('statTotalUsers')) {
      document.getElementById('statTotalUsers').textContent = stats.totalUsers;
    }
    if (document.getElementById('statTotalBuses')) {
      document.getElementById('statTotalBuses').textContent = stats.totalBuses;
    }
    if (document.getElementById('statActiveBuses')) {
      document.getElementById('statActiveBuses').textContent = stats.activeBuses;
    }
    if (document.getElementById('statTotalBookings')) {
      document.getElementById('statTotalBookings').textContent = stats.totalBookings;
    }
    if (document.getElementById('statTotalRevenue')) {
      document.getElementById('statTotalRevenue').textContent = stats.totalRevenue;
    }
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

  // ============================================
  // LOCATION TRACKING METHODS
  // ============================================

  /**
   * Start location tracking
   */
  startTracking(onLocationUpdate, onError) {
    if (!navigator.geolocation) {
      const error = '❌ Geolocation is not supported by your browser';
      console.error(error);
      onError?.(error);
      return false;
    }

    try {
      console.log('🗺️ Starting location tracking...');
      
      this.tracking.watchId = navigator.geolocation.watchPosition(
        (position) => {
          const { latitude, longitude, accuracy } = position.coords;
          this.tracking.currentLocation = { 
            latitude, 
            longitude, 
            accuracy,
            timestamp: new Date()
          };
          
          console.log(`📍 Location updated: ${latitude}, ${longitude}`);
          onLocationUpdate?.(this.tracking.currentLocation);
          
          // Fetch next stop using service
          this.fetchNextStop(latitude, longitude);
        },
        (error) => {
          console.error('❌ Geolocation error:', error.message);
          onError?.(error.message);
        },
        { 
          enableHighAccuracy: true, 
          timeout: 10000, 
          maximumAge: 0 
        }
      );

      this.tracking.isActive = true;
      return true;
    } catch (error) {
      console.error('❌ Error starting tracking:', error);
      onError?.(error.message);
      return false;
    }
  }

  /**
   * Stop location tracking
   */
  stopTracking() {
    if (this.tracking.watchId !== null) {
      navigator.geolocation.clearWatch(this.tracking.watchId);
      this.tracking.watchId = null;
    }
    
    this.tracking.isActive = false;
    this.stopVoiceAnnouncements();
    
    console.log('⏹️ Location tracking stopped');
    return true;
  }

  /**
   * Fetch next stop using service
   */
  async fetchNextStop(latitude, longitude) {
    try {
      const busInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
      
      const response = await busService.getNextStop(
        latitude, 
        longitude,
        busInfo?.busId || null
      );
      
      this.tracking.nextStop = response.nextStop;
      
      console.log('🛑 Next stop updated:', response.nextStop.name);
      this.updateNextStopDisplay();
      
      // Auto-play voice if enabled
      if (this.voiceSettings.enabled) {
        this.playVoiceAnnouncement(response.nextStop);
      }
      
      return response.nextStop;
    } catch (error) {
      console.error('❌ Error fetching next stop:', error);
      throw error;
    }
  }

  /**
   * Update next stop display
   */
  updateNextStopDisplay() {
    const stop = this.tracking.nextStop;
    if (!stop) return;

    if (document.getElementById('nextStopName')) {
      document.getElementById('nextStopName').textContent = stop.name;
    }
    if (document.getElementById('nextStopDistance')) {
      document.getElementById('nextStopDistance').textContent = 
        stop.distance?.toFixed(2) + ' km';
    }
    if (document.getElementById('nextStopTime') && stop.estimatedTime) {
      document.getElementById('nextStopTime').textContent = 
        stop.estimatedTime + ' min';
    }
  }

  /**
   * Update location display
   */
  updateLocationDisplay() {
    const loc = this.tracking.currentLocation;
    if (!loc) return;

    if (document.getElementById('currentLat')) {
      document.getElementById('currentLat').textContent = loc.latitude.toFixed(6);
    }
    if (document.getElementById('currentLng')) {
      document.getElementById('currentLng').textContent = loc.longitude.toFixed(6);
    }
    if (document.getElementById('currentAccuracy')) {
      document.getElementById('currentAccuracy').textContent = 
        loc.accuracy.toFixed(0) + 'm';
    }
  }

  // ============================================
  // VOICE ANNOUNCEMENT METHODS
  // ============================================

  /**
   * Enable voice announcements
   */
  enableVoiceAnnouncements() {
    if (!this.tracking.isActive) {
      console.warn('⚠️ Cannot enable voice announcements - tracking not active');
      return false;
    }

    this.voiceSettings.enabled = true;
    console.log('🔊 Voice announcements enabled');
    
    if (this.tracking.nextStop) {
      this.playVoiceAnnouncement(this.tracking.nextStop);
    }
    
    return true;
  }

  /**
   * Stop voice announcements
   */
  stopVoiceAnnouncements() {
    window.speechSynthesis.cancel();
    this.voiceSettings.enabled = false;
    console.log('🔇 Voice announcements disabled');
    return true;
  }

  /**
   * Toggle voice announcements
   */
  toggleVoiceAnnouncements() {
    if (this.voiceSettings.enabled) {
      return this.stopVoiceAnnouncements();
    } else {
      return this.enableVoiceAnnouncements();
    }
  }

  /**
   * Play voice announcement
   */
  playVoiceAnnouncement(stop) {
    if (!stop) {
      console.warn('⚠️ No stop information to announce');
      return false;
    }

    try {
      const text = `Next stop: ${stop.name}. Distance: ${stop.distance.toFixed(2)} kilometers`;
      const utterance = new SpeechSynthesisUtterance(text);
      
      utterance.rate = this.voiceSettings.rate;
      utterance.pitch = this.voiceSettings.pitch;
      utterance.volume = this.voiceSettings.volume;
      
      utterance.onstart = () => {
        console.log('🔊 Speaking:', text);
      };
      
      utterance.onend = () => {
        console.log('✅ Speech ended');
      };
      
      utterance.onerror = (event) => {
        console.error('❌ Speech error:', event.error);
      };
      
      window.speechSynthesis.speak(utterance);
      return true;
    } catch (error) {
      console.error('❌ Error playing voice announcement:', error);
      return false;
    }
  }

  /**
   * Setup event listeners for buttons
   */
  setupEventListeners() {
    const trackBtn = document.getElementById('trackingToggleBtn');
    const voiceBtn = document.getElementById('voiceToggleBtn');

    if (trackBtn) {
      trackBtn.addEventListener('click', () => {
        if (this.tracking.isActive) {
          this.stopTracking();
          trackBtn.textContent = '▶ Start Tracking';
          trackBtn.classList.remove('active');
        } else {
          this.startTracking(
            (location) => this.updateLocationDisplay(),
            (error) => alert('Location Error: ' + error)
          );
          trackBtn.textContent = '⏹ Stop Tracking';
          trackBtn.classList.add('active');
        }
      });
    }

    if (voiceBtn) {
      voiceBtn.addEventListener('click', () => {
        if (!this.tracking.isActive) {
          alert('Please start tracking first');
          return;
        }
        this.toggleVoiceAnnouncements();
        voiceBtn.classList.toggle('active');
      });
    }
  }

  /**
   * Get complete dashboard state
   */
  getDashboardState() {
    return {
      stats: this.getFormattedStats(),
      tracking: {
        isActive: this.tracking.isActive,
        currentLocation: this.tracking.currentLocation,
        nextStop: this.tracking.nextStop
      },
      voice: {
        enabled: this.voiceSettings.enabled
      }
    };
  }

  /**
   * Reset dashboard
   */
  reset() {
    this.stopTracking();
    this.tracking = {
      isActive: false,
      currentLocation: null,
      nextStop: null,
      watchId: null
    };
    console.log('🔄 Dashboard reset');
  }
}

// Create global instance
const dashboard = new Dashboard();
