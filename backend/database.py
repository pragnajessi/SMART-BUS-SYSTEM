from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

db = SQLAlchemy()

# ========== USER MODELS ==========

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(15), nullable=False)
    gender = db.Column(db.String(10), nullable=False)  # male, female, other
    password = db.Column(db.String(255), nullable=False)
    account_type = db.Column(db.String(20), default='passenger')  # passenger, worker, driver, admin
    profile_picture = db.Column(db.String(255), nullable=True)
    
    # Location tracking
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(255), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    bookings = db.relationship('Booking', backref='user', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='user', lazy=True, cascade='all, delete-orphan')
    reserved_seats = db.relationship('Seat', backref='user', lazy=True)
    emergencies = db.relationship('Emergency', backref='user', lazy=True)
    reported_lost_items = db.relationship('LostItem', foreign_keys='LostItem.reported_by_user_id', backref='reported_by_user', lazy=True)
    found_items = db.relationship('LostItem', foreign_keys='LostItem.found_by_worker_id', backref='found_by_worker', lazy=True)
    wakeup_alerts = db.relationship('WakeUpAlert', backref='user', lazy=True, cascade='all, delete-orphan')
    wallet = db.relationship('Wallet', backref='user', uselist=False, cascade='all, delete-orphan')
    admin_profile = db.relationship('AdminUser', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'gender': self.gender,
            'account_type': self.account_type,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }


# ========== BUS MODELS ==========

class Bus(db.Model):
    __tablename__ = 'buses'
    
    id = db.Column(db.Integer, primary_key=True)
    bus_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    driver_name = db.Column(db.String(100), nullable=False)
    driver_phone = db.Column(db.String(15), nullable=False)
    
    # Bus details
    total_seats = db.Column(db.Integer, default=50)
    bus_type = db.Column(db.String(50), default='standard')  # standard, deluxe, ac, sleeper
    registration_number = db.Column(db.String(50), unique=True)
    manufacturer = db.Column(db.String(100), nullable=True)
    model = db.Column(db.String(100), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    
    # Route information
    route = db.Column(db.String(200), nullable=False, index=True)
    route_code = db.Column(db.String(50), nullable=True)
    start_point = db.Column(db.String(100), nullable=False)
    end_point = db.Column(db.String(100), nullable=False)
    
    # GPS Location
    current_lat = db.Column(db.Float, nullable=True)
    current_lng = db.Column(db.Float, nullable=True)
    last_location_update = db.Column(db.DateTime, nullable=True)
    
    # Status
    status = db.Column(db.String(20), default='active')  # active, inactive, maintenance
    is_available = db.Column(db.Boolean, default=True)
    
    # Amenities
    amenities = db.Column(db.JSON, nullable=True)  # wifi, usb_charging, water, etc.
    
    # Ratings
    average_rating = db.Column(db.Float, default=0)
    total_reviews = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    seats = db.relationship('Seat', backref='bus', lazy=True, cascade='all, delete-orphan')
    bookings = db.relationship('Booking', backref='bus', lazy=True, cascade='all, delete-orphan')
    gps_trackers = db.relationship('GPSTracker', backref='bus', lazy=True, cascade='all, delete-orphan')
    route_stops = db.relationship('RouteStop', backref='bus', lazy=True, cascade='all, delete-orphan')
    announcements = db.relationship('Announcement', backref='bus', lazy=True, cascade='all, delete-orphan')
    emergencies = db.relationship('Emergency', backref='bus', lazy=True, cascade='all, delete-orphan')
    wakeup_alerts = db.relationship('WakeUpAlert', backref='bus', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Bus {self.bus_number}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'bus_number': self.bus_number,
            'driver_name': self.driver_name,
            'route': self.route,
            'total_seats': self.total_seats,
            'available_seats': sum(1 for seat in self.seats if not seat.is_reserved),
            'status': self.status,
            'current_lat': self.current_lat,
            'current_lng': self.current_lng
        }


class Seat(db.Model):
    __tablename__ = 'seats'
    
    id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False, index=True)
    seat_number = db.Column(db.Integer, nullable=False)
    
    # Seat properties
    seat_type = db.Column(db.String(50), default='standard')  # standard, window, aisle, wheelchair
    is_reserved = db.Column(db.Boolean, default=False)
    is_women_seat = db.Column(db.Boolean, default=False)
    is_accessible = db.Column(db.Boolean, default=False)
    
    # Reservation info
    reserved_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reserved_at = db.Column(db.DateTime, nullable=True)
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('bus_id', 'seat_number', name='_bus_seat_uc'),)
    
    # Relationships
    bookings = db.relationship('Booking', backref='seat', lazy=True)
    
    def __repr__(self):
        return f'<Seat {self.bus_id}-{self.seat_number}>'
    
    def to_dict(self):
        return {
            'seat_id': self.id,
            'seat_number': self.seat_number,
            'is_reserved': self.is_reserved,
            'is_women_seat': self.is_women_seat,
            'reserved_by': self.user.name if self.user else None
        }


# ========== BOOKING & PAYMENT MODELS ==========

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Booking details
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    seat_id = db.Column(db.Integer, db.ForeignKey('seats.id'), nullable=False)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False, index=True)
    
    # Journey details
    travel_date = db.Column(db.DateTime, nullable=False, index=True)
    journey_start_time = db.Column(db.DateTime, nullable=True)
    journey_end_time = db.Column(db.DateTime, nullable=True)
    
    # Pricing
    price = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0)
    final_price = db.Column(db.Float, nullable=False)
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled, completed
    cancellation_reason = db.Column(db.String(255), nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    booking_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    payments = db.relationship('Payment', backref='booking_ref', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Booking {self.booking_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'bus_number': self.bus.bus_number if self.bus else None,
            'seat_number': self.seat.seat_number if self.seat else None,
            'travel_date': self.travel_date.isoformat(),
            'price': self.final_price,
            'status': self.status
        }


class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    
    # Payment details
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=True)
    
    # Amount
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='INR')
    
    # Payment method
    payment_method = db.Column(db.String(50), nullable=False)  # card, upi, wallet, net_banking
    payment_gateway = db.Column(db.String(50), default='razorpay')  # razorpay, stripe, paypal
    gateway_transaction_id = db.Column(db.String(100), nullable=True)
    
    # Status
    payment_status = db.Column(db.String(20), default='pending')  # pending, completed, failed, refunded
    
    # Payment details (JSON)
    payment_details = db.Column(db.JSON, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    refunds = db.relationship('Refund', backref='payment', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Payment {self.transaction_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'amount': self.amount,
            'payment_method': self.payment_method,
            'status': self.payment_status,
            'created_at': self.created_at.isoformat()
        }


class Refund(db.Model):
    __tablename__ = 'refunds'
    
    id = db.Column(db.Integer, primary_key=True)
    refund_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    
    # Refund details
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=False)
    refund_amount = db.Column(db.Float, nullable=False)
    refund_reason = db.Column(db.String(500), nullable=False)
    
    # Status
    refund_status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    gateway_refund_id = db.Column(db.String(100), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Refund {self.refund_id}>'


class Wallet(db.Model):
    __tablename__ = 'wallets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # Balance
    balance = db.Column(db.Float, default=0)
    total_added = db.Column(db.Float, default=0)
    total_spent = db.Column(db.Float, default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('WalletTransaction', backref='wallet', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Wallet User:{self.user_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'balance': self.balance,
            'currency': 'INR'
        }


class WalletTransaction(db.Model):
    __tablename__ = 'wallet_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'), nullable=False)
    
    # Transaction details
    transaction_type = db.Column(db.String(20), nullable=False)  # credit, debit
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    
    # Balance
    balance_before = db.Column(db.Float, nullable=False)
    balance_after = db.Column(db.Float, nullable=False)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<WalletTransaction {self.transaction_type}>'


# ========== GPS & LOCATION MODELS ==========

class GPSTracker(db.Model):
    __tablename__ = 'gps_trackers'
    
    id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False, index=True)
    
    # Location
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    
    # Movement details
    speed = db.Column(db.Float, default=0)
    heading = db.Column(db.Float, default=0)
    accuracy = db.Column(db.Float, default=0)
    altitude = db.Column(db.Float, default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamp
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<GPSTracker Bus:{self.bus_id}>'
    
    def to_dict(self):
        return {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'speed': self.speed,
            'heading': self.heading,
            'timestamp': self.timestamp.isoformat()
        }


class RouteStop(db.Model):
    __tablename__ = 'route_stops'
    
    id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False, index=True)
    
    # Stop details
    stop_order = db.Column(db.Integer, nullable=False)
    stop_name = db.Column(db.String(200), nullable=False)
    stop_code = db.Column(db.String(50), nullable=True)
    
    # Location
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    
    # Time
    estimated_arrival = db.Column(db.DateTime, nullable=True)
    actual_arrival = db.Column(db.DateTime, nullable=True)
    
    # Status
    is_completed = db.Column(db.Boolean, default=False)
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('bus_id', 'stop_order', name='_bus_stop_order_uc'),)
    
    def __repr__(self):
        return f'<RouteStop {self.stop_name}>'


# ========== ANNOUNCEMENT & ALERT MODELS ==========

class Announcement(db.Model):
    __tablename__ = 'announcements'
    
    id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False, index=True)
    
    # Announcement details
    stop_name = db.Column(db.String(200), nullable=False)
    stop_lat = db.Column(db.Float, nullable=False)
    stop_lng = db.Column(db.Float, nullable=False)
    announcement_text = db.Column(db.String(500), nullable=False)
    
    # Timing
    time_before_arrival = db.Column(db.Integer, default=120)  # seconds
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, announced, completed
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    announced_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Announcement {self.stop_name}>'


class WakeUpAlert(db.Model):
    __tablename__ = 'wakeup_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False, index=True)
    
    # Alert details
    stop_name = db.Column(db.String(200), nullable=False)
    stop_lat = db.Column(db.Float, nullable=False)
    stop_lng = db.Column(db.Float, nullable=False)
    alert_before_time = db.Column(db.Integer, default=120)  # seconds
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    alert_sent_before = db.Column(db.Boolean, default=False)
    alert_sent_after = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<WakeUpAlert User:{self.user_id}>'


# ========== EMERGENCY & LOST & FOUND MODELS ==========

class Emergency(db.Model):
    __tablename__ = 'emergencies'
    
    id = db.Column(db.Integer, primary_key=True)
    emergency_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Emergency details
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    emergency_type = db.Column(db.String(100), nullable=False)  # accident, medical, security, etc.
    
    # Location
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    
    # Details
    description = db.Column(db.String(500), nullable=True)
    severity = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    
    # Status
    status = db.Column(db.String(20), default='active')  # active, resolved
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Emergency {self.emergency_id}>'


class LostItem(db.Model):
    __tablename__ = 'lost_items'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Item details
    item_name = db.Column(db.String(200), nullable=False)
    item_description = db.Column(db.String(500), nullable=False)
    item_image = db.Column(db.String(255), nullable=True)
    item_category = db.Column(db.String(50), nullable=True)  # bag, phone, wallet, document, etc.
    
    # Bus info
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=True)
    
    # Reporting
    reported_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Found info
    found_by_worker_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    location_found = db.Column(db.String(200), nullable=True)
    
    # Status
    item_status = db.Column(db.String(20), default='lost')  # lost, found, claimed
    
    # Timestamps
    report_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    found_date = db.Column(db.DateTime, nullable=True)
    claimed_date = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<LostItem {self.item_name}>'


# ========== ADMIN MODELS ==========

class AdminUser(db.Model):
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Admin details
    role = db.Column(db.String(50), nullable=False)  # super_admin, manager, operator
    permissions = db.Column(db.JSON, nullable=True)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    logs = db.relationship('AdminLog', backref='admin', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<AdminUser {self.role}>'


class AdminLog(db.Model):
    __tablename__ = 'admin_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=False, index=True)
    
    # Action details
    action = db.Column(db.String(100), nullable=False)  # CREATE, UPDATE, DELETE, etc.
    entity_type = db.Column(db.String(50), nullable=False)  # bus, user, payment, etc.
    entity_id = db.Column(db.Integer, nullable=True)
    
    # Changes
    changes = db.Column(db.JSON, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    
    # Timestamp
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<AdminLog {self.action}>'


class SystemReport(db.Model):
    __tablename__ = 'system_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Report details
    report_type = db.Column(db.String(50), nullable=False)  # daily, weekly, monthly
    report_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Statistics
    total_revenue = db.Column(db.Float, default=0)
    total_bookings = db.Column(db.Integer, default=0)
    total_users = db.Column(db.Integer, default=0)
    total_buses = db.Column(db.Integer, default=0)
    active_buses = db.Column(db.Integer, default=0)
    
    # Data
    report_data = db.Column(db.JSON, nullable=True)
    
    def __repr__(self):
        return f'<SystemReport {self.report_type}>'


# ========== REVIEW & RATING MODELS ==========

class BusReview(db.Model):
    __tablename__ = 'bus_reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Review details
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Rating
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    title = db.Column(db.String(200), nullable=False)
    review_text = db.Column(db.String(1000), nullable=False)
    
    # Status
    is_verified = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<BusReview Bus:{self.bus_id}>'


# ========== NOTIFICATION MODEL ==========

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Notification details
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # booking, payment, alert, emergency
    
    # Data
    related_id = db.Column(db.Integer, nullable=True)
    related_type = db.Column(db.String(50), nullable=True)
    
    # Status
    is_read = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    read_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='notifications')
    
    def __repr__(self):
        return f'<Notification {self.notification_type}>'


# ========== PROMO CODE MODEL ==========

class PromoCode(db.Model):
    __tablename__ = 'promo_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Discount details
    discount_type = db.Column(db.String(20), nullable=False)  # percentage, fixed
    discount_value = db.Column(db.Float, nullable=False)
    min_booking_amount = db.Column(db.Float, default=0)
    max_discount = db.Column(db.Float, nullable=True)
    
    # Validity
    valid_from = db.Column(db.DateTime, nullable=False)
    valid_until = db.Column(db.DateTime, nullable=False)
    
    # Limits
    max_uses = db.Column(db.Integer, default=-1)  # -1 for unlimited
    current_uses = db.Column(db.Integer, default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PromoCode {self.code}>'