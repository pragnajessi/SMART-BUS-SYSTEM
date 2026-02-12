from flask import Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import db, app
import uuid
import hmac
import hashlib

# Payment Service Blueprint
payment_bp = Blueprint('payment', __name__, url_prefix='/api/payments')

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    booking_id = db.Column(db.Integer, nullable=True)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='INR')
    payment_method = db.Column(db.String(50), nullable=False)  # card, upi, wallet
    payment_status = db.Column(db.String(20), default='pending')  # pending, completed, failed, refunded
    payment_gateway = db.Column(db.String(50), default='razorpay')  # razorpay, stripe, paypal
    gateway_transaction_id = db.Column(db.String(100), nullable=True)
    payment_details = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    user = db.relationship('User', backref='payments')


class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    seat_id = db.Column(db.Integer, db.ForeignKey('seats.id'), nullable=False)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    travel_date = db.Column(db.DateTime, nullable=False)
    
    user = db.relationship('User', backref='bookings')
    seat = db.relationship('Seat', backref='bookings')
    bus = db.relationship('Bus', backref='bookings')
    payments = db.relationship('Payment', backref='booking_ref', foreign_keys='Payment.booking_id')


class Refund(db.Model):
    __tablename__ = 'refunds'
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=False)
    refund_amount = db.Column(db.Float, nullable=False)
    refund_reason = db.Column(db.String(500), nullable=False)
    refund_status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    gateway_refund_id = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    payment = db.relationship('Payment', backref='refunds')


class Wallet(db.Model):
    __tablename__ = 'wallets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    balance = db.Column(db.Float, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='wallet', uselist=False)


class WalletTransaction(db.Model):
    __tablename__ = 'wallet_transactions'
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # credit, debit
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    balance_before = db.Column(db.Float, nullable=False)
    balance_after = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    wallet = db.relationship('Wallet', backref='transactions')


# ========== PAYMENT ROUTES ==========

@payment_bp.route('/bookings', methods=['POST'])
def create_booking():
    """Create a booking (reserve seat and initiate payment)"""
    try:
        from app import Seat, Bus
        
        data = request.json
        user_id = data['user_id']
        seat_id = data['seat_id']
        bus_id = data['bus_id']
        
        seat = Seat.query.get(seat_id)
        bus = Bus.query.get(bus_id)
        
        if not seat or not bus:
            return jsonify({'message': 'Seat or Bus not found'}), 404
        
        if seat.is_reserved:
            return jsonify({'message': 'Seat already reserved'}), 400
        
        # Create booking
        booking_id = f"BK{uuid.uuid4().hex[:10].upper()}"
        booking = Booking(
            booking_id=booking_id,
            user_id=user_id,
            seat_id=seat_id,
            bus_id=bus_id,
            price=data.get('price', 200.0),
            travel_date=datetime.fromisoformat(data.get('travel_date', datetime.utcnow().isoformat()))
        )
        
        db.session.add(booking)
        db.session.commit()
        
        return jsonify({
            'message': 'Booking created',
            'booking_id': booking.id,
            'booking_ref': booking_id,
            'amount': booking.price,
            'currency': 'INR'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@payment_bp.route('/initiate', methods=['POST'])
def initiate_payment():
    """Initiate payment using Razorpay/Stripe"""
    try:
        data = request.json
        booking_id = data['booking_id']
        payment_method = data.get('payment_method', 'card')
        
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'message': 'Booking not found'}), 404
        
        # Create payment record
        transaction_id = f"TXN{uuid.uuid4().hex[:12].upper()}"
        payment = Payment(
            transaction_id=transaction_id,
            user_id=booking.user_id,
            booking_id=booking_id,
            amount=booking.price,
            payment_method=payment_method
        )
        
        db.session.add(payment)
        db.session.commit()
        
        # Razorpay integration (mock - replace with actual Razorpay API)
        razorpay_order = {
            'amount': int(booking.price * 100),  # Convert to paise
            'currency': 'INR',
            'receipt': transaction_id,
            'description': f'Bus Ticket - {booking.booking_ref}',
            'customer_notify': 1
        }
        
        return jsonify({
            'message': 'Payment initiated',
            'transaction_id': transaction_id,
            'payment_id': payment.id,
            'razorpay_order': razorpay_order,
            'amount': booking.price,
            'currency': 'INR',
            'customer_email': booking.user.email if booking.user else None,
            'customer_phone': booking.user.phone if booking.user else None
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@payment_bp.route('/verify', methods=['POST'])
def verify_payment():
    """Verify payment after successful gateway transaction"""
    try:
        data = request.json
        payment_id = data['payment_id']
        gateway_transaction_id = data['gateway_transaction_id']
        signature = data.get('signature')
        
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({'message': 'Payment not found'}), 404
        
        # Verify signature (Razorpay/Stripe verification)
        # In production, verify with actual gateway
        payment_valid = True
        
        if payment_valid:
            payment.payment_status = 'completed'
            payment.gateway_transaction_id = gateway_transaction_id
            payment.completed_at = datetime.utcnow()
            
            # Confirm booking
            booking = Booking.query.get(payment.booking_id)
            if booking:
                booking.status = 'confirmed'
                
                # Reserve the seat
                seat = Seat.query.get(booking.seat_id)
                if seat:
                    seat.is_reserved = True
                    seat.reserved_by_user_id = booking.user_id
                    seat.reserved_at = datetime.utcnow()
            
            db.session.commit()
            
            return jsonify({
                'message': 'Payment verified and confirmed',
                'payment_status': 'completed',
                'booking_ref': booking.booking_ref if booking else None
            }), 200
        else:
            payment.payment_status = 'failed'
            db.session.commit()
            
            return jsonify({'message': 'Payment verification failed'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@payment_bp.route('/<int:payment_id>/refund', methods=['POST'])
def initiate_refund(payment_id):
    """Initiate refund for a payment"""
    try:
        data = request.json
        payment = Payment.query.get(payment_id)
        
        if not payment:
            return jsonify({'message': 'Payment not found'}), 404
        
        if payment.payment_status != 'completed':
            return jsonify({'message': 'Can only refund completed payments'}), 400
        
        # Create refund record
        refund = Refund(
            payment_id=payment_id,
            refund_amount=payment.amount,
            refund_reason=data.get('reason', 'User requested refund')
        )
        
        db.session.add(refund)
        payment.payment_status = 'refunded'
        
        # Cancel booking and free up seat
        booking = Booking.query.get(payment.booking_id)
        if booking:
            booking.status = 'cancelled'
            seat = Seat.query.get(booking.seat_id)
            if seat:
                seat.is_reserved = False
                seat.reserved_by_user_id = None
                seat.reserved_at = None
        
        db.session.commit()
        
        return jsonify({
            'message': 'Refund initiated',
            'refund_id': refund.id,
            'amount': refund.refund_amount
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@payment_bp.route('/wallet/balance/<int:user_id>', methods=['GET'])
def get_wallet_balance(user_id):
    """Get user's wallet balance"""
    try:
        wallet = Wallet.query.filter_by(user_id=user_id).first()
        
        if not wallet:
            # Create wallet if doesn't exist
            wallet = Wallet(user_id=user_id, balance=0)
            db.session.add(wallet)
            db.session.commit()
        
        return jsonify({
            'wallet_id': wallet.id,
            'user_id': user_id,
            'balance': wallet.balance,
            'currency': 'INR'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payment_bp.route('/wallet/add-money', methods=['POST'])
def add_wallet_money():
    """Add money to wallet"""
    try:
        data = request.json
        user_id = data['user_id']
        amount = data['amount']
        
        wallet = Wallet.query.filter_by(user_id=user_id).first()
        if not wallet:
            wallet = Wallet(user_id=user_id, balance=0)
            db.session.add(wallet)
            db.session.flush()
        
        # Create transaction record
        transaction = WalletTransaction(
            wallet_id=wallet.id,
            transaction_type='credit',
            amount=amount,
            description='Money added to wallet',
            balance_before=wallet.balance,
            balance_after=wallet.balance + amount
        )
        
        wallet.balance += amount
        wallet.last_updated = datetime.utcnow()
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'message': 'Money added to wallet',
            'new_balance': wallet.balance,
            'transaction_id': transaction.id
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@payment_bp.route('/wallet/transactions/<int:user_id>', methods=['GET'])
def get_wallet_transactions(user_id):
    """Get wallet transaction history"""
    try:
        wallet = Wallet.query.filter_by(user_id=user_id).first()
        
        if not wallet:
            return jsonify({'message': 'Wallet not found'}), 404
        
        limit = request.args.get('limit', 20, type=int)
        transactions = WalletTransaction.query.filter_by(wallet_id=wallet.id).order_by(
            WalletTransaction.created_at.desc()
        ).limit(limit).all()
        
        result = []
        for txn in transactions:
            result.append({
                'id': txn.id,
                'type': txn.transaction_type,
                'amount': txn.amount,
                'description': txn.description,
                'balance_before': txn.balance_before,
                'balance_after': txn.balance_after,
                'date': txn.created_at.isoformat()
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payment_bp.route('/wallet/pay-booking', methods=['POST'])
def pay_with_wallet():
    """Pay for booking using wallet"""
    try:
        data = request.json
        user_id = data['user_id']
        booking_id = data['booking_id']
        
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'message': 'Booking not found'}), 404
        
        wallet = Wallet.query.filter_by(user_id=user_id).first()
        if not wallet:
            return jsonify({'message': 'Wallet not found'}), 404
        
        if wallet.balance < booking.price:
            return jsonify({'message': 'Insufficient wallet balance'}), 400
        
        # Debit wallet
        transaction = WalletTransaction(
            wallet_id=wallet.id,
            transaction_type='debit',
            amount=booking.price,
            description=f'Booking payment - {booking.booking_ref}',
            balance_before=wallet.balance,
            balance_after=wallet.balance - booking.price
        )
        
        wallet.balance -= booking.price
        
        # Create payment record
        payment = Payment(
            transaction_id=f"WAL{uuid.uuid4().hex[:12].upper()}",
            user_id=user_id,
            booking_id=booking_id,
            amount=booking.price,
            payment_method='wallet',
            payment_status='completed',
            completed_at=datetime.utcnow()
        )
        
        # Confirm booking
        booking.status = 'confirmed'
        seat = Seat.query.get(booking.seat_id)
        if seat:
            seat.is_reserved = True
            seat.reserved_by_user_id = user_id
            seat.reserved_at = datetime.utcnow()
        
        db.session.add(transaction)
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({
            'message': 'Payment successful',
            'booking_ref': booking.booking_ref,
            'amount': booking.price,
            'new_wallet_balance': wallet.balance
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500