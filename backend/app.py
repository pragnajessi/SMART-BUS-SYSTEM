from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import threading
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv()

app = Flask(__name__)
CORS(app)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smart_bus.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==================== DATABASE MODELS ====================

class Bus(db.Model):
    __tablename__ = 'buses'
    id = db.Column(db.Integer, primary_key=True)
    bus_number = db.Column(db.String(50), unique=True, nullable=False)
    driver_name = db.Column(db.String(100), nullable=False)
    driver_phone = db.Column(db.String(15), nullable=False)
    total_seats = db.Column(db.Integer, default=50)
    current_lat = db.Column(db.Float, nullable=True)
    current_lng = db.Column(db.Float, nullable=True)
    route = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='active')  # active, inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    seats = db.relationship('Seat', backref='bus', lazy=True, cascade='all, delete-orphan')
    announcements = db.relationship('Announcement', backref='bus', lazy=True)
    emergencies = db.relationship('Emergency', backref='bus', lazy=True)


class Seat(db.Model):
    __tablename__ = 'seats'
    id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False)
    seat_number = db.Column(db.Integer, nullable=False)
    is_reserved = db.Column(db.Boolean, default=False)
    is_women_seat = db.Column(db.Boolean, default=False)
    reserved_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reserved_at = db.Column(db.DateTime, nullable=True)
    
    __table_args__ = (db.UniqueConstraint('bus_id', 'seat_number', name='_bus_seat_uc'),)
    
    user = db.relationship('User', backref='reserved_seats')


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    gender = db.Column(db.String(10), nullable=False)  # male, female, other
    password = db.Column(db.String(200), nullable=False)
    account_type = db.Column(db.String(20), default='passenger')  # passenger, worker, driver
    profile_picture = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Announcement(db.Model):
    __tablename__ = 'announcements'
    id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False)
    stop_name = db.Column(db.String(200), nullable=False)
    stop_lat = db.Column(db.Float, nullable=False)
    stop_lng = db.Column(db.Float, nullable=False)
    announcement_text = db.Column(db.String(500), nullable=False)
    time_before_arrival = db.Column(db.Integer, default=120)  # seconds (2 minutes)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, announced, completed


class WakeUpAlert(db.Model):
    __tablename__ = 'wakeup_alerts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False)
    stop_name = db.Column(db.String(200), nullable=False)
    stop_lat = db.Column(db.Float, nullable=False)
    stop_lng = db.Column(db.Float, nullable=False)
    alert_before_time = db.Column(db.Integer, default=120)  # seconds (2 minutes)
    is_active = db.Column(db.Boolean, default=True)
    alert_sent_before = db.Column(db.Boolean, default=False)
    alert_sent_after = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='wakeup_alerts')
    bus = db.relationship('Bus', backref='wakeup_alerts')


class Emergency(db.Model):
    __tablename__ = 'emergencies'
    id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    emergency_type = db.Column(db.String(100), nullable=False)  # accident, medical, security, etc.
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(20), default='active')  # active, resolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    user = db.relationship('User', backref='emergencies')


class LostItem(db.Model):
    __tablename__ = 'lost_items'
    id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=True)
    item_name = db.Column(db.String(200), nullable=False)
    item_description = db.Column(db.String(500), nullable=False)
    item_image = db.Column(db.String(200), nullable=True)
    reported_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    found_by_worker_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    location_found = db.Column(db.String(200), nullable=True)
    item_status = db.Column(db.String(20), default='lost')  # lost, found, claimed
    report_date = db.Column(db.DateTime, default=datetime.utcnow)
    found_date = db.Column(db.DateTime, nullable=True)
    claimed_date = db.Column(db.DateTime, nullable=True)
    
    reported_by_user = db.relationship('User', foreign_keys=[reported_by_user_id], backref='reported_lost_items')
    found_by_worker = db.relationship('User', foreign_keys=[found_by_worker_id], backref='found_items')


# ==================== ROUTES: AUTHENTICATION ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.json
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already registered'}), 400
        
        # Create new user
        user = User(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            gender=data['gender'],
            password=data['password'],  # In production, hash this!
            account_type=data.get('account_type', 'passenger')
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'Registration successful',
            'user_id': user.id,
            'name': user.name
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.json
        user = User.query.filter_by(email=data['email']).first()
        
        if user and user.password == data['password']:  # In production, use proper hashing!
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


# ==================== ROUTES: BUS MANAGEMENT ====================

@app.route('/api/buses', methods=['GET'])
def get_buses():
    try:
        buses = Bus.query.filter_by(status='active').all()
        return jsonify([{
            'id': bus.id,
            'bus_number': bus.bus_number,
            'driver_name': bus.driver_name,
            'route': bus.route,
            'total_seats': bus.total_seats,
            'available_seats': sum(1 for seat in bus.seats if not seat.is_reserved),
            'current_lat': bus.current_lat,
            'current_lng': bus.current_lng
        } for bus in buses]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/buses', methods=['POST'])
def create_bus():
    try:
        data = request.json
        bus = Bus(
            bus_number=data['bus_number'],
            driver_name=data['driver_name'],
            driver_phone=data['driver_phone'],
            total_seats=data.get('total_seats', 50),
            route=data['route']
        )
        
        db.session.add(bus)
        db.session.commit()
        
        # Create seats for the bus
        women_seats = int(bus.total_seats * 0.2)  # 20% women seats
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


@app.route('/api/buses/<int:bus_id>/update-location', methods=['POST'])
def update_bus_location(bus_id):
    try:
        data = request.json
        bus = Bus.query.get(bus_id)
        
        if not bus:
            return jsonify({'message': 'Bus not found'}), 404
        
        bus.current_lat = data['latitude']
        bus.current_lng = data['longitude']
        db.session.commit()
        
        return jsonify({'message': 'Location updated'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== ROUTES: SEAT RESERVATION ====================

@app.route('/api/buses/<int:bus_id>/seats', methods=['GET'])
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


@app.route('/api/seats/<int:seat_id>/reserve', methods=['POST'])
def reserve_seat(seat_id):
    try:
        data = request.json
        user_id = data['user_id']
        
        # Get user and seat
        user = User.query.get(user_id)
        seat = Seat.query.get(seat_id)
        
        if not user or not seat:
            return jsonify({'message': 'User or Seat not found'}), 404
        
        if seat.is_reserved:
            return jsonify({'message': 'Seat already reserved'}), 400
        
        # Women seat security check
        if seat.is_women_seat and user.gender != 'female':
            return jsonify({'message': 'This is a women-only seat'}), 400
        
        # Reserve the seat
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


@app.route('/api/seats/<int:seat_id>/cancel', methods=['POST'])
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


# ==================== ROUTES: ANNOUNCEMENTS ====================

@app.route('/api/buses/<int:bus_id>/announcements', methods=['GET'])
def get_announcements(bus_id):
    try:
        announcements = Announcement.query.filter_by(bus_id=bus_id).all()
        
        return jsonify([{
            'id': ann.id,
            'stop_name': ann.stop_name,
            'announcement_text': ann.announcement_text,
            'status': ann.status
        } for ann in announcements]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/buses/<int:bus_id>/announcements', methods=['POST'])
def create_announcement(bus_id):
    try:
        data = request.json
        bus = Bus.query.get(bus_id)
        
        if not bus:
            return jsonify({'message': 'Bus not found'}), 404
        
        announcement = Announcement(
            bus_id=bus_id,
            stop_name=data['stop_name'],
            stop_lat=data['stop_lat'],
            stop_lng=data['stop_lng'],
            announcement_text=data['announcement_text'],
            time_before_arrival=data.get('time_before_arrival', 120)
        )
        
        db.session.add(announcement)
        db.session.commit()
        
        return jsonify({
            'message': 'Announcement created',
            'announcement_id': announcement.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== ROUTES: WAKE-UP ALERTS ====================

@app.route('/api/wakeup-alerts', methods=['POST'])
def create_wakeup_alert():
    try:
        data = request.json
        
        alert = WakeUpAlert(
            user_id=data['user_id'],
            bus_id=data['bus_id'],
            stop_name=data['stop_name'],
            stop_lat=data['stop_lat'],
            stop_lng=data['stop_lng'],
            alert_before_time=data.get('alert_before_time', 120)
        )
        
        db.session.add(alert)
        db.session.commit()
        
        return jsonify({
            'message': 'Wake-up alert created',
            'alert_id': alert.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/users/<int:user_id>/wakeup-alerts', methods=['GET'])
def get_user_wakeup_alerts(user_id):
    try:
        alerts = WakeUpAlert.query.filter_by(user_id=user_id, is_active=True).all()
        
        return jsonify([{
            'id': alert.id,
            'stop_name': alert.stop_name,
            'alert_before_time': alert.alert_before_time,
            'bus_id': alert.bus_id
        } for alert in alerts]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== ROUTES: EMERGENCY ====================

@app.route('/api/emergencies', methods=['POST'])
def report_emergency():
    try:
        data = request.json
        
        emergency = Emergency(
            bus_id=data['bus_id'],
            user_id=data.get('user_id'),
            emergency_type=data['emergency_type'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            description=data.get('description')
        )
        
        db.session.add(emergency)
        db.session.commit()
        
        # In production, send alerts to authorities/driver
        bus = Bus.query.get(data['bus_id'])
        print(f"EMERGENCY ALERT: {data['emergency_type']} on Bus {bus.bus_number} at ({data['latitude']}, {data['longitude']})")
        
        return jsonify({
            'message': 'Emergency reported',
            'emergency_id': emergency.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/emergencies/<int:emergency_id>/resolve', methods=['POST'])
def resolve_emergency(emergency_id):
    try:
        emergency = Emergency.query.get(emergency_id)
        
        if not emergency:
            return jsonify({'message': 'Emergency not found'}), 404
        
        emergency.status = 'resolved'
        emergency.resolved_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Emergency resolved'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/emergencies', methods=['GET'])
def get_emergencies():
    try:
        emergencies = Emergency.query.filter_by(status='active').all()
        
        return jsonify([{
            'id': emergency.id,
            'bus_id': emergency.bus_id,
            'emergency_type': emergency.emergency_type,
            'latitude': emergency.latitude,
            'longitude': emergency.longitude,
            'description': emergency.description,
            'created_at': emergency.created_at.isoformat()
        } for emergency in emergencies]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== ROUTES: LOST & FOUND ====================

@app.route('/api/lost-items', methods=['POST'])
def report_lost_item():
    try:
        data = request.json
        
        item = LostItem(
            bus_id=data.get('bus_id'),
            item_name=data['item_name'],
            item_description=data['item_description'],
            reported_by_user_id=data['user_id'],
            item_image=data.get('item_image')
        )
        
        db.session.add(item)
        db.session.commit()
        
        # Notify workers
        print(f"LOST ITEM ALERT: {data['item_name']} - {data['item_description']}")
        
        return jsonify({
            'message': 'Lost item reported',
            'item_id': item.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/lost-items', methods=['GET'])
def get_lost_items():
    try:
        status = request.args.get('status', 'lost')
        items = LostItem.query.filter_by(item_status=status).all()
        
        return jsonify([{
            'id': item.id,
            'item_name': item.item_name,
            'item_description': item.item_description,
            'item_image': item.item_image,
            'item_status': item.item_status,
            'reported_by': item.reported_by_user.name,
            'report_date': item.report_date.isoformat(),
            'found_by': item.found_by_worker.name if item.found_by_worker else None
        } for item in items]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/lost-items/<int:item_id>/mark-found', methods=['POST'])
def mark_item_found(item_id):
    try:
        data = request.json
        item = LostItem.query.get(item_id)
        
        if not item:
            return jsonify({'message': 'Item not found'}), 404
        
        item.item_status = 'found'
        item.found_by_worker_id = data['worker_id']
        item.location_found = data['location_found']
        item.found_date = datetime.utcnow()
        db.session.commit()
        
        # Notify the person who reported it
        print(f"Item {item.item_name} found! Notifying {item.reported_by_user.name}")
        
        return jsonify({'message': 'Item marked as found'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/lost-items/<int:item_id>/claim', methods=['POST'])
def claim_lost_item(item_id):
    try:
        item = LostItem.query.get(item_id)
        
        if not item:
            return jsonify({'message': 'Item not found'}), 404
        
        item.item_status = 'claimed'
        item.claimed_date = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Item claimed successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Route not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500


# ==================== DATABASE INITIALIZATION ====================

def init_db():
    with app.app_context():
        db.create_all()
        print("Database initialized!")


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)