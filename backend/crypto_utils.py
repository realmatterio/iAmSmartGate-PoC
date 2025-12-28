"""
Dummy HSM and Crypto functions for iAmSmartGate
Simulates Hardware Security Module with in-memory key storage
"""
import os
import json
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import logging

logger = logging.getLogger(__name__)

class DummyHSM:
    """Dummy HSM for key generation and signing"""
    
    def __init__(self, storage_file='hsm_keys.json'):
        self.storage_file = storage_file
        self.keys = {}
        self.load_keys()
    
    def load_keys(self):
        """Load keys from file"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    for key_id, key_data in data.items():
                        # Load private key
                        private_key = serialization.load_pem_private_key(
                            key_data['private_key'].encode(),
                            password=None,
                            backend=default_backend()
                        )
                        # Load public key
                        public_key = serialization.load_pem_public_key(
                            key_data['public_key'].encode(),
                            backend=default_backend()
                        )
                        self.keys[key_id] = {
                            'private_key': private_key,
                            'public_key': public_key
                        }
                logger.info(f"Loaded {len(self.keys)} keys from HSM storage")
            except Exception as e:
                logger.error(f"Error loading HSM keys: {e}")
                self.keys = {}
        else:
            logger.info("No HSM storage file found, starting fresh")
    
    def save_keys(self):
        """Save keys to file"""
        try:
            data = {}
            for key_id, key_pair in self.keys.items():
                # Serialize private key
                private_pem = key_pair['private_key'].private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ).decode()
                # Serialize public key
                public_pem = key_pair['public_key'].public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ).decode()
                data[key_id] = {
                    'private_key': private_pem,
                    'public_key': public_pem
                }
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Saved {len(self.keys)} keys to HSM storage")
        except Exception as e:
            logger.error(f"Error saving HSM keys: {e}")
    
    def generate_key_pair(self, key_id):
        """Generate RSA key pair"""
        try:
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            public_key = private_key.public_key()
            
            # Store in memory
            self.keys[key_id] = {
                'private_key': private_key,
                'public_key': public_key
            }
            
            # Persist to disk
            self.save_keys()
            
            # Return public key as PEM
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode()
            
            logger.info(f"Generated key pair for {key_id}")
            return key_id, public_pem
        except Exception as e:
            logger.error(f"Error generating key pair: {e}")
            raise
    
    def sign_data(self, key_id, data):
        """Sign data with private key"""
        try:
            if key_id not in self.keys:
                raise ValueError(f"Key {key_id} not found in HSM")
            
            private_key = self.keys[key_id]['private_key']
            
            # Convert data to bytes if string
            if isinstance(data, str):
                data = data.encode()
            
            # Sign with RSA-PSS
            signature = private_key.sign(
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            logger.debug(f"Signed data for key {key_id}")
            return signature.hex()
        except Exception as e:
            logger.error(f"Error signing data: {e}")
            raise
    
    def verify_signature(self, public_key_pem, data, signature):
        """Verify signature with public key"""
        try:
            # Load public key
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode(),
                backend=default_backend()
            )
            
            # Convert data to bytes if string
            if isinstance(data, str):
                data = data.encode()
            
            # Convert hex signature to bytes
            signature_bytes = bytes.fromhex(signature)
            
            # Verify with RSA-PSS
            public_key.verify(
                signature_bytes,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            logger.debug("Signature verification successful")
            return True
        except Exception as e:
            logger.warning(f"Signature verification failed: {e}")
            return False
    
    def get_public_key(self, key_id):
        """Get public key for a key ID"""
        if key_id not in self.keys:
            raise ValueError(f"Key {key_id} not found in HSM")
        
        public_key = self.keys[key_id]['public_key']
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()
        
        return public_pem

# Global HSM instance
hsm = DummyHSM()
