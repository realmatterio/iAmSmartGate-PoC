"""Check signature length from database"""
from models import db, Pass
from app import create_app

app = create_app()

with app.app_context():
    passes = Pass.query.filter(Pass.qr_signature.isnot(None)).first()
    
    if passes and passes.qr_signature:
        sig_hex_len = len(passes.qr_signature)
        sig_bytes_len = sig_hex_len // 2
        
        print(f"\n{'='*60}")
        print("CURRENT SIGNATURE (RSA 2048-bit with PSS)")
        print(f"{'='*60}")
        print(f"Signature length (hex):   {sig_hex_len} characters")
        print(f"Signature length (bytes): {sig_bytes_len} bytes")
        print(f"First 100 chars: {passes.qr_signature[:100]}")
        print(f"\n{'='*60}")
        print("POST-QUANTUM CRYPTOGRAPHY (PQC) SIGNATURE COMPARISON")
        print(f"{'='*60}\n")
        
        print("NIST PQC Selected Algorithms (2022):")
        print("-" * 60)
        print(f"{'Algorithm':<25} {'Signature Size':<20} {'vs Current':<15}")
        print("-" * 60)
        
        # NIST selected algorithms
        algorithms = [
            ("Current (RSA-2048 PSS)", sig_bytes_len, 1.0),
            ("CRYSTALS-Dilithium2", 2420, 2420/sig_bytes_len),
            ("CRYSTALS-Dilithium3", 3293, 3293/sig_bytes_len),
            ("CRYSTALS-Dilithium5", 4595, 4595/sig_bytes_len),
            ("FALCON-512", 666, 666/sig_bytes_len),
            ("FALCON-1024", 1280, 1280/sig_bytes_len),
            ("SPHINCS+-128f", 17088, 17088/sig_bytes_len),
            ("SPHINCS+-128s", 7856, 7856/sig_bytes_len),
            ("SPHINCS+-256f", 49856, 49856/sig_bytes_len),
        ]
        
        for name, size, ratio in algorithms:
            comparison = f"{ratio:.2f}x" if ratio != 1.0 else "baseline"
            print(f"{name:<25} {size:>8} bytes     {comparison:>12}")
        
        print("\n" + "=" * 60)
        print("KEY INSIGHTS:")
        print("=" * 60)
        print(f"• FALCON-512 is {666/sig_bytes_len:.1f}x LARGER than current RSA")
        print(f"• Dilithium2 is {2420/sig_bytes_len:.1f}x LARGER than current RSA")
        print(f"• SPHINCS+ variants are {7856/sig_bytes_len:.1f}x to {49856/sig_bytes_len:.1f}x LARGER")
        print(f"\n• Current RSA-2048: {sig_bytes_len} bytes")
        print(f"• Best PQC option (FALCON-512): 666 bytes")
        print(f"• Most common PQC (Dilithium2): 2420 bytes")
        print(f"\nAll PQC signatures are significantly LARGER than classical RSA!")
        print("=" * 60 + "\n")
        
    else:
        print("No signatures found in database. Generate a QR code first.")
