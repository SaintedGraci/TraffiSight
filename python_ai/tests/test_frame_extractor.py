"""
Unit tests for FrameExtractor
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.core.video_loader import VideoLoader
from src.core.frame_extractor import FrameExtractor


def test_frame_extraction(video_path: str):
    """Test frame extraction functionality"""
    print("\n" + "="*60)
    print("TEST: Frame Extraction")
    print("="*60)
    
    try:
        with VideoLoader(video_path) as loader:
            extractor = FrameExtractor(loader)
            
            # Test sample frame extraction
            print("\n1. Testing sample frame extraction...")
            samples = extractor.extract_sample_frames(num_samples=5)
            assert len(samples) == 5, f"Expected 5 samples, got {len(samples)}"
            print(f"✓ Extracted {len(samples)} sample frames")
            
            # Verify sample structure
            for i, (frame_num, frame, timestamp) in enumerate(samples):
                assert frame is not None, f"Sample {i} frame is None"
                assert frame.shape[0] > 0 and frame.shape[1] > 0, "Invalid frame dimensions"
                print(f"  Sample {i+1}: Frame #{frame_num}, Time: {timestamp:.2f}s, Shape: {frame.shape}")
            
            # Test interval extraction
            print("\n2. Testing interval extraction...")
            interval_frames = extractor.extract_frames_at_intervals(interval_seconds=1.0, max_frames=3)
            assert len(interval_frames) > 0, "Should extract frames at intervals"
            print(f"✓ Extracted {len(interval_frames)} frames at 1s intervals")
            
            # Test thumbnail creation
            print("\n3. Testing thumbnail creation...")
            thumbnail_path = Path("./output/test_thumbnail.jpg")
            success = extractor.create_thumbnail(thumbnail_path)
            assert success, "Thumbnail creation should succeed"
            assert thumbnail_path.exists(), "Thumbnail file should exist"
            print(f"✓ Thumbnail created: {thumbnail_path}")
            
            # Cleanup
            if thumbnail_path.exists():
                thumbnail_path.unlink()
            
            print("\n✅ ALL FRAME EXTRACTOR TESTS PASSED!")
            return True
            
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_frame_extractor.py <video_path>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    success = test_frame_extraction(video_path)
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Frame Extraction Test: {'✅ PASSED' if success else '❌ FAILED'}")
    print("="*60)
    
    sys.exit(0 if success else 1)
