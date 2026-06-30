"""
Video Loader Module
Handles loading and reading video files using OpenCV
"""

import cv2
from pathlib import Path
from typing import Optional, Tuple
import numpy as np

from ..utils.logger import Logger
from ..utils.file_manager import FileManager


class VideoLoader:
    """Load and read video files"""
    
    def __init__(self, video_path: str):
        """
        Initialize video loader
        
        Args:
            video_path: Path to video file
        """
        self.video_path = Path(video_path)
        self.logger = Logger.get_logger("VideoLoader")
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_opened = False
        
        # Video properties
        self.width = 0
        self.height = 0
        self.fps = 0.0
        self.frame_count = 0
        self.duration = 0.0
        
        self._validate_and_load()
    
    def _validate_and_load(self):
        """Validate video file and load properties"""
        if not self.video_path.exists():
            self.logger.error(f"Video file not found: {self.video_path}")
            raise FileNotFoundError(f"Video file not found: {self.video_path}")
        
        if not FileManager.is_video_file(self.video_path):
            self.logger.error(f"Unsupported video format: {self.video_path.suffix}")
            raise ValueError(f"Unsupported video format: {self.video_path.suffix}")
        
        # Open video
        self.cap = cv2.VideoCapture(str(self.video_path))
        
        if not self.cap.isOpened():
            self.logger.error(f"Failed to open video: {self.video_path}")
            raise RuntimeError(f"Failed to open video: {self.video_path}")
        
        self.is_opened = True
        self._load_properties()
        
        self.logger.info(f"Video loaded: {self.video_path.name}")
        self.logger.info(f"Resolution: {self.width}x{self.height}, FPS: {self.fps:.2f}, "
                        f"Frames: {self.frame_count}, Duration: {self.duration:.2f}s")
    
    def _load_properties(self):
        """Load video properties"""
        if not self.is_opened:
            return
        
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if self.fps > 0:
            self.duration = self.frame_count / self.fps
    
    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read next frame from video
        
        Returns:
            Tuple of (success, frame)
            - success: True if frame was read successfully
            - frame: Frame as numpy array (BGR format) or None
        """
        if not self.is_opened:
            return False, None
        
        success, frame = self.cap.read()
        return success, frame if success else None
    
    def get_frame_at(self, frame_number: int) -> Optional[np.ndarray]:
        """
        Get specific frame by frame number
        
        Args:
            frame_number: Frame number to retrieve (0-indexed)
            
        Returns:
            Frame as numpy array or None if failed
        """
        if not self.is_opened:
            return None
        
        if frame_number < 0 or frame_number >= self.frame_count:
            self.logger.warning(f"Frame number out of range: {frame_number}")
            return None
        
        # Set frame position
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        success, frame = self.cap.read()
        
        return frame if success else None
    
    def get_frame_at_time(self, time_seconds: float) -> Optional[np.ndarray]:
        """
        Get frame at specific time
        
        Args:
            time_seconds: Time in seconds
            
        Returns:
            Frame as numpy array or None if failed
        """
        if not self.is_opened or self.fps == 0:
            return None
        
        frame_number = int(time_seconds * self.fps)
        return self.get_frame_at(frame_number)
    
    def reset(self):
        """Reset video to beginning"""
        if self.is_opened:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.logger.debug("Video reset to beginning")
    
    def get_current_frame_number(self) -> int:
        """Get current frame number"""
        if not self.is_opened:
            return -1
        return int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
    
    def get_current_time(self) -> float:
        """Get current time in seconds"""
        if not self.is_opened or self.fps == 0:
            return 0.0
        return self.get_current_frame_number() / self.fps
    
    def get_progress_percentage(self) -> float:
        """Get progress percentage (0-100)"""
        if not self.is_opened or self.frame_count == 0:
            return 0.0
        return (self.get_current_frame_number() / self.frame_count) * 100
    
    def get_metadata(self) -> dict:
        """
        Get video metadata
        
        Returns:
            Dictionary with video metadata
        """
        return {
            'filename': self.video_path.name,
            'filepath': str(self.video_path),
            'width': self.width,
            'height': self.height,
            'resolution': f"{self.width}x{self.height}",
            'fps': round(self.fps, 2),
            'frame_count': self.frame_count,
            'duration': round(self.duration, 2),
            'duration_formatted': self._format_duration(self.duration),
            'filesize': FileManager.get_file_size(self.video_path),
            'filesize_human': FileManager.get_file_size_human(self.video_path),
            'format': self.video_path.suffix.lstrip('.').upper(),
        }
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration as HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"
    
    def release(self):
        """Release video capture resources"""
        if self.cap is not None:
            self.cap.release()
            self.is_opened = False
            self.logger.info(f"Video released: {self.video_path.name}")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.release()
    
    def __del__(self):
        """Destructor"""
        self.release()
    
    def __repr__(self) -> str:
        return f"VideoLoader('{self.video_path.name}', {self.width}x{self.height}, {self.fps:.2f}fps)"


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python video_loader.py <video_path>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    # Load video using context manager
    with VideoLoader(video_path) as loader:
        # Print metadata
        metadata = loader.get_metadata()
        print("\nVideo Metadata:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")
        
        # Read first few frames
        print("\nReading first 5 frames...")
        for i in range(5):
            success, frame = loader.read_frame()
            if success:
                print(f"  Frame {i}: {frame.shape}")
            else:
                print(f"  Failed to read frame {i}")
                break
