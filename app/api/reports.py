from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.report import Report
from app.models.user import User
from app.middleware.decorators import role_required

api_reports_bp = Blueprint('api_reports', __name__)


@api_reports_bp.route('', methods=['GET', 'POST'])
@role_required(['staff', 'admin'])
def reports(current_user_jwt):
    if request.method == 'GET':
        if current_user_jwt.role == 'admin':
            items = Report.query.order_by(Report.created_at.desc()).all()
        else:
            items = Report.query.filter_by(user_id=current_user_jwt.id).order_by(Report.created_at.desc()).all()

        return jsonify([{
            'id': r.id, 'title': r.title, 'category': r.category,
            'description': r.description, 'status': r.status,
            'admin_comment': r.admin_comment, 'user_id': r.user_id,
            'staff_name': _staff_name(r.user_id),
            'created_at': r.created_at.strftime('%b %d, %Y')
        } for r in items]), 200

    data = request.get_json()
    if not data.get('title') or not data.get('description'):
        return jsonify({'error': 'Title and description are required'}), 400

    report = Report(
        title=data.get('title'),
        category=data.get('category', 'Other'),
        description=data.get('description'),
        user_id=current_user_jwt.id
    )
    db.session.add(report)
    db.session.commit()
    return jsonify({'message': 'Report submitted successfully'}), 201


@api_reports_bp.route('/<int:report_id>', methods=['PUT', 'DELETE'])
@role_required(['admin'])
def report_detail(current_user_jwt, report_id):
    report = db.session.get(Report, report_id)
    if not report:
        return jsonify({'error': 'Report not found'}), 404

    if request.method == 'PUT':
        data = request.get_json()
        if 'status' in data:
            report.status = data['status']
        if 'admin_comment' in data:
            report.admin_comment = data['admin_comment']
        db.session.commit()
        return jsonify({'message': 'Report updated successfully'})

    db.session.delete(report)
    db.session.commit()
    return jsonify({'message': 'Report deleted successfully'})


def _staff_name(user_id):
    user = db.session.get(User, user_id)
    return f"{user.first_name} {user.last_name}" if user else "Unknown"
