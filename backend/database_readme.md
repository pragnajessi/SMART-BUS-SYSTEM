# Smart Bus Management System - Database Documentation

## Database Structure

The system uses a relational database with the following main entities:

### Core Tables

#### 1. Users
- Stores all users (passengers, drivers, workers, admins)
- Fields: id, name, email, phone, gender, password, account_type, location, status

#### 2. Buses
- Bus information and routes
- Fields: id, bus_number, driver_id, total_seats, route, status, GPS location

#### 3. Seats
- Individual seats in buses
- Fields: id, bus_id, seat_number, is_reserved, is_women_seat, reserved_by_user_id

#### 4. Bookings
- Passenger bookings
- Fields: id, user_id, bus_id, seat_id, travel_date, price, status

#### 5. Payments
- Payment transactions
- Fields: id, user_id, booking_id, amount, payment_method, status

#### 6. Wallets
- User wallet accounts
- Fields: id, user_id, balance

### Supporting Tables

#### GPS & Location
- **gps_trackers**: Real-time GPS data for buses
- **route_stops**: Bus route stops with ETAs

#### Alerts & Announcements
- **announcements**: GPS-triggered announcements
- **wakeup_alerts**: User wake-up alerts for stops

#### Emergency & Lost & Found
- **emergencies**: Emergency reports
- **lost_items**: Lost and found items

#### Admin
- **admin_users**: Admin user profiles
- **admin_logs**: Admin activity logs

#### Reviews & Ratings
- **bus_reviews**: User reviews for buses

#### Other
- **notifications**: User notifications
- **promo_codes**: Discount promo codes

## Database Setup

### 1. Using SQLite (Default)
```bash
python migrations.py
# Choose option 3 to reset database
# Create database
createdb smart_bus_db

# Update .env
DATABASE_URL=postgresql://user:password@localhost:5432/smart_bus_db
DB_TYPE=postgresql

# Run migrations
python migrations.py
# Create database
mysql -u root -p
CREATE DATABASE smart_bus_db;

# Update .env
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/smart_bus_db
DB_TYPE=mysql

# Run migrations
python migrations.py