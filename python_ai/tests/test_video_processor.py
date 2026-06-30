"""
Unit tests for Video Processor with Detection
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    from src.core.video_processor import VideoProcessor
    from src.models.yolo_detector import YOLODetector
    from src.core.video_loader import VideoLoader
    PROCESSOR_AVAILABLE = True
except ImportError as e:
    print(f"❌ ERROR: Video processor dependencies not installed")
    print(f"   {e}")
    print("\nInstall Phase 4 requirements:")
    print("   pip install -r requirements-phase4.txt")
    PROCESSOR_AVAILABLE = False
    sys.exit(1)


def test_processor_initialization():
    """Test processor initialization"""
    print("\n" + "="*60)
    print("TEST: Processor Initialization")
    print("="*60)
    
    try:
        processor = VideoProcessor()
        
        assert processor.detector is not None, "Detector should be initialized"
        assert processor.visualizer is not None, "Visualizer should be initialized"
        print("✓ Processor initialized with detector and visualizer")
        
        print("\n✅ PROCESSOR INITIALIZATION TEST PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_video_processing(video_path: str):
    """Test complete video processing with detection"""
    print("\n" + "="*60)
    print("TEST: Video Processing with Detection")
    print("="*60)
    
    try:
        # Create processor
        processor = VideoProcessor()
        print("✓ Processor created")
        
        # Process video (only first 20 frames for testing)
        output_dir = Path("output/test_detection")
        
        print(f"\n  Processing video: {Path(video_path).name}")
        print(f"  Output directory: {output_dir}")
        print(f"  Processing first 20 frames...\n")
        
        results = processor.process_video(
            video_path,
            output_dir=output_dir,
            skip_frames=1,
            max_frames=20,
            save_video=True,
            save_frames=False,
            show_progress=True
        )
        
        # Verify results
        assert 'frames_processed' in results, "Results should contain frames_processed"
        assert 'total_detections' in results, "Results should contain total_detections"
        assert results['frames_processed'] > 0, "Should process at least one frame"
        
        print(f"\n✓ Processed {results['frames_processed']} frames")
        print(f"✓ Detected {results['total_detections']} vehicles")
        print(f"✓ Average FPS: {results['average_fps']:.1f}")
        print(f"✓ Output saved to: {results['output_dir']}")
        
        # Check if output files exist
        output_path = Path(results['output_dir'])
        if output_path.exists():
            print(f"✓ Output directory created")
            
            video_output = output_path / f"{Path(video_path).stem}_detected.mp4"
            if video_output.exists():
                print(f"✓ Output video created: {video_output.name}")
            
            results_json = output_path / "detection_results.json"
            if results_json.exists():
                print(f"✓ Results JSON created")
        
        print("\n✅ VIDEO PROCESSING TEST PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_single_frame_processing(video_path: str):
    """Test processing a single frame"""
    print("\n" + "="*60)
    print("TEST: Single Frame Processing")
    print("="*60)
    
    try:
        processor = VideoProcessor()
        
        # Load video and get one frame
        with VideoLoader(video_path) as loader:
            success, frame = loader.read_frame()
            assert success, "Should read frame successfully"
            print(f"✓ Frame loaded: {frame.shape}")
            
            # Process frame
            annotated_frame, detections, detection_time = processor.process_frame(frame)
            
            print(f"✓ Frame processed in {detection_time:.3f}s")
            print(f"✓ Detected {len(detections)} vehicles")
            print(f"✓ Annotated frame shape: {annotated_frame.shape}")
            
            if detections:
                for i, det in enumerate(detections[:3]):  # Show first 3
                    print(f"  Detection {i+1}: {det.class_name} ({det.confidence:.2f})")
        
        print("\n✅ SINGLE FRAME PROCESSING TEST PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    if not PROCESSOR_AVAILABLE:
        sys.exit(1)
    
    if len(sys.argv) < 2:
        print("Usage: python test_video_processor.py <video_path>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    # Run tests
    test1 = test_processor_initialization()
    test2 = test_single_frame_processing(video_path)
    test3 = test_video_processing(video_path)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Initialization Test: {'✅ PASSED' if test1 else '❌ FAILED'}")
    print(f"Single Frame Test: {'✅ PASSED' if test2 else '❌ FAILED'}")
    print(f"Video Processing Test: {'✅ PASSED' if test3 else '❌ FAILED'}")
    print("="*60)
    
    sys.exit(0 if (test1 and test2 and test3) else 1)
