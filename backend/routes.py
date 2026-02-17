"""
API Routes Module
Contains all API endpoints that use database operations from database_operations.py
Add new routes here and use the Operation classes
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta, date
from database import db, Seat
from database_operations import (
    BusOperations, BookingOperations, WalletOperations,
    GPSOperations, StatisticsOperations
)

# Create blueprint
api = Blueprint('api', __name__, url_prefix='/api')

# ==================== BUS ROUTES ====================

@api.route('/buses', methods=['GET'])
def get_buses():
    """
    Get all buses with pagination
    Query params: page (default 1), per_page (default 10)
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        buses_page = BusOperations.get_all_buses(page=page, per_page=per_page)
        
        return jsonify({
            'buses': [{
                'id': bus.id,
                'bus_number': bus.bus_number,
                'driver_name': bus.driver_name,
                'route': bus.route,
                'total_seats': bus.total_seats,
                'available_seats': len(BusOperations.get_available_seats(bus.id)),
                'occupancy': round(BusOperations.get_bus_occupancy(bus.id), 2)
            } for bus in buses_page.items],
            'total': buses_page.total,
            'pages': buses_page.pages,
            'current_page': page
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/buses', methods=['POST'])
def create_bus():
    """
    Create new bus
    Body: {
        "bus_number": "BUS001",
        "driver_name": "John Doe",
        "driver_phone": "9876543210",
        "route": "Delhi-Jaipur",
        "total_seats": 50
    }
    """

    data = request.json
    bus, error = BusOperations.create_bus(
        bus_number=data['bus_number'],
        driver_name=data['driver_name'],
        driver_phone=data['driver_phone'],
        route=data['route'],
        total_seats=data.get('total_seats', 50)
    )
    if error:
        return jsonify({'error': error}), 500
    return jsonify({'bus_id': bus.id}), 201

        
# Use BusOperations to create bus
@api.route('/buses', methods=['POST'])
def create_bus():
    """
    Create new bus
    Body: {
        "bus_number": "BUS001",
        "driver_name": "John Doe",
        "driver_phone": "9876543210",
        "route": "Delhi-Jaipur",
        "total_seats": 50
    }
    """
    try:
        data = request.json
        
        # Use BusOperations to create bus
        bus, error = BusOperations.create_bus(
            bus_number=data['bus_number'],
            driver_name=data['driver_name'],
            driver_phone=data['driver_phone'],
            route=data['route'],
            total_seats=data.get('total_seats', 50)
        )
        
        if error:
            return jsonify({'error': error}), 500
        
        return jsonify({
            'message': 'Bus created successfully',
            'bus_id': bus.id,
            'bus_number': bus.bus_number,
            'total_seats': bus.total_seats
        }), 201
    except KeyError as e:
        return jsonify({'error': f'Missing field: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/buses/<int:bus_id>/update-location', methods=['POST'])
def update_bus_location(bus_id):
    """
    Update bus GPS location
    Body: {
        "latitude": 28.6139,
        "longitude": 77.2090
    }
    """
    try:
        data = request.json
        
        bus, error = BusOperations.update_bus_location(
            bus_id=bus_id,
            latitude=data['latitude'],
            longitude=data['longitude']
        )
        
        if error:
            return jsonify({'error': error}), 404 if 'not found' in error else 500
        
        return jsonify({'message': 'Location updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== BOOKING ROUTES ====================

@api.route('/bookings', methods=['POST'])
def create_booking():
    """
    Create new booking
    Body: {
        "user_id": 1,
        "bus_id": 1,
        "seat_id": 5,
        "travel_date": "2026-02-15",
        "price": 250
    }
    """
    try:
        data = request.json
        
        # Use BookingOperations to create booking
        booking, error = BookingOperations.create_booking(
            user_id=data['user_id'],
            bus_id=data['bus_id'],
            seat_id=data['seat_id'],
            travel_date=datetime.fromisoformat(data['travel_date']),
            price=data['price']
        )
        
        if error:
            return jsonify({'error': error}), 500
        
        # Reserve the seat
        seat = Seat.query.get(data['seat_id'])
        if seat:
            seat.is_reserved = True
            seat.reserved_by_user_id = data['user_id']
            seat.reserved_at = datetime.utcnow()
            db.session.commit()
        
        return jsonify({
            'message': 'Booking created',
            'booking_id': booking.id,
            'booking_ref': booking.booking_id,
            'status': booking.status
        }), 201
    except KeyError as e:
        return jsonify({'error': f'Missing field: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/bookings/<int:booking_id>/confirm', methods=['POST'])
def confirm_booking(booking_id):
    """Confirm a booking"""
    try:
        booking, error = BookingOperations.confirm_booking(booking_id)
        
        if error:
            return jsonify({'error': error}), 404 if 'not found' in error else 500
        
        return jsonify({
            'message': 'Booking confirmed',
            'booking_ref': booking.booking_id,
            'status': booking.status
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/bookings/<int:booking_id>/cancel', methods=['POST'])
def cancel_booking(booking_id):
    """Cancel a booking"""
    try:
        data = request.json
        reason = data.get('reason', 'User requested cancellation')
        
        booking, error = BookingOperations.cancel_booking(booking_id, reason)
        
        if error:
            return jsonify({'error': error}), 404 if 'not found' in error else 500
        
        return jsonify({
            'message': 'Booking cancelled',
            'booking_ref': booking.booking_id,
            'status': booking.status
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== WALLET ROUTES ====================

@api.route('/wallet/<int:user_id>', methods=['GET'])
def get_wallet(user_id):
    """Get user wallet details"""
    try:
        wallet = WalletOperations.get_wallet(user_id)
        
        return jsonify({
            'wallet_id': wallet.id,
            'user_id': user_id,
            'balance': wallet.balance,
            'total_added': wallet.total_added,
            'total_spent': wallet.total_spent,
            'currency': 'INR'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/wallet/<int:user_id>/add-money', methods=['POST'])
def add_wallet_money(user_id):
    """
    Add money to wallet
    Body: {
        "amount": 1000,
        "description": "Initial topup"
    }
    """
    try:
        data = request.json
        amount = data['amount']
        description = data.get('description', 'Money added to wallet')
        
        # Use WalletOperations to add balance
        wallet, error = WalletOperations.add_balance(
            user_id=user_id,
            amount=amount,
            description=description
        )
        
        if error:
            return jsonify({'error': error}), 500
        
        return jsonify({
            'message': 'Money added to wallet',
            'new_balance': wallet.balance,
            'amount_added': amount,
            'currency': 'INR'
        }), 200
    except KeyError as e:
        return jsonify({'error': f'Missing field: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/wallet/<int:user_id>/transactions', methods=['GET'])
def get_wallet_transactions(user_id):
    """Get wallet transaction history"""
    try:
        limit = request.args.get('limit', 20, type=int)
        
        transactions = WalletOperations.get_wallet_transactions(user_id, limit=limit)
        
        return jsonify([{
            'id': t.id,
            'type': t.transaction_type,
            'amount': t.amount,
            'description': t.description,
            'balance_before': t.balance_before,
            'balance_after': t.balance_after,
            'date': t.created_at.isoformat()
        } for t in transactions]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== GPS ROUTES ====================

@api.route('/gps/buses/<int:bus_id>/log', methods=['POST'])
def log_gps(bus_id):
    """
    Log GPS position for a bus
    Body: {
        "latitude": 28.6139,
        "longitude": 77.2090,
        "speed": 40,
        "heading": 90
    }
    """
    try:
        data = request.json
        
        # Use GPSOperations to log position
        gps, error = GPSOperations.log_gps(
            bus_id=bus_id,
            latitude=data['latitude'],
            longitude=data['longitude'],
            speed=data.get('speed', 0),
            heading=data.get('heading', 0),
            accuracy=data.get('accuracy', 0),
            altitude=data.get('altitude', 0)
        )
        
        if error:
            return jsonify({'error': error}), 500
        
        return jsonify({
            'message': 'GPS logged',
            'latitude': gps.latitude,
            'longitude': gps.longitude,
            'timestamp': gps.timestamp.isoformat()
        }), 200
    except KeyError as e:
        return jsonify({'error': f'Missing field: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/gps/buses/<int:bus_id>/latest', methods=['GET'])
def get_latest_gps(bus_id):
    """Get latest GPS position for a bus"""
    try:
        gps = GPSOperations.get_latest_gps(bus_id)
        
        if not gps:
            return jsonify({'message': 'No GPS data available'}), 404
        
        return jsonify({
            'bus_id': bus_id,
            'latitude': gps.latitude,
            'longitude': gps.longitude,
            'speed': gps.speed,
            'heading': gps.heading,
            'timestamp': gps.timestamp.isoformat()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/gps/buses/<int:bus_id>/history', methods=['GET'])
def get_gps_history(bus_id):
    """
    Get GPS history for a bus
    Query params: hours (default 24)
    """
    try:
        hours = request.args.get('hours', 24, type=int)
        
        history = GPSOperations.get_gps_history(bus_id, hours=hours)
        
        return jsonify([{
            'latitude': gps.latitude,
            'longitude': gps.longitude,
            'speed': gps.speed,
            'heading': gps.heading,
            'timestamp': gps.timestamp.isoformat()
        } for gps in history]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== STATISTICS ROUTES ====================

@api.route('/statistics/dashboard', methods=['GET'])
def get_statistics():
    """
    Get dashboard statistics
    
    Returns all key metrics for dashboard display
    """
    try:
        stats = StatisticsOperations.get_dashboard_stats()
        
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/statistics/revenue', methods=['GET'])
def get_revenue():
    """
    Get revenue statistics
    Query params: date (optional, format: YYYY-MM-DD)
    """
    try:
        date_str = request.args.get('date')
        
        if date_str:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            daily_revenue = StatisticsOperations.get_daily_revenue(target_date)
            return jsonify({
                'date': target_date.isoformat(),
                'daily_revenue': daily_revenue,
                'currency': 'INR'
            }), 200
        else:
            total_revenue = StatisticsOperations.get_total_revenue()
            return jsonify({
                'total_revenue': total_revenue,
                'currency': 'INR'
            }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/statistics/routes', methods=['GET'])
def get_route_stats():
    """Get statistics for busiest routes"""
    try:
        routes = StatisticsOperations.get_busiest_routes()
        
        return jsonify([{
            'route': route[0],
            'bookings': route[1]
        } for route in routes]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500