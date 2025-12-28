"""
Dummy external integration stubs
"""
import logging
import time

logger = logging.getLogger(__name__)

def dummy_iamsmart_authenticate(iamsmart_id, password):
    """
    Dummy iAmSmart authentication
    Returns True for demo purposes with specific test credentials
    """
    logger.info(f"[DUMMY iAmSmart] Authenticating user: {iamsmart_id}")
    
    # Simulate network delay
    time.sleep(0.5)
    
    # Test mode: accept specific credentials or any ID starting with 'USER'
    if iamsmart_id.startswith('USER') or iamsmart_id.startswith('GATE'):
        logger.info(f"[DUMMY iAmSmart] Authentication SUCCESS for {iamsmart_id}")
        return True
    
    # For demo, accept password 'demo123' for any user
    if password == 'demo123':
        logger.info(f"[DUMMY iAmSmart] Authentication SUCCESS for {iamsmart_id} with demo password")
        return True
    
    logger.warning(f"[DUMMY iAmSmart] Authentication FAILED for {iamsmart_id}")
    return False

def dummy_validate_gps(tablet_id, reported_gps, expected_gps):
    """
    Dummy GPS validation
    Returns True for demo purposes
    Note: Browser geolocation is spoofable - for demo only
    """
    logger.info(f"[DUMMY GPS] Validating location for {tablet_id}")
    logger.debug(f"[DUMMY GPS] Reported: {reported_gps}, Expected: {expected_gps}")
    
    # For demo, accept any GPS within reasonable range or exact match
    if reported_gps == expected_gps:
        logger.info(f"[DUMMY GPS] Exact match - VALID")
        return True
    
    # Simple validation - check if coordinates are close (demo only)
    try:
        reported_parts = reported_gps.split(',')
        expected_parts = expected_gps.split(',')
        if len(reported_parts) == 2 and len(expected_parts) == 2:
            reported_lat = float(reported_parts[0])
            reported_lng = float(reported_parts[1])
            expected_lat = float(expected_parts[0])
            expected_lng = float(expected_parts[1])
            
            # Accept within 0.01 degrees (roughly 1km)
            if abs(reported_lat - expected_lat) < 0.01 and abs(reported_lng - expected_lng) < 0.01:
                logger.info(f"[DUMMY GPS] Within tolerance - VALID")
                return True
    except:
        pass
    
    # For demo purposes, accept anyway with warning
    logger.warning(f"[DUMMY GPS] Location mismatch but accepting for demo")
    return True
