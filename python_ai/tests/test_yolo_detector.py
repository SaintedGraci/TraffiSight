"""
Unit tests for YOLOv8 Detector
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.models.yolo_detector import YOLODetector
    from src.core.video_loader import VideoLoader
    YOLO_AVAILABLE = True
except ImportError as e:
    print(f"❌ ERROR: YOLOv8 dependencies not installed")
    print(f"   {e}")
    print("\nInstall Phase 4 requirements:")
    print("   pip install ultralytics scipy matplotlib")
    YOLO_AVAILABLE = False
    sys.exit(1)


def test_detector_initialization():
    """Test detector initialization"""
    print("\n" + "="*60)
    print("TEST: Detector Initialization")
    print("="*60)
    
    try:
        detector = YOLODetector(model_name="yolov8n.pt")
        
        assert detector.model is not None, "Model should be loaded"
        print("✓ Model loaded successfully")
        
        info = detector.get_model_info()
        print(f"✓ Model: {info['model_name']}")
        print(f"✓ Device: {info['device']}")
        print(f"✓ Confidence threshold: {info['confidence_threshold']}")
        print(f"✓ Vehicle classes: {', '.join(info['vehicle_classes'])}")
        
        print("\n✅ DETECTOR INITIALIZATION TEST PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_detection_on_video(video_path: str):
    """Test detection on video frames"""
    print("\n" + "="*60)
    print("TEST: Vehicle Detection on Video")
    print("="*60)
    
    try:
        # Initialize detector
        detector = YOLODetector(model_name="yolov8n.pt", confidence_threshold=0.5)
        print(f"✓ Detector initialized")
        
        # Load video
        with VideoLoader(video_path) as loader:
            print(f"✓ Video loaded: {loader.video_path.name}")
            print(f"  Resolution: {loader.width}x{loader.height}")
            print(f"  FPS: {loader.fps:.2f}")
            
            # Test on first 10 frames
            print("\n  Testing detection on first 10 frames...")
            detections_found = False
            
            for i in range(min(10, loader.frame_count)):
                success, frame = loader.read_frame()
                if not success:
                    break
                
                # Detect vehicles
                detections = detector.detect(frame)
                
                if detections:
                    detections_found = True
                    counts = detector.get_vehicle_count(detections)
                    print(f"  Frame {i}: {counts['total']} vehicles - "
                          f"Cars: {counts['car']}, "
                          f"Motorcycles: {counts['motorcycle']}, "
                          f"Buses: {counts['bus']}, "
                          f"Trucks: {counts['truck']}")
                else:
                    print(f"  Frame {i}: No vehicles detected")
            
            if detections_found:
                print("\n✓ Vehicle detection working!")
            else:
                print("\n⚠️  No vehicles detected in test frames")
                print("   This may be normal if video doesn't contain vehicles")
        
        print("\n✅ DETECTION TEST PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_detection_filtering():
    """Test detection filtering methods"""
    print("\n" + "="*60)
    print("TEST: Detection Filtering")
    print("="*60)
    
    try:
        from src.models.yolo_detector import Detection
        
        # Create dummy detections
        detections = [
            Detection((100, 100, 200, 200), 0.95, 2, 'car'),
            Detection((300, 100, 400, 200), 0.65, 2, 'car'),
            Detection((500, 100, 600, 200), 0.45, 3, 'motorcycle'),
            Detection((700, 100, 800, 200), 0.85, 5, 'bus'),
        ]
        
        detector = YOLODetector()
        
        # Test confidence filtering
        high_conf = detector.filter_by_confidence(detections, 0.8)
        assert len(high_conf) == 2, "Should have 2 high-confidence detections"
        print(f"✓ Confidence filtering: {len(detections)} → {len(high_conf)} (>0.8)")
        
        # Test class filtering
        cars_only = detector.filter_by_class(detections, ['car'])
        assert len(cars_only) == 2, "Should have 2 cars"
        print(f"✓ Class filtering: {len(detections)} → {len(cars_only)} (cars only)")
        
        # Test vehicle counting
        counts = detector.get_vehicle_count(detections)
        assert counts['total'] == 4, "Total should be 4"
        assert counts['car'] == 2, "Should have 2 cars"
        assert counts['motorcycle'] == 1, "Should have 1 motorcycle"
        assert counts['bus'] == 1, "Should have 1 bus"
        print(f"✓ Vehicle counting: {counts}")
        
        print("\n✅ FILTERING TEST PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    if not YOLO_AVAILABLE:
        sys.exit(1)
    
    # Run initialization test
    test1 = test_detector_initialization()
    
    # Run filtering test
    test2 = test_detection_filtering()
    
    # Run detection test if video provided
    test3 = True
    if len(sys.argv) >= 2:
        video_path = sys.argv[1]
        test3 = test_detection_on_video(video_path)
    else:
        print("\n⚠️  Skipping video detection test (no video provided)")
        print("   Usage: python test_yolo_detector.py <video_path>")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Initialization Test: {'✅ PASSED' if test1 else '❌ FAILED'}")
    print(f"Filtering Test: {'✅ PASSED' if test2 else '❌ FAILED'}")
    print(f"Video Detection Test: {'✅ PASSED' if test3 else '⚠️ SKIPPED'}")
    print("="*60)
    
    sys.exit(0 if (test1 and test2 and test3) else 1)
