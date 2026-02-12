const GPS_API_BASE_URL = 'http://localhost:5000/api/gps';

let map;
let markers = {};
let trackingEnabled = true;
let selectedBusId = null;
let infoWindows = {};
let polylines = {};

// Initialize map
function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 12,
        center: { lat: 28.6139, lng: 77.2090 }  // Default: Delhi
    });

    loadActiveBuses();
    startRealTimeTracking();
}

// Load and display all active buses
async function loadActiveBuses() {
    try {
        const buses = await fetch(`${GPS_API_BASE_URL}/buses/active/locations`).then(r => r.json());
        
        const busesList = document.getElementById('busesList');
        busesList.innerHTML = '';

        buses.forEach(bus => {
            // Add to map
            addBusMarker(bus);

            // Add to sidebar list
            const busItem = document.createElement('div');
            busItem.className = 'bus-item';
            busItem.innerHTML = `
                <h4>${bus.bus_number}</h4>
                <p>${bus.route}</p>
                <small>Speed: ${bus.speed} km/h</small>
            `;
            busItem.onclick = () => selectBus(bus.id, bus);
            busesList.appendChild(busItem);
        });
    } catch (error) {
        console.error('Error loading buses:', error);
    }
}

// Add bus marker to map
function addBusMarker(bus) {
    const position = { lat: bus.latitude, lng: bus.longitude };

    if (markers[bus.bus_id]) {
        // Update existing marker
        markers[bus.bus_id].setPosition(position);
    } else {
        // Create new marker
        const marker = new google.maps.Marker({
            position: position,
            map: map,
            title: bus.bus_number,
            icon: getBusIcon(bus.heading)
        });

        marker.addListener('click', () => {
            showBusPopup(bus.bus_id, bus);
        });

        markers[bus.bus_id] = marker;
    }
}

// Get rotated bus icon based on heading
function getBusIcon(heading) {
    return {
        path: 'M0,-28 C-7.73,-28 -14,-21.73 -14,-14 L-14,21 C-14,23.66 -11.66,26 -9,26 L9,26 C11.66,26 14,23.66 14,21 L14,-14 C14,-21.73 7.73,-28 0,-28 Z',
        fillColor: '#FF6B6B',
        fillOpacity: 0.8,
        strokeColor: '#fff',
        strokeWeight: 2,
        rotation: heading || 0,
        scale: 1
    };
}

// Select bus from sidebar
async function selectBus(busId, busData) {
    selectedBusId = busId;
    
    // Center map on bus
    map.setCenter({ lat: busData.latitude, lng: busData.longitude });
    map.setZoom(15);

    // Show bus details
    const detailsContent = document.getElementById('busDetailsContent');
    detailsContent.innerHTML = `
        <p><strong>Bus #:</strong> ${busData.bus_number}</p>
        <p><strong>Driver:</strong> ${busData.driver_name}</p>
        <p><strong>Route:</strong> ${busData.route}</p>
        <p><strong>Speed:</strong> ${busData.speed} km/h</p>
        <p><strong>Latitude:</strong> ${busData.latitude.toFixed(6)}</p>
        <p><strong>Longitude:</strong> ${busData.longitude.toFixed(6)}</p>
        <button onclick="viewGPSHistory(${busId})" style="width: 100%; padding: 0.5rem; margin-top: 1rem;">View GPS History</button>
    `;
    document.getElementById('busInfo').style.display = 'block';

    // Load stops
    loadRoutStops(busId);
}

// Load and display route stops
async function loadRoutStops(busId) {
    try {
        const response = await fetch(`${GPS_API_BASE_URL}/buses/${busId}/route-stops`);
        const stops = await response.json();

        stops.forEach(stop => {
            addStopMarker(stop, busId);
        });

        // Draw route line
        drawRouteLine(stops);
    } catch (error) {
        console.error('Error loading stops:', error);
    }
}

// Add stop marker
function addStopMarker(stop, busId) {
    const position = { lat: stop.latitude, lng: stop.longitude };

    const marker = new google.maps.Marker({
        position: position,
        map: map,
        title: stop.stop_name,
        icon: getStopIcon(stop.is_completed)
    });

    const infoWindow = new google.maps.InfoWindow({
        content: `
            <div style="padding: 10px;">
                <h3>${stop.stop_name}</h3>
                <p>Order: ${stop.stop_order}</p>
                ${stop.estimated_arrival ? `<p>ETA: ${new Date(stop.estimated_arrival).toLocaleTimeString()}</p>` : ''}
                <p>Status: ${stop.is_completed ? '✅ Completed' : '⏳ Pending'}</p>
            </div>
        `
    });

    marker.addListener('click', () => {
        // Close other info windows
        Object.values(infoWindows).forEach(w => w.close());
        infoWindow.open(map, marker);
    });

    infoWindows[stop.id] = infoWindow;
}

// Get stop icon
function getStopIcon(isCompleted) {
    return {
        path: google.maps.SymbolPath.CIRCLE,
        fillColor: isCompleted ? '#95E1D3' : '#4ECDC4',
        fillOpacity: 0.8,
        strokeColor: '#fff',
        strokeWeight: 2,
        scale: 8
    };
}

// Draw route line
function drawRouteLine(stops) {
    if (!stops || stops.length === 0) return;

    const routePath = stops.map(stop => ({
        lat: stop.latitude,
        lng: stop.longitude
    }));

    const polyline = new google.maps.Polyline({
        path: routePath,
        geodesic: true,
        strokeColor: '#4ECDC4',
        strokeOpacity: 0.7,
        strokeWeight: 3,
        map: map
    });

    polylines[selectedBusId] = polyline;
}

// Show bus popup
function showBusPopup(busId, busData) {
    document.getElementById('popupBusNumber').textContent = busData.bus_number;
    document.getElementById('popupBusInfo').innerHTML = `
        <p><strong>Driver:</strong> ${busData.driver_name}</p>
        <p><strong>Speed:</strong> ${busData.speed} km/h</p>
        <p><strong>Route:</strong> ${busData.route}</p>
    `;
    document.getElementById('busPopup').classList.remove('hidden');
}

function closeBusPopup() {
    document.getElementById('busPopup').classList.add('hidden');
}

// View GPS history
async function viewGPSHistory(busId) {
    try {
        const response = await fetch(`${GPS_API_BASE_URL}/buses/${busId}/history?limit=50`);
        const history = await response.json();

        // Draw history path
        const historyPath = history.map(point => ({
            lat: point.latitude,
            lng: point.longitude
        }));

        const polyline = new google.maps.Polyline({
            path: historyPath,
            geodesic: true,
            strokeColor: '#FFE66D',
            strokeOpacity: 0.5,
            strokeWeight: 2,
            map: map
        });

        alert('GPS history displayed on map (yellow line)');
    } catch (error) {
        alert('Failed to load GPS history');
    }
}

// Real-time tracking
function startRealTimeTracking() {
    setInterval(() => {
        if (trackingEnabled) {
            loadActiveBuses();
        }
    }, 10000);  // Update every 10 seconds
}

// Control functions
function toggleTracking() {
    trackingEnabled = !trackingEnabled;
    alert(trackingEnabled ? 'Tracking enabled' : 'Tracking disabled');
}

function centerMap() {
    if (selectedBusId && markers[selectedBusId]) {
        map.setCenter(markers[selectedBusId].getPosition());
    }
}

function zoomIn() {
    map.setZoom(map.getZoom() + 1);
}

function zoomOut() {
    map.setZoom(map.getZoom() - 1);
}

function searchBuses() {
    const searchTerm = document.getElementById('searchBus').value.toLowerCase();
    const busItems = document.querySelectorAll('.bus-item');

    busItems.forEach(item => {
        const busNumber = item.querySelector('h4').textContent.toLowerCase();
        item.style.display = busNumber.includes(searchTerm) ? 'block' : 'none';
    });
}

// Initialize on load
window.addEventListener('load', initMap);