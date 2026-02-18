"""
API Routes - All endpoints
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from database import db, User, Bus, Seat, Wallet

# Create blueprint
api = Blueprint('api', __name__, url_prefix='/api')

# ==================== AUTHENTICATION ====================

@api.route('/auth/register', methods=['POST'])
def register():
    try:
        data = request.json
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already registered'}), 400
        
        user = User(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            gender=data['gender'],
            password=data['password'],
            account_type=data.get('account_type', 'passenger')
        )
        
        db.session.add(user)
        db.session.commit()
        
        wallet = Wallet(user_id=user.id, balance=0)
        db.session.add(wallet)
        db.session.commit()
        
        return jsonify({
            'message': 'Registration successful',
            'user_id': user.id,
            'name': user.name
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.json
        user = User.query.filter_by(email=data['email']).first()
        
        if user and user.password == data['password']:
            return jsonify({
                'message': 'Login successful',
                'user_id': user.id,
                'name': user.name,
                'email': user.email,
                'account_type': user.account_type
            }), 200
        
        return jsonify({'message': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== BUSES ====================

@api.route('/buses', methods=['GET'])
def get_buses():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        buses = Bus.query.filter_by(status='active').paginate(page=page, per_page=per_page)
        
        return jsonify({
            'buses': [{
                'id': bus.id,
                'bus_number': bus.bus_number,
                'driver_name': bus.driver_name,
                'route': bus.route,
                'total_seats': bus.total_seats,
                'available_seats': sum(1 for seat in bus.seats if not seat.is_reserved),
            } for bus in buses.items],
            'total': buses.total,
            'pages': buses.pages,
            'current_page': page
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/buses', methods=['POST'])
def create_bus():
    try:
        data = request.json
        bus = Bus(
            bus_number=data['bus_number'],
            driver_name=data['driver_name'],
            driver_phone=data['driver_phone'],
            total_seats=data.get('total_seats', 50),
            route=data['route'],
            status='active'
        )
        
        db.session.add(bus)
        db.session.commit()
        
        women_seats = int(bus.total_seats * 0.2)
        for seat_num in range(1, bus.total_seats + 1):
            seat = Seat(
                bus_id=bus.id,
                seat_number=seat_num,
                is_women_seat=(seat_num <= women_seats)
            )
            db.session.add(seat)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Bus created successfully',
            'bus_id': bus.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api.route('/buses/<int:bus_id>/seats', methods=['GET'])
def get_seats(bus_id):
    try:
        seats = Seat.query.filter_by(bus_id=bus_id).all()
        
        return jsonify([{
            'seat_id': seat.id,
            'seat_number': seat.seat_number,
            'is_reserved': seat.is_reserved,
            'is_women_seat': seat.is_women_seat,
            'reserved_by': seat.user.name if seat.user else None
        } for seat in seats]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/seats/<int:seat_id>/reserve', methods=['POST'])
def reserve_seat(seat_id):
    try:
        data = request.json
        user_id = data['user_id']
        
        user = User.query.get(user_id)
        seat = Seat.query.get(seat_id)
        
        if not user or not seat:
            return jsonify({'message': 'User or Seat not found'}), 404
        
        if seat.is_reserved:
            return jsonify({'message': 'Seat already reserved'}), 400
        
        if seat.is_women_seat and user.gender != 'female':
            return jsonify({'message': 'This is a women-only seat'}), 400
        
        seat.is_reserved = True
        seat.reserved_by_user_id = user_id
        seat.reserved_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Seat reserved successfully',
            'seat_number': seat.seat_number
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api.route('/seats/<int:seat_id>/cancel', methods=['POST'])
def cancel_reservation(seat_id):
    try:
        seat = Seat.query.get(seat_id)
        
        if not seat:
            return jsonify({'message': 'Seat not found'}), 404
        
        if not seat.is_reserved:
            return jsonify({'message': 'Seat is not reserved'}), 400
        
        seat.is_reserved = False
        seat.reserved_by_user_id = None
        seat.reserved_at = None
        db.session.commit()
        
        return jsonify({'message': 'Reservation cancelled'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== WALLET ====================

@api.route('/wallet/<int:user_id>', methods=['GET'])
def get_wallet(user_id):
    try:
        wallet = Wallet.query.filter_by(user_id=user_id).first()
        
        if not wallet:
            wallet = Wallet(user_id=user_id, balance=0)
            db.session.add(wallet)
            db.session.commit()
        
        return jsonify({
            'wallet_id': wallet.id,
            'balance': wallet.balance,
            'currency': 'INR'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/wallet/<int:user_id>/add-money', methods=['POST'])
def add_wallet_money(user_id):
    try:
        data = request.json
        amount = data['amount']
        
        wallet = Wallet.query.filter_by(user_id=user_id).first()
        if not wallet:
            wallet = Wallet(user_id=user_id, balance=0)
            db.session.add(wallet)
            db.session.commit()
        
        wallet.balance += amount
        db.session.commit()
        
        return jsonify({
            'message': 'Money added',
            'new_balance': wallet.balance
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== STATISTICS ====================

@api.route('/statistics/dashboard', methods=['GET'])
def get_statistics():
    try:
        stats = {
            'total_users': User.query.count(),
            'total_buses': Bus.query.count(),
            'active_buses': Bus.query.filter_by(status='active').count(),
            'total_bookings': 0,
            'confirmed_bookings': 0,
            'total_revenue': 0,
            'user_stats': {
                'total_users': User.query.count(),
                'passengers': User.query.filter_by(account_type='passenger').count(),
                'drivers': User.query.filter_by(account_type='driver').count(),
                'workers': User.query.filter_by(account_type='worker').count()
            },
            'payment_stats': {
                'total_payments': 0,
                'completed': 0,
                'failed': 0,
                'refunded': 0
            }
        }
        
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500