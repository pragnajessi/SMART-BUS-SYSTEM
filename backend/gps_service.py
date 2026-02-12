import math
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from app import db, app
import json

# GPS Service Blueprint
gps_bp = Blueprint('gps', __name__, url_prefix='/api/gps')

# In-memory storage for real-time GPS data (use Redis in production)
active_buses_gps = {}

class GPSTracker(db.Model):
    __tablename__ = 'gps_trackers'
    id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    speed = db.Column(db.Float, default=0)
    heading = db.Column(db.Float, default=0)
    accuracy = db.Column(db.Float, default=0)
    altitude = db.Column(db.Float, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    bus = db.relationship('Bus', backref='gps_trackers')


class RouteStop(db.Model):
    __tablename__ = 'route_stops'
    id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False)
    stop_order = db.Column(db.Integer, nullable=False)
    stop_name = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    estimated_arrival = db.Column(db.DateTime, nullable=True)
    actual_arrival = db.Column(db.DateTime, nullable=True)
    is_completed = db.Column(db.Boolean, default=False)
    
    bus = db.relationship('Bus', backref='route_stops')


# ========== UTILITY FUNCTIONS ==========

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates using Haversine formula (in km)"""
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


def calculate_bearing(lat1, lon1, lat2, lon2):
    """Calculate bearing between two coordinates"""
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lon = math.radians(lon2 - lon1)
    
    y = math.sin(delta_lon) * math.cos(lat2_rad)
    x = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon)
    
    bearing = math.degrees(math.atan2(y, x))
    return (bearing + 360) % 360


def estimate_arrival_time(current_lat, current_lng, stop_lat, stop_lng, speed_kmh=40):
    """Estimate arrival time based on current position and distance"""
    if speed_kmh == 0:
        return None
    
    distance_km = calculate_distance(current_lat, current_lng, stop_lat, stop_lng)
    hours = distance_km / speed_kmh
    minutes = hours * 60
    
    return minutes


# ========== GPS ROUTES ==========

@gps_bp.route('/buses/<int:bus_id>/location', methods=['GET'])
def get_bus_location(bus_id):
    """Get current location of a bus"""
    try:
        tracker = GPSTracker.query.filter_by(bus_id=bus_id, is_active=True).order_by(
            GPSTracker.timestamp.desc()
        ).first()
        
        if not tracker:
            return jsonify({'message': 'No GPS data available'}), 404
        
        return jsonify({
            'bus_id': bus_id,
            'latitude': tracker.latitude,
            'longitude': tracker.longitude,
            'speed': tracker.speed,
            'heading': tracker.heading,
            'accuracy': tracker.accuracy,
            'altitude': tracker.altitude,
            'timestamp': tracker.timestamp.isoformat()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@gps_bp.route('/buses/<int:bus_id>/location', methods=['POST'])
def update_bus_location(bus_id):
    """Update bus location (called by GPS device/driver app)"""
    try:
        from app import Bus
        
        data = request.json
        bus = Bus.query.get(bus_id)
        
        if not bus:
            return jsonify({'message': 'Bus not found'}), 404
        
        # Create GPS tracker entry
        tracker = GPSTracker(
            bus_id=bus_id,
            latitude=data['latitude'],
            longitude=data['longitude'],
            speed=data.get('speed', 0),
            heading=data.get('heading', 0),
            accuracy=data.get('accuracy', 0),
            altitude=data.get('altitude', 0)
        )
        
        # Update bus location
        bus.current_lat = data['latitude']
        bus.current_lng = data['longitude']
        
        db.session.add(tracker)
        db.session.commit()
        
        # Update in-memory cache
        active_buses_gps[bus_id] = {
            'latitude': data['latitude'],
            'longitude': data['longitude'],
            'speed': data.get('speed', 0),
            'heading': data.get('heading', 0),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify({'message': 'Location updated'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@gps_bp.route('/buses/active/locations', methods=['GET'])
def get_all_active_buses():
    """Get locations of all active buses"""
    try:
        from app import Bus
        
        buses = Bus.query.filter_by(status='active').all()
        result = []
        
        for bus in buses:
            tracker = GPSTracker.query.filter_by(bus_id=bus.id, is_active=True).order_by(
                GPSTracker.timestamp.desc()
            ).first()
            
            if tracker:
                result.append({
                    'bus_id': bus.id,
                    'bus_number': bus.bus_number,
                    'driver_name': bus.driver_name,
                    'route': bus.route,
                    'latitude': tracker.latitude,
                    'longitude': tracker.longitude,
                    'speed': tracker.speed,
                    'heading': tracker.heading,
                    'timestamp': tracker.timestamp.isoformat()
                })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@gps_bp.route('/buses/<int:bus_id>/route-stops', methods=['GET'])
def get_route_stops(bus_id):
    """Get all stops for a bus route"""
    try:
        stops = RouteStop.query.filter_by(bus_id=bus_id).order_by(RouteStop.stop_order).all()
        
        result = []
        for stop in stops:
            result.append({
                'id': stop.id,
                'stop_order': stop.stop_order,
                'stop_name': stop.stop_name,
                'latitude': stop.latitude,
                'longitude': stop.longitude,
                'estimated_arrival': stop.estimated_arrival.isoformat() if stop.estimated_arrival else None,
                'actual_arrival': stop.actual_arrival.isoformat() if stop.actual_arrival else None,
                'is_completed': stop.is_completed
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@gps_bp.route('/buses/<int:bus_id>/route-stops', methods=['POST'])
def create_route_stops(bus_id):
    """Create route stops for a bus"""
    try:
        from app import Bus
        
        bus = Bus.query.get(bus_id)
        if not bus:
            return jsonify({'message': 'Bus not found'}), 404
        
        data = request.json
        stops_data = data.get('stops', [])
        
        # Delete existing stops
        RouteStop.query.filter_by(bus_id=bus_id).delete()
        
        for idx, stop in enumerate(stops_data, 1):
            route_stop = RouteStop(
                bus_id=bus_id,
                stop_order=idx,
                stop_name=stop['stop_name'],
                latitude=stop['latitude'],
                longitude=stop['longitude']
            )
            db.session.add(route_stop)
        
        db.session.commit()
        
        return jsonify({
            'message': f'{len(stops_data)} stops created',
            'stops_count': len(stops_data)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@gps_bp.route('/buses/<int:bus_id>/calculate-eta', methods=['GET'])
def calculate_eta(bus_id):
    """Calculate ETA to next stops"""
    try:
        from app import Bus
        
        bus = Bus.query.get(bus_id)
        if not bus or not bus.current_lat or not bus.current_lng:
            return jsonify({'message': 'Bus not found or GPS data unavailable'}), 404
        
        stops = RouteStop.query.filter_by(bus_id=bus_id, is_completed=False).order_by(
            RouteStop.stop_order
        ).all()
        
        result = []
        for stop in stops:
            distance_km = calculate_distance(
                bus.current_lat, bus.current_lng,
                stop.latitude, stop.longitude
            )
            
            # Assume average speed of 40 km/h if not available
            speed = 40
            eta_minutes = estimate_arrival_time(
                bus.current_lat, bus.current_lng,
                stop.latitude, stop.longitude,
                speed
            )
            
            result.append({
                'stop_id': stop.id,
                'stop_name': stop.stop_name,
                'stop_order': stop.stop_order,
                'distance_km': round(distance_km, 2),
                'eta_minutes': round(eta_minutes) if eta_minutes else None
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@gps_bp.route('/buses/<int:bus_id>/history', methods=['GET'])
def get_gps_history(bus_id):
    """Get GPS history for a bus"""
    try:
        limit = request.args.get('limit', 100, type=int)
        
        trackers = GPSTracker.query.filter_by(bus_id=bus_id).order_by(
            GPSTracker.timestamp.desc()
        ).limit(limit).all()
        
        result = []
        for tracker in reversed(trackers):  # Reverse to get chronological order
            result.append({
                'latitude': tracker.latitude,
                'longitude': tracker.longitude,
                'speed': tracker.speed,
                'heading': tracker.heading,
                'timestamp': tracker.timestamp.isoformat()
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@gps_bp.route('/buses/<int:bus_id>/route-stops/<int:stop_id>/arrive', methods=['POST'])
def mark_stop_arrival(bus_id, stop_id):
    """Mark arrival at a stop"""
    try:
        stop = RouteStop.query.get(stop_id)
        
        if not stop or stop.bus_id != bus_id:
            return jsonify({'message': 'Stop not found'}), 404
        
        stop.actual_arrival = datetime.utcnow()
        stop.is_completed = True
        db.session.commit()
        
        return jsonify({'message': 'Stop arrival recorded'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@gps_bp.route('/buses/<int:bus_id>/nearby-passengers', methods=['GET'])
def get_nearby_passengers(bus_id):
    """Get passengers near the bus (for pickup)"""
    try:
        from app import Bus, User, Seat
        
        bus = Bus.query.get(bus_id)
        if not bus or not bus.current_lat or not bus.current_lng:
            return jsonify({'message': 'Bus not found or GPS data unavailable'}), 404
        
        # Get reserved passengers
        reserved_seats = Seat.query.filter_by(bus_id=bus_id, is_reserved=True).all()
        
        result = []
        for seat in reserved_seats:
            if seat.user:
                distance_km = calculate_distance(
                    bus.current_lat, bus.current_lng,
                    seat.user.latitude if hasattr(seat.user, 'latitude') else 0,
                    seat.user.longitude if hasattr(seat.user, 'longitude') else 0
                )
                
                if distance_km < 1:  # Within 1 km
                    result.append({
                        'user_id': seat.user.id,
                        'name': seat.user.name,
                        'phone': seat.user.phone,
                        'seat_number': seat.seat_number,
                        'distance_km': round(distance_km, 2)
                    })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500