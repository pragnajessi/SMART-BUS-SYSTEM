import os
import sys
from datetime import datetime, timedelta
from database import db, User, Bus, Seat, Booking, Payment, Wallet, GPSTracker, RouteStop
from database import Announcement, WakeUpAlert, Emergency, LostItem, AdminUser, AdminLog
from database import BusReview, Notification, PromoCode, Refund, WalletTransaction
from database import SystemReport

def create_all_tables(app):
    """Create all database tables"""
    with app.app_context():
        db.create_all()
        print("✅ All tables created successfully!")

def seed_sample_data(app):
    """Seed database with sample data"""
    with app.app_context():
        # Check if data already exists
        if User.query.first() is not None:
            print("⚠️  Database already has data. Skipping seeding.")
            return
        
        print("🌱 Seeding sample data...")
        
        # Create sample users
        user1 = User(
            name="Raj Kumar",
            email="raj@example.com",
            phone="9876543210",
            gender="male",
            password="password123",
            account_type="passenger",
            is_verified=True
        )
        
        user2 = User(
            name="Priya Singh",
            email="priya@example.com",
            phone="9876543211",
            gender="female",
            password="password123",
            account_type="passenger",
            is_verified=True
        )
        
        driver1 = User(
            name="Arjun Verma",
            email="driver@example.com",
            phone="9876543212",
            gender="male",
            password="password123",
            account_type="driver",
            is_verified=True
        )
        
        worker1 = User(
            name="Amita Sharma",
            email="worker@example.com",
            phone="9876543213",
            gender="female",
            password="password123",
            account_type="worker",
            is_verified=True
        )
        
        admin1 = User(
            name="Admin User",
            email="admin@example.com",
            phone="9876543214",
            gender="male",
            password="admin123",
            account_type="admin",
            is_verified=True
        )
        
        db.session.add_all([user1, user2, driver1, worker1, admin1])
        db.session.commit()
        print("✅ Created 5 sample users")
        
        # Create sample buses
        bus1 = Bus(
            bus_number="BUS001",
            driver_id=driver1.id,
            driver_name="Arjun Verma",
            driver_phone="9876543212",
            total_seats=50,
            bus_type="ac",
            registration_number="DL01AB1234",
            manufacturer="Volvo",
            model="B9R",
            year=2022,
            route="Delhi - Jaipur",
            route_code="DJ001",
            start_point="Delhi Central",
            end_point="Jaipur Station",
            current_lat=28.6139,
            current_lng=77.2090,
            status="active",
            is_available=True,
            amenities=['wifi', 'usb_charging', 'water']
        )
        
        bus2 = Bus(
            bus_number="BUS002",
            driver_id=driver1.id,
            driver_name="Arjun Verma",
            driver_phone="9876543212",
            total_seats=48,
            bus_type="deluxe",
            registration_number="DL01AB1235",
            manufacturer="Scania",
            model="K440",
            year=2021,
            route="Delhi - Agra",
            route_code="DA001",
            start_point="Delhi ISBT",
            end_point="Agra Fort",
            current_lat=27.1751,
            current_lng=78.0421,
            status="active",
            is_available=True,
            amenities=['wifi', 'usb_charging', 'water', 'blanket']
        )
        
        db.session.add_all([bus1, bus2])
        db.session.commit()
        print("✅ Created 2 sample buses")
        
        # Create seats for buses
        for bus in [bus1, bus2]:
            for seat_num in range(1, bus.total_seats + 1):
                is_women = seat_num <= int(bus.total_seats * 0.2)  # 20% women seats
                seat = Seat(
                    bus_id=bus.id,
                    seat_number=seat_num,
                    is_women_seat=is_women,
                    seat_type='window' if seat_num % 2 == 0 else 'aisle'
                )
                db.session.add(seat)
        
        db.session.commit()
        print("✅ Created seats for all buses")
        
        # Create sample route stops
        stops_bus1 = [
            RouteStop(bus_id=bus1.id, stop_order=1, stop_name="Delhi ISBT", latitude=28.6139, longitude=77.2090),
            RouteStop(bus_id=bus1.id, stop_order=2, stop_name="Gurgaon", latitude=28.4595, longitude=77.0266),
            RouteStop(bus_id=bus1.id, stop_order=3, stop_name="Faridabad", latitude=28.4089, longitude=77.3178),
            RouteStop(bus_id=bus1.id, stop_order=4, stop_name="Jaipur Station", latitude=26.8124, longitude=75.8231),
        ]
        
        db.session.add_all(stops_bus1)
        db.session.commit()
        print("✅ Created route stops")
        
        # Create sample wallet
        wallet1 = Wallet(user_id=user1.id, balance=1000, total_added=1000, is_active=True)
        wallet2 = Wallet(user_id=user2.id, balance=500, total_added=500, is_active=True)
        
        db.session.add_all([wallet1, wallet2])
        db.session.commit()
        print("✅ Created sample wallets")
        
        # Create admin user
        admin_profile = AdminUser(
            user_id=admin1.id,
            role="super_admin",
            permissions=['all'],
            is_active=True
        )
        
        db.session.add(admin_profile)
        db.session.commit()
        print("✅ Created admin profile")
        
        # Create sample booking
        booking1 = Booking(
            booking_id="BK001",
            user_id=user1.id,
            seat_id=1,
            bus_id=bus1.id,
            travel_date=datetime.utcnow() + timedelta(days=5),
            price=250,
            discount=0,
            final_price=250,
            status="confirmed"
        )
        
        db.session.add(booking1)
        db.session.commit()
        print("✅ Created sample booking")
        
        # Create sample payment
        payment1 = Payment(
            transaction_id="TXN001",
            user_id=user1.id,
            booking_id=booking1.id,
            amount=250,
            payment_method="card",
            payment_gateway="razorpay",
            payment_status="completed",
            completed_at=datetime.utcnow()
        )
        
        db.session.add(payment1)
        db.session.commit()
        print("✅ Created sample payment")
        
        # Create sample notifications
        notification1 = Notification(
            user_id=user1.id,
            title="Booking Confirmed",
            message="Your booking BK001 is confirmed",
            notification_type="booking",
            related_id=booking1.id,
            related_type="booking"
        )
        
        db.session.add(notification1)
        db.session.commit()
        print("✅ Created sample notifications")
        
        print("\n✅ Sample data seeded successfully!")
        print(f"   - Users: 5")
        print(f"   - Buses: 2")
        print(f"   - Seats: {len(db.session.query(Seat).all())}")
        print(f"   - Bookings: 1")
        print(f"   - Payments: 1")

def reset_database(app):
    """Drop all tables and recreate them"""
    with app.app_context():
        print("⚠️  Dropping all tables...")
        db.drop_all()
        print("✅ All tables dropped")
        
        print("🔨 Creating new tables...")
        db.create_all()
        print("✅ All tables created")
        
        print("\n🌱 Seeding sample data...")
        seed_sample_data(app)

def get_database_info(app):
    """Print database information"""
    with app.app_context():
        print("\n📊 Database Information:")
        print(f"   Total Users: {User.query.count()}")
        print(f"   Total Buses: {Bus.query.count()}")
        print(f"   Total Seats: {Seat.query.count()}")
        print(f"   Total Bookings: {Booking.query.count()}")
        print(f"   Total Payments: {Payment.query.count()}")
        print(f"   Total Wallets: {Wallet.query.count()}")
        print(f"   Total Notifications: {Notification.query.count()}")

def cleanup_expired_data(app):
    """Clean up expired data from database"""
    with app.app_context():
        # Delete expired promo codes
        PromoCode.query.filter(PromoCode.valid_until < datetime.utcnow()).delete()
        
        # Delete old GPS data (older than 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        GPSTracker.query.filter(GPSTracker.timestamp < thirty_days_ago).delete()
        
        db.session.commit()
        print("✅ Expired data cleaned up")

if __name__ == '__main__':
    from app import app
    
    print("Smart Bus Management System - Database Setup")
    print("=" * 50)
    print("\nOptions:")
    print("1. Create all tables")
    print("2. Seed sample data")
    print("3. Reset database (drop + create + seed)")
    print("4. Get database info")
    print("5. Cleanup expired data")
    
    choice = input("\nEnter your choice (1-5): ")
    
    if choice == '1':
        create_all_tables(app)
    elif choice == '2':
        seed_sample_data(app)
    elif choice == '3':
        confirm = input("This will delete all data. Continue? (yes/no): ")
        if confirm.lower() == 'yes':
            reset_database(app)
    elif choice == '4':
        get_database_info(app)
    elif choice == '5':
        cleanup_expired_data(app)
    else:
        print("Invalid choice!")
