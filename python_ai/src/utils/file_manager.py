"""
File management utilities for TraffiSight AI
Handles file operations, validation, and organization
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional
import hashlib


class FileManager:
    """Manage file operations for video processing"""
    
    @staticmethod
    def get_file_hash(filepath: Path) -> str:
        """
        Calculate MD5 hash of file
        
        Args:
            filepath: Path to file
            
        Returns:
            MD5 hash string
        """
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    @staticmethod
    def get_file_size(filepath: Path) -> int:
        """
        Get file size in bytes
        
        Args:
            filepath: Path to file
            
        Returns:
            File size in bytes
        """
        return filepath.stat().st_size
    
    @staticmethod
    def get_file_size_human(filepath: Path) -> str:
        """
        Get human-readable file size
        
        Args:
            filepath: Path to file
            
        Returns:
            Human-readable size string (e.g., "15.2 MB")
        """
        size = FileManager.get_file_size(filepath)
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        return f"{size:.2f} {units[unit_index]}"
    
    @staticmethod
    def is_video_file(filepath: Path, supported_formats: Optional[List[str]] = None) -> bool:
        """
        Check if file is a supported video format
        
        Args:
            filepath: Path to file
            supported_formats: List of supported extensions (e.g., ['mp4', 'avi'])
            
        Returns:
            True if file is a supported video format
        """
        if supported_formats is None:
            supported_formats = ['mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv']
        
        extension = filepath.suffix.lower().lstrip('.')
        return extension in supported_formats
    
    @staticmethod
    def ensure_directory(directory: Path):
        """
        Create directory if it doesn't exist
        
        Args:
            directory: Path to directory
        """
        directory.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def clean_directory(directory: Path, keep_structure: bool = True):
        """
        Remove all files from directory
        
        Args:
            directory: Path to directory
            keep_structure: If True, keep directory structure, only delete files
        """
        if not directory.exists():
            return
        
        if keep_structure:
            for item in directory.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
        else:
            shutil.rmtree(directory)
            directory.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def copy_file(source: Path, destination: Path, overwrite: bool = False) -> bool:
        """
        Copy file from source to destination
        
        Args:
            source: Source file path
            destination: Destination file path
            overwrite: Whether to overwrite existing file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if destination.exists() and not overwrite:
                return False
            
            # Ensure destination directory exists
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(source, destination)
            return True
        except Exception:
            return False
    
    @staticmethod
    def move_file(source: Path, destination: Path, overwrite: bool = False) -> bool:
        """
        Move file from source to destination
        
        Args:
            source: Source file path
            destination: Destination file path
            overwrite: Whether to overwrite existing file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if destination.exists() and not overwrite:
                return False
            
            # Ensure destination directory exists
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(str(source), str(destination))
            return True
        except Exception:
            return False
    
    @staticmethod
    def list_video_files(directory: Path, supported_formats: Optional[List[str]] = None) -> List[Path]:
        """
        List all video files in directory
        
        Args:
            directory: Directory to search
            supported_formats: List of supported video formats
            
        Returns:
            List of video file paths
        """
        if not directory.exists():
            return []
        
        video_files = []
        for file in directory.iterdir():
            if file.is_file() and FileManager.is_video_file(file, supported_formats):
                video_files.append(file)
        
        return sorted(video_files)
    
    @staticmethod
    def create_output_structure(base_dir: Path, video_name: str) -> dict:
        """
        Create organized output directory structure for a video
        
        Args:
            base_dir: Base output directory
            video_name: Name of the video (without extension)
            
        Returns:
            Dictionary with paths to different output directories
        """
        video_dir = base_dir / video_name
        
        structure = {
            'root': video_dir,
            'frames': video_dir / 'frames',
            'detections': video_dir / 'detections',
            'violations': video_dir / 'violations',
            'results': video_dir / 'results',
        }
        
        # Create all directories
        for directory in structure.values():
            directory.mkdir(parents=True, exist_ok=True)
        
        return structure


# Example usage
if __name__ == "__main__":
    # Test file operations
    test_dir = Path("./test_files")
    FileManager.ensure_directory(test_dir)
    
    # Create dummy video file
    test_video = test_dir / "test.mp4"
    test_video.touch()
    
    # Test functions
    print(f"Is video file: {FileManager.is_video_file(test_video)}")
    print(f"File size: {FileManager.get_file_size_human(test_video)}")
    
    # List video files
    videos = FileManager.list_video_files(test_dir)
    print(f"Found videos: {videos}")
    
    # Create output structure
    output = Path("./output")
    structure = FileManager.create_output_structure(output, "test_video")
    print(f"Output structure: {structure}")
    
    # Cleanup
    shutil.rmtree(test_dir)
