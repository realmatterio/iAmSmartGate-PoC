"""
Admin routes for iAmSmartGate
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from models import db, User, Gate, Pass, AuditLog, SystemState
from crypto_utils import hsm
import json
import logging

admin_bp = Blueprint('admin', __name__)
logger = logging.getLogger(__name__)

@admin_bp.route('/pending-passes', methods=['GET'])
def pending_passes():
    """Get all pending pass applications"""
    try:
        passes = Pass.query.filter_by(status='In Process').order_by(Pass.created_timestamp.desc()).all()
        return jsonify({'passes': [p.to_dict() for p in passes]}), 200
    except Exception as e:
        logger.error(f"[ADMIN] Get pending passes error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/all-passes', methods=['GET'])
def all_passes():
    """Get all passes"""
    try:
        status_filter = request.args.get('status')
        site_filter = request.args.get('site_id')
        
        query = Pass.query
        if status_filter:
            query = query.filter_by(status=status_filter)
        if site_filter:
            query = query.filter_by(site_id=site_filter)
        
        passes = query.order_by(Pass.created_timestamp.desc()).all()
        return jsonify({'passes': [p.to_dict() for p in passes]}), 200
    except Exception as e:
        logger.error(f"[ADMIN] Get all passes error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/approve-pass/<pass_id>', methods=['POST'])
def approve_pass(pass_id):
    """Approve a pass application"""
    try:
        data = request.json or {}
        expiry_hours = data.get('expiry_hours', 24)  # Default 24 hours
        
        pass_obj = Pass.query.filter_by(pass_id=pass_id).first()
        if not pass_obj:
            return jsonify({'error': 'Pass not found'}), 404
        
        if pass_obj.status != 'In Process':
            return jsonify({'error': f'Pass cannot be approved (status: {pass_obj.status})'}), 400
        
        pass_obj.status = 'Pass'
        pass_obj.approved_timestamp = datetime.utcnow()
        pass_obj.expiry_timestamp = datetime.utcnow() + timedelta(hours=expiry_hours)
        db.session.commit()
        
        # Audit log
        audit = AuditLog(
            event_type='approval',
            pass_id=pass_id,
            user_id=pass_obj.iamsmart_id,
            result='APPROVED',
            details=f'Expiry: {expiry_hours}h'
        )
        db.session.add(audit)
        db.session.commit()
        
        logger.info(f"[ADMIN] Pass approved: {pass_id}")
        
        return jsonify({
            'message': 'Pass approved',
            'pass': pass_obj.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"[ADMIN] Approve pass error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/reject-pass/<pass_id>', methods=['POST'])
def reject_pass(pass_id):
    """Reject a pass application"""
    try:
        data = request.json or {}
        reason = data.get('reason', 'No reason provided')
        
        pass_obj = Pass.query.filter_by(pass_id=pass_id).first()
        if not pass_obj:
            return jsonify({'error': 'Pass not found'}), 404
        
        if pass_obj.status != 'In Process':
            return jsonify({'error': f'Pass cannot be rejected (status: {pass_obj.status})'}), 400
        
        pass_obj.status = 'No Pass'
        db.session.commit()
        
        # Audit log
        audit = AuditLog(
            event_type='rejection',
            pass_id=pass_id,
            user_id=pass_obj.iamsmart_id,
            result='REJECTED',
            details=reason
        )
        db.session.add(audit)
        db.session.commit()
        
        logger.info(f"[ADMIN] Pass rejected: {pass_id}")
        
        return jsonify({
            'message': 'Pass rejected',
            'pass': pass_obj.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"[ADMIN] Reject pass error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/revoke-pass/<pass_id>', methods=['POST'])
def revoke_pass(pass_id):
    """Revoke an approved pass"""
    try:
        data = request.json or {}
        reason = data.get('reason', 'No reason provided')
        
        pass_obj = Pass.query.filter_by(pass_id=pass_id).first()
        if not pass_obj:
            return jsonify({'error': 'Pass not found'}), 404
        
        pass_obj.revoked_flag = True
        pass_obj.status = 'Revoked'
        db.session.commit()
        
        # Audit log
        audit = AuditLog(
            event_type='revoke',
            pass_id=pass_id,
            user_id=pass_obj.iamsmart_id,
            result='REVOKED',
            details=reason
        )
        db.session.add(audit)
        db.session.commit()
        
        logger.info(f"[ADMIN] Pass revoked: {pass_id}")
        
        return jsonify({
            'message': 'Pass revoked',
            'pass': pass_obj.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"[ADMIN] Revoke pass error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/pause-system', methods=['POST'])
def pause_system():
    """Pause/unpause entire system"""
    try:
        data = request.json
        paused = data.get('paused', True)
        
        state = SystemState.query.filter_by(key='global_pause').first()
        if state:
            state.value = 'true' if paused else 'false'
            state.updated_at = datetime.utcnow()
        else:
            state = SystemState(key='global_pause', value='true' if paused else 'false')
            db.session.add(state)
        
        db.session.commit()
        
        # Audit log
        audit = AuditLog(
            event_type='pause',
            result='SYSTEM_PAUSED' if paused else 'SYSTEM_RESUMED',
            details='Global system pause toggled'
        )
        db.session.add(audit)
        db.session.commit()
        
        logger.info(f"[ADMIN] System {'paused' if paused else 'resumed'}")
        
        return jsonify({
            'message': f"System {'paused' if paused else 'resumed'}",
            'paused': paused
        }), 200
        
    except Exception as e:
        logger.error(f"[ADMIN] Pause system error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/pause-site', methods=['POST'])
def pause_site():
    """Pause/unpause specific site"""
    try:
        data = request.json
        site_id = data.get('site_id')
        paused = data.get('paused', True)
        
        if not site_id:
            return jsonify({'error': 'Missing site_id'}), 400
        
        state = SystemState.query.filter_by(key='site_pauses').first()
        if state:
            pauses = json.loads(state.value)
        else:
            pauses = {}
        
        pauses[site_id] = paused
        
        if state:
            state.value = json.dumps(pauses)
            state.updated_at = datetime.utcnow()
        else:
            state = SystemState(key='site_pauses', value=json.dumps(pauses))
            db.session.add(state)
        
        db.session.commit()
        
        # Audit log
        audit = AuditLog(
            event_type='pause',
            result=f'SITE_{"PAUSED" if paused else "RESUMED"}',
            details=f'Site {site_id} pause toggled'
        )
        db.session.add(audit)
        db.session.commit()
        
        logger.info(f"[ADMIN] Site {site_id} {'paused' if paused else 'resumed'}")
        
        return jsonify({
            'message': f"Site {site_id} {'paused' if paused else 'resumed'}",
            'site_id': site_id,
            'paused': paused
        }), 200
        
    except Exception as e:
        logger.error(f"[ADMIN] Pause site error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/system-status', methods=['GET'])
def system_status():
    """Get system status"""
    try:
        global_pause = SystemState.query.filter_by(key='global_pause').first()
        site_pauses = SystemState.query.filter_by(key='site_pauses').first()
        
        return jsonify({
            'global_pause': global_pause.value.lower() == 'true' if global_pause else False,
            'site_pauses': json.loads(site_pauses.value) if site_pauses else {}
        }), 200
        
    except Exception as e:
        logger.error(f"[ADMIN] Get system status error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/statistics', methods=['GET'])
def statistics():
    """Get system statistics"""
    try:
        site_id = request.args.get('site_id')
        
        stats = {}
        
        # Overall statistics
        stats['total_users'] = User.query.count()
        stats['total_gates'] = Gate.query.count()
        stats['total_passes'] = Pass.query.count()
        
        # Pass statistics by status
        for status in ['In Process', 'Pass', 'No Pass', 'Used', 'Revoked']:
            query = Pass.query.filter_by(status=status)
            if site_id:
                query = query.filter_by(site_id=site_id)
            stats[f'passes_{status.lower().replace(" ", "_")}'] = query.count()
        
        # Site-specific statistics
        if site_id:
            stats['site_id'] = site_id
        else:
            site_stats = {}
            for site_id_key in ['SITE001', 'SITE002', 'SITE003', 'SITE004']:
                site_stats[site_id_key] = {
                    'approved': Pass.query.filter_by(site_id=site_id_key, status='Pass').count(),
                    'requested': Pass.query.filter_by(site_id=site_id_key, status='In Process').count(),
                    'used': Pass.query.filter_by(site_id=site_id_key, status='Used').count(),
                    'revoked': Pass.query.filter_by(site_id=site_id_key, status='Revoked').count()
                }
            stats['by_site'] = site_stats
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"[ADMIN] Get statistics error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/audit-logs', methods=['GET'])
def audit_logs():
    """Get audit logs"""
    try:
        limit = int(request.args.get('limit', 100))
        event_type = request.args.get('event_type')
        
        query = AuditLog.query
        if event_type:
            query = query.filter_by(event_type=event_type)
        
        logs = query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
        
        return jsonify({'logs': [log.to_dict() for log in logs]}), 200
        
    except Exception as e:
        logger.error(f"[ADMIN] Get audit logs error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/register-gate', methods=['POST'])
def register_gate():
    """Register a new gate"""
    try:
        data = request.json
        tablet_id = data.get('tablet_id')
        gps_location = data.get('gps_location')
        site_id = data.get('site_id')
        
        if not all([tablet_id, gps_location, site_id]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if gate already exists
        existing = Gate.query.filter_by(tablet_id=tablet_id).first()
        if existing:
            return jsonify({'error': 'Gate already registered'}), 409
        
        # Generate key pair
        key_ref, public_key = hsm.generate_key_pair(f"gate_{tablet_id}")
        
        # Create gate
        gate = Gate(
            tablet_id=tablet_id,
            gps_location=gps_location,
            public_key=public_key,
            private_key_ref=key_ref,
            site_id=site_id
        )
        db.session.add(gate)
        db.session.commit()
        
        logger.info(f"[ADMIN] Gate registered: {tablet_id}")
        
        return jsonify({
            'message': 'Gate registered',
            'gate': gate.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"[ADMIN] Register gate error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500
@admin_bp.route('/hsm/query-public-key/<user_id>', methods=['GET'])
def query_public_key(user_id):
    """Query HSM for user public key via PKCS#11 interface"""
    try:
        # Query user from database
        user = User.query.filter_by(iamsmart_id=user_id).first()
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Get public key from HSM
        public_key = user.public_key
        
        # Log the query
        audit = AuditLog(
            event_type='hsm_query',
            user_id=user_id,
            result='SUCCESS',
            details='PKCS#11 public key query'
        )
        db.session.add(audit)
        db.session.commit()
        
        logger.info(f"[HSM] Public key queried for user: {user_id}")
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'algorithm': 'Dilithium3 (Post-Quantum)',
            'key_size': 2592,  # Dilithium3 public key size
            'created_at': user.registered_timestamp.isoformat(),
            'public_key': public_key
        }), 200
        
    except Exception as e:
        logger.error(f"[HSM] Query public key error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@admin_bp.route('/hsm/signature-logs', methods=['GET'])
def signature_logs():
    """Get HSM signature operation logs"""
    try:
        filter_type = request.args.get('filter', 'all')
        
        # Query audit logs for signature operations
        query = AuditLog.query.filter(
            AuditLog.event_type.in_(['sign', 'verify', 'pass_sign', 'gate_verify'])
        )
        
        logs = query.order_by(AuditLog.timestamp.desc()).limit(100).all()
        
        # Format logs for HSM console
        formatted_logs = []
        for log in logs:
            # Determine operation type
            operation = 'SIGN' if 'sign' in log.event_type else 'VERIFY'
            
            # Apply filter
            if filter_type == 'sign' and operation != 'SIGN':
                continue
            if filter_type == 'verify' and operation != 'VERIFY':
                continue
            if filter_type == 'success' and log.result not in ['SUCCESS', 'VERIFIED', 'PASS']:
                continue
            if filter_type == 'failed' and log.result in ['SUCCESS', 'VERIFIED', 'PASS']:
                continue
            
            formatted_logs.append({
                'timestamp': log.timestamp.isoformat(),
                'operation': operation,
                'user_id': log.user_id or 'N/A',
                'pass_id': log.pass_id or None,
                'gate_id': log.gate_id or None,
                'status': log.result or 'UNKNOWN',
                'details': log.details or f'{operation} operation completed'
            })
        
        return jsonify({'logs': formatted_logs}), 200
        
    except Exception as e:
        logger.error(f"[HSM] Get signature logs error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500