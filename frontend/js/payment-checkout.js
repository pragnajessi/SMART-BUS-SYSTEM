const PAYMENT_API_BASE_URL = 'http://localhost:5000/api/payments';

let currentBooking = null;
let currentPaymentMethod = 'card';
let walletBalance = 0;

// Initialize payment page
document.addEventListener('DOMContentLoaded', () => {
    loadBookingDetails();
    loadWalletBalance();

    // Card form submission
    document.getElementById('cardPaymentForm').addEventListener('submit', submitCardPayment);
    
    // UPI form submission
    document.getElementById('upiPaymentForm').addEventListener('submit', submitUPIPayment);
});

// Load booking details from query params or session
function loadBookingDetails() {
    // Mock data - replace with actual booking data
    const booking = {
        bus_number: 'BUS001',
        route: 'Station A - Station B',
        seat_number: 12,
        date: '2026-02-15',
        passenger_name: 'John Doe',
        amount: 250,
        booking_id: 1
    };

    currentBooking = booking;

    document.getElementById('summaryBusNumber').textContent = booking.bus_number;
    document.getElementById('summaryRoute').textContent = booking.route;
    document.getElementById('summarySeatNumber').textContent = booking.seat_number;
    document.getElementById('summaryDate').textContent = new Date(booking.date).toLocaleDateString();
    document.getElementById('summaryPassenger').textContent = booking.passenger_name;
    document.getElementById('summaryAmount').textContent = `₹${booking.amount}`;
    document.getElementById('walletAmount').textContent = booking.amount;
}

// Switch payment method
function switchPaymentMethod(method) {
    currentPaymentMethod = method;

    // Update tab highlighting
    document.querySelectorAll('.method-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    event.target.classList.add('active');

    // Show/hide forms
    document.getElementById('cardPaymentForm').classList.add('hidden');
    document.getElementById('upiPaymentForm').classList.add('hidden');
    document.getElementById('walletPaymentForm').classList.add('hidden');

    if (method === 'card') {
        document.getElementById('cardPaymentForm').classList.remove('hidden');
    } else if (method === 'upi') {
        document.getElementById('upiPaymentForm').classList.remove('hidden');
    } else if (method === 'wallet') {
        document.getElementById('walletPaymentForm').classList.remove('hidden');
    }
}

// Submit card payment
async function submitCardPayment(event) {
    event.preventDefault();

    const paymentData = {
        booking_id: currentBooking.booking_id,
        payment_method: 'card',
        card_name: document.getElementById('cardName').value,
        card_email: document.getElementById('cardEmail').value,
        card_phone: document.getElementById('cardPhone').value
    };

    try {
        // Initiate payment
        const response = await fetch(`${PAYMENT_API_BASE_URL}/initiate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(paymentData)
        });

        const result = await response.json();

        // Open Razorpay checkout
        openRazorpayCheckout(result.razorpay_order, result.payment_id);
    } catch (error) {
        alert('Failed to initiate payment');
    }
}

// Open Razorpay checkout
function openRazorpayCheckout(orderData, paymentId) {
    const options = {
        key: 'YOUR_RAZORPAY_KEY_ID',
        amount: orderData.amount,
        currency: orderData.currency,
        name: 'Smart Bus Management',
        description: orderData.description,
        order_id: orderData.receipt,
        handler: function(response) {
            verifyRazorpayPayment(paymentId, response.razorpay_payment_id, response.razorpay_signature);
        },
        prefill: {
            email: document.getElementById('cardEmail').value,
            contact: document.getElementById('cardPhone').value
        },
        theme: {
            color: '#FF6B6B'
        }
    };

    const rzp = new Razorpay(options);
    rzp.open();
}

// Verify Razorpay payment
async function verifyRazorpayPayment(paymentId, razorpayPaymentId, signature) {
  try {
    const response = await fetch(`${PAYMENT_API_BASE_URL}/verify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        payment_id: paymentId,
        gateway_transaction_id: razorpayPaymentId,
        razorpay_signature: signature,
      }),
    });

    const data = await response.json();
    return data;

  } catch (error) {
    console.error('Payment verification failed:', error);
    throw error;
  }
}
