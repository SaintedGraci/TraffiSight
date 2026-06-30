"""
Unit tests for VideoLoader
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.core.video_loader import VideoLoader
from src.utils.logger import Logger


def test_video_loading(video_path: str):
    """Test basic video loading"""
    print("\n" + "="*60)
    print("TEST: Video Loading")
    print("="*60)
    
    try:
        loader = VideoLoader(video_path)
        
        # Check if video opened
        assert loader.is_opened, "Video should be opened"
        print("✓ Video opened successfully")
        
        # Check metadata
        assert loader.width > 0, "Width should be positive"
        assert loader.height > 0, "Height should be positive"
        assert loader.fps > 0, "FPS should be positive"
        assert loader.frame_count > 0, "Frame count should be positive"
        print(f"✓ Metadata loaded: {loader.width}x{loader.height}, {loader.fps:.2f} FPS")
        
        # Test frame reading
        success, frame = loader.read_frame()
        assert success, "Should read first frame"
        assert frame is not None, "Frame should not be None"
        print(f"✓ Frame read successfully: {frame.shape}")
        
        # Test get_frame_at
        mid_frame = loader.get_frame_at(loader.frame_count // 2)
        assert mid_frame is not None, "Should get middle frame"
        print("✓ Random frame access works")
        
        # Test metadata dictionary
        metadata = loader.get_metadata()
        assert 'width' in metadata, "Metadata should have width"
        assert 'height' in metadata, "Metadata should have height"
        print("✓ Metadata dictionary complete")
        
        loader.release()
        print("✓ Video released")
        
        print("\n✅ ALL VIDEO LOADER TESTS PASSED!")
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def test_context_manager(video_path: str):
    """Test context manager usage"""
    print("\n" + "="*60)
    print("TEST: Context Manager")
    print("="*60)
    
    try:
        with VideoLoader(video_path) as loader:
            print(f"✓ Context manager entered")
            success, frame = loader.read_frame()
            assert success, "Should read frame"
            print(f"✓ Frame read: {frame.shape}")
        
        print("✓ Context manager exited cleanly")
        print("\n✅ CONTEXT MANAGER TEST PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_video_loader.py <video_path>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    # Run tests
    test1 = test_video_loading(video_path)
    test2 = test_context_manager(video_path)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Video Loading Test: {'✅ PASSED' if test1 else '❌ FAILED'}")
    print(f"Context Manager Test: {'✅ PASSED' if test2 else '❌ FAILED'}")
    print("="*60)
    
    sys.exit(0 if (test1 and test2) else 1)
