from marshmallow import Schema, fields, validate, ValidationError

class UserSchema(Schema):
    """User schema for validation"""
    id = fields.Int()
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    phone = fields.Str(required=True, validate=validate.Length(min=10, max=15))
    gender = fields.Str(validate=validate.OneOf(['male', 'female', 'other']))
    account_type = fields.Str(validate=validate.OneOf(['passenger', 'driver', 'worker', 'admin']))
    password = fields.Str(required=True, validate=validate.Length(min=6))
    is_active = fields.Bool()
    created_at = fields.DateTime()


class BusSchema(Schema):
    """Bus schema for validation"""
    id = fields.Int()
    bus_number = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    driver_name = fields.Str(required=True)
    driver_phone = fields.Str(required=True)
    total_seats = fields.Int(validate=validate.Range(min=10, max=100))
    route = fields.Str(required=True)
    status = fields.Str(validate=validate.OneOf(['active', 'inactive', 'maintenance']))
    current_lat = fields.Float()
    current_lng = fields.Float()


class BookingSchema(Schema):
    """Booking schema for validation"""
    id = fields.Int()
    user_id = fields.Int(required=True)
    bus_id = fields.Int(required=True)
    seat_id = fields.Int(required=True)
    travel_date = fields.DateTime(required=True)
    price = fields.Float(required=True, validate=validate.Range(min=0))
    status = fields.Str(validate=validate.OneOf(['pending', 'confirmed', 'cancelled', 'completed']))


class PaymentSchema(Schema):
    """Payment schema for validation"""
    id = fields.Int()
    user_id = fields.Int(required=True)
    booking_id = fields.Int()
    amount = fields.Float(required=True, validate=validate.Range(min=0))
    payment_method = fields.Str(required=True, validate=validate.OneOf(['card', 'upi', 'wallet', 'net_banking']))
    payment_status = fields.Str(validate=validate.OneOf(['pending', 'completed', 'failed', 'refunded']))


class GPSTrackerSchema(Schema):
    """GPS Tracker schema for validation"""
    bus_id = fields.Int(required=True)
    latitude = fields.Float(required=True, validate=validate.Range(min=-90, max=90))
    longitude = fields.Float(required=True, validate=validate.Range(min=-180, max=180))
    speed = fields.Float()
    heading = fields.Float()


# Initialize schemas
user_schema = UserSchema()
users_schema = UserSchema(many=True)
bus_schema = BusSchema()
buses_schema = BusSchema(many=True)
booking_schema = BookingSchema()
bookings_schema = BookingSchema(many=True)
payment_schema = PaymentSchema()
payments_schema = PaymentSchema(many=True)
gps_schema = GPSTrackerSchema()