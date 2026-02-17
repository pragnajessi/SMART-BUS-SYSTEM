# Database Operations Guide

## Where to Add Database Operations

### 1. **database_operations.py** (New File)
This is where ALL database queries and operations are defined. Never write raw SQLAlchemy queries in routes!

Location: `backend/database_operations.py`

Classes organized by functionality:
- `UserOperations` - User management
- `BusOperations` - Bus management
- `BookingOperations` - Bookings
- `PaymentOperations` - Payments
- `WalletOperations` - Wallet management
- `GPSOperations` - GPS tracking
- `AlertOperations` - Alerts & announcements
- `EmergencyOperations` - Emergency management
- `LostFoundOperations` - Lost & Found
- `StatisticsOperations` - Statistics & reporting

### 2. **app.py** (Routes)
Use the operations from `database_operations.py` in your route handlers.

Location: `backend/app.py`

Pattern:
```python
@app.route('/api/endpoint', methods=['GET/POST'])
def route_handler():
    try:
        # Use operations from database_operations
        result, error = SomeOperation.perform_action(params)
        if error:
            return jsonify({'error': error}), 500
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500