from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
from dotenv import load_dotenv

# Import database
from database import db, User, Bus, Seat, Wallet

# Import routes blueprint
from routes import api

load_dotenv()

app = Flask(__name__)  # ← Keep only ONE of these
CORS(app)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'sqlite:///smart_bus.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)

# Register blueprints (ALL routes are in routes.py)
app.register_blueprint(api)

# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'API is running',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


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
    """Initialize database and seed sample data"""
    with app.app_context():
        db.create_all()
        print("✅ Database initialized!")
        
        # Check if sample data exists
        if User.query.count() == 0:
            print("📊 No data found. Seeding sample data...")
            seed_sample_data()


def seed_sample_data():
    """Seed sample data for testing"""
    try:
        # Create sample users
        user1 = User(
            name="Raj Kumar",
            email="raj@example.com",
            phone="9876543210",
            gender="male",
            password="password123",
            account_type="passenger"
        )
        
        user2 = User(
            name="Priya Singh",
            email="priya@example.com",
            phone="9876543211",
            gender="female",
            password="password123",
            account_type="passenger"
        )
        
        db.session.add_all([user1, user2])
        db.session.commit()
        
        # Create wallets
        wallet1 = Wallet(user_id=user1.id, balance=1000)
        wallet2 = Wallet(user_id=user2.id, balance=500)
        db.session.add_all([wallet1, wallet2])
        db.session.commit()
        
        # Create sample bus
        bus1 = Bus(
            bus_number="BUS001",
            driver_name="Arjun Verma",
            driver_phone="9876543212",
            total_seats=50,
            route="Delhi - Jaipur",
            status="active",
            current_lat=28.6139,
            current_lng=77.2090
        )
        
        db.session.add(bus1)
        db.session.commit()
        
        # Create seats for bus
        women_seats = 10
        for seat_num in range(1, bus1.total_seats + 1):
            seat = Seat(
                bus_id=bus1.id,
                seat_number=seat_num,
                is_women_seat=(seat_num <= women_seats)
            )
            db.session.add(seat)
        
        db.session.commit()
        print("✅ Sample data created!")
        print(f"   - Users: 2 (Raj Kumar, Priya Singh)")
        print(f"   - Wallets: 2 (₹1000, ₹500)")
        print(f"   - Bus: 1 (BUS001 - Delhi-Jaipur)")
        print(f"   - Seats: 50 (10 women-only seats)")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error seeding data: {e}")


# ==================== MAIN ====================

if __name__ == '__main__':
    init_db()
    print("\n" + "="*60)
    print("🚀 Starting Smart Bus Management System API")
    print("="*60)
    print(f"📡 Server running on: http://localhost:5000")
    print(f"🗄️  Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"📚 API Docs: Check routes.py for all endpoints")
    print("="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)