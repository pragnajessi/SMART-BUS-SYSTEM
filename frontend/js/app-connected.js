/**
 * Main Application Logic
 * Handles UI interactions and integrates all managers
 */

// ==================== INITIALIZATION ====================

document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 Smart Bus Management System Started');
    
    // Check if user is logged in
    if (authManager.isLoggedIn()) {
        console.log('✅ User logged in:', authManager.getCurrentUser().name);
        showPage('buses');
        updateUserMenu();
        loadInitialData();
    } else {
        console.log('⚠️ User not logged in');
        showPage('auth');
    }
});

// ==================== PAGE NAVIGATION ====================

function showPage(pageName) {
    // Check authentication for protected pages
    const protectedPages = ['buses', 'dashboard', 'wallet', 'booking', 'emergency', 'lost-found'];
    
    if (protectedPages.includes(pageName) && !authManager.isLoggedIn()) {
        showPage('auth');
        return;
    }

    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.add('hidden');
    });

    // Show selected page
    const targetPage = document.getElementById(pageName);
    if (targetPage) {
        targetPage.classList.remove('hidden');
        
        // Load data for specific pages
        if (pageName === 'buses') loadBuses();
        else if (pageName === 'dashboard') loadDashboard();
        else if (pageName === 'wallet') loadWallet();
        else if (pageName === 'emergency') prepareEmergency();
        else if (pageName === 'lost-found') loadLostFound();
    }
}

// ==================== AUTHENTICATION ====================

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

async function handleLogin(event) {
    event.preventDefault();
    
    try {
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;

        await authManager.login(email, password);
        
        updateUserMenu();
        showPage('buses');
        document.getElementById('loginForm').reset();
        await loadInitialData();
    } catch (error) {
        showError('loginError', error.message);
    }
}

async function handleRegister(event) {
    event.preventDefault();
    
    try {
        const password = document.getElementById('registerPassword').value;
        const confirmPassword = document.getElementById('registerConfirmPassword').value;

        if (password !== confirmPassword) {
            throw new Error('Passwords do not match');
        }

        const userData = {
            name: document.getElementById('registerName').value,
            email: document.getElementById('registerEmail').value,
            phone: document.getElementById('registerPhone').value,
            gender: document.getElementById('registerGender').value,
            password: password
        };

        await authManager.register(userData);
        
        alert('✅ Registration successful! Please login.');
        switchAuthTab('login');
        document.getElementById('registerForm').reset();
    } catch (error) {
        showError('registerError', error.message);
    }
}

function updateUserMenu() {
    if (authManager.isLoggedIn()) {
        const user = authManager.getCurrentUser();
        document.getElementById('userMenu').style.display = 'block';
        document.getElementById('userName').textContent = `👤 ${user.name}`;
    } else {
        document.getElementById('userMenu').style.display = 'none';
    }
}

function logoutUser() {
    if (confirm('Are you sure you want to logout?')) {
        authManager.logout();
        showPage('home');
        updateUserMenu();
    }
}

// ==================== BUSES ====================

async function loadBuses() {
    try {
        console.log('Loading buses...');
        const buses = await busManager.loadBuses();
        
        const container = document.getElementById('busesContainer');
        container.innerHTML = '';

        buses.forEach(bus => {
            const card = document.createElement('div');
            card.className = 'bus-card';
            card.innerHTML = `
                <h3>${bus.bus_number}</h3>
                <p><strong>Route:</strong> ${bus.route}</p>
                <p><strong>Driver:</strong> ${bus.driver_name}</p>
                <p><strong>Seats:</strong> ${bus.available_seats}/${bus.total_seats} available</p>
                <button onclick="selectBusForBooking(${bus.id})">Book Seat</button>
            `;
            container.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading buses:', error);
        alert('Failed to load buses');
    }
}

async function selectBusForBooking(busId) {
    try {
        await busManager.selectBus(busId);
        displaySeatsForBooking();
    } catch (error) {
        alert('Error selecting bus: ' + error.message);
    }
}

function displaySeatsForBooking() {
    const bus = busManager.selectedBus;
    const seats = busManager.seats;
    
    const container = document.getElementById('bookingSeats');
    container.innerHTML = `<h4>${bus.bus_number} - Select a Seat</h4>`;
    
    const seatsGrid = document.createElement('div');
    seatsGrid.className = 'seats-layout';
    
    seats.forEach(seat => {
        const button = document.createElement('button');
        button.className = `seat ${seat.is_reserved ? 'reserved' : 'available'} ${seat.is_women_seat ? 'women' : ''}`;
        button.textContent = seat.seat_number;
        button.disabled = seat.is_reserved;
        button.onclick = () => selectSeatForBooking(seat.seat_id);
        seatsGrid.appendChild(button);
    });
    
    container.appendChild(seatsGrid);
}

let selectedSeatId = null;

function selectSeatForBooking(seatId) {
    selectedSeatId = seatId;
    console.log('Selected seat:', seatId);
}

async function confirmBooking() {
    if (!selectedSeatId || !busManager.selectedBus) {
        alert('Please select a seat first');
        return;
    }

    try {
        const bookingData = {
            bus_id: busManager.selectedBus.id,
            seat_id: selectedSeatId,
            travel_date: new Date().toISOString().split('T')[0],
            price: 250
        };

        const response = await bookingManager.createBooking(bookingData);
        alert(`✅ Booking created: ${response.booking_ref}`);
        selectedSeatId = null;
    } catch (error) {
        alert('Error creating booking: ' + error.message);
    }
}

// ==================== DASHBOARD ====================

async function loadDashboard() {
    try {
        const stats = await dashboardManager.loadStats();
        const formatted = dashboardManager.getFormattedStats();
        
        document.getElementById('statTotalUsers').textContent = formatted.totalUsers;
        document.getElementById('statTotalBuses').textContent = formatted.totalBuses;
        document.getElementById('statTotalBookings').textContent = formatted.totalBookings;
        document.getElementById('statTotalRevenue').textContent = formatted.totalRevenue;
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// ==================== WALLET ====================

async function loadWallet() {
    try {
        const userId = authManager.getCurrentUser().id;
        await walletManager.loadBalance(userId);
        document.getElementById('walletBalance').textContent = walletManager.formatBalance();
        
        const transactions = await walletManager.loadTransactions(userId);
        displayTransactions(transactions);
    } catch (error) {
        console.error('Error loading wallet:', error);
        alert('Failed to load wallet');
    }
}

function showAddMoneyForm() {
    document.getElementById('addMoneyForm').classList.toggle('hidden');
}

async function handleAddMoney() {
    try {
        const amount = parseFloat(document.getElementById('addAmount').value);
        if (!amount || amount < 100) {
            alert('Minimum amount is ₹100');
            return;
        }

        const userId = authManager.getCurrentUser().id;
        await walletManager.addMoney(userId, amount, 'Money added');
        
        document.getElementById('walletBalance').textContent = walletManager.formatBalance();
        document.getElementById('addAmount').value = '';
        showAddMoneyForm();
        alert(`✅ ₹${amount} added to wallet`);
    } catch (error) {
        alert('Error adding money: ' + error.message);
    }
}

function displayTransactions(transactions) {
    const container = document.getElementById('transactionsTable');
    container.innerHTML = '';

    transactions.forEach(txn => {
        const row = document.createElement('div');
        row.className = 'transaction-row';
        row.innerHTML = `
            <span>${txn.description}</span>
            <span>${txn.type === 'credit' ? '+' : '-'}₹${txn.amount}</span>
            <span>${new Date(txn.date).toLocaleDateString()}</span>
        `;
        container.appendChild(row);
    });
}

// ==================== EMERGENCY ====================

function prepareEmergency() {
    // Get current location if available
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(position => {
            console.log('📍 Current location:', position.coords);
        });
    }
}

async function reportEmergency(event) {
    event.preventDefault();
    
    try {
        const emergencyType = document.getElementById('emergencyType').value;
        const description = document.getElementById('emergencyDescription').value;

        const emergencyData = {
            bus_id: busManager.selectedBus?.id || 1,
            user_id: authManager.getCurrentUser().id,
            emergency_type: emergencyType,
            latitude: 28.6139,
            longitude: 77.2090,
            description: description
        };

        await apiService.reportEmergency(emergencyData);
        alert('🆘 Emergency reported! Help is on the way.');
        document.getElementById('emergencyForm').reset();
    } catch (error) {
        alert('Error reporting emergency: ' + error.message);
    }
}

// ==================== LOST & FOUND ====================

async function loadLostFound() {
    try {
        const items = await apiService.getLostItems('found');
        displayFoundItems(items);
    } catch (error) {
        console.error('Error loading lost & found:', error);
    }
}

async function reportLostItem(event) {
    event.preventDefault();
    
    try {
        const itemData = {
            item_name: document.getElementById('lostItemName').value,
            item_description: document.getElementById('lostItemDescription').value,
            user_id: authManager.getCurrentUser().id
        };

        await apiService.reportLostItem(itemData);
        alert('✅ Lost item reported!');
        document.getElementById('reportLostForm').reset();
    } catch (error) {
        alert('Error reporting lost item: ' + error.message);
    }
}

function displayFoundItems(items) {
    const container = document.getElementById('foundItemsContainer');
    container.innerHTML = '';

    items.forEach(item => {
        const card = document.createElement('div');
        card.className = 'item-card';
        card.innerHTML = `
            <div class="item-details">
                <h3>${item.item_name}</h3>
                <p>${item.item_description}</p>
                <p><strong>Found by:</strong> ${item.found_by}</p>
                <button onclick="claimItem(${item.id})">Claim Item</button>
            </div>
        `;
        container.appendChild(card);
    });
}

async function claimItem(itemId) {
    try {
        await apiService.claimLostItem(itemId);
        alert('✅ Item claimed! Contact to collect.');
        loadLostFound();
    } catch (error) {
        alert('Error claiming item: ' + error.message);
    }
}

// ==================== UTILITY FUNCTIONS ====================

function showError(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = message;
        element.classList.add('show');
        setTimeout(() => element.classList.remove('show'), 5000);
    }
}

async function loadInitialData() {
    try {
        console.log('Loading initial data...');
        await busManager.loadBuses();
        const userId = authManager.getCurrentUser().id;
        await walletManager.loadBalance(userId);
        console.log('✅ Initial data loaded');
    } catch (error) {
        console.error('Error loading initial data:', error);
    }
}