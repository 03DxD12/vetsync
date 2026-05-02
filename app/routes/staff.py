import json
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.extensions import db
from app.models.booking import Booking
from app.models.report import Report
from app.models.availability import DoctorAvailability
from app.models.user import User
from app.middleware.decorators import login_required, admin_required, staff_required, _get_current_user
from app.services.push_service import send_push_notification

staff_bp = Blueprint('staff', __name__, url_prefix='/staff')


@staff_bp.route('/appointments')
@login_required
@staff_required
def appointments():
    user     = _get_current_user()
    bookings = Booking.query.order_by(Booking.date.desc(), Booking.slot.desc()).all()
    return render_template('staff_appointments.html', user=user, bookings=bookings)


@staff_bp.route('/submitted-reports')
@login_required
@staff_required
def submitted_reports():
    user = _get_current_user()
    # View all submitted reports for validation/audit
    reports = Report.query.order_by(Report.created_at.desc()).all()
    return render_template('staff_submitted_reports.html', user=user, reports=reports)


@staff_bp.route('/offers')
@login_required
@staff_required
def offers():
    return redirect(url_for('staff.control_panel'))


@staff_bp.route('/control-panel')
@login_required
@staff_required
def control_panel():
    user = _get_current_user()
    bookings = Booking.query.order_by(Booking.date.asc(), Booking.slot.asc()).all()
    bookings_json = [{
        'id': b.id,
        'date': b.date.isoformat(),
        'slot': b.slot,
        'client_name': b.name,
        'pet_name': b.pet_name,
        'pet_type': b.pet_type,
        'service': b.service_ref.name if b.service_ref else 'Unknown',
        'status': b.status,
    } for b in bookings]
    return render_template(
        'staff_control_panel.html',
        user=user,
        bookings_json=json.dumps(bookings_json),
    )


@staff_bp.route('/pet-records')
@login_required
@staff_required
def pet_records():
    user = _get_current_user()
    all_bookings = Booking.query.all()
    pet_history = {}
    for b in all_bookings:
        key = f"{b.pet_name}|{b.email}"
        if key not in pet_history:
            pet_history[key] = {
                'name': b.pet_name, 'type': b.pet_type, 'breed': b.pet_breed,
                'owner': b.name, 'email': b.email, 'records': []
            }
        pet_history[key]['records'].append({
            'date': b.date.isoformat(), 'service': b.service_ref.name,
            'reason': b.visit_reason, 'status': b.status, 'notes': b.notes
        })
    return render_template('staff_pet_records.html', user=user, pet_history=pet_history)


@staff_bp.route('/audit-logs')
@login_required
@admin_required
def audit_logs():
    user = _get_current_user()
    # In a real system, this would pull from an AuditLog model
    return render_template('admin_audit_logs.html', user=user)


@staff_bp.route('/booking/<int:bid>/status', methods=['POST'])
@login_required
@staff_required
def update_booking_status(bid):
    status = request.form.get('status')
    if status not in ['confirmed', 'pending', 'cancelled', 'completed']:
        flash('Invalid status.', 'error')
        return redirect(request.referrer or url_for('dashboard.staff_dashboard'))

    booking = db.session.get(Booking, bid)
    if not booking:
        flash('Booking not found.', 'error')
    else:
        booking.status = status
        user = _get_current_user()
        if user:
            booking.handled_by = f"{user.first_name} {user.last_name}"
        db.session.commit()

        if booking.user_id:
            send_push_notification(
                booking.user_id,
                f"Booking {status.capitalize()}",
                f"Your appointment for {booking.pet_name} ({booking.service_ref.name}) on {booking.date} is now {status}."
            )
        flash(f'Booking #{bid} updated to {status}.', 'success')

    return redirect(request.referrer or url_for('dashboard.staff_dashboard'))


@staff_bp.route('/booking/<int:bid>/delete', methods=['POST'])
@login_required
@staff_required
def delete_booking(bid):
    booking = db.session.get(Booking, bid)
    if not booking:
        flash('Booking not found.', 'error')
    else:
        if booking.user_id:
            send_push_notification(
                booking.user_id,
                "Booking Cancelled",
                f"Your booking for {booking.pet_name} on {booking.date} has been cancelled by staff."
            )
        db.session.delete(booking)
        db.session.commit()
        flash(f'Booking #{bid} has been removed.', 'success')

    return redirect(request.referrer or url_for('dashboard.staff_dashboard'))


@staff_bp.route('/availability', methods=['GET', 'POST'])
@login_required
@staff_required
def availability():
    if request.method == 'GET':
        blocks = DoctorAvailability.query.all()
        return jsonify([{'date': b.date.isoformat(), 'slot': b.slot, 'status': b.status} for b in blocks])

    data = request.get_json()
    target_date = data.get('date')
    slot        = data.get('slot')

    if not target_date or not slot:
        return jsonify({'error': 'Missing data'}), 400

    try:
        d = datetime.strptime(target_date, '%Y-%m-%d').date()
    except Exception:
        return jsonify({'error': 'Invalid date format'}), 400

    existing = DoctorAvailability.query.filter_by(date=d, slot=slot).first()
    if existing:
        db.session.delete(existing)
        status = 'available'
    else:
        db.session.add(DoctorAvailability(date=d, slot=slot, status='unavailable'))
        status = 'unavailable'

    db.session.commit()
    return jsonify({'success': True, 'date': target_date, 'slot': slot, 'new_status': status})
