/**
 * Booking Manager
 * Handles all booking-related operations
 */

class BookingManager {
    constructor() {
        this.bookings = [];
        this.currentBooking = null;
    }

    /**
     * Create new booking
     */
    async createBooking(bookingData) {
        try {
            console.log('📋 Creating booking...');
            
            // Add user ID
            bookingData.user_id = authManager.currentUser.id;
            
            const response = await apiService.createBooking(bookingData);
            
            this.currentBooking = response;
            console.log('✅ Booking created:', response.booking_ref);
            
            return response;
        } catch (error) {
            console.error('❌ Failed to create booking:', error.message);
            throw error;
        }
    }

    /**
     * Get booking details
     */
    async getBooking(bookingId) {
        try {
            console.log(`📖 Getting booking ${bookingId}...`);
            
            const response = await apiService.getBooking(bookingId);
            
            console.log('✅ Booking retrieved');
            return response;
        } catch (error) {
            console.error('❌ Failed to get booking:', error.message);
            throw error;
        }
    }

    /**
     * Confirm booking
     */
    async confirmBooking(bookingId) {
        try {
            console.log(`✅ Confirming booking ${bookingId}...`);
            
            const response = await apiService.confirmBooking(bookingId);
            
            console.log('✅ Booking confirmed');
            return response;
        } catch (error) {
            console.error('❌ Failed to confirm booking:', error.message);
            throw error;
        }
    }

    /**
     * Cancel booking
     */
    async cancelBooking(bookingId, reason = null) {
        try {
            console.log(`🚫 Cancelling booking ${bookingId}...`);
            
            const response = await apiService.cancelBooking(bookingId, reason);
            
            console.log('✅ Booking cancelled');
            return response;
        } catch (error) {
            console.error('❌ Failed to cancel booking:', error.message);
            throw error;
        }
    }

    /**
     * Get current booking
     */
    getCurrentBooking() {
        return this.currentBooking;
    }
}

// Create global instance
const bookingManager = new BookingManager();