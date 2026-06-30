"""
Video Processor with Detection
Process videos with vehicle detection
"""

import cv2
import time
from pathlib import Path
from typing import Optional, List
from tqdm import tqdm

from .video_loader import VideoLoader
from .frame_extractor import FrameExtractor
from ..models.yolo_detector import YOLODetector, Detection
from ..models.byte_tracker import ByteTracker, Track
from ..utils.visualizer import DetectionVisualizer
from ..utils.logger import Logger
from ..utils.file_manager import FileManager


class VideoProcessor:
    """Process videos with vehicle detection"""
    
    def __init__(
        self,
        detector: Optional[YOLODetector] = None,
        visualizer: Optional[DetectionVisualizer] = None,
        use_tracking: bool = True
    ):
        """
        Initialize video processor
        
        Args:
            detector: YOLODetector instance (creates default if None)
            visualizer: DetectionVisualizer instance (creates default if None)
            use_tracking: Enable vehicle tracking with ByteTracker
        """
        self.logger = Logger.get_logger("VideoProcessor")
        
        # Initialize detector
        if detector is None:
            self.logger.info("Initializing default YOLOv8 detector...")
            self.detector = YOLODetector()
        else:
            self.detector = detector
        
        # Initialize visualizer
        if visualizer is None:
            self.visualizer = DetectionVisualizer()
        else:
            self.visualizer = visualizer
        
        # Initialize tracker
        self.use_tracking = use_tracking
        if use_tracking:
            self.logger.info("Initializing ByteTracker...")
            self.tracker = ByteTracker(
                max_age=30,
                min_hits=3,
                iou_threshold=0.3
            )
        else:
            self.tracker = None
    
    def process_video(
        self,
        video_path: str,
        output_dir: Optional[Path] = None,
        skip_frames: int = 1,
        max_frames: int = 0,
        save_video: bool = True,
        save_frames: bool = False,
        show_progress: bool = True
    ) -> dict:
        """
        Process video with vehicle detection
        
        Args:
            video_path: Path to input video
            output_dir: Output directory (None = auto-create)
            skip_frames: Process every Nth frame
            max_frames: Maximum frames to process (0 = all)
            save_video: Save output video with detections
            save_frames: Save individual frames
            show_progress: Show progress bar
            
        Returns:
            Dictionary with processing results
        """
        video_path = Path(video_path)
        
        if not video_path.exists():
            self.logger.error(f"Video not found: {video_path}")
            return {}
        
        self.logger.info(f"Processing video: {video_path.name}")
        
        # Create output directory
        if output_dir is None:
            output_dir = Path("output") / video_path.stem
        FileManager.ensure_directory(output_dir)
        
        # Results storage
        all_detections = []
        all_tracks = []
        frame_count = 0
        total_vehicles = 0
        processing_times = []
        
        # Reset tracker if enabled
        if self.tracker:
            self.tracker.reset()
        
        # Load video
        with VideoLoader(str(video_path)) as loader:
            metadata = loader.get_metadata()
            self.logger.info(f"Video: {metadata['resolution']}, "
                           f"{metadata['fps']} FPS, "
                           f"{metadata['duration_formatted']}")
            
            # Setup video writer if saving
            video_writer = None
            if save_video:
                output_video_path = output_dir / f"{video_path.stem}_detected.mp4"
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                video_writer = cv2.VideoWriter(
                    str(output_video_path),
                    fourcc,
                    loader.fps,
                    (loader.width, loader.height)
                )
                self.logger.info(f"Output video: {output_video_path}")
            
            # Setup progress bar
            total_frames = loader.frame_count if max_frames == 0 else min(max_frames * skip_frames, loader.frame_count)
            pbar = tqdm(total=total_frames, desc="Processing", disable=not show_progress)
            
            try:
                frame_num = 0
                while True:
                    success, frame = loader.read_frame()
                    if not success:
                        break
                    
                    # Skip frames logic
                    if frame_num % skip_frames == 0:
                        # Detect vehicles
                        start_time = time.time()
                        detections = self.detector.detect(frame)
                        detection_time = time.time() - start_time
                        processing_times.append(detection_time)
                        
                        # Update tracker if enabled
                        tracks = []
                        if self.tracker:
                            tracks = self.tracker.update(detections)
                        
                        # Store results
                        frame_data = {
                            'frame_number': frame_num,
                            'timestamp': frame_num / loader.fps,
                            'detections': len(detections),
                            'vehicles': [
                                {
                                    'class': d.class_name,
                                    'confidence': float(d.confidence),
                                    'bbox': d.bbox
                                }
                                for d in detections
                            ]
                        }
                        
                        # Add tracking info if enabled
                        if self.tracker and tracks:
                            frame_data['tracked_vehicles'] = [
                                {
                                    'track_id': t.track_id,
                                    'class': t.class_name,
                                    'confidence': float(t.confidence),
                                    'bbox': t.bbox,
                                    'trajectory_length': len(t.history)
                                }
                                for t in tracks
                            ]
                            all_tracks.append(frame_data)
                        
                        all_detections.append(frame_data)
                        total_vehicles += len(detections)
                        frame_count += 1
                        
                        # Create annotated frame
                        if self.tracker and tracks:
                            # Draw with tracking IDs
                            annotated_frame = self.visualizer.draw_tracks(
                                frame,
                                tracks,
                                show_trajectory=True
                            )
                        else:
                            # Draw with detections only
                            annotated_frame = self.visualizer.create_detection_frame(
                                frame,
                                detections,
                                show_stats=True
                            )
                        
                        # Add FPS
                        if processing_times:
                            current_fps = 1.0 / (sum(processing_times[-10:]) / min(10, len(processing_times)))
                            annotated_frame = self.visualizer.draw_fps(annotated_frame, current_fps)
                        
                        # Save frame if requested
                        if save_frames:
                            frame_path = output_dir / "frames" / f"frame_{frame_num:06d}.jpg"
                            frame_path.parent.mkdir(exist_ok=True)
                            cv2.imwrite(str(frame_path), annotated_frame)
                        
                        # Write to output video
                        if video_writer is not None:
                            video_writer.write(annotated_frame)
                        
                        # Check max frames limit
                        if max_frames > 0 and frame_count >= max_frames:
                            break
                    
                    frame_num += 1
                    pbar.update(1)
            
            finally:
                pbar.close()
                if video_writer is not None:
                    video_writer.release()
            
            # Calculate statistics
            avg_detection_time = sum(processing_times) / len(processing_times) if processing_times else 0
            avg_fps = 1.0 / avg_detection_time if avg_detection_time > 0 else 0
            
            results = {
                'video_name': video_path.name,
                'frames_processed': frame_count,
                'total_detections': total_vehicles,
                'average_detection_time': avg_detection_time,
                'average_fps': avg_fps,
                'output_dir': str(output_dir),
                'detections_by_frame': all_detections,
                'metadata': metadata
            }
            
            # Add tracking statistics if enabled
            if self.tracker:
                tracker_stats = self.tracker.get_statistics()
                results['tracking_enabled'] = True
                results['tracking_stats'] = tracker_stats
                results['tracked_vehicles_by_frame'] = all_tracks
                results['unique_vehicles_tracked'] = tracker_stats['max_track_id']
                self.logger.info(f"Unique vehicles tracked: {tracker_stats['max_track_id']}")
            else:
                results['tracking_enabled'] = False
            
            # Save results to JSON
            import json
            results_path = output_dir / "detection_results.json"
            with open(results_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            self.logger.info(f"Processed {frame_count} frames")
            self.logger.info(f"Total vehicles detected: {total_vehicles}")
            self.logger.info(f"Average detection time: {avg_detection_time:.3f}s")
            self.logger.info(f"Average FPS: {avg_fps:.1f}")
            self.logger.info(f"Results saved to: {output_dir}")
            
            return results
    
    def process_frame(self, frame) -> tuple:
        """
        Process a single frame
        
        Args:
            frame: Input frame
            
        Returns:
            Tuple of (annotated_frame, detections, detection_time)
        """
        start_time = time.time()
        detections = self.detector.detect(frame)
        detection_time = time.time() - start_time
        
        annotated_frame = self.visualizer.create_detection_frame(
            frame,
            detections
        )
        
        return annotated_frame, detections, detection_time


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python video_processor.py <video_path>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    # Create processor
    processor = VideoProcessor()
    
    # Process video
    results = processor.process_video(
        video_path,
        skip_frames=2,  # Process every 2nd frame
        save_video=True,
        save_frames=False
    )
    
    print("\n" + "=" * 60)
    print("PROCESSING COMPLETE")
    print("=" * 60)
    print(f"Frames processed: {results['frames_processed']}")
    print(f"Total vehicles detected: {results['total_detections']}")
    print(f"Average FPS: {results['average_fps']:.1f}")
    print(f"Output: {results['output_dir']}")
