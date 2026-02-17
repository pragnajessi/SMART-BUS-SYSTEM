/**
 * Wallet Manager
 * Handles wallet and payment operations
 */

class WalletManager {
    constructor() {
        this.balance = 0;
        this.transactions = [];
    }

    /**
     * Load wallet balance
     */
    async loadBalance(userId) {
        try {
            console.log('💰 Loading wallet balance...');
            
            const response = await apiService.getWalletBalance(userId);
            this.balance = response.balance || 0;
            
            console.log(`✅ Wallet balance: ₹${this.balance}`);
            return this.balance;
        } catch (error) {
            console.error('❌ Failed to load wallet:', error.message);
            throw error;
        }
    }

    /**
     * Add money to wallet
     */
    async addMoney(userId, amount, description = null) {
        try {
            console.log(`➕ Adding ₹${amount} to wallet...`);
            
            const response = await apiService.addWalletMoney(userId, amount, description);
            this.balance = response.new_balance;
            
            console.log(`✅ Money added. New balance: ₹${this.balance}`);
            return response;
        } catch (error) {
            console.error('❌ Failed to add money:', error.message);
            throw error;
        }
    }

    /**
     * Load transaction history
     */
    async loadTransactions(userId, limit = 20) {
        try {
            console.log('📜 Loading transactions...');
            
            const response = await apiService.getWalletTransactions(userId, limit);
            this.transactions = response;
            
            console.log(`✅ Loaded ${this.transactions.length} transactions`);
            return this.transactions;
        } catch (error) {
            console.error('❌ Failed to load transactions:', error.message);
            throw error;
        }
    }

    /**
     * Get current balance
     */
    getBalance() {
        return this.balance;
    }

    /**
     * Check if sufficient balance
     */
    hasSufficientBalance(amount) {
        return this.balance >= amount;
    }

    /**
     * Format balance for display
     */
    formatBalance() {
        return `₹${this.balance.toFixed(2)}`;
    }
}

// Create global instance
const walletManager = new WalletManager();