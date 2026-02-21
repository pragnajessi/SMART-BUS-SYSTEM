/**
 * GPS Tracking Application
 * Real-time location tracking, voice announcements, and bus monitoring
 */

class GPSTracker {
    constructor() {
        this.map = null;
        this.userMarker = null;
        this.nextStopMarker = null;
        this.busMarkers = {};
        this.trackingLine = [];
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
        this.init();
    }

    /**
     * Initialize the GPS Tracker
     */
    init() {
        console.log('🗺️ Initializing GPS Tracker...');
        this.initializeMap();
        this.loadUserInfo();
        console.log('✅ GPS Tracker initialized');
    }

    /**
     * Initialize the Leaflet Map
     */
    initializeMap() {
        try {
            // Create map centered on India (default)
            this.map = L.map('map').setView([28.6139, 77.2090], 13);

            // Add OpenStreetMap tiles
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenStreetMap contributors',
                maxZoom: 19,
            }).addTo(this.map);

            console.log('✅ Map initialized successfully');
        } catch (error) {
            console.error('❌ Error initializing map:', error);
            this.showError('Failed to initialize map');
        }
    }

    /**
     * Load user information
     */
    loadUserInfo() {
        try {
            const userData = JSON.parse(localStorage.getItem('userInfo') || '{}');
            if (userData.busId) {
                document.getElementById('busId').textContent = userData.busId;
                document.getElementById('busRoute').textContent = userData.route || '--';
                document.getElementById('busDriver').textContent = userData.driverName || '--';
                document.getElementById('busInfoCard').style.display = 'block';
            }
        } catch (error) {
            console.error('❌ Error loading user info:', error);
        }
    }

    /**
     * Start location tracking
     */
    startTracking() {
        if (!navigator.geolocation) {
            this.showError('❌ Geolocation not supported by your browser');
            return;
        }

        try {
            console.log('🗺️ Starting location tracking...');

            this.tracking.watchId = navigator.geolocation.watchPosition(
                (position) => this.handleLocationUpdate(position),
                (error) => this.handleLocationError(error),
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 0
                }
            );

            this.tracking.isActive = true;
            this.updateUI();
            this.showSuccess('✅ Tracking started');
        } catch (error) {
            console.error('❌ Error starting tracking:', error);
            this.showError('Failed to start tracking');
        }
    }

    /**
     * Handle location update
     */
    handleLocationUpdate(position) {
        const { latitude, longitude, accuracy } = position.coords;
        
        this.tracking.currentLocation = {
            latitude,
            longitude,
            accuracy,
            timestamp: new Date()
        };

        console.log(`📍 Location: ${latitude.toFixed(4)}, ${longitude.toFixed(4)}`);

        // Update UI
        this.updateLocationDisplay();
        this.updateMap();
        this.fetchNextStop(latitude, longitude);
    }

    /**
     * Handle location error
     */
    handleLocationError(error) {
        let message = 'Unknown error';
        switch (error.code) {
            case error.PERMISSION_DENIED:
                message = 'Permission denied. Please enable location access.';
                break;
            case error.POSITION_UNAVAILABLE:
                message = 'Location unavailable.';
                break;
            case error.TIMEOUT:
                message = 'Location request timeout.';
                break;
        }
        console.error('❌ Location error:', message);
        this.showError('📍 ' + message);
    }

    /**
     * Update location display in sidebar
     */
    updateLocationDisplay() {
        const loc = this.tracking.currentLocation;
        if (!loc) return;

        document.getElementById('currentLat').textContent = loc.latitude.toFixed(6);
        document.getElementById('currentLng').textContent = loc.longitude.toFixed(6);
        document.getElementById('currentAccuracy').textContent = Math.round(loc.accuracy) + ' m';
        document.getElementById('locationTime').textContent = loc.timestamp.toLocaleTimeString();
        document.getElementById('currentLocationCard').style.display = 'block';

        // Update signal quality
        const quality = loc.accuracy < 20 ? 'Excellent' : 
                       loc.accuracy < 50 ? 'Good' : 
                       loc.accuracy < 100 ? 'Fair' : 'Poor';
        document.getElementById('signalQuality').textContent = quality;
    }

    /**
     * Update map with current location
     */
    updateMap() {
        const loc = this.tracking.currentLocation;
        if (!loc) return;

        const latlng = [loc.latitude, loc.longitude];

        // Remove old marker
        if (this.userMarker) {
            this.map.removeLayer(this.userMarker);
        }

        // Add new marker with custom styling
        this.userMarker = L.circleMarker(latlng, {
            radius: 10,
            fillColor: '#667eea',
            color: '#667eea',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        })
        .bindPopup('📍 Your Location')
        .addTo(this.map);

        // Center map on user
        this.map.setView(latlng, this.map.getZoom());

        // Add to tracking line (every 5th update to avoid clutter)
        if (this.trackingLine.length === 0 || 
            this.getDistance(this.trackingLine[this.trackingLine.length - 1], latlng) > 0.01) {
            this.trackingLine.push(latlng);
            
            if (this.trackingLine.length > 1) {
                L.polyline(this.trackingLine, {
                    color: '#667eea',
                    weight: 2,
                    opacity: 0.5,
                    dashArray: '5, 5'
                }).addTo(this.map);
            }
        }
    }

    /**
     * Calculate distance between two coordinates
     */
    getDistance(latlng1, latlng2) {
        return Math.sqrt(Math.pow(latlng2[0] - latlng1[0], 2) + 
                        Math.pow(latlng2[1] - latlng1[1], 2));
    }

    /**
     * Fetch next stop
     */
    async fetchNextStop(latitude, longitude) {
        try {
            if (typeof busService === 'undefined') {
                console.warn('⚠️ busService not available');
                return;
            }

            const response = await busService.getNextStop(latitude, longitude);
            
            if (response && response.nextStop) {
                this.tracking.nextStop = response.nextStop;
                this.updateNextStopDisplay();
                this.updateNextStopMarker();

                // Auto-play voice if enabled
                if (this.voiceSettings.enabled) {
                    this.playVoiceAnnouncement(response.nextStop);
                }
            }
        } catch (error) {
            console.error('❌ Error fetching next stop:', error);
        }
    }

    /**
     * Update next stop display in sidebar
     */
    updateNextStopDisplay() {
        const stop = this.tracking.nextStop;
        if (!stop) return;

        document.getElementById('nextStopName').textContent = stop.name || '--';
        document.getElementById('nextStopDistance').textContent = 
            (stop.distance?.toFixed(2) || '--') + ' km';
        document.getElementById('nextStopTime').textContent = 
            (stop.estimatedTime || '--') + ' min';
        document.getElementById('nextStopCard').style.display = 'block';
    }

    /**
     * Update next stop marker on map
     */
    updateNextStopMarker() {
        const stop = this.tracking.nextStop;
        if (!stop || !stop.latitude || !stop.longitude) return;

        // Remove old marker
        if (this.nextStopMarker) {
            this.map.removeLayer(this.nextStopMarker);
        }

        // Add new marker (red)
        this.nextStopMarker = L.circleMarker([stop.latitude, stop.longitude], {
            radius: 8,
            fillColor: '#ff6b6b',
            color: '#ff5252',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        })
        .bindPopup(`<b>${stop.name}</b><br>📍 ${stop.distance?.toFixed(2) || 0} km away`)
        .addTo(this.map);
    }

    /**
     * Stop tracking
     */
    stopTracking() {
        if (this.tracking.watchId !== null) {
            navigator.geolocation.clearWatch(this.tracking.watchId);
            this.tracking.watchId = null;
        }

        this.tracking.isActive = false;
        this.stopVoiceAnnouncements();
        this.updateUI();
        this.showSuccess('⏹️ Tracking stopped');
        
        console.log('⏹️ Tracking stopped');
    }

    /**
     * Toggle voice announcements
     */
    toggleVoiceAnnouncements() {
        if (!this.tracking.isActive) {
            this.showError('❌ Please start tracking first');
            return;
        }

        if (this.voiceSettings.enabled) {
            this.stopVoiceAnnouncements();
        } else {
            this.enableVoiceAnnouncements();
        }
    }

    /**
     * Enable voice announcements
     */
    enableVoiceAnnouncements() {
        this.voiceSettings.enabled = true;
        
        if (this.tracking.nextStop) {
            this.playVoiceAnnouncement(this.tracking.nextStop);
        }

        this.updateUI();
        this.showSuccess('🔊 Voice announcements enabled');
    }

    /**
     * Stop voice announcements
     */
    stopVoiceAnnouncements() {
        window.speechSynthesis.cancel();
        this.voiceSettings.enabled = false;
        this.updateUI();
    }

    /**
     * Play voice announcement
     */
    playVoiceAnnouncement(stop) {
        if (!stop) return;

        try {
            const text = `Next stop: ${stop.name}. Distance: ${stop.distance?.toFixed(2) || 0} kilometers`;
            const utterance = new SpeechSynthesisUtterance(text);
            
            utterance.rate = this.voiceSettings.rate;
            utterance.pitch = this.voiceSettings.pitch;
            utterance.volume = this.voiceSettings.volume;
            
            utterance.onstart = () => console.log('🔊 Speaking:', text);
            utterance.onend = () => console.log('✅ Speech ended');
            utterance.onerror = (event) => console.error('❌ Speech error:', event.error);
            
            window.speechSynthesis.speak(utterance);
        } catch (error) {
            console.error('❌ Error playing voice:', error);
        }
    }

    /**
     * Update UI elements
     */
    updateUI() {
        const startBtn = document.getElementById('startTrackingBtn');
        const stopBtn = document.getElementById('stopTrackingBtn');
        const voiceBtn = document.getElementById('voiceAnnouncementBtn');
        const trackingIndicator = document.getElementById('trackingIndicator');
        const voiceIndicator = document.getElementById('voiceIndicator');

        if (this.tracking.isActive) {
            startBtn.style.display = 'none';
            stopBtn.style.display = 'flex';
            voiceBtn.disabled = false;
            trackingIndicator.className = 'status-indicator active';
            document.getElementById('trackingStatus').textContent = 'Active';
        } else {
            startBtn.style.display = 'flex';
            stopBtn.style.display = 'none';
            voiceBtn.disabled = true;
            trackingIndicator.className = 'status-indicator inactive';
            document.getElementById('trackingStatus').textContent = 'Inactive';
        }

        if (this.voiceSettings.enabled) {
            voiceBtn.classList.add('active');
            voiceIndicator.className = 'status-indicator active';
            document.getElementById('voiceStatus').textContent = 'On';
        } else {
            voiceBtn.classList.remove('active');
            voiceIndicator.className = 'status-indicator inactive';
            document.getElementById('voiceStatus').textContent = 'Off';
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        const errorDiv = document.getElementById('errorMessage');
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    }

    /**
     * Show success message
     */
    showSuccess(message) {
        const successDiv = document.getElementById('successMessage');
        successDiv.textContent = message;
        successDiv.style.display = 'block';
        setTimeout(() => {
            successDiv.style.display = 'none';
        }, 3000);
    }

    /**
     * Center map on current location
     */
    centerMap() {
        if (this.tracking.currentLocation) {
            const loc = this.tracking.currentLocation;
            this.map.setView([loc.latitude, loc.longitude], this.map.getZoom());
        } else {
            this.showError('No location available');
        }
    }

    /**
     * Zoom in
     */
    zoomIn() {
        this.map.zoomIn();
    }

    /**
     * Zoom out
     */
    zoomOut() {
        this.map.zoomOut();
    }

    /**
     * Close bus popup
     */
    closeBusPopup() {
        document.getElementById('busPopup').classList.add('hidden');
    }

    /**
     * Search buses
     */
    searchBuses() {
        const searchTerm = document.getElementById('searchBus').value.toLowerCase();
        const busItems = document.querySelectorAll('.bus-item');
        
        busItems.forEach(item => {
            if (item.textContent.toLowerCase().includes(searchTerm)) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    }

    /**
     * Toggle tracking (for button)
     */
    toggleTracking() {
        if (this.tracking.isActive) {
            this.stopTracking();
        } else {
            this.startTracking();
        }
    }
}

// Global tracker instance
let tracker = null;

// Initialize when page loads
window.addEventListener('load', () => {
    tracker = new GPSTracker();
});

// Global function wrappers for HTML onclick handlers
function startTracking() {
    if (tracker) tracker.startTracking();
}

function stopTracking() {
    if (tracker) tracker.stopTracking();
}

function toggleVoiceAnnouncements() {
    if (tracker) tracker.toggleVoiceAnnouncements();
}

function centerMap() {
    if (tracker) tracker.centerMap();
}

function zoomIn() {
    if (tracker) tracker.zoomIn();
}

function zoomOut() {
    if (tracker) tracker.zoomOut();
}

function toggleTracking() {
    if (tracker) tracker.toggleTracking();
}

function closeBusPopup() {
    if (tracker) tracker.closeBusPopup();
}

function searchBuses() {
    if (tracker) tracker.searchBuses();
}
