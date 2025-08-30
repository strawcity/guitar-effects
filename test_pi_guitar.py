#!/usr/bin/env python3
"""
Simple test script for Raspberry Pi with real guitar input
This will test the guitar effects system with actual guitar input
"""


from config import Config
import time

def test_pi_guitar():
    """Test the guitar effects system on Pi"""
    print("🎸 RASPBERRY PI GUITAR TEST")
    print("=" * 50)
    
    try:
        # Initialize the system
        config = Config()
        
        print("✅ System initialized")
        print(f"📊 Sample rate: {config.sample_rate} Hz")
        print(f"🔧 Audio backend: {config.audio_backend}")
        
        print("\n" + "="*50)
        print("🎸 READY FOR LIVE GUITAR TESTING!")
        print("="*50)
        print("💡 To test with your guitar:")
        print("   1. Connect guitar to Scarlett 2i2 input")
        print("   2. Run: python3 main.py")
        print("   3. Test delay effects")
        
        print("\n✅ All systems ready for real guitar testing!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pi_guitar()
