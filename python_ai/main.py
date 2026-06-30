"""
TraffiSight AI - Main Entry Point
Traffic Violation Detection and Monitoring System
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.utils.logger import Logger
from src.utils.config_loader import get_config
from src.core.video_loader import VideoLoader
from src.core.frame_extractor import FrameExtractor
from src.core.image_processor import ImageProcessor

# Phase 4: Vehicle Detection
try:
    from src.models.yolo_detector import YOLODetector
    from src.core.video_processor import VideoProcessor
    DETECTION_AVAILABLE = True
except ImportError:
    DETECTION_AVAILABLE = False


class TraffiSightAI:
    """Main application class"""
    
    def __init__(self, config_path: str = "./config/config.yaml"):
        """
        Initialize TraffiSight AI
        
        Args:
            config_path: Path to configuration file
        """
        self.config = get_config(config_path)
        self.logger = Logger.get_logger("TraffiSightAI")
        self.logger.info("=" * 60)
        self.logger.info("TraffiSight AI - Starting")
        self.logger.info("=" * 60)
        
        # Create necessary directories
        self.config.ensure_directories()
    
    def process_video(self, video_path: str, detect_vehicles: bool = False):
        """
        Process a single video
        
        Args:
            video_path: Path to video file
            detect_vehicles: Enable vehicle detection (Phase 4)
        """
        video_path = Path(video_path)
        
        if not video_path.exists():
            self.logger.error(f"Video file not found: {video_path}")
            return False
        
        self.logger.info(f"Processing video: {video_path.name}")
        
        try:
            # Check if detection is requested and available
            if detect_vehicles:
                if not DETECTION_AVAILABLE:
                    self.logger.error("Vehicle detection not available. Install Phase 4 requirements:")
                    self.logger.error("pip install -r requirements-phase4.txt")
                    return False
                
                # Use VideoProcessor with detection
                self.logger.info("Starting vehicle detection...")
                processor = VideoProcessor()
                
                results = processor.process_video(
                    str(video_path),
                    skip_frames=2,
                    save_video=True,
                    save_frames=False
                )
                
                self.logger.info(f"Detection complete: {results['total_detections']} vehicles detected")
                self.logger.info(f"Output saved to: {results['output_dir']}")
                return True
            
            else:
                # Phase 3: Basic processing (no detection)
                # Load video
                with VideoLoader(str(video_path)) as loader:
                    # Get metadata
                    metadata = loader.get_metadata()
                    self.logger.info(f"Video loaded: {metadata['resolution']}, "
                                   f"{metadata['fps']} FPS, {metadata['duration_formatted']}")
                    
                    # Create frame extractor
                    extractor = FrameExtractor(loader)
                    
                    # Create thumbnail
                    output_dir = self.config.get_path('paths.output_dir')
                    thumbnail_dir = output_dir / 'thumbnails'
                    thumbnail_dir.mkdir(parents=True, exist_ok=True)
                    
                    thumbnail_path = thumbnail_dir / f"{video_path.stem}_thumbnail.jpg"
                    extractor.create_thumbnail(thumbnail_path)
                    
                    # Extract sample frames for preview
                    self.logger.info("Extracting sample frames...")
                    samples = extractor.extract_sample_frames(num_samples=5)
                    self.logger.info(f"Extracted {len(samples)} sample frames")
                    
                    self.logger.info(f"Video processing complete: {video_path.name}")
                    return True
        
        except Exception as e:
            Logger.log_exception(self.logger, e, f"Error processing video: {video_path.name}")
            return False
    
    def extract_metadata(self, video_path: str) -> dict:
        """
        Extract metadata from video
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video metadata
        """
        try:
            with VideoLoader(video_path) as loader:
                return loader.get_metadata()
        except Exception as e:
            self.logger.error(f"Failed to extract metadata: {e}")
            return {}
    
    def test_video_loading(self, video_path: str):
        """
        Test video loading functionality
        
        Args:
            video_path: Path to test video
        """
        self.logger.info("Testing video loading...")
        
        try:
            with VideoLoader(video_path) as loader:
                metadata = loader.get_metadata()
                
                print("\n" + "=" * 60)
                print("VIDEO METADATA")
                print("=" * 60)
                for key, value in metadata.items():
                    print(f"{key:20s}: {value}")
                print("=" * 60)
                
                # Test frame reading
                print("\nTesting frame extraction...")
                extractor = FrameExtractor(loader)
                
                # Extract 3 sample frames
                samples = extractor.extract_sample_frames(3)
                print(f"Successfully extracted {len(samples)} sample frames")
                
                for i, (frame_num, frame, timestamp) in enumerate(samples):
                    print(f"  Frame {i+1}: #{frame_num}, Time: {timestamp:.2f}s, Shape: {frame.shape}")
                
                self.logger.info("Video loading test completed successfully!")
                return True
        
        except Exception as e:
            Logger.log_exception(self.logger, e, "Video loading test failed")
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="TraffiSight AI - Traffic Violation Detection System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a video (Phase 3)
  python main.py process -i video.mp4
  
  # Detect vehicles in video (Phase 4)
  python main.py detect -i video.mp4
  
  # Extract metadata
  python main.py metadata -i video.mp4
  
  # Test video loading
  python main.py test -i video.mp4
        """
    )
    
    parser.add_argument(
        'command',
        choices=['process', 'metadata', 'test', 'detect', 'analyze'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Input video file path'
    )
    
    parser.add_argument(
        '--video-id',
        type=int,
        help='Video ID for database reference (used with analyze command)'
    )
    
    parser.add_argument(
        '-c', '--config',
        default='./config/config.yaml',
        help='Configuration file path'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Create application instance
    app = TraffiSightAI(config_path=args.config)
    
    # Execute command
    if args.command == 'process':
        success = app.process_video(args.input, detect_vehicles=False)
        sys.exit(0 if success else 1)
    
    elif args.command == 'detect':
        # Phase 4: Vehicle Detection
        success = app.process_video(args.input, detect_vehicles=True)
        sys.exit(0 if success else 1)
    
    elif args.command == 'metadata':
        metadata = app.extract_metadata(args.input)
        if metadata:
            import json
            print(json.dumps(metadata, indent=2))
            sys.exit(0)
        else:
            sys.exit(1)
    
    elif args.command == 'test':
        success = app.test_video_loading(args.input)
        sys.exit(0 if success else 1)
    
    elif args.command == 'analyze':
        # Complete AI analysis with all features
        print("=" * 60)
        print("TraffiSight AI - Complete Analysis")
        if args.video_id:
            print(f"Video ID: {args.video_id}")
        print("=" * 60)
        
        success = app.process_video(args.input, detect_vehicles=True)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
