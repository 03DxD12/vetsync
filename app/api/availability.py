from datetime import datetime
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.availability import DoctorAvailability
from app.middleware.decorators import jwt_required, role_required

api_availability_bp = Blueprint('api_availability', __name__)


@api_availability_bp.route('', methods=['GET'])
@jwt_required
@role_required(['staff', 'admin'])
def get_schedule(current_user_jwt):
    blocks = DoctorAvailability.query.all()
    return jsonify([{'date': b.date.isoformat(), 'slot': b.slot, 'status': b.status} for b in blocks]), 200


@api_availability_bp.route('/block', methods=['POST'])
@jwt_required
@role_required(['staff', 'admin'])
def block_time(current_user_jwt):
    data = request.get_json()
    try:
        d = datetime.strptime(data['date'], '%Y-%m-%d').date()
    except Exception:
        return jsonify({'error': 'Invalid date format'}), 400

    if not DoctorAvailability.query.filter_by(date=d, slot=data['slot']).first():
        db.session.add(DoctorAvailability(date=d, slot=data['slot'], status='unavailable'))
        db.session.commit()
    return jsonify({'message': 'Time slot blocked successfully'}), 201


@api_availability_bp.route('/unblock', methods=['DELETE'])
@jwt_required
@role_required(['staff', 'admin'])
def unblock_time(current_user_jwt):
    data = request.get_json()
    try:
        d = datetime.strptime(data['date'], '%Y-%m-%d').date()
    except Exception:
        return jsonify({'error': 'Invalid date format'}), 400

    existing = DoctorAvailability.query.filter_by(date=d, slot=data['slot']).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
    return jsonify({'message': 'Time slot is now available'}), 200


@api_availability_bp.route('/workload', methods=['GET'])
@role_required(['staff', 'admin'])
def get_workload(current_user_jwt):
    from datetime import date
    from app.models.booking import Booking

    today = date.today()
    slots = ["8:00 AM","9:00 AM","10:00 AM","11:00 AM","12:00 PM",
             "1:00 PM","2:00 PM","3:00 PM","4:00 PM","5:00 PM",
             "6:00 PM","7:00 PM","8:00 PM","9:00 PM"]

    counts = {slot: Booking.query.filter_by(date=today, slot=slot, status='confirmed').count()
              for slot in slots}

    confirmed_today = Booking.query.filter_by(date=today, status='confirmed').count()
    percentage = round(confirmed_today / len(slots) * 100, 1) if slots else 0

    return jsonify({
        'hourly': counts,
        'total_confirmed': confirmed_today,
        'percentage': percentage
    }), 200
