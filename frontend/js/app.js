// ========== GLOBAL STATE ==========
let currentUser = null;
let currentBus = null;
let selectedSeat = null;

// ========== PAGE NAVIGATION ==========
function showPage(pageName) {
    if (!currentUser && pageName !== 'auth' && pageName !== 'home') {
        showPage('auth');
        return;
    }

    const pages = document.querySelectorAll('.page');
    pages.forEach(page => page.classList.add('hidden'));

    const targetPage = document.getElementById(pageName);
    if (targetPage) {
        targetPage.classList.remove('hidden');
        
        // Load data for specific pages
        if (pageName === 'buses') loadBuses();
        else if (pageName === 'alerts') loadAlerts();
        else if (pageName === 'lost-found') loadFoundItems();
    }
}

// ========== AUTHENTICATION ==========
function switchAuthTab(tab) {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const tabBtns = document.querySelectorAll('.tab-btn');

    if (tab === 'login') {
        loginForm.classList.remove('hidden');
        registerForm.classList.add('hidden');
        tabBtns[0].classList.add('active');
        tabBtns[1].classList.remove('active');
    } else {
        loginForm.classList.add('hidden');
        registerForm.classList.remove('hidden');
        tabBtns[0].classList.remove('active');
        tabBtns[1].classList.add('active');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Login Form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;

            try {
                const result = await loginUser(email, password);
                if (result.user_id) {
                    currentUser = result;
                    localStorage.setItem('user', JSON.stringify(result));
                    showPage('home');
                    clearLoginForm();
                } else {
                    showError('loginError', result.message || 'Login failed');
                }
            } catch (error) {
                showError('loginError', 'Login failed');
            }
        });
    }

    // Register Form
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const password = document.getElementById('registerPassword').value;
            const confirmPassword = document.getElementById('registerConfirmPassword').value;

            if (password !== confirmPassword) {
                showError('registerError', 'Passwords do not match');
                return;
            }

            const userData = {
                name: document.getElementById('registerName').value,
                email: document.getElementById('registerEmail').value,
                phone: document.getElementById('registerPhone').value,
                gender: document.getElementById('registerGender').value,
                password: password
            };

            try {
                const result = await registerUser(userData);
                if (result.user_id) {
                    currentUser = result;
                    localStorage.setItem('user', JSON.stringify(result));
                    showPage('home');
                    clearRegisterForm();
                } else {
                    showError('registerError', result.message || 'Registration failed');
                }
            } catch (error) {
                showError('registerError', 'Registration failed');
            }
        });
    }

    // Alert Form
    const alertForm = document.getElementById('alertForm');
    if (alertForm) {
        alertForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const alertData = {
                user_id: currentUser.user_id,
                bus_id: parseInt(document.getElementById('alertBusId').value),
                stop_name: document.getElementById('alertStopName').value,
                stop_lat: parseFloat(document.getElementById('alertStopLat').value),
                stop_lng: parseFloat(document.getElementById('alertStopLng').value),
                alert_before_time: parseInt(document.getElementById('alertBeforeTime').value)
            };

            try {
                const result = await createWakeupAlert(alertData);
                alert('Alert created successfully!');
                alertForm.reset();
                loadAlerts();
            } catch (error) {
                alert('Failed to create alert');
            }
        });
    }

    // Emergency Form
    const emergencyForm = document.getElementById('emergencyForm');
    if (emergencyForm) {
        emergencyForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            if (!currentBus) {
                alert('Please select a bus first');
                return;
            }

            const emergencyData = {
                bus_id: currentBus.id,
                user_id: currentUser.user_id,
                emergency_type: document.getElementById('emergencyType').value,
                latitude: currentBus.current_lat || 0,
                longitude: currentBus.current_lng || 0,
                description: document.getElementById('emergencyDescription').value
            };

            try {
                const result = await reportEmergency(emergencyData);
                alert('Emergency reported! Help is on the way.');
                emergencyForm.reset();
            } catch (error) {
                alert('Failed to report emergency');
            }
        });
    }

    // Report Lost Item Form
    const reportLostForm = document.getElementById('reportLostForm');
    if (reportLostForm) {
        reportLostForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const itemData = {
                item_name: document.getElementById('lostItemName').value,
                item_description: document.getElementById('lostItemDescription').value,
                user_id: currentUser.user_id
            };

            try {
                const result = await reportLostItem(itemData);
                alert('Lost item reported! Bus workers will be notified.');
                reportLostForm.reset();
            } catch (error) {
                alert('Failed to report lost item');
            }
        });
    }

    // Initialize user session
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
        currentUser = JSON.parse(savedUser);
        showPage('home');
    } else {
        showPage('auth');
    }
});

// ========== BUS MANAGEMENT ==========
async function loadBuses() {
    try {
        const buses = await fetchBuses();
        const container = document.getElementById('busesContainer');
        container.innerHTML = '';

        buses.forEach(bus => {
            const availablePercent = (bus.available_seats / bus.total_seats) * 100;
            const busCard = document.createElement('div');
            busCard.className = 'bus-card';
            busCard.innerHTML = `
                <h3>🚌 ${bus.bus_number}</h3>
                <div class="bus-info">
                    <span><strong>Driver:</strong> ${bus.driver_name}</span>
                    <span><strong>Route:</strong> ${bus.route}</span>
                    <span><strong>Available Seats:</strong> ${bus.available_seats}/${bus.total_seats}</span>
                </div>
                <div class="availability-bar">
                    <div class="availability-fill" style="width: ${availablePercent}%"></div>
                </div>
                <button onclick="openBusModal(${bus.id}, '${bus.bus_number}')">View Seats & Book</button>
            `;
            container.appendChild(busCard);
        });
    } catch (error) {
        console.error('Error loading buses:', error);
    }
}

async function openBusModal(busId, busNumber) {
    currentBus = { id: busId, bus_number: busNumber };
    
    try {
        const seats = await fetchSeats(busId);
        const modal = document.getElementById('busModal');
        const modalTitle = document.getElementById('busModalTitle');
        const modalBody = document.getElementById('busModalBody');

        modalTitle.textContent = `Bus ${busNumber} - Seat Selection`;
        
        let seatsHTML = '<div class="seats-layout">';
        seats.forEach(seat => {
            const seatClass = seat.is_reserved ? 'reserved' : 'available';
            const womenClass = seat.is_women_seat ? 'women' : '';
            const seatTypeIcon = seat.is_women_seat ? '♀' : '';
            
            seatsHTML += `
                <button class="seat ${seatClass} ${womenClass}" 
                        onclick="selectSeat(${seat.seat_id}, ${seat.is_reserved})"
                        ${seat.is_reserved ? 'disabled' : ''}>
                    ${seat.seat_number}${seatTypeIcon}
                </button>
            `;
        });
        seatsHTML += '</div>';
        seatsHTML += `
            <button onclick="confirmReservation(${busId})" style="width: 100%; padding: 0.75rem; margin-top: 1rem; background: linear-gradient(135deg, #FF6B6B, #4ECDC4); color: white; border: none; border-radius: 8px; cursor: pointer;">
                Confirm Reservation
            </button>
        `;

        modalBody.innerHTML = seatsHTML;
        modal.classList.remove('hidden');
    } catch (error) {
        console.error('Error opening bus modal:', error);
    }
}

function selectSeat(seatId, isReserved) {
    if (isReserved) return;
    
    const seatElements = document.querySelectorAll('.seat');
    seatElements.forEach(seat => seat.classList.remove('selected'));
    
    event.target.classList.add('selected');
    selectedSeat = seatId;
}

async function confirmReservation(busId) {
    if (!selectedSeat) {
        alert('Please select a seat');
        return;
    }

    try {
        const result = await reserveSeat(selectedSeat, currentUser.user_id);
        alert('Seat reserved successfully!');
        closeBusModal();
        loadBuses();
    } catch (error) {
        alert('Failed to reserve seat');
    }
}

function closeBusModal() {
    document.getElementById('busModal').classList.add('hidden');
    selectedSeat = null;
}

// ========== ALERTS ==========
async function loadAlerts() {
    try {
        // Load buses for dropdown
        const buses = await fetchBuses();
        const busSelect = document.getElementById('alertBusId');
        busSelect.innerHTML = '<option value="">Select Bus</option>';
        buses.forEach(bus => {
            const option = document.createElement('option');
            option.value = bus.id;
            option.textContent = `${bus.bus_number} - ${bus.route}`;
            busSelect.appendChild(option);
        });

        // Load user's alerts
        const alerts = await fetchUserWakeupAlerts(currentUser.user_id);
        const container = document.getElementById('alertsContainer');
        container.innerHTML = '';

        if (alerts.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: #999;">No active alerts. Create one!</p>';
            return;
        }

        alerts.forEach(alert => {
            const alertCard = document.createElement('div');
            alertCard.className = 'alert-card';
            alertCard.innerHTML = `
                <h3>📍 ${alert.stop_name}</h3>
                <p><strong>Bus:</strong> Bus ${alert.bus_id}</p>
                <p><strong>Alert Time:</strong> ${alert.alert_before_time / 60} minutes before arrival</p>
            `;
            container.appendChild(alertCard);
        });
    } catch (error) {
        console.error('Error loading alerts:', error);
    }
}

// ========== LOST & FOUND ==========
function switchLostFoundTab(tab) {
    const reportForm = document.getElementById('reportLostForm');
    const foundItems = document.getElementById('foundItemsContainer');
    const tabBtns = document.querySelectorAll('#lost-found .tab-btn');

    if (tab === 'report') {
        reportForm.classList.remove('hidden');
        foundItems.classList.add('hidden');
        tabBtns[0].classList.add('active');
        tabBtns[1].classList.remove('active');
    } else {
        reportForm.classList.add('hidden');
        foundItems.classList.remove('hidden');
        tabBtns[0].classList.remove('active');
        tabBtns[1].classList.add('active');
        loadFoundItems();
    }
}

async function loadFoundItems() {
    try {
        const items = await fetchLostItems('found');
        const container = document.getElementById('foundItemsContainer');
        container.innerHTML = '';

        if (items.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: #999; grid-column: 1/-1;">No found items yet</p>';
            return;
        }

        items.forEach(item => {
            const itemCard = document.createElement('div');
            itemCard.className = 'item-card';
            itemCard.innerHTML = `
                <div class="item-image">📦</div>
                <div class="item-details">
                    <h3>${item.item_name}</h3>
                    <p>${item.item_description}</p>
                    <p><strong>Found by:</strong> ${item.found_by}</p>
                    <span class="item-status">${item.item_status.toUpperCase()}</span>
                    <button onclick="claimItem(${item.id})">Claim Item</button>
                </div>
            `;
            container.appendChild(itemCard);
        });
    } catch (error) {
        console.error('Error loading found items:', error);
    }
}

async function claimItem(itemId) {
    try {
        const result = await claimLostItem(itemId);
        alert('Item claimed successfully! Contact bus workers to collect it.');
        loadFoundItems();
    } catch (error) {
        alert('Failed to claim item');
    }
}

// ========== UTILITY FUNCTIONS ==========
function showError(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = message;
        element.classList.add('show');
        setTimeout(() => element.classList.remove('show'), 5000);
    }
}

function clearLoginForm() {
    document.getElementById('loginForm').reset();
}

function clearRegisterForm() {
    document.getElementById('registerForm').reset();
}

function logout() {
    currentUser = null;
    localStorage.removeItem('user');
    showPage('auth');
}