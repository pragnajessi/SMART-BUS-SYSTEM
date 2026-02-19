import random
from datetime import datetime
from flask import Blueprint, request, jsonify
from database import db, User, Bus, Seat, Wallet

# 1. INITIALIZE BLUEPRINT FIRST (Fixes the NameError)
api = Blueprint('api', __name__)

# ==================== GPS & TRACKING ====================

@api.route('/bus/location/<int:bus_id>', methods=['GET'])
def get_bus_location(bus_id):
    try:
        bus = Bus.query.get(bus_id)
        if not bus:
            return jsonify({'error': 'Bus not found'}), 404

        # DEVELOPMENT MOCK: Generate coordinates near Delhi to test map/voice
        mock_lat = 28.6139 + (random.uniform(-0.01, 0.01))
        mock_lng = 77.2090 + (random.uniform(-0.01, 0.01))

        return jsonify({
            'bus_id': bus_id,
            'bus_number': bus.bus_number,
            'latitude': mock_lat,
            'longitude': mock_lng,
            'last_updated': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
        
        return jsonify({'message': 'Registration successful', 'user_id': user.id}), 201
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
                'account_type': user.account_type
            }), 200
        return jsonify({'message': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== BUSES & SEATS ====================

@api.route('/buses', methods=['GET'])
def get_buses():
    try:
        buses = Bus.query.filter_by(status='active').all()
        return jsonify({
            'buses': [{
                'id': b.id,
                'bus_number': b.bus_number,
                'route': b.route,
                'available_seats': sum(1 for s in b.seats if not s.is_reserved)
            } for b in buses]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/seats/<int:seat_id>/reserve', methods=['POST'])
def reserve_seat(seat_id):
    try:
        data = request.json
        user = User.query.get(data['user_id'])
        seat = Seat.query.get(seat_id)
        
        if not user or not seat:
            return jsonify({'message': 'Not found'}), 404
        if seat.is_reserved:
            return jsonify({'message': 'Already reserved'}), 400
        if seat.is_women_seat and user.gender != 'female':
            return jsonify({'message': 'Women-only seat'}), 400
        
        seat.is_reserved = True
        seat.reserved_by_user_id = user.id
        db.session.commit()
        return jsonify({'message': 'Reserved successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== WALLET & STATS ====================

@api.route('/wallet/<int:user_id>', methods=['GET'])
def get_wallet(user_id):
    wallet = Wallet.query.filter_by(user_id=user_id).first()
    if not wallet:
        wallet = Wallet(user_id=user_id, balance=0)
        db.session.add(wallet)
        db.session.commit()
    return jsonify({'balance': wallet.balance}), 200

@api.route('/statistics/dashboard', methods=['GET'])
def get_statistics():
    confirmed = Seat.query.filter_by(is_reserved=True).count()
    return jsonify({
        'total_users': User.query.count(),
        'total_buses': Bus.query.count(),
        'total_bookings': confirmed,
        'total_revenue': confirmed * 250
    }), 200
