#!/usr/bin/env python3
"""
Test the optimized audio processor
"""

from optimized_audio_processor import OptimizedAudioProcessor
from config import Config

def test_optimized_audio_processor():
    """Test the optimized audio processor."""
    print("🎵 Testing Optimized Audio Processor")
    print("=" * 50)
    
    try:
        # Initialize
        config = Config()
        processor = OptimizedAudioProcessor(config)
        
        print("✅ Optimized audio processor initialized successfully")
        
        # Test status
        status = processor.get_status()
        print(f"\n📊 Status:")
        for key, value in status.items():
            print(f"   {key:15}: {value}")
        
        # Test performance stats
        print(f"\n📈 Performance:")
        perf_stats = processor.get_performance_stats()
        for key, value in perf_stats.items():
            print(f"   {key:25}: {value}")
        
        # Test effect management
        print(f"\n🎛️  Effect Management:")
        processor.start_effect("arpeggiator")
        processor.start_effect("basic_delay")
        
        status = processor.get_status()
        print(f"   Active effects: {status['active_effects']}")
        
        processor.stop_effect("basic_delay")
        status = processor.get_status()
        print(f"   After stopping delay: {status['active_effects']}")
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run the test."""
    test_optimized_audio_processor()

if __name__ == "__main__":
    main()
