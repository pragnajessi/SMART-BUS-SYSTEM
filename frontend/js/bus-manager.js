/**
 * Bus Manager
 * Handles all bus-related operations
 */

class BusManager {
    constructor() {
        this.buses = [];
        this.selectedBus = null;
        this.seats = [];
    }

    /**
     * Fetch all buses
     */
    async loadBuses(page = 1, perPage = 10) {
        try {
            console.log('🚌 Loading buses...');
            
            const response = await apiService.getAllBuses(page, perPage);
            this.buses = response.buses || [];
            
            console.log(`✅ Loaded ${this.buses.length} buses`);
            return this.buses;
        } catch (error) {
            console.error('❌ Failed to load buses:', error.message);
            throw error;
        }
    }

    /**
     * Create new bus
     */
    async createBus(busData) {
        try {
            console.log('🚌 Creating new bus:', busData.bus_number);
            
            const response = await apiService.createBus(busData);
            
            console.log('✅ Bus created successfully');
            await this.loadBuses();
            
            return response;
        } catch (error) {
            console.error('❌ Failed to create bus:', error.message);
            throw error;
        }
    }

    /**
     * Select bus and load its seats
     */
    async selectBus(busId) {
        try {
            console.log(`🔍 Selecting bus ${busId}...`);
            
            const bus = this.buses.find(b => b.id === busId);
            if (!bus) {
                throw new Error('Bus not found');
            }

            this.selectedBus = bus;
            await this.loadSeats(busId);
            
            console.log('✅ Bus selected');
            return this.selectedBus;
        } catch (error) {
            console.error('❌ Failed to select bus:', error.message);
            throw error;
        }
    }

    /**
     * Load seats for a bus
     */
    async loadSeats(busId) {
        try {
            console.log(`🪑 Loading seats for bus ${busId}...`);
            
            const response = await apiService.getBusSeats(busId);
            this.seats = response;
            
            console.log(`✅ Loaded ${this.seats.length} seats`);
            return this.seats;
        } catch (error) {
            console.error('❌ Failed to load seats:', error.message);
            throw error;
        }
    }

    /**
     * Reserve a seat
     */
    async reserveSeat(seatId, userId) {
        try {
            console.log(`🎟️ Reserving seat ${seatId}...`);
            
            const response = await apiService.reserveSeat(seatId, userId);
            
            // Update seat status locally
            const seat = this.seats.find(s => s.seat_id === seatId);
            if (seat) {
                seat.is_reserved = true;
            }
            
            console.log('✅ Seat reserved successfully');
            return response;
        } catch (error) {
            console.error('❌ Failed to reserve seat:', error.message);
            throw error;
        }
    }

    /**
     * Cancel seat reservation
     */
    async cancelReservation(seatId) {
        try {
            console.log(`❌ Cancelling seat ${seatId}...`);
            
            const response = await apiService.cancelSeatReservation(seatId);
            
            // Update seat status locally
            const seat = this.seats.find(s => s.seat_id === seatId);
            if (seat) {
                seat.is_reserved = false;
            }
            
            console.log('✅ Seat reservation cancelled');
            return response;
        } catch (error) {
            console.error('❌ Failed to cancel reservation:', error.message);
            throw error;
        }
    }

    /**
     * Get available seats count
     */
    getAvailableSeatsCount() {
        return this.seats.filter(s => !s.is_reserved).length;
    }

    /**
     * Get reserved seats count
     */
    getReservedSeatsCount() {
        return this.seats.filter(s => s.is_reserved).length;
    }

    /**
     * Get seat occupancy percentage
     */
    getSeatOccupancy() {
        if (this.seats.length === 0) return 0;
        return (this.getReservedSeatsCount() / this.seats.length) * 100;
    }
}

// Create global instance
const busManager = new BusManager();