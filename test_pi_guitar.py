#!/usr/bin/env python3
"""
Simple test script for Raspberry Pi with real guitar input
This will test the enhanced detection system with actual guitar chords
"""

from arpeggiator import WorkingArpeggiatorSystem
from config import Config
import time

def test_pi_guitar():
    """Test the working arpeggiator with real guitar on Pi"""
    print("🎸 RASPBERRY PI GUITAR TEST")
    print("=" * 50)
    
    try:
        # Initialize the working arpeggiator system
        config = Config()
        arpeggiator = WorkingArpeggiatorSystem(config)
        
        print("✅ Working arpeggiator system initialized")
        print(f"📊 Sample rate: {config.sample_rate} Hz")
        print(f"🔧 Audio backend: {config.audio_backend}")
        
        # Show current status
        status = arpeggiator.get_status()
        print("\n📊 System Status:")
        for key, value in status.items():
            print(f"  {key:20}: {value}")
        
        print("\n🎵 Testing demo mode (C major arpeggio):")
        arpeggiator.demo_mode()
        
        print("\n" + "="*50)
        print("🎸 READY FOR LIVE GUITAR TESTING!")
        print("="*50)
        print("💡 To test with your guitar:")
        print("   1. Connect guitar to Scarlett 2i2 input")
        print("   2. Run: python3 arpeggiator/working_arpeggiator.py")
        print("   3. Type 'start' to begin chord detection")
        print("   4. Strum these chords to test:")
        print("      • C major (C-E-G)")
        print("      • G major (G-B-D)")  
        print("      • A minor (A-C-E)")
        print("      • F major (F-A-C)")
        print("   5. Listen for arpeggios!")
        print("\n💡 Or test through interactive CLI:")
        print("   python3 interactive_cli.py")
        print("   select arpeggiator")
        print("   start")
        
        print("\n✅ All systems ready for real guitar testing!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pi_guitar()
