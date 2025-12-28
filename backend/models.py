"""
Database models for iAmSmartGate
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    """User account model"""
    __tablename__ = 'users'
    
    iamsmart_id = db.Column(db.String(100), primary_key=True)
    public_key = db.Column(db.Text, nullable=False)
    private_key_ref = db.Column(db.String(200), nullable=False)  # HSM reference
    device_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    passes = db.relationship('Pass', backref='user', lazy=True)
    
    def to_dict(self):
        return {
            'iamsmart_id': self.iamsmart_id,
            'public_key': self.public_key,
            'device_id': self.device_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Gate(db.Model):
    """Access gate model"""
    __tablename__ = 'gates'
    
    tablet_id = db.Column(db.String(100), primary_key=True)
    gps_location = db.Column(db.String(200), nullable=False)
    public_key = db.Column(db.Text, nullable=False)
    private_key_ref = db.Column(db.String(200), nullable=False)  # HSM reference
    site_id = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'tablet_id': self.tablet_id,
            'gps_location': self.gps_location,
            'public_key': self.public_key,
            'site_id': self.site_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Pass(db.Model):
    """Visit pass model"""
    __tablename__ = 'passes'
    
    pass_id = db.Column(db.String(100), primary_key=True)
    iamsmart_id = db.Column(db.String(100), db.ForeignKey('users.iamsmart_id'), nullable=False)
    site_id = db.Column(db.String(50), nullable=False)
    purpose_id = db.Column(db.String(50), nullable=False)
    visit_date_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='In Process')  # In Process/Pass/No Pass/Used/Revoked
    qr_signature = db.Column(db.Text)
    created_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    approved_timestamp = db.Column(db.DateTime)
    used_timestamp = db.Column(db.DateTime)
    expiry_timestamp = db.Column(db.DateTime)
    used_flag = db.Column(db.Boolean, default=False)
    revoked_flag = db.Column(db.Boolean, default=False)
    device_id = db.Column(db.String(100))
    
    def to_dict(self):
        return {
            'pass_id': self.pass_id,
            'iamsmart_id': self.iamsmart_id,
            'site_id': self.site_id,
            'purpose_id': self.purpose_id,
            'visit_date_time': self.visit_date_time.isoformat() if self.visit_date_time else None,
            'status': self.status,
            'created_timestamp': self.created_timestamp.isoformat() if self.created_timestamp else None,
            'approved_timestamp': self.approved_timestamp.isoformat() if self.approved_timestamp else None,
            'used_timestamp': self.used_timestamp.isoformat() if self.used_timestamp else None,
            'expiry_timestamp': self.expiry_timestamp.isoformat() if self.expiry_timestamp else None,
            'used_flag': self.used_flag,
            'revoked_flag': self.revoked_flag,
            'device_id': self.device_id
        }

class AuditLog(db.Model):
    """Audit log model"""
    __tablename__ = 'audit_logs'
    
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # login/approval/scan/revoke/pause
    user_id = db.Column(db.String(100))
    gate_id = db.Column(db.String(100))
    pass_id = db.Column(db.String(100))
    result = db.Column(db.String(50))
    details = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'log_id': self.log_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'event_type': self.event_type,
            'user_id': self.user_id,
            'gate_id': self.gate_id,
            'pass_id': self.pass_id,
            'result': self.result,
            'details': self.details
        }

class SystemState(db.Model):
    """System state for pause controls"""
    __tablename__ = 'system_state'
    
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'key': self.key,
            'value': self.value,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

def init_db():
    """Initialize database with tables and demo data"""
    from crypto_utils import DummyHSM
    
    db.create_all()
    
    # Initialize system state if not exists
    if not SystemState.query.filter_by(key='global_pause').first():
        db.session.add(SystemState(key='global_pause', value='false'))
    
    if not SystemState.query.filter_by(key='site_pauses').first():
        db.session.add(SystemState(key='site_pauses', value=json.dumps({})))
    
    # Create test gates if not exist
    hsm = DummyHSM()
    
    test_gates = [
        {'tablet_id': 'GATE001', 'site_id': 'SITE001', 'gps_location': '22.3193,114.1694'},
        {'tablet_id': 'GATE002', 'site_id': 'SITE002', 'gps_location': '22.3200,114.1700'},
        {'tablet_id': 'GATE003', 'site_id': 'SITE003', 'gps_location': '22.3210,114.1710'},
        {'tablet_id': 'GATE004', 'site_id': 'SITE004', 'gps_location': '22.3220,114.1720'},
    ]
    
    for gate_data in test_gates:
        if not Gate.query.filter_by(tablet_id=gate_data['tablet_id']).first():
            # Generate key pair for gate
            private_key_ref, public_key = hsm.generate_key_pair(gate_data['tablet_id'])
            
            gate = Gate(
                tablet_id=gate_data['tablet_id'],
                gps_location=gate_data['gps_location'],
                public_key=public_key,
                private_key_ref=private_key_ref,
                site_id=gate_data['site_id']
            )
            db.session.add(gate)
    
    db.session.commit()
