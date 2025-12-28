"""
API routes for iAmSmartGate
User and Gate endpoints
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from models import db, User, Gate, Pass, AuditLog, SystemState
from crypto_utils import hsm
from dummy_integrations import dummy_iamsmart_authenticate, dummy_validate_gps
import jwt
import uuid
import json
import logging
from config import Config

api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

def create_audit_log(event_type, result, user_id=None, gate_id=None, pass_id=None, details=None):
    """Helper to create audit log entry"""
    log = AuditLog(
        event_type=event_type,
        user_id=user_id,
        gate_id=gate_id,
        pass_id=pass_id,
        result=result,
        details=details
    )
    db.session.add(log)
    db.session.commit()
    logger.info(f"[AUDIT] {event_type}: {result} - {details}")

def generate_jwt_token(user_id):
    """Generate JWT token for authentication"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=Config.JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')
    return token

def verify_jwt_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@api_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.json
        iamsmart_id = data.get('iamsmart_id')
        password = data.get('password')
        device_id = data.get('device_id')
        
        logger.info(f"[API] Login request for user: {iamsmart_id}")
        
        if not iamsmart_id or not password:
            return jsonify({'error': 'Missing credentials'}), 400
        
        # Authenticate via dummy iAmSmart
        if not dummy_iamsmart_authenticate(iamsmart_id, password):
            create_audit_log('login', 'FAILED', user_id=iamsmart_id, details='Invalid credentials')
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check if user exists
        user = User.query.filter_by(iamsmart_id=iamsmart_id).first()
        
        if not user:
            # Create new user with key pair
            logger.info(f"[API] Creating new user: {iamsmart_id}")
            key_ref, public_key = hsm.generate_key_pair(f"user_{iamsmart_id}")
            user = User(
                iamsmart_id=iamsmart_id,
                public_key=public_key,
                private_key_ref=key_ref,
                device_id=device_id
            )
            db.session.add(user)
            db.session.commit()
            logger.info(f"[API] User created: {iamsmart_id}")
        else:
            # Update device ID if provided
            if device_id and device_id != user.device_id:
                user.device_id = device_id
                db.session.commit()
        
        # Generate JWT token
        token = generate_jwt_token(iamsmart_id)
        
        create_audit_log('login', 'SUCCESS', user_id=iamsmart_id, details=f'Device: {device_id}')
        
        return jsonify({
            'token': token,
            'user': user.to_dict(),
            'message': 'Login successful'
        }), 200
        
    except Exception as e:
        logger.error(f"[API] Login error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@api_bp.route('/gate-login', methods=['POST'])
def gate_login():
    """Gate login endpoint"""
    try:
        data = request.json
        tablet_id = data.get('tablet_id')
        password = data.get('password')
        gps_location = data.get('gps_location')
        
        logger.info(f"[API] Gate login request for: {tablet_id}")
        
        if not tablet_id or not password:
            return jsonify({'error': 'Missing credentials'}), 400
        
        # Authenticate (dummy)
        if not dummy_iamsmart_authenticate(tablet_id, password):
            create_audit_log('login', 'FAILED', gate_id=tablet_id, details='Invalid credentials')
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check if gate exists
        gate = Gate.query.filter_by(tablet_id=tablet_id).first()
        
        if not gate:
            return jsonify({'error': 'Gate not registered'}), 404
        
        # Validate GPS
        if gps_location:
            if not dummy_validate_gps(tablet_id, gps_location, gate.gps_location):
                create_audit_log('login', 'FAILED', gate_id=tablet_id, details='GPS validation failed')
                return jsonify({'error': 'GPS validation failed'}), 403
        
        # Generate JWT token
        token = generate_jwt_token(tablet_id)
        
        create_audit_log('login', 'SUCCESS', gate_id=tablet_id, details=f'GPS: {gps_location}')
        
        return jsonify({
            'token': token,
            'gate': gate.to_dict(),
            'message': 'Gate login successful'
        }), 200
        
    except Exception as e:
        logger.error(f"[API] Gate login error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@api_bp.route('/apply-pass', methods=['POST'])
def apply_pass():
    """Apply for visit pass"""
    try:
        data = request.json
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        # Verify token
        user_id = verify_jwt_token(token)
        if not user_id:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        site_id = data.get('site_id')
        purpose_id = data.get('purpose_id')
        visit_date_time_str = data.get('visit_date_time')
        device_id = data.get('device_id')
        
        logger.info(f"[API] Pass application from user: {user_id}")
        
        if not all([site_id, purpose_id, visit_date_time_str]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Parse date time
        try:
            visit_date_time = datetime.fromisoformat(visit_date_time_str.replace('Z', '+00:00'))
        except:
            return jsonify({'error': 'Invalid date time format'}), 400
        
        # Create pass
        pass_id = f"PASS{uuid.uuid4().hex[:12].upper()}"
        new_pass = Pass(
            pass_id=pass_id,
            iamsmart_id=user_id,
            site_id=site_id,
            purpose_id=purpose_id,
            visit_date_time=visit_date_time,
            status='In Process',
            device_id=device_id
        )
        db.session.add(new_pass)
        db.session.commit()
        
        create_audit_log('application', 'SUBMITTED', user_id=user_id, pass_id=pass_id, 
                        details=f'Site: {site_id}, Purpose: {purpose_id}')
        
        logger.info(f"[API] Pass created: {pass_id}")
        
        return jsonify({
            'pass': new_pass.to_dict(),
            'message': 'Pass application submitted'
        }), 201
        
    except Exception as e:
        logger.error(f"[API] Apply pass error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@api_bp.route('/my-passes', methods=['GET'])
def my_passes():
    """Get user's passes"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        # Verify token
        user_id = verify_jwt_token(token)
        if not user_id:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Get all passes for user
        passes = Pass.query.filter_by(iamsmart_id=user_id).order_by(Pass.created_timestamp.desc()).all()
        
        return jsonify({
            'passes': [p.to_dict() for p in passes]
        }), 200
        
    except Exception as e:
        logger.error(f"[API] Get passes error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@api_bp.route('/get-qr/<pass_id>', methods=['GET'])
def get_qr(pass_id):
    """Generate dynamic QR code for pass"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        # Verify token
        user_id = verify_jwt_token(token)
        if not user_id:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Get pass
        pass_obj = Pass.query.filter_by(pass_id=pass_id, iamsmart_id=user_id).first()
        if not pass_obj:
            return jsonify({'error': 'Pass not found'}), 404
        
        # Check pass status
        if pass_obj.status != 'Pass':
            return jsonify({'error': f'Pass not approved (status: {pass_obj.status})'}), 403
        
        if pass_obj.used_flag:
            return jsonify({'error': 'Pass already used'}), 403
        
        if pass_obj.revoked_flag:
            return jsonify({'error': 'Pass has been revoked'}), 403
        
        # Check if pass is expired
        if pass_obj.expiry_timestamp and datetime.utcnow() > pass_obj.expiry_timestamp:
            return jsonify({'error': 'Pass has expired'}), 403
        
        # Generate minimal QR payload (only pass_id + timestamp)
        timestamp = datetime.utcnow().isoformat()
        
        # Sign minimal data
        data_to_sign = f"{pass_obj.pass_id}|{timestamp}"
        user = User.query.filter_by(iamsmart_id=user_id).first()
        signature = hsm.sign_data(user.private_key_ref, data_to_sign)
        
        # Minimal QR payload
        qr_payload = {
            'p': pass_obj.pass_id,      # pass_id (shortened key)
            't': timestamp,              # timestamp (shortened key)
            's': signature               # signature (shortened key)
        }
        
        # Store signature in pass
        pass_obj.qr_signature = signature
        db.session.commit()
        
        logger.info(f"[API] QR code generated for pass: {pass_id}")
        
        return jsonify({
            'qr_payload': json.dumps(qr_payload),
            'expires_in': Config.QR_EXPIRATION_SECONDS,
            'message': 'QR code generated'
        }), 200
        
    except Exception as e:
        logger.error(f"[API] Get QR error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@api_bp.route('/scan-qr', methods=['POST'])
def scan_qr():
    """Validate scanned QR code"""
    try:
        data = request.json
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        # Verify gate token
        gate_id = verify_jwt_token(token)
        if not gate_id:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        qr_payload_str = data.get('qr_payload')
        if not qr_payload_str:
            return jsonify({'error': 'Missing QR payload'}), 400
        
        logger.info(f"[API] QR scan by gate: {gate_id}")
        
        # Parse minimal QR payload
        try:
            qr_payload = json.loads(qr_payload_str)
            pass_id = qr_payload['p']      # pass_id
            timestamp = qr_payload['t']    # timestamp
            signature = qr_payload['s']    # signature
        except Exception as e:
            logger.error(f"[API] Invalid QR format: {e}")
            return jsonify({'result': 'No Pass', 'reason': 'Invalid QR format'}), 400
        
        # Fetch pass from database
        pass_obj = Pass.query.filter_by(pass_id=pass_id).first()
        if not pass_obj:
            create_audit_log('scan', 'PASS_NOT_FOUND', gate_id=gate_id, pass_id=pass_id, 
                           details='Pass not found in database')
            logger.warning(f"[API] Pass not found: {pass_id}")
            return jsonify({'result': 'No Pass', 'reason': 'Pass not found'}), 200
        
        # Fetch user's public key from database
        user = User.query.filter_by(iamsmart_id=pass_obj.iamsmart_id).first()
        if not user:
            create_audit_log('scan', 'USER_NOT_FOUND', gate_id=gate_id, pass_id=pass_id, 
                           details=f'User {pass_obj.iamsmart_id} not found')
            logger.warning(f"[API] User not found: {pass_obj.iamsmart_id}")
            return jsonify({'result': 'No Pass', 'reason': 'User not found'}), 200
        
        # Verify signature using public key from database
        data_to_verify = f"{pass_id}|{timestamp}"
        if not hsm.verify_signature(user.public_key, data_to_verify, signature):
            create_audit_log('scan', 'INVALID_SIGNATURE', gate_id=gate_id, pass_id=pass_id, 
                           details='Signature verification failed')
            logger.warning(f"[API] Invalid signature for pass: {pass_id}")
            return jsonify({'result': 'No Pass', 'reason': 'Invalid signature'}), 200
        
        # Check QR timestamp (1 minute expiration)
        try:
            qr_timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            age = (datetime.utcnow() - qr_timestamp).total_seconds()
            if age > Config.QR_EXPIRATION_SECONDS:
                create_audit_log('scan', 'EXPIRED_QR', gate_id=gate_id, pass_id=pass_id, 
                               details=f'QR age: {age}s')
                logger.warning(f"[API] Expired QR for pass: {pass_id} (age: {age}s)")
                return jsonify({'result': 'No Pass', 'reason': 'QR code expired'}), 200
        except:
            pass
        
        # Check system pauses
        global_pause = SystemState.query.filter_by(key='global_pause').first()
        if global_pause and global_pause.value.lower() == 'true':
            create_audit_log('scan', 'SYSTEM_PAUSED', gate_id=gate_id, pass_id=pass_id, 
                           details='Global pause active')
            logger.warning(f"[API] System paused - denying access")
            return jsonify({'result': 'No Pass', 'reason': 'System is paused'}), 200
        
        site_pauses = SystemState.query.filter_by(key='site_pauses').first()
        if site_pauses:
            pauses = json.loads(site_pauses.value)
            gate = Gate.query.filter_by(tablet_id=gate_id).first()
            if gate and gate.site_id in pauses and pauses[gate.site_id]:
                create_audit_log('scan', 'SITE_PAUSED', gate_id=gate_id, pass_id=pass_id, 
                               details=f'Site {gate.site_id} paused')
                logger.warning(f"[API] Site {gate.site_id} paused - denying access")
                return jsonify({'result': 'No Pass', 'reason': f'Site is paused'}), 200
        
        # Re-fetch pass with lock for atomic transaction
        pass_obj = Pass.query.filter_by(pass_id=pass_id).with_for_update().first()
        
        # Check pass status
        if pass_obj.status != 'Pass':
            create_audit_log('scan', 'NOT_APPROVED', gate_id=gate_id, pass_id=pass_id, 
                           details=f'Status: {pass_obj.status}')
            logger.warning(f"[API] Pass not approved: {pass_id} (status: {pass_obj.status})")
            return jsonify({'result': 'No Pass', 'reason': f'Pass not approved'}), 200
        
        if pass_obj.used_flag:
            create_audit_log('scan', 'ALREADY_USED', gate_id=gate_id, pass_id=pass_id, 
                           details='Pass already used')
            logger.warning(f"[API] Pass already used: {pass_id}")
            return jsonify({'result': 'No Pass', 'reason': 'Pass already used'}), 200
        
        if pass_obj.revoked_flag:
            create_audit_log('scan', 'REVOKED', gate_id=gate_id, pass_id=pass_id, 
                           details='Pass revoked')
            logger.warning(f"[API] Pass revoked: {pass_id}")
            return jsonify({'result': 'Revoked', 'reason': 'Pass has been revoked'}), 200
        
        # Check expiry
        if pass_obj.expiry_timestamp and datetime.utcnow() > pass_obj.expiry_timestamp:
            create_audit_log('scan', 'EXPIRED', gate_id=gate_id, pass_id=pass_id, 
                           details='Pass expired')
            logger.warning(f"[API] Pass expired: {pass_id}")
            return jsonify({'result': 'No Pass', 'reason': 'Pass expired'}), 200
        
        # Mark as used
        pass_obj.used_flag = True
        pass_obj.used_timestamp = datetime.utcnow()
        pass_obj.status = 'Used'
        db.session.commit()
        
        create_audit_log('scan', 'PASS', gate_id=gate_id, pass_id=pass_id, user_id=pass_obj.iamsmart_id,
                        details=f'Site: {pass_obj.site_id}, Purpose: {pass_obj.purpose_id}')
        
        logger.info(f"[API] Access granted for pass: {pass_id}")
        
        return jsonify({
            'result': 'Pass',
            'pass_details': {
                'pass_id': pass_obj.pass_id,
                'user': pass_obj.iamsmart_id,
                'site': pass_obj.site_id,
                'purpose': pass_obj.purpose_id
            },
            'message': 'Access granted'
        }), 200
        
    except Exception as e:
        logger.error(f"[API] Scan QR error: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/user-info', methods=['GET'])
def user_info():
    """Get user information"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        # Verify token
        user_id = verify_jwt_token(token)
        if not user_id:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        user = User.query.filter_by(iamsmart_id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        logger.error(f"[API] User info error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@api_bp.route('/sites', methods=['GET'])
def get_sites():
    """Get available sites"""
    return jsonify({'sites': Config.SITES}), 200

@api_bp.route('/purposes', methods=['GET'])
def get_purposes():
    """Get available purposes"""
    return jsonify({'purposes': Config.PURPOSES}), 200
