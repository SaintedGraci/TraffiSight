"""
Test ByteTracker functionality
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.yolo_detector import Detection
from src.models.byte_tracker import ByteTracker, Track


def test_basic_tracking():
    """Test basic tracking functionality"""
    print("Testing ByteTracker...")
    
    # Initialize tracker
    tracker = ByteTracker(
        max_age=30,
        min_hits=3,
        iou_threshold=0.3
    )
    
    # Simulate detections across frames
    print("\n=== Frame 1 ===")
    detections_frame1 = [
        Detection((100, 100, 200, 200), 0.9, 2, 'car'),
        Detection((300, 150, 400, 250), 0.85, 2, 'car'),
    ]
    
    tracks = tracker.update(detections_frame1)
    print(f"Detections: {len(detections_frame1)}")
    print(f"Confirmed tracks: {len(tracks)}")
    for track in tracker.get_all_tracks():
        print(f"  {track}")
    
    # Frame 2 - same vehicles moved slightly
    print("\n=== Frame 2 ===")
    detections_frame2 = [
        Detection((110, 105, 210, 205), 0.88, 2, 'car'),
        Detection((310, 155, 410, 255), 0.87, 2, 'car'),
    ]
    
    tracks = tracker.update(detections_frame2)
    print(f"Detections: {len(detections_frame2)}")
    print(f"Confirmed tracks: {len(tracks)}")
    for track in tracker.get_all_tracks():
        print(f"  {track}")
    
    # Frame 3 - vehicles moved more
    print("\n=== Frame 3 ===")
    detections_frame3 = [
        Detection((120, 110, 220, 210), 0.91, 2, 'car'),
        Detection((320, 160, 420, 260), 0.89, 2, 'car'),
    ]
    
    tracks = tracker.update(detections_frame3)
    print(f"Detections: {len(detections_frame3)}")
    print(f"Confirmed tracks: {len(tracks)}")
    for track in tracker.get_all_tracks():
        print(f"  {track}")
    
    # Frame 4 - one vehicle exits, new one enters
    print("\n=== Frame 4 ===")
    detections_frame4 = [
        Detection((330, 165, 430, 265), 0.86, 2, 'car'),  # Existing vehicle
        Detection((500, 200, 600, 300), 0.92, 3, 'motorcycle'),  # New vehicle
    ]
    
    tracks = tracker.update(detections_frame4)
    print(f"Detections: {len(detections_frame4)}")
    print(f"Confirmed tracks: {len(tracks)}")
    for track in tracker.get_all_tracks():
        print(f"  {track}")
    
    # Get statistics
    print("\n=== Final Statistics ===")
    stats = tracker.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Test trajectory
    print("\n=== Testing Trajectory ===")
    for track in tracks:
        trajectory = track.get_trajectory()
        velocity = track.get_velocity()
        print(f"Track {track.track_id}: {len(trajectory)} points, velocity: {velocity}")
    
    print("\n✓ ByteTracker test completed successfully!")


if __name__ == "__main__":
    test_basic_tracking()
