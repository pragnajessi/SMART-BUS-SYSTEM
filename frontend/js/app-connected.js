// ==================== MAIN ROUTER & CONTROLLER ====================

document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 Smart Bus Management System Started');
    
    // Initial check: Show home page by default
    if (typeof authManager !== 'undefined' && authManager.isLoggedIn()) {
        console.log('✅ User logged in:', authManager.getCurrentUser().name);
        updateUserMenu();
        showPage('buses');
    } else {
        showPage('home');
    }
});

/**
 * Main function to switch between sections
 * Compulsory login check has been disabled for development
 */
function showPage(pageId) {
    console.log("Navigating to:", pageId);

    // 1. SECURITY CHECK (DISABLED FOR ADMIN/DEVELOPMENT VIEW)
    /* const protectedPages = ['buses', 'dashboard', 'wallet', 'booking', 'emergency', 'lost-found'];
    if (protectedPages.includes(pageId)) {
        if (typeof authManager !== 'undefined' && !authManager.isLoggedIn()) {
            alert("Please login to access this page.");
            showPage('home'); 
            return;
        }
    }
    */

    // 2. Visual Switch: Hide all sections, show the target
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => {
        page.classList.add('hidden');
    });

    const targetPage = document.getElementById(pageId);
    if (targetPage) {
        targetPage.classList.remove('hidden');
        window.scrollTo(0, 0); // Reset scroll position to top
    } else {
        console.error("Target section not found:", pageId);
    }

    // 3. Data Trigger: Call functions in specialized manager files
    triggerPageData(pageId);
}

/**
 * Triggers data loading for specific sections using other JS files
 */
/**
 * Triggers data loading for specific sections using other JS files
 */
/**
 * Triggers data loading for specific sections using other JS files
 */
function triggerPageData(pageId) {
    // 1. Load Bus List
    if (pageId === 'buses' && typeof loadBuses === 'function') loadBuses();
    
    // 2. Load Wallet Data
    if (pageId === 'wallet' && typeof loadWallet === 'function') loadWallet();
    
    // 3. Load Dashboard Stats AND Start Live GPS/Map/Voice Monitor
    if (pageId === 'dashboard') {
    if (typeof loadDashboard === 'function') loadDashboard();
    
    // This timeout ensures the 'hidden' class is removed BEFORE the map loads
    setTimeout(() => {
        if (typeof startTransitMonitor === 'function') {
            startTransitMonitor();
            // This forces the grey box to load the actual map tiles
            if (map) map.invalidateSize(); 
        }
    }, 200);
}
    // 4. Load Lost & Found Data
    if (pageId === 'lost-found' && typeof loadLostFound === 'function') loadLostFound();
    
    // 5. Load Booking Initial State
    if (pageId === 'booking' && typeof loadBookingData === 'function') loadBookingData();
}
/**
 * Updates the UI to show user-specific menu items
 */
function updateUserMenu() {
    const userMenu = document.getElementById('userMenu');
    const userName = document.getElementById('userName');
    
    if (userMenu && typeof authManager !== 'undefined' && authManager.isLoggedIn()) {
        const user = authManager.getCurrentUser();
        userMenu.style.display = 'block';
        userName.textContent = `👤 ${user.name}`;
    }
}

/**
 * Handles user logout
 */
function logoutUser() {
    if (confirm('Are you sure you want to logout?')) {
        if (typeof authManager !== 'undefined') {
            authManager.logout();
        }
        location.reload(); // Refresh to clear all states
    }
}
