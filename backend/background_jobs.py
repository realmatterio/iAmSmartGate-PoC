"""
Background jobs for iAmSmartGate
"""
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def pass_expiration_check(app):
    """Check and mark expired passes"""
    with app.app_context():
        from models import db, Pass
        
        try:
            # Find passes that have expired
            expired_passes = Pass.query.filter(
                Pass.status == 'Pass',
                Pass.expiry_timestamp <= datetime.utcnow(),
                Pass.used_flag == False
            ).all()
            
            count = 0
            for pass_obj in expired_passes:
                pass_obj.status = 'Expired'
                count += 1
            
            if count > 0:
                db.session.commit()
                logger.info(f"[BACKGROUND] Marked {count} passes as expired")
            else:
                logger.debug(f"[BACKGROUND] No passes to expire")
                
        except Exception as e:
            logger.error(f"[BACKGROUND] Pass expiration check error: {e}", exc_info=True)
            db.session.rollback()

def audit_log_cleanup(app):
    """Clean up old audit logs"""
    with app.app_context():
        from models import db, AuditLog
        from config import Config
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=Config.AUDIT_LOG_RETENTION_DAYS)
            
            deleted = AuditLog.query.filter(AuditLog.timestamp < cutoff_date).delete()
            
            if deleted > 0:
                db.session.commit()
                logger.info(f"[BACKGROUND] Cleaned up {deleted} old audit logs")
            else:
                logger.debug(f"[BACKGROUND] No audit logs to clean up")
                
        except Exception as e:
            logger.error(f"[BACKGROUND] Audit log cleanup error: {e}", exc_info=True)
            db.session.rollback()

def start_background_jobs(app):
    """Start background scheduler"""
    from config import Config
    
    scheduler = BackgroundScheduler()
    
    # Pass expiration check every 5 minutes
    scheduler.add_job(
        func=lambda: pass_expiration_check(app),
        trigger='interval',
        seconds=Config.PASS_EXPIRATION_CHECK_INTERVAL,
        id='pass_expiration_check',
        name='Check expired passes',
        replace_existing=True
    )
    
    # Audit log cleanup once per day
    scheduler.add_job(
        func=lambda: audit_log_cleanup(app),
        trigger='cron',
        hour=2,
        minute=0,
        id='audit_log_cleanup',
        name='Clean up old audit logs',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("[BACKGROUND] Background jobs started")
    
    return scheduler
