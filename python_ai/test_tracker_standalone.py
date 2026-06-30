"""
Standalone test for ByteTracker (no dependencies)
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple


@dataclass
class SimpleDetection:
    """Simple detection for testing"""
    bbox: Tuple[int, int, int, int]
    confidence: float
    class_id: int
    class_name: str
    
    @property
    def center_x(self):
        return (self.bbox[0] + self.bbox[2]) // 2
    
    @property
    def center_y(self):
        return (self.bbox[1] + self.bbox[3]) // 2


def test_tracker():
    """Test ByteTracker with minimal setup"""
    print("=" * 60)
    print("ByteTracker Standalone Test")
    print("=" * 60)
    
    # Import ByteTracker
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent / 'src'))
    
    try:
        from models.byte_tracker import ByteTracker, Track
        print("✓ ByteTracker imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import ByteTracker: {e}")
        return False
    
    # Initialize tracker
    try:
        tracker = ByteTracker(max_age=30, min_hits=3, iou_threshold=0.3)
        print("✓ ByteTracker initialized")
    except Exception as e:
        print(f"✗ Failed to initialize ByteTracker: {e}")
        return False
    
    # Test tracking across multiple frames
    print("\n" + "=" * 60)
    print("Testing Multi-Frame Tracking")
    print("=" * 60)
    
    # Frame 1
    print("\nFrame 1: 2 vehicles detected")
    det1 = SimpleDetection((100, 100, 200, 200), 0.9, 2, 'car')
    det2 = SimpleDetection((300, 150, 400, 250), 0.85, 2, 'car')
    
    try:
        tracks = tracker.update([det1, det2])
        print(f"  Active tracks: {len(tracks)} (confirmed)")
        print(f"  Total tracks: {len(tracker.get_all_tracks())} (including tentative)")
    except Exception as e:
        print(f"✗ Frame 1 failed: {e}")
        return False
    
    # Frame 2
    print("\nFrame 2: Vehicles moved slightly")
    det1 = SimpleDetection((110, 105, 210, 205), 0.88, 2, 'car')
    det2 = SimpleDetection((310, 155, 410, 255), 0.87, 2, 'car')
    
    try:
        tracks = tracker.update([det1, det2])
        print(f"  Active tracks: {len(tracks)} (confirmed)")
        print(f"  Total tracks: {len(tracker.get_all_tracks())}")
    except Exception as e:
        print(f"✗ Frame 2 failed: {e}")
        return False
    
    # Frame 3 (tracks should be confirmed now)
    print("\nFrame 3: Vehicles moved more")
    det1 = SimpleDetection((120, 110, 220, 210), 0.91, 2, 'car')
    det2 = SimpleDetection((320, 160, 420, 260), 0.89, 2, 'car')
    
    try:
        tracks = tracker.update([det1, det2])
        print(f"  Active tracks: {len(tracks)} (confirmed)")
        print(f"  Total tracks: {len(tracker.get_all_tracks())}")
        
        for track in tracks:
            velocity = track.get_velocity()
            trajectory = track.get_trajectory()
            print(f"    Track ID {track.track_id}: {track.class_name}, "
                  f"trajectory: {len(trajectory)} points, velocity: {velocity}")
    except Exception as e:
        print(f"✗ Frame 3 failed: {e}")
        return False
    
    # Frame 4 (one exits, one new enters)
    print("\nFrame 4: One vehicle exits, new one enters")
    det1 = SimpleDetection((330, 165, 430, 265), 0.86, 2, 'car')
    det2 = SimpleDetection((500, 200, 600, 300), 0.92, 3, 'motorcycle')
    
    try:
        tracks = tracker.update([det1, det2])
        print(f"  Active tracks: {len(tracks)} (confirmed)")
        print(f"  Total tracks: {len(tracker.get_all_tracks())}")
    except Exception as e:
        print(f"✗ Frame 4 failed: {e}")
        return False
    
    # Get statistics
    print("\n" + "=" * 60)
    print("Tracker Statistics")
    print("=" * 60)
    
    try:
        stats = tracker.get_statistics()
        for key, value in stats.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"✗ Failed to get statistics: {e}")
        return False
    
    # Test reset
    print("\n" + "=" * 60)
    print("Testing Reset")
    print("=" * 60)
    
    try:
        tracker.reset()
        stats = tracker.get_statistics()
        print(f"  Total tracks after reset: {stats['total_tracks']}")
        print(f"  Frame count after reset: {stats['frame_count']}")
    except Exception as e:
        print(f"✗ Reset failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ All tests passed successfully!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_tracker()
    exit(0 if success else 1)
