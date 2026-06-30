"""
Image Processor Module
Basic image processing operations for video frames
"""

import cv2
import numpy as np
from typing import Tuple, Optional
from pathlib import Path

from ..utils.logger import Logger


class ImageProcessor:
    """Process and manipulate images/frames"""
    
    def __init__(self):
        """Initialize image processor"""
        self.logger = Logger.get_logger("ImageProcessor")
    
    def resize(
        self,
        image: np.ndarray,
        width: Optional[int] = None,
        height: Optional[int] = None,
        maintain_aspect: bool = True
    ) -> np.ndarray:
        """
        Resize image
        
        Args:
            image: Input image
            width: Target width (None to calculate from height)
            height: Target height (None to calculate from width)
            maintain_aspect: Maintain aspect ratio
            
        Returns:
            Resized image
        """
        h, w = image.shape[:2]
        
        if width is None and height is None:
            return image
        
        if maintain_aspect:
            if width is not None and height is None:
                # Calculate height
                aspect = h / w
                height = int(width * aspect)
            elif height is not None and width is None:
                # Calculate width
                aspect = w / h
                width = int(height * aspect)
        else:
            if width is None:
                width = w
            if height is None:
                height = h
        
        resized = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
        return resized
    
    def crop(
        self,
        image: np.ndarray,
        x: int,
        y: int,
        width: int,
        height: int
    ) -> np.ndarray:
        """
        Crop image
        
        Args:
            image: Input image
            x: Top-left x coordinate
            y: Top-left y coordinate
            width: Crop width
            height: Crop height
            
        Returns:
            Cropped image
        """
        return image[y:y+height, x:x+width]
    
    def rotate(self, image: np.ndarray, angle: float) -> np.ndarray:
        """
        Rotate image
        
        Args:
            image: Input image
            angle: Rotation angle in degrees (positive = counter-clockwise)
            
        Returns:
            Rotated image
        """
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        
        # Get rotation matrix
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # Perform rotation
        rotated = cv2.warpAffine(image, matrix, (w, h))
        return rotated
    
    def flip(self, image: np.ndarray, mode: str = "horizontal") -> np.ndarray:
        """
        Flip image
        
        Args:
            image: Input image
            mode: Flip mode ("horizontal", "vertical", "both")
            
        Returns:
            Flipped image
        """
        if mode == "horizontal":
            return cv2.flip(image, 1)
        elif mode == "vertical":
            return cv2.flip(image, 0)
        elif mode == "both":
            return cv2.flip(image, -1)
        else:
            return image
    
    def adjust_brightness(self, image: np.ndarray, factor: float) -> np.ndarray:
        """
        Adjust image brightness
        
        Args:
            image: Input image
            factor: Brightness factor (1.0 = no change, >1.0 = brighter, <1.0 = darker)
            
        Returns:
            Adjusted image
        """
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 2] = hsv[:, :, 2] * factor
        hsv[:, :, 2] = np.clip(hsv[:, :, 2], 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    
    def adjust_contrast(self, image: np.ndarray, factor: float) -> np.ndarray:
        """
        Adjust image contrast
        
        Args:
            image: Input image
            factor: Contrast factor (1.0 = no change, >1.0 = more contrast, <1.0 = less contrast)
            
        Returns:
            Adjusted image
        """
        return cv2.convertScaleAbs(image, alpha=factor, beta=0)
    
    def blur(self, image: np.ndarray, kernel_size: int = 5) -> np.ndarray:
        """
        Apply Gaussian blur
        
        Args:
            image: Input image
            kernel_size: Blur kernel size (must be odd)
            
        Returns:
            Blurred image
        """
        if kernel_size % 2 == 0:
            kernel_size += 1
        return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
    
    def sharpen(self, image: np.ndarray) -> np.ndarray:
        """
        Sharpen image
        
        Args:
            image: Input image
            
        Returns:
            Sharpened image
        """
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        return cv2.filter2D(image, -1, kernel)
    
    def to_grayscale(self, image: np.ndarray) -> np.ndarray:
        """
        Convert image to grayscale
        
        Args:
            image: Input image (BGR or RGB)
            
        Returns:
            Grayscale image
        """
        if len(image.shape) == 2:
            return image  # Already grayscale
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    def draw_rectangle(
        self,
        image: np.ndarray,
        x: int,
        y: int,
        width: int,
        height: int,
        color: Tuple[int, int, int] = (0, 255, 0),
        thickness: int = 2
    ) -> np.ndarray:
        """
        Draw rectangle on image
        
        Args:
            image: Input image
            x: Top-left x coordinate
            y: Top-left y coordinate
            width: Rectangle width
            height: Rectangle height
            color: BGR color tuple
            thickness: Line thickness
            
        Returns:
            Image with rectangle
        """
        result = image.copy()
        cv2.rectangle(result, (x, y), (x + width, y + height), color, thickness)
        return result
    
    def draw_text(
        self,
        image: np.ndarray,
        text: str,
        x: int,
        y: int,
        color: Tuple[int, int, int] = (255, 255, 255),
        font_scale: float = 0.6,
        thickness: int = 2
    ) -> np.ndarray:
        """
        Draw text on image
        
        Args:
            image: Input image
            text: Text to draw
            x: Text x coordinate
            y: Text y coordinate
            color: BGR color tuple
            font_scale: Font scale
            thickness: Text thickness
            
        Returns:
            Image with text
        """
        result = image.copy()
        cv2.putText(result, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                   font_scale, color, thickness, cv2.LINE_AA)
        return result
    
    def save_image(
        self,
        image: np.ndarray,
        output_path: Path,
        quality: int = 95
    ) -> bool:
        """
        Save image to file
        
        Args:
            image: Image to save
            output_path: Output file path
            quality: JPEG quality (0-100)
            
        Returns:
            True if successful
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if output_path.suffix.lower() in ['.jpg', '.jpeg']:
                cv2.imwrite(str(output_path), image, [cv2.IMWRITE_JPEG_QUALITY, quality])
            else:
                cv2.imwrite(str(output_path), image)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to save image: {e}")
            return False


# Example usage
if __name__ == "__main__":
    # Create processor
    processor = ImageProcessor()
    
    # Create sample image
    image = np.zeros((480, 640, 3), dtype=np.uint8)
    image[:] = (100, 150, 200)  # Fill with color
    
    # Test operations
    resized = processor.resize(image, width=320)
    print(f"Original shape: {image.shape}, Resized shape: {resized.shape}")
    
    # Draw on image
    with_rect = processor.draw_rectangle(image, 50, 50, 200, 100)
    with_text = processor.draw_text(with_rect, "TraffiSight AI", 60, 90)
    
    # Save result
    output_path = Path("./output/test_image.jpg")
    success = processor.save_image(with_text, output_path)
    if success:
        print(f"Image saved to {output_path}")
