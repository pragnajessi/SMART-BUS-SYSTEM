"""
Database Operations Module
Contains all database query operations for the Smart Bus Management System
"""

from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from database import db, User, Bus, Seat, Booking, Payment, Wallet, GPSTracker
from database import RouteStop, Announcement, WakeUpAlert, Emergency, LostItem
from database import AdminUser, AdminLog, BusReview, Notification, PromoCode
from database import WalletTransaction, Refund, SystemReport

# ==================== USER OPERATIONS ====================

class UserOperations:
    """User database operations"""
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        return User.query.get(user_id)
    
    @staticmethod
    def get_user_by_email(email):
        """Get user by email"""
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def get_all_users(page=1, per_page=10):
        """Get all users with pagination"""
        return User.query.paginate(page=page, per_page=per_page)
    
    @staticmethod
    def get_users_by_type(account_type, page=1, per_page=10):
        """Get users by account type"""
        return User.query.filter_by(account_type=account_type).paginate(page=page, per_page=per_page)
    
    @staticmethod
    def create_user(name, email, phone, gender, password, account_type='passenger'):
        """Create new user"""
        try:
            user = User(
                name=name,
                email=email,
                phone=phone,
                gender=gender,
                password=password,
                account_type=account_type
            )
            db.session.add(user)
            db.session.commit()
            return user, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def update_user(user_id, **kwargs):
        """Update user information"""
        try:
            user = User.query.get(user_id)
            if not user:
                return None, "User not found"
            
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            user.updated_at = datetime.utcnow()
            db.session.commit()
            return user, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def delete_user(user_id):
        """Delete user"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "User not found"
            
            db.session.delete(user)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def get_user_bookings(user_id):
        """Get all bookings for a user"""
        return Booking.query.filter_by(user_id=user_id).all()
    
    @staticmethod
    def get_user_payments(user_id):
        """Get all payments for a user"""
        return Payment.query.filter_by(user_id=user_id).all()
    
    @staticmethod
    def get_active_users():
        """Get all active users"""
        return User.query.filter_by(is_active=True).all()
    
    @staticmethod
    def search_users(query):
        """Search users by name or email"""
        return User.query.filter(
            or_(
                User.name.ilike(f'%{query}%'),
                User.email.ilike(f'%{query}%')
            )
        ).all()


# ==================== BUS OPERATIONS ====================

class BusOperations:
    """Bus database operations"""
    
    @staticmethod
    def get_bus_by_id(bus_id):
        """Get bus by ID"""
        return Bus.query.get(bus_id)
    
    @staticmethod
    def get_bus_by_number(bus_number):
        """Get bus by bus number"""
        return Bus.query.filter_by(bus_number=bus_number).first()
    
    @staticmethod
    def get_all_buses(page=1, per_page=10):
        """Get all buses with pagination"""
        return Bus.query.paginate(page=page, per_page=per_page)
    
    @staticmethod
    def get_active_buses():
        """Get all active buses"""
        return Bus.query.filter_by(status='active').all()
    
    @staticmethod
    def get_buses_by_route(route):
        """Get buses by route"""
        return Bus.query.filter_by(route=route).all()
    
    @staticmethod
    def create_bus(bus_number, driver_name, driver_phone, route, total_seats=50, **kwargs):
        """Create new bus"""
        try:
            bus = Bus(
                bus_number=bus_number,
                driver_name=driver_name,
                driver_phone=driver_phone,
                route=route,
                total_seats=total_seats,
                **kwargs
            )
            db.session.add(bus)
            db.session.commit()
            
            # Create seats for bus
            BusOperations.create_bus_seats(bus.id, total_seats)
            
            return bus, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def create_bus_seats(bus_id, total_seats):
        """Create seats for a bus"""
        try:
            women_seats = int(total_seats * 0.2)  # 20% women seats
            
            for seat_num in range(1, total_seats + 1):
                seat = Seat(
                    bus_id=bus_id,
                    seat_number=seat_num,
                    is_women_seat=(seat_num <= women_seats)
                )
                db.session.add(seat)
            
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def update_bus(bus_id, **kwargs):
        """Update bus information"""
        try:
            bus = Bus.query.get(bus_id)
            if not bus:
                return None, "Bus not found"
            
            for key, value in kwargs.items():
                if hasattr(bus, key):
                    setattr(bus, key, value)
            
            bus.updated_at = datetime.utcnow()
            db.session.commit()
            return bus, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def get_available_seats(bus_id):
        """Get available seats for a bus"""
        return Seat.query.filter(
            Seat.bus_id == bus_id,
            Seat.is_reserved == False
        ).all()
    
    @staticmethod
    def get_reserved_seats(bus_id):
        """Get reserved seats for a bus"""
        return Seat.query.filter(
            Seat.bus_id == bus_id,
            Seat.is_reserved == True
        ).all()
    
    @staticmethod
    def get_bus_occupancy(bus_id):
        """Get bus occupancy percentage"""
        bus = Bus.query.get(bus_id)
        if not bus:
            return 0
        
        reserved = len(BusOperations.get_reserved_seats(bus_id))
        return (reserved / bus.total_seats) * 100
    
    @staticmethod
    def update_bus_location(bus_id, latitude, longitude):
        """Update bus GPS location"""
        try:
            bus = Bus.query.get(bus_id)
            if not bus:
                return None, "Bus not found"
            
            bus.current_lat = latitude
            bus.current_lng = longitude
            bus.last_location_update = datetime.utcnow()
            
            # Create GPS tracker entry
            gps_tracker = GPSTracker(
                bus_id=bus_id,
                latitude=latitude,
                longitude=longitude
            )
            db.session.add(gps_tracker)
            db.session.commit()
            
            return bus, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def search_buses(query):
        """Search buses by number or route"""
        return Bus.query.filter(
            or_(
                Bus.bus_number.ilike(f'%{query}%'),
                Bus.route.ilike(f'%{query}%')
            )
        ).all()


# ==================== BOOKING OPERATIONS ====================

class BookingOperations:
    """Booking database operations"""
    
    @staticmethod
    def create_booking(user_id, bus_id, seat_id, travel_date, price, booking_id=None):
        """Create new booking
        
        Args:
            user_id: ID of user making booking
            bus_id: ID of bus
            seat_id: ID of seat to book
            travel_date: Date of travel (datetime object)
            price: Ticket price
            booking_id: Custom booking reference (optional)
        
        Returns:
            tuple: (booking_object, error_message)
        
        Example:
            from datetime import datetime
            booking, error = BookingOperations.create_booking(
                user_id=1,
                bus_id=1,
                seat_id=5,
                travel_date=datetime(2026, 2, 15),
                price=250,
                booking_id='BK20260215001'
            )
            if error:
                print(f"Error: {error}")
            else:
                print(f"Booking created: {booking.booking_id}")"""
    
        try:
            if not booking_id:
                booking_id = f"BK{datetime.utcnow().timestamp()}"
            
            booking = Booking(
                booking_id=booking_id,
                user_id=user_id,
                bus_id=bus_id,
                seat_id=seat_id,
                travel_date=travel_date,
                price=price,
                final_price=price,
                status='pending'
            )
            db.session.add(booking)
            db.session.commit()
            return booking, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def get_booking_by_id(booking_id):
        """Get booking by ID"""
        return Booking.query.get(booking_id)
    
    @staticmethod
    def get_booking_by_ref(booking_ref):
        """Get booking by booking reference"""
        return Booking.query.filter_by(booking_id=booking_ref).first()
    
    @staticmethod
    def get_user_bookings(user_id, status=None):
        """Get all bookings for a user"""
        query = Booking.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        return query.all()
    
    @staticmethod
    def get_bus_bookings(bus_id, status=None):
        """Get all bookings for a bus"""
        query = Booking.query.filter_by(bus_id=bus_id)
        if status:
            query = query.filter_by(status=status)
        return query.all()
    
    @staticmethod
    def confirm_booking(booking_id):
        """Confirm a booking"""
        try:
            booking = Booking.query.get(booking_id)
            if not booking:
                return None, "Booking not found"
            
            booking.status = 'confirmed'
            db.session.commit()
            return booking, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def cancel_booking(booking_id, reason=None):
        """Cancel a booking and a free up the seat
         Args:
            booking_id: ID of booking to cancel
            reason: Cancellation reason
        
        Returns:
            tuple: (booking_object, error_message)"""
        try:
            booking = Booking.query.get(booking_id)
            if not booking:
                return None, "Booking not found"
            
            booking.status = 'cancelled'
            booking.cancellation_reason = reason
            booking.cancelled_at = datetime.utcnow()
            
            # Free up the seat
            seat = Seat.query.get(booking.seat_id)
            if seat:
                seat.is_reserved = False
                seat.reserved_by_user_id = None
                seat.reserved_at = None
            
            db.session.commit()
            return booking, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def get_bookings_by_date(date):
        """Get all bookings for a specific date"""
        start_date = datetime.combine(date, datetime.min.time())
        end_date = datetime.combine(date, datetime.max.time())
        
        return Booking.query.filter(
            Booking.travel_date >= start_date,
            Booking.travel_date <= end_date
        ).all()


# ==================== PAYMENT OPERATIONS ====================

class PaymentOperations:
    """Payment database operations"""
    
    @staticmethod
    def create_payment(user_id, booking_id, amount, payment_method, transaction_id=None):
        """Create new payment"""
        try:
            if not transaction_id:
                transaction_id = f"TXN{datetime.utcnow().timestamp()}"
            
            payment = Payment(
                transaction_id=transaction_id,
                user_id=user_id,
                booking_id=booking_id,
                amount=amount,
                payment_method=payment_method,
                payment_status='pending'
            )
            db.session.add(payment)
            db.session.commit()
            return payment, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def get_payment_by_id(payment_id):
        """Get payment by ID"""
        return Payment.query.get(payment_id)
    
    @staticmethod
    def get_payment_by_transaction_id(transaction_id):
        """Get payment by transaction ID"""
        return Payment.query.filter_by(transaction_id=transaction_id).first()
    
    @staticmethod
    def get_user_payments(user_id, status=None):
        """Get all payments for a user"""
        query = Payment.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(payment_status=status)
        return query.all()
    
    @staticmethod
    def complete_payment(payment_id, gateway_id=None):
        """Mark payment as completed"""
        try:
            payment = Payment.query.get(payment_id)
            if not payment:
                return None, "Payment not found"
            
            payment.payment_status = 'completed'
            payment.completed_at = datetime.utcnow()
            if gateway_id:
                payment.gateway_transaction_id = gateway_id
            
            db.session.commit()
            return payment, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def fail_payment(payment_id):
        """Mark payment as failed"""
        try:
            payment = Payment.query.get(payment_id)
            if not payment:
                return None, "Payment not found"
            
            payment.payment_status = 'failed'
            db.session.commit()
            return payment, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def refund_payment(payment_id, reason):
        """Refund a payment"""
        try:
            payment = Payment.query.get(payment_id)
            if not payment:
                return None, "Payment not found"
            
            refund = Refund(
                payment_id=payment_id,
                refund_amount=payment.amount,
                refund_reason=reason,
                refund_status='pending'
            )
            
            payment.payment_status = 'refunded'
            db.session.add(refund)
            db.session.commit()
            return refund, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def get_revenue_by_date(date):
        """Get total revenue for a date"""
        start_date = datetime.combine(date, datetime.min.time())
        end_date = datetime.combine(date, datetime.max.time())
        
        result = db.session.query(func.sum(Payment.amount)).filter(
            Payment.created_at >= start_date,
            Payment.created_at <= end_date,
            Payment.payment_status == 'completed'
        ).scalar()
        
        return result or 0
    
    @staticmethod
    def get_revenue_by_method(days=30):
        """Get revenue breakdown by payment method"""
        date_filter = datetime.utcnow() - timedelta(days=days)
        
        result = db.session.query(
            Payment.payment_method,
            func.sum(Payment.amount).label('total')
        ).filter(
            Payment.created_at >= date_filter,
            Payment.payment_status == 'completed'
        ).group_by(Payment.payment_method).all()
        
        return {method: total for method, total in result}


# ==================== WALLET OPERATIONS ====================

class WalletOperations:
    """Wallet database operations"""
    
    @staticmethod
    def get_wallet(user_id):
        """Get wallet for a user(create if doesn't exist)
        Args:
            user_id: ID of user
        
        Returns:
            wallet_object
        
        Example:
            wallet = WalletOperations.get_wallet(1)
            print(f"Balance: {wallet.balance}")"""
        wallet = Wallet.query.filter_by(user_id=user_id).first()
        if not wallet:
            # Create wallet if doesn't exist
            wallet = Wallet(user_id=user_id, balance=0)
            db.session.add(wallet)
            db.session.commit()
        return wallet
    
    @staticmethod
    def add_balance(user_id, amount, description):
        """Add money to wallet(credit)
        Args:
            user_id: ID of user
            amount: Amount to add
            description: Transaction description
        
        Returns:
            tuple: (wallet_object, error_message)
        
        Example:
            wallet, error = WalletOperations.add_balance(
                user_id=1,
                amount=1000,
                description='Initial topup'
            )
            if error:
                print(f"Error: {error}")
            else:
                print(f"New balance: ₹{wallet.balance}")"""
        try:
            wallet = WalletOperations.get_wallet(user_id)
            
            transaction = WalletTransaction(
                wallet_id=wallet.id,
                transaction_type='credit',
                amount=amount,
                description=description,
                balance_before=wallet.balance,
                balance_after=wallet.balance + amount
            )
            
            wallet.balance += amount
            wallet.total_added += amount
            wallet.last_updated = datetime.utcnow()
            
            db.session.add(transaction)
            db.session.commit()
            return wallet, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def deduct_balance(user_id, amount, description):
        """Deduct money from wallet(debit)
        Args:
            user_id: ID of user
            amount: Amount to deduct
            description: Transaction description
        
        Returns:
            tuple: (wallet_object, error_message)
        
        Example:
            wallet, error = WalletOperations.deduct_balance(
                user_id=1,
                amount=250,
                description='Booking payment - BK001'
            )
            if error:
                print(f"Error: {error}")"""
        try:
            wallet = WalletOperations.get_wallet(user_id)
            
            if wallet.balance < amount:
                return None, "Insufficient balance"
            
            transaction = WalletTransaction(
                wallet_id=wallet.id,
                transaction_type='debit',
                amount=amount,
                description=description,
                balance_before=wallet.balance,
                balance_after=wallet.balance - amount
            )
            
            wallet.balance -= amount
            wallet.total_spent += amount
            wallet.last_updated = datetime.utcnow()
            
            db.session.add(transaction)
            db.session.commit()
            return wallet, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def get_wallet_transactions(user_id, limit=20):
        """Get wallet transaction history"""
        wallet = WalletOperations.get_wallet(user_id)
        return WalletTransaction.query.filter_by(wallet_id=wallet.id).order_by(
            WalletTransaction.created_at.desc()
        ).limit(limit).all()


# ==================== GPS OPERATIONS ====================

class GPSOperations:
    """GPS tracking database operations"""
    
    @staticmethod
    def log_gps(bus_id, latitude, longitude, speed=0, heading=0, accuracy=0, altitude=0):
        """Log GPS position for a bus
         Args:
            bus_id: ID of bus
            latitude: Current latitude
            longitude: Current longitude
            speed: Current speed (km/h)
            heading: Direction of travel (degrees)
            accuracy: GPS accuracy (meters)
            altitude: Current altitude (meters)
        
        Returns:
            tuple: (gps_tracker_object, error_message)
        
        Example:
            gps, error = GPSOperations.log_gps(
                bus_id=1,
                latitude=28.6139,
                longitude=77.2090,
                speed=40,
                heading=90,
                accuracy=5,
                altitude=200
            )
            if error:
                print(f"Error logging GPS: {error}")
            else:
                print(f"GPS logged at {gps.timestamp}")"""
        try:
            gps = GPSTracker(
                bus_id=bus_id,
                latitude=latitude,
                longitude=longitude,
                speed=speed,
                heading=heading,
                accuracy=accuracy,
                altitude=altitude
            )
            db.session.add(gps)
            db.session.commit()
            return gps, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def get_latest_gps(bus_id):
        """Get latest GPS position for a bus"""
        return GPSTracker.query.filter_by(bus_id=bus_id, is_active=True).order_by(
            GPSTracker.timestamp.desc()
        ).first()
    
    @staticmethod
    def get_gps_history(bus_id, hours=24):
        """Get GPS history for a bus"""
        time_filter = datetime.utcnow() - timedelta(hours=hours)
        return GPSTracker.query.filter(
            GPSTracker.bus_id == bus_id,
            GPSTracker.timestamp >= time_filter
        ).order_by(GPSTracker.timestamp.asc()).all()
    
    @staticmethod
    def get_all_active_buses_gps():
        """Get latest GPS for all active buses"""
        buses = Bus.query.filter_by(status='active').all()
        gps_data = []
        
        for bus in buses:
            gps = GPSOperations.get_latest_gps(bus.id)
            if gps:
                gps_data.append({
                    'bus_id': bus.id,
                    'bus_number': bus.bus_number,
                    'latitude': gps.latitude,
                    'longitude': gps.longitude,
                    'speed': gps.speed,
                    'heading': gps.heading
                })
        
        return gps_data


# ==================== ALERT OPERATIONS ====================

class AlertOperations:
    """Alert and announcement database operations"""
    
    @staticmethod
    def create_wakeup_alert(user_id, bus_id, stop_name, stop_lat, stop_lng, alert_time=120):
        """Create wake-up alert"""
        try:
            alert = WakeUpAlert(
                user_id=user_id,
                bus_id=bus_id,
                stop_name=stop_name,
                stop_lat=stop_lat,
                stop_lng=stop_lng,
                alert_before_time=alert_time
            )
            db.session.add(alert)
            db.session.commit()
            return alert, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def get_user_alerts(user_id):
        """Get all active alerts for a user"""
        return WakeUpAlert.query.filter_by(user_id=user_id, is_active=True).all()
    
    @staticmethod
    def deactivate_alert(alert_id):
        """Deactivate alert"""
        try:
            alert = WakeUpAlert.query.get(alert_id)
            if not alert:
                return None, "Alert not found"
            
            alert.is_active = False
            db.session.commit()
            return alert, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def create_announcement(bus_id, stop_name, stop_lat, stop_lng, text, alert_time=120):
        """Create announcement"""
        try:
            announcement = Announcement(
                bus_id=bus_id,
                stop_name=stop_name,
                stop_lat=stop_lat,
                stop_lng=stop_lng,
                announcement_text=text,
                time_before_arrival=alert_time
            )
            db.session.add(announcement)
            db.session.commit()
            return announcement, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def get_bus_announcements(bus_id):
        """Get all announcements for a bus"""
        return Announcement.query.filter_by(bus_id=bus_id).all()


# ==================== EMERGENCY OPERATIONS ====================

class EmergencyOperations:
    """Emergency database operations"""
    
    @staticmethod
    def create_emergency(bus_id, emergency_type, latitude, longitude, user_id=None, description=None):
        """Create emergency report"""
        try:
            emergency = Emergency(
                bus_id=bus_id,
                user_id=user_id,
                emergency_type=emergency_type,
                latitude=latitude,
                longitude=longitude,
                description=description,
                severity='medium'
            )
            db.session.add(emergency)
            db.session.commit()
            return emergency, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def get_active_emergencies():
        """Get all active emergencies"""
        return Emergency.query.filter_by(status='active').all()
    
    @staticmethod
    def resolve_emergency(emergency_id):
        """Resolve emergency"""
        try:
            emergency = Emergency.query.get(emergency_id)
            if not emergency:
                return None, "Emergency not found"
            
            emergency.status = 'resolved'
            emergency.resolved_at = datetime.utcnow()
            db.session.commit()
            return emergency, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)


# ==================== LOST & FOUND OPERATIONS ====================

class LostFoundOperations:
    """Lost & Found database operations"""
    
    @staticmethod
    def report_lost_item(user_id, item_name, description, bus_id=None, image=None):
        """Report lost item"""
        try:
            item = LostItem(
                item_name=item_name,
                item_description=description,
                reported_by_user_id=user_id,
                bus_id=bus_id,
                item_image=image
            )
            db.session.add(item)
            db.session.commit()
            return item, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def get_lost_items():
        """Get all lost items"""
        return LostItem.query.filter_by(item_status='lost').all()
    
    @staticmethod
    def get_found_items():
        """Get all found items"""
        return LostItem.query.filter_by(item_status='found').all()
    
    @staticmethod
    def mark_as_found(item_id, worker_id, location):
        """Mark item as found"""
        try:
            item = LostItem.query.get(item_id)
            if not item:
                return None, "Item not found"
            
            item.item_status = 'found'
            item.found_by_worker_id = worker_id
            item.location_found = location
            item.found_date = datetime.utcnow()
            db.session.commit()
            return item, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def claim_item(item_id):
        """Claim found item"""
        try:
            item = LostItem.query.get(item_id)
            if not item:
                return None, "Item not found"
            
            item.item_status = 'claimed'
            item.claimed_date = datetime.utcnow()
            db.session.commit()
            return item, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)


# ==================== STATISTICS OPERATIONS ====================

class StatisticsOperations:
    """Statistics and reporting database operations"""
    
    @staticmethod
    def get_total_users():
        """
        Get total number of users
        
        Returns:
            int: Total user count
        
        Example:
            total = StatisticsOperations.get_total_users()
            print(f"Total users: {total}")
        """
        return User.query.count()
    
    @staticmethod
    def get_total_buses():
        """Get total number of buses"""
        return Bus.query.count()
    
    @staticmethod
    def get_active_buses_count():
        """Get count of active buses"""
        return Bus.query.filter_by(status='active').count()
    
    @staticmethod
    def get_total_bookings():
        """Get total number of bookings"""
        return Booking.query.count()
    
    @staticmethod
    def get_confirmed_bookings():
        """Get number of confirmed bookings"""
        return Booking.query.filter_by(status='confirmed').count()
    
    @staticmethod
    def get_total_revenue():
        """
        Get total revenue from completed payments
        
        Returns:
            float: Total revenue amount
        
        Example:
            revenue = StatisticsOperations.get_total_revenue()
            print(f"Total revenue: ₹{revenue}")
        """
        result = db.session.query(func.sum(Payment.amount)).filter(
            Payment.payment_status == 'completed'
        ).scalar()
        return result or 0
    
    @staticmethod
    def get_daily_revenue(date):
        """
        Get revenue for a specific date
        
        Args:
            date: Date object (e.g., datetime.date(2026, 2, 12))
        
        Returns:
            float: Daily revenue
        
        Example:
            from datetime import date
            daily_revenue = StatisticsOperations.get_daily_revenue(date.today())
            print(f"Today's revenue: ₹{daily_revenue}")
        """
        start_date = datetime.combine(date, datetime.min.time())
        end_date = datetime.combine(date, datetime.max.time())
        
        result = db.session.query(func.sum(Payment.amount)).filter(
            Payment.created_at >= start_date,
            Payment.created_at <= end_date,
            Payment.payment_status == 'completed'
        ).scalar()
        
        return result or 0
    
    @staticmethod
    def get_busiest_routes():
        """
        Get busiest routes by number of bookings
        
        Returns:
            list: List of (route, booking_count) tuples
        
        Example:
            routes = StatisticsOperations.get_busiest_routes()
            for route, count in routes:
                print(f"{route}: {count} bookings")
        """
        result = db.session.query(
            Bus.route,
            func.count(Booking.id).label('booking_count')
        ).join(Booking, Bus.id == Booking.bus_id).group_by(
            Bus.route
        ).order_by(func.count(Booking.id).desc()).all()
        
        return result
    
    @staticmethod
    def get_user_stats():
        """
        Get user statistics
        
        Returns:
            dict: User statistics breakdown
        
        Example:
            stats = StatisticsOperations.get_user_stats()
            print(f"Passengers: {stats['passengers']}")
            print(f"Drivers: {stats['drivers']}")
        """
        total_users = User.query.count()
        passengers = User.query.filter_by(account_type='passenger').count()
        drivers = User.query.filter_by(account_type='driver').count()
        workers = User.query.filter_by(account_type='worker').count()
        
        return {
            'total_users': total_users,
            'passengers': passengers,
            'drivers': drivers,
            'workers': workers
        }
    
    @staticmethod
    def get_payment_stats():
        """
        Get payment statistics
        
        Returns:
            dict: Payment statistics breakdown
        
        Example:
            stats = StatisticsOperations.get_payment_stats()
            print(f"Completed: {stats['completed']}")
            print(f"Failed: {stats['failed']}")
        """
        total_payments = Payment.query.count()
        completed = Payment.query.filter_by(payment_status='completed').count()
        failed = Payment.query.filter_by(payment_status='failed').count()
        refunded = Payment.query.filter_by(payment_status='refunded').count()
        
        return {
            'total_payments': total_payments,
            'completed': completed,
            'failed': failed,
            'refunded': refunded
        }
    
    @staticmethod
    def get_dashboard_stats():
        """
        Get all dashboard statistics
        
        Returns:
            dict: Complete dashboard data
        
        Example:
            dashboard = StatisticsOperations.get_dashboard_stats()
            print(dashboard)
        """
        return {
            'total_users': StatisticsOperations.get_total_users(),
            'total_buses': StatisticsOperations.get_total_buses(),
            'active_buses': StatisticsOperations.get_active_buses_count(),
            'total_bookings': StatisticsOperations.get_total_bookings(),
            'confirmed_bookings': StatisticsOperations.get_confirmed_bookings(),
            'total_revenue': StatisticsOperations.get_total_revenue(),
            'user_stats': StatisticsOperations.get_user_stats(),
            'payment_stats': StatisticsOperations.get_payment_stats()
        }