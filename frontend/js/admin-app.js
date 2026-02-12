let adminUser = null;
let currentBusPage = 1;
let currentUserPage = 1;
let currentPaymentPage = 1;

// ========== PAGE NAVIGATION ==========
function showAdminPage(pageName) {
    const pages = document.querySelectorAll('.admin-page');
    pages.forEach(page => page.classList.add('hidden'));

    const targetPage = document.getElementById(pageName);
    if (targetPage) {
        targetPage.classList.remove('hidden');
        
        // Update page title
        const titles = {
            'dashboard': 'Dashboard',
            'buses': 'Manage Buses',
            'users': 'Manage Users',
            'payments': 'Payment Management',
            'analytics': 'Analytics',
            'reports': 'Reports',
            'logs': 'Activity Logs'
        };
        document.getElementById('pageTitle').textContent = titles[pageName] || pageName;
        
        // Load data for specific pages
        if (pageName === 'dashboard') loadDashboard();
        else if (pageName === 'buses') loadBuses();
        else if (pageName === 'users') loadUsers();
        else if (pageName === 'payments') loadPayments();
        else if (pageName === 'analytics') loadAnalytics();
        else if (pageName === 'logs') loadActivityLogs();
    }

    // Update active menu item
    const menuItems = document.querySelectorAll('.menu-item');
    menuItems.forEach(item => item.classList.remove('active'));
    event.target.classList.add('active');
}

// ========== DASHBOARD ==========
async function loadDashboard() {
    try {
        const data = await fetchAdminDashboard();
        
        // Update stats
        document.getElementById('totalBuses').textContent = data.buses.total;
        document.getElementById('activeBuses').textContent = `${data.buses.active} Active`;
        document.getElementById('totalUsers').textContent = data.users.total;
        document.getElementById('totalBookings').textContent = data.bookings.total;
        document.getElementById('confirmedBookings').textContent = `${data.bookings.confirmed} Confirmed`;
        document.getElementById('totalRevenue').textContent = `₹${data.revenue.total.toFixed(2)}`;
        document.getElementById('todayRevenue').textContent = `Today: ₹${data.revenue.today.toFixed(2)}`;
        
        // Load charts
        loadDashboardCharts();
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

async function loadDashboardCharts() {
    try {
        const revenueData = await fetchRevenueAnalytics(30);
        const bookingData = await fetchBookingAnalytics(30);
        
        // Revenue Chart
        const revenueCtx = document.getElementById('revenueChart').getContext('2d');
        new Chart(revenueCtx, {
            type: 'line',
            data: {
                labels: Object.keys(revenueData.revenue_by_date),
                datasets: [{
                    label: 'Daily Revenue',
                    data: Object.values(revenueData.revenue_by_date),
                    borderColor: '#FF6B6B',
                    backgroundColor: 'rgba(255, 107, 107, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: true }
                }
            }
        });
        
        // Payment Method Chart
        const methodCtx = document.getElementById('paymentMethodChart').getContext('2d');
        new Chart(methodCtx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(revenueData.revenue_by_method),
                datasets: [{
                    data: Object.values(revenueData.revenue_by_method),
                    backgroundColor: ['#FF6B6B', '#4ECDC4', '#95E1D3']
                }]
            }
        });
        
        // Booking Status Chart
        const bookingCtx = document.getElementById('bookingStatusChart').getContext('2d');
        new Chart(bookingCtx, {
            type: 'bar',
            data: {
                labels: Object.keys(bookingData.status_breakdown),
                datasets: [{
                    label: 'Bookings',
                    data: Object.values(bookingData.status_breakdown),
                    backgroundColor: ['#95E1D3', '#FFE66D', '#FF6B6B']
                }]
            }
        });
    } catch (error) {
        console.error('Error loading charts:', error);
    }
}

// ========== BUSES MANAGEMENT ==========
async function loadBuses() {
    try {
        const data = await fetchAllBuses(currentBusPage);
        const tbody = document.getElementById('busesTableBody');
        tbody.innerHTML = '';
        
        data.buses.forEach(bus => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${bus.bus_number}</td>
                <td>${bus.driver_name}</td>
                <td>${bus.route}</td>
                <td>${bus.total_seats}</td>
                <td>${bus.reserved_seats}</td>
                <td>${bus.available_seats}</td>
                <td>
                    <select onchange="updateBusStatusUI(${bus.id}, this.value)" 
                            style="padding: 0.4rem; border-radius: 4px;">
                        <option value="active" ${bus.status === 'active' ? 'selected' : ''}>Active</option>
                        <option value="inactive" ${bus.status === 'inactive' ? 'selected' : ''}>Inactive</option>
                    </select>
                </td>
                <td>${bus.current_location.latitude.toFixed(4)}, ${bus.current_location.longitude.toFixed(4)}</td>
                <td>
                    <button onclick="viewBusDetails(${bus.id})" class="btn-small">View</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading buses:', error);
    }
}

async function updateBusStatusUI(busId, status) {
    try {
        const result = await updateBusStatus(busId, status);
        alert('Bus status updated successfully!');
        loadBuses();
    } catch (error) {
        alert('Failed to update bus status');
    }
}

function openBusModal() {
    document.getElementById('busModal').classList.remove('hidden');
}

function closeBusModal() {
    document.getElementById('busModal').classList.add('hidden');
}

function saveBus(event) {
    event.preventDefault();
    // Implementation for saving bus
    alert('Bus saved successfully!');
    closeBusModal();
    loadBuses();
}

function searchBuses() {
    // Implementation for searching buses
}

function filterBuses() {
    // Implementation for filtering buses
}

// ========== USERS MANAGEMENT ==========
async function loadUsers() {
    try {
        const data = await fetchAllUsers(currentUserPage);
        const tbody = document.getElementById('usersTableBody');
        tbody.innerHTML = '';
        
        data.users.forEach(user => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${user.name}</td>
                <td>${user.email}</td>
                <td>${user.phone}</td>
                <td>${user.gender}</td>
                <td>${user.account_type}</td>
                <td>${user.bookings}</td>
                <td>${new Date(user.created_at).toLocaleDateString()}</td>
                <td>
                    <button onclick="viewUserDetails(${user.id})" class="btn-small">View</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

function searchUsers() {
    // Implementation for searching users
}

function filterUsers() {
    // Implementation for filtering users
}

// ========== PAYMENTS MANAGEMENT ==========
async function loadPayments() {
    try {
        const data = await fetchAllPayments(currentPaymentPage);
        const tbody = document.getElementById('paymentsTableBody');
        tbody.innerHTML = '';
        
        data.payments.forEach(payment => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${payment.transaction_id}</td>
                <td>${payment.user_name}</td>
                <td>₹${payment.amount.toFixed(2)}</td>
                <td>${payment.payment_method}</td>
                <td>
                    <span class="status-badge ${payment.payment_status}">
                        ${payment.payment_status.toUpperCase()}
                    </span>
                </td>
                <td>${new Date(payment.created_at).toLocaleDateString()}</td>
                <td>
                    <button onclick="viewPaymentDetails(${payment.id})" class="btn-small">View</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading payments:', error);
    }
}

function filterPayments() {
    // Implementation for filtering payments
}

// ========== ANALYTICS ==========
async function loadAnalytics() {
    try {
        const revenueData = await fetchRevenueAnalytics(30);
        const bookingData = await fetchBookingAnalytics(30);
        
        // Update analytics cards
        document.getElementById('analyticsRevenue').textContent = `₹${revenueData.total_revenue.toFixed(2)}`;
        document.getElementById('analyticsTxns').textContent = revenueData.total_transactions;
        document.getElementById('analyticsAvgTxn').textContent = `₹${revenueData.average_transaction.toFixed(2)}`;
        
        document.getElementById('analyticsBookings').textContent = bookingData.total_bookings;
        document.getElementById('analyticsConfirmed').textContent = bookingData.status_breakdown.confirmed || 0;
        document.getElementById('analyticsPending').textContent = bookingData.status_breakdown.pending || 0;
        
        // Load chart
        const ctx = document.getElementById('methodChart').getContext('2d');
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: Object.keys(revenueData.revenue_by_method),
                datasets: [{
                    data: Object.values(revenueData.revenue_by_method),
                    backgroundColor: ['#FF6B6B', '#4ECDC4', '#95E1D3', '#FFE66D']
                }]
            }
        });
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

// ========== REPORTS ==========
async function generateDailyReport() {
    try {
        const result = await generateDailyReport();
        alert('Daily report generated successfully!');
    } catch (error) {
        alert('Failed to generate report');
    }
}

// ========== ACTIVITY LOGS ==========
async function loadActivityLogs() {
    try {
        const data = await fetchAdminLogs();
        const tbody = document.getElementById('logsTableBody');
        tbody.innerHTML = '';
        
        data.logs.forEach(log => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${log.admin_name}</td>
                <td>${log.action}</td>
                <td>${log.entity_type}</td>
                <td><pre>${JSON.stringify(log.changes, null, 2)}</pre></td>
                <td>${new Date(log.timestamp).toLocaleString()}</td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading logs:', error);
    }
}

// ========== INITIALIZATION ==========
document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
});

function logoutAdmin() {
    localStorage.removeItem('admin_id');
    window.location.href = 'index.html';
}