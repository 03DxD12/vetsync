from datetime import datetime
from app.extensions import db


class Report(db.Model):
    __tablename__ = 'reports'

    id            = db.Column(db.Integer, primary_key=True)
    title         = db.Column(db.String(150), nullable=False)
    category      = db.Column(db.String(50),  nullable=False)
    description   = db.Column(db.Text,        nullable=False)
    status        = db.Column(db.String(20),  default='Pending')  # Pending, Reviewed, Resolved
    admin_comment = db.Column(db.Text,        nullable=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at    = db.Column(db.DateTime,    default=datetime.utcnow)
