"""
Frame Extractor Module
Extract frames from video files with various options
"""

import cv2
from pathlib import Path
from typing import Optional, Generator, List
import numpy as np
from tqdm import tqdm

from .video_loader import VideoLoader
from ..utils.logger import Logger
from ..utils.file_manager import FileManager


class FrameExtractor:
    """Extract frames from videos"""
    
    def __init__(self, video_loader: VideoLoader):
        """
        Initialize frame extractor
        
        Args:
            video_loader: VideoLoader instance
        """
        self.video_loader = video_loader
        self.logger = Logger.get_logger("FrameExtractor")
    
    def extract_all_frames(
        self,
        skip_frames: int = 1,
        max_frames: int = 0,
        show_progress: bool = True
    ) -> Generator[tuple, None, None]:
        """
        Extract all frames from video
        
        Args:
            skip_frames: Extract every Nth frame (1 = all frames, 2 = every other frame)
            max_frames: Maximum number of frames to extract (0 = no limit)
            show_progress: Show progress bar
            
        Yields:
            Tuple of (frame_number, frame, timestamp)
        """
        self.video_loader.reset()
        frames_extracted = 0
        frame_number = 0
        
        # Setup progress bar
        total_frames = self.video_loader.frame_count
        if max_frames > 0:
            total_frames = min(total_frames, max_frames * skip_frames)
        
        pbar = None
        if show_progress:
            pbar = tqdm(total=total_frames, desc="Extracting frames", unit="frame")
        
        try:
            while True:
                success, frame = self.video_loader.read_frame()
                
                if not success:
                    break
                
                # Skip frames logic
                if frame_number % skip_frames == 0:
                    timestamp = frame_number / self.video_loader.fps
                    yield (frame_number, frame, timestamp)
                    frames_extracted += 1
                    
                    # Check max frames limit
                    if max_frames > 0 and frames_extracted >= max_frames:
                        break
                
                frame_number += 1
                
                if pbar:
                    pbar.update(1)
        
        finally:
            if pbar:
                pbar.close()
        
        self.logger.info(f"Extracted {frames_extracted} frames from {frame_number} total frames")
    
    def save_frames(
        self,
        output_dir: Path,
        skip_frames: int = 1,
        max_frames: int = 0,
        prefix: str = "frame",
        format: str = "jpg",
        quality: int = 95
    ) -> int:
        """
        Extract and save frames to disk
        
        Args:
            output_dir: Directory to save frames
            skip_frames: Extract every Nth frame
            max_frames: Maximum frames to save
            prefix: Filename prefix
            format: Image format (jpg, png)
            quality: JPEG quality (0-100) or PNG compression (0-9)
            
        Returns:
            Number of frames saved
        """
        FileManager.ensure_directory(output_dir)
        
        frames_saved = 0
        
        for frame_num, frame, timestamp in self.extract_all_frames(skip_frames, max_frames):
            # Generate filename
            filename = f"{prefix}_{frame_num:06d}.{format}"
            filepath = output_dir / filename
            
            # Save frame
            if format.lower() == 'jpg' or format.lower() == 'jpeg':
                cv2.imwrite(str(filepath), frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
            elif format.lower() == 'png':
                cv2.imwrite(str(filepath), frame, [cv2.IMWRITE_PNG_COMPRESSION, quality])
            else:
                cv2.imwrite(str(filepath), frame)
            
            frames_saved += 1
        
        self.logger.info(f"Saved {frames_saved} frames to {output_dir}")
        return frames_saved
    
    def extract_frames_at_intervals(
        self,
        interval_seconds: float,
        max_frames: int = 0
    ) -> List[tuple]:
        """
        Extract frames at specific time intervals
        
        Args:
            interval_seconds: Time interval between frames in seconds
            max_frames: Maximum number of frames to extract (0 = no limit)
            
        Returns:
            List of tuples (frame_number, frame, timestamp)
        """
        frames = []
        current_time = 0.0
        frame_count = 0
        
        while current_time <= self.video_loader.duration:
            frame = self.video_loader.get_frame_at_time(current_time)
            
            if frame is not None:
                frame_number = int(current_time * self.video_loader.fps)
                frames.append((frame_number, frame, current_time))
                frame_count += 1
                
                if max_frames > 0 and frame_count >= max_frames:
                    break
            
            current_time += interval_seconds
        
        self.logger.info(f"Extracted {len(frames)} frames at {interval_seconds}s intervals")
        return frames
    
    def extract_key_frames(
        self,
        threshold: float = 30.0,
        max_frames: int = 0
    ) -> List[tuple]:
        """
        Extract key frames based on frame difference
        
        Args:
            threshold: Difference threshold for key frame detection
            max_frames: Maximum key frames to extract (0 = no limit)
            
        Returns:
            List of tuples (frame_number, frame, timestamp)
        """
        key_frames = []
        prev_frame = None
        frame_count = 0
        
        self.video_loader.reset()
        
        for frame_num, frame, timestamp in self.extract_all_frames(skip_frames=1, max_frames=0):
            if prev_frame is None:
                # First frame is always a key frame
                key_frames.append((frame_num, frame, timestamp))
                prev_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frame_count += 1
                continue
            
            # Convert to grayscale
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate frame difference
            diff = cv2.absdiff(prev_frame, gray_frame)
            mean_diff = np.mean(diff)
            
            # Check if frame is significantly different
            if mean_diff > threshold:
                key_frames.append((frame_num, frame, timestamp))
                frame_count += 1
                prev_frame = gray_frame
                
                if max_frames > 0 and frame_count >= max_frames:
                    break
        
        self.logger.info(f"Extracted {len(key_frames)} key frames")
        return key_frames
    
    def extract_sample_frames(self, num_samples: int = 10) -> List[tuple]:
        """
        Extract evenly distributed sample frames
        
        Args:
            num_samples: Number of sample frames to extract
            
        Returns:
            List of tuples (frame_number, frame, timestamp)
        """
        if num_samples <= 0:
            return []
        
        frames = []
        frame_interval = max(1, self.video_loader.frame_count // num_samples)
        
        for i in range(num_samples):
            frame_number = i * frame_interval
            frame = self.video_loader.get_frame_at(frame_number)
            
            if frame is not None:
                timestamp = frame_number / self.video_loader.fps
                frames.append((frame_number, frame, timestamp))
        
        self.logger.info(f"Extracted {len(frames)} sample frames")
        return frames
    
    def create_thumbnail(
        self,
        output_path: Path,
        frame_number: Optional[int] = None,
        size: tuple = (320, 180),
        quality: int = 85
    ) -> bool:
        """
        Create thumbnail from video frame
        
        Args:
            output_path: Path to save thumbnail
            frame_number: Frame number to use (None = middle frame)
            size: Thumbnail size (width, height)
            quality: JPEG quality
            
        Returns:
            True if successful
        """
        try:
            # Get frame
            if frame_number is None:
                frame_number = self.video_loader.frame_count // 2
            
            frame = self.video_loader.get_frame_at(frame_number)
            
            if frame is None:
                self.logger.error("Failed to extract frame for thumbnail")
                return False
            
            # Resize frame
            thumbnail = cv2.resize(frame, size, interpolation=cv2.INTER_AREA)
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save thumbnail
            cv2.imwrite(str(output_path), thumbnail, [cv2.IMWRITE_JPEG_QUALITY, quality])
            
            self.logger.info(f"Thumbnail created: {output_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to create thumbnail: {e}")
            return False


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python frame_extractor.py <video_path>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    output_dir = Path("./output/frames")
    
    # Load video
    with VideoLoader(video_path) as loader:
        extractor = FrameExtractor(loader)
        
        # Extract sample frames
        print("\nExtracting 10 sample frames...")
        samples = extractor.extract_sample_frames(10)
        print(f"Extracted {len(samples)} samples")
        
        # Save frames to disk
        print("\nSaving frames (every 30 frames)...")
        num_saved = extractor.save_frames(
            output_dir=output_dir,
            skip_frames=30,
            max_frames=20,
            quality=90
        )
        print(f"Saved {num_saved} frames to {output_dir}")
        
        # Create thumbnail
        thumbnail_path = Path("./output/thumbnail.jpg")
        success = extractor.create_thumbnail(thumbnail_path)
        if success:
            print(f"Thumbnail saved to {thumbnail_path}")
