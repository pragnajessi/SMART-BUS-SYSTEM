from flask import Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from app import db, app
from functools import wraps

# Admin Service Blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

class AdminUser(db.Model):
    __tablename__ = 'admin_users'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # super_admin, manager, operator
    permissions = db.Column(db.JSON, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='admin_profile')


class AdminLog(db.Model):
    __tablename__ = 'admin_logs'
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)  # bus, user, payment, etc.
    entity_id = db.Column(db.Integer, nullable=True)
    changes = db.Column(db.JSON, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    admin = db.relationship('AdminUser', backref='logs')


class SystemReport(db.Model):
    __tablename__ = 'system_reports'
    id = db.Column(db.Integer, primary_key=True)
    report_type = db.Column(db.String(50), nullable=False)  # daily, weekly, monthly
    report_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_revenue = db.Column(db.Float, default=0)
    total_bookings = db.Column(db.Integer, default=0)
    total_users = db.Column(db.Integer, default=0)
    total_buses = db.Column(db.Integer, default=0)
    active_buses = db.Column(db.Integer, default=0)
    report_data = db.Column(db.JSON, nullable=True)


# ========== AUTHENTICATION DECORATOR ==========

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = request.headers.get('X-User-Id')
        if not user_id:
            return jsonify({'message': 'Unauthorized'}), 401
        
        admin = AdminUser.query.filter_by(user_id=int(user_id), is_active=True).first()
        if not admin:
            return jsonify({'message': 'Admin access required'}), 403
        
        return f(*args, admin=admin, **kwargs)
    return decorated


# ========== ADMIN ROUTES ==========

@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def get_dashboard(admin=None):
    """Get admin dashboard data"""
    try:
        from app import Bus, User, Seat
        from payment_service import Payment, Booking
        
        # Statistics
        total_buses = Bus.query.count()
        active_buses = Bus.query.filter_by(status='active').count()
        total_users = User.query.count()
        total_seats = Seat.query.count()
        reserved_seats = Seat.query.filter_by(is_reserved=True).count()
        
        # Revenue
        today = datetime.utcnow().date()
        today_payments = Payment.query.filter(
            db.func.date(Payment.created_at) == today,
            Payment.payment_status == 'completed'
        ).all()
        
        today_revenue = sum(p.amount for p in today_payments)
        total_revenue = sum(p.amount for p in Payment.query.filter_by(payment_status='completed').all())
        
        # Bookings
        today_bookings = Booking.query.filter(
            db.func.date(Booking.booking_date) == today
        ).count()
        
        total_bookings = Booking.query.count()
        confirmed_bookings = Booking.query.filter_by(status='confirmed').count()
        
        return jsonify({
            'buses': {
                'total': total_buses,
                'active': active_buses,
                'inactive': total_buses - active_buses
            },
            'users': {
                'total': total_users
            },
            'seats': {
                'total': total_seats,
                'reserved': reserved_seats,
                'available': total_seats - reserved_seats
            },
            'revenue': {
                'today': today_revenue,
                'total': total_revenue,
                'currency': 'INR'
            },
            'bookings': {
                'today': today_bookings,
                'total': total_bookings,
                'confirmed': confirmed_bookings
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/buses/manage', methods=['GET'])
@admin_required
def get_all_buses(admin=None):
    """Get all buses for management"""
    try:
        from app import Bus
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        buses = Bus.query.paginate(page=page, per_page=per_page)
        
        result = []
        for bus in buses.items:
            reserved_seats = sum(1 for seat in bus.seats if seat.is_reserved)
            result.append({
                'id': bus.id,
                'bus_number': bus.bus_number,
                'driver_name': bus.driver_name,
                'driver_phone': bus.driver_phone,
                'route': bus.route,
                'total_seats': bus.total_seats,
                'reserved_seats': reserved_seats,
                'available_seats': bus.total_seats - reserved_seats,
                'status': bus.status,
                'current_location': {
                    'latitude': bus.current_lat,
                    'longitude': bus.current_lng
                },
                'created_at': bus.created_at.isoformat()
            })
        
        return jsonify({
            'buses': result,
            'total': buses.total,
            'pages': buses.pages,
            'current_page': page
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/buses/<int:bus_id>/status', methods=['PUT'])
@admin_required
def update_bus_status(bus_id, admin=None):
    """Update bus status (active/inactive)"""
    try:
        from app import Bus
        
        data = request.json
        bus = Bus.query.get(bus_id)
        
        if not bus:
            return jsonify({'message': 'Bus not found'}), 404
        
        old_status = bus.status
        bus.status = data['status']
        
        # Log action
        log = AdminLog(
            admin_id=admin.id,
            action='UPDATE_STATUS',
            entity_type='bus',
            entity_id=bus_id,
            changes={'old_status': old_status, 'new_status': bus.status}
        )
        
        db.session.add(log)
        db.session.commit()
        
        return jsonify({'message': 'Bus status updated'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/users/manage', methods=['GET'])
@admin_required
def get_all_users(admin=None):
    """Get all users for management"""
    try:
        from app import User
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        users = User.query.paginate(page=page, per_page=per_page)
        
        result = []
        for user in users.items:
            result.append({
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'gender': user.gender,
                'account_type': user.account_type,
                'bookings': len(user.bookings) if hasattr(user, 'bookings') else 0,
                'created_at': user.created_at.isoformat()
            })
        
        return jsonify({
            'users': result,
            'total': users.total,
            'pages': users.pages,
            'current_page': page
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/payments/manage', methods=['GET'])
@admin_required
def get_all_payments(admin=None):
    """Get all payments for management"""
    try:
        from payment_service import Payment
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        
        query = Payment.query
        if status:
            query = query.filter_by(payment_status=status)
        
        payments = query.order_by(Payment.created_at.desc()).paginate(page=page, per_page=per_page)
        
        result = []
        for payment in payments.items:
            result.append({
                'id': payment.id,
                'transaction_id': payment.transaction_id,
                'user_id': payment.user_id,
                'user_name': payment.user.name if payment.user else None,
                'booking_id': payment.booking_id,
                'amount': payment.amount,
                'currency': payment.currency,
                'payment_method': payment.payment_method,
                'payment_status': payment.payment_status,
                'gateway': payment.payment_gateway,
                'created_at': payment.created_at.isoformat()
            })
        
        return jsonify({
            'payments': result,
            'total': payments.total,
            'pages': payments.pages,
            'current_page': page
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/analytics/revenue', methods=['GET'])
@admin_required
def get_revenue_analytics(admin=None):
    """Get revenue analytics"""
    try:
        from payment_service import Payment
        
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        payments = Payment.query.filter(
            Payment.created_at >= start_date,
            Payment.payment_status == 'completed'
        ).all()
        
        # Group by date
        revenue_by_date = {}
        for payment in payments:
            date_key = payment.created_at.date().isoformat()
            if date_key not in revenue_by_date:
                revenue_by_date[date_key] = 0
            revenue_by_date[date_key] += payment.amount
        
        # Get payment method breakdown
        method_breakdown = {}
        for payment in payments:
            method = payment.payment_method
            if method not in method_breakdown:
                method_breakdown[method] = 0
            method_breakdown[method] += payment.amount
        
        total_revenue = sum(p.amount for p in payments)
        
        return jsonify({
            'total_revenue': total_revenue,
            'period_days': days,
            'revenue_by_date': revenue_by_date,
            'revenue_by_method': method_breakdown,
            'total_transactions': len(payments),
            'average_transaction': total_revenue / len(payments) if payments else 0
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/analytics/bookings', methods=['GET'])
@admin_required
def get_booking_analytics(admin=None):
    """Get booking analytics"""
    try:
        from payment_service import Booking
        
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        bookings = Booking.query.filter(Booking.booking_date >= start_date).all()
        
        # Status breakdown
        status_breakdown = {}
        for booking in bookings:
            status = booking.status
            if status not in status_breakdown:
                status_breakdown[status] = 0
            status_breakdown[status] += 1
        
        return jsonify({
            'total_bookings': len(bookings),
            'status_breakdown': status_breakdown,
            'period_days': days
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/reports/daily', methods=['POST'])
@admin_required
def generate_daily_report(admin=None):
    """Generate daily report"""
    try:
        from app import Bus, User
        from payment_service import Payment, Booking
        
        today = datetime.utcnow().date()
        
        # Collect data
        total_revenue = sum(p.amount for p in Payment.query.filter(
            db.func.date(Payment.created_at) == today,
            Payment.payment_status == 'completed'
        ).all())
        
        total_bookings = Booking.query.filter(
            db.func.date(Booking.booking_date) == today
        ).count()
        
        total_users = User.query.count()
        total_buses = Bus.query.count()
        active_buses = Bus.query.filter_by(status='active').count()
        
        # Create report
        report = SystemReport(
            report_type='daily',
            report_date=datetime.utcnow(),
            total_revenue=total_revenue,
            total_bookings=total_bookings,
            total_users=total_users,
            total_buses=total_buses,
            active_buses=active_buses,
            report_data={
                'date': today.isoformat(),
                'generated_at': datetime.utcnow().isoformat()
            }
        )
        
        db.session.add(report)
        db.session.commit()
        
        return jsonify({
            'message': 'Daily report generated',
            'report_id': report.id,
            'data': {
                'total_revenue': total_revenue,
                'total_bookings': total_bookings,
                'total_users': total_users,
                'total_buses': total_buses,
                'active_buses': active_buses
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/logs', methods=['GET'])
@admin_required
def get_admin_logs(admin=None):
    """Get admin activity logs"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        logs = AdminLog.query.order_by(AdminLog.timestamp.desc()).paginate(
            page=page, per_page=per_page
        )
        
        result = []
        for log in logs.items:
            result.append({
                'id': log.id,
                'admin_name': log.admin.user.name if log.admin and log.admin.user else None,
                'action': log.action,
                'entity_type': log.entity_type,
                'entity_id': log.entity_id,
                'changes': log.changes,
                'timestamp': log.timestamp.isoformat()
            })
        
        return jsonify({
            'logs': result,
            'total': logs.total,
            'pages': logs.pages,
            'current_page': page
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500