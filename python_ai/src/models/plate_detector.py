"""
License Plate Detector
Detect license plate regions within vehicle bounding boxes
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass

from ..utils.logger import Logger
from ..utils.config_loader import ConfigLoader as Config


@dataclass
class PlateRegion:
    """Detected plate region"""
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    confidence: float
    image: np.ndarray  # Cropped plate image
    
    @property
    def width(self):
        return self.bbox[2] - self.bbox[0]
    
    @property
    def height(self):
        return self.bbox[3] - self.bbox[1]
    
    @property
    def aspect_ratio(self):
        return self.width / self.height if self.height > 0 else 0


class PlateDetector:
    """Detect license plates using traditional CV methods"""
    
    def __init__(self):
        """Initialize plate detector"""
        self.logger = Logger.get_logger("PlateDetector")
        
        # Load configuration
        config = Config()
        plate_config = config.get('plate_recognition', {})
        
        self.min_width = plate_config.get('min_plate_width', 60)
        self.min_height = plate_config.get('min_plate_height', 20)
        self.max_width = plate_config.get('max_plate_width', 400)
        self.max_height = plate_config.get('max_plate_height', 200)
        self.aspect_ratio_min = plate_config.get('aspect_ratio_min', 1.5)
        self.aspect_ratio_max = plate_config.get('aspect_ratio_max', 5.0)
        self.enhance_image = plate_config.get('enhance_image', True)
        
        self.logger.info("PlateDetector initialized")
    
    def detect_plates(
        self,
        frame: np.ndarray,
        vehicle_bbox: Tuple[int, int, int, int]
    ) -> List[PlateRegion]:
        """
        Detect license plates within a vehicle bounding box
        
        Args:
            frame: Full frame image
            vehicle_bbox: Vehicle bounding box (x1, y1, x2, y2)
            
        Returns:
            List of detected plate regions
        """
        # Crop vehicle region
        x1, y1, x2, y2 = vehicle_bbox
        vehicle_region = frame[y1:y2, x1:x2].copy()
        
        if vehicle_region.size == 0:
            return []
        
        # Find plate regions
        plate_contours = self._find_plate_contours(vehicle_region)
        
        plates = []
        for contour in plate_contours:
            # Get bounding rectangle
            px, py, pw, ph = cv2.boundingRect(contour)
            
            # Validate dimensions
            if not self._validate_dimensions(pw, ph):
                continue
            
            # Convert to absolute coordinates
            abs_x1 = x1 + px
            abs_y1 = y1 + py
            abs_x2 = abs_x1 + pw
            abs_y2 = abs_y1 + ph
            
            # Crop plate image with padding
            plate_img = self._crop_plate_with_padding(
                frame,
                (abs_x1, abs_y1, abs_x2, abs_y2)
            )
            
            if plate_img is None:
                continue
            
            # Enhance plate image if enabled
            if self.enhance_image:
                plate_img = self._enhance_plate(plate_img)
            
            # Create plate region
            plate = PlateRegion(
                bbox=(abs_x1, abs_y1, abs_x2, abs_y2),
                confidence=0.8,  # Fixed confidence for CV method
                image=plate_img
            )
            
            plates.append(plate)
        
        return plates
    
    def _find_plate_contours(self, region: np.ndarray) -> List[np.ndarray]:
        """
        Find potential plate contours using edge detection
        
        Args:
            region: Vehicle region image
            
        Returns:
            List of contours that might be plates
        """
        # Convert to grayscale
        gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        
        # Apply bilateral filter to reduce noise while keeping edges sharp
        filtered = cv2.bilateralFilter(gray, 11, 17, 17)
        
        # Edge detection
        edges = cv2.Canny(filtered, 30, 200)
        
        # Find contours
        contours, _ = cv2.findContours(
            edges,
            cv2.RETR_TREE,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Filter contours by characteristics
        plate_contours = []
        for contour in contours:
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            
            # Basic dimension check
            if w < self.min_width or h < self.min_height:
                continue
            
            # Aspect ratio check
            aspect_ratio = w / h if h > 0 else 0
            if not (self.aspect_ratio_min <= aspect_ratio <= self.aspect_ratio_max):
                continue
            
            # Area check
            area = cv2.contourArea(contour)
            rect_area = w * h
            if rect_area == 0:
                continue
            
            extent = area / rect_area
            if extent < 0.5:  # Contour should fill most of bounding box
                continue
            
            plate_contours.append(contour)
        
        # Sort by area (larger plates first)
        plate_contours.sort(key=lambda c: cv2.contourArea(c), reverse=True)
        
        # Return top candidates
        return plate_contours[:3]
    
    def _validate_dimensions(self, width: int, height: int) -> bool:
        """
        Validate plate dimensions
        
        Args:
            width: Plate width in pixels
            height: Plate height in pixels
            
        Returns:
            True if dimensions are valid
        """
        # Check size constraints
        if width < self.min_width or width > self.max_width:
            return False
        
        if height < self.min_height or height > self.max_height:
            return False
        
        # Check aspect ratio
        aspect_ratio = width / height if height > 0 else 0
        if not (self.aspect_ratio_min <= aspect_ratio <= self.aspect_ratio_max):
            return False
        
        return True
    
    def _crop_plate_with_padding(
        self,
        frame: np.ndarray,
        bbox: Tuple[int, int, int, int],
        padding: int = 5
    ) -> Optional[np.ndarray]:
        """
        Crop plate region with padding
        
        Args:
            frame: Full frame
            bbox: Plate bounding box
            padding: Padding in pixels
            
        Returns:
            Cropped plate image or None
        """
        h, w = frame.shape[:2]
        x1, y1, x2, y2 = bbox
        
        # Add padding
        x1 = max(0, x1 - padding)
        y1 = max(0, y1 - padding)
        x2 = min(w, x2 + padding)
        y2 = min(h, y2 + padding)
        
        # Crop
        plate_img = frame[y1:y2, x1:x2].copy()
        
        if plate_img.size == 0:
            return None
        
        return plate_img
    
    def _enhance_plate(self, plate_img: np.ndarray) -> np.ndarray:
        """
        Enhance plate image for better OCR
        
        Args:
            plate_img: Plate image
            
        Returns:
            Enhanced plate image
        """
        # Convert to grayscale
        if len(plate_img.shape) == 3:
            gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
        else:
            gray = plate_img
        
        # Resize if too small
        if gray.shape[1] < 200:
            scale = 200 / gray.shape[1]
            new_width = 200
            new_height = int(gray.shape[0] * scale)
            gray = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(enhanced, None, 10, 7, 21)
        
        # Sharpen
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        sharpened = cv2.filter2D(denoised, -1, kernel)
        
        # Threshold to binary
        _, binary = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
    
    def detect_plates_simple(
        self,
        frame: np.ndarray,
        vehicle_bbox: Tuple[int, int, int, int]
    ) -> List[PlateRegion]:
        """
        Simple plate detection - looks at bottom portion of vehicle
        
        Args:
            frame: Full frame
            vehicle_bbox: Vehicle bounding box
            
        Returns:
            List of potential plate regions
        """
        x1, y1, x2, y2 = vehicle_bbox
        vehicle_height = y2 - y1
        
        # Focus on bottom 30% of vehicle (where plates typically are)
        plate_y1 = y1 + int(vehicle_height * 0.6)
        plate_y2 = y2
        
        # Crop region
        search_region = frame[plate_y1:plate_y2, x1:x2].copy()
        
        if search_region.size == 0:
            return []
        
        # Enhance for plate detection
        if self.enhance_image:
            enhanced = self._enhance_plate(search_region)
        else:
            enhanced = search_region
        
        # Create plate region for entire bottom section
        plate_img = self._crop_plate_with_padding(
            frame,
            (x1, plate_y1, x2, plate_y2)
        )
        
        if plate_img is None:
            return []
        
        plate = PlateRegion(
            bbox=(x1, plate_y1, x2, plate_y2),
            confidence=0.6,
            image=plate_img
        )
        
        return [plate]


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python plate_detector.py <image_path>")
        sys.exit(1)
    
    # Load test image
    img = cv2.imread(sys.argv[1])
    
    # Create detector
    detector = PlateDetector()
    
    # Assume whole image is vehicle (for testing)
    h, w = img.shape[:2]
    vehicle_bbox = (0, 0, w, h)
    
    # Detect plates
    plates = detector.detect_plates(img, vehicle_bbox)
    
    print(f"Found {len(plates)} potential plates")
    
    # Display results
    for i, plate in enumerate(plates):
        x1, y1, x2, y2 = plate.bbox
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Save plate image
        cv2.imwrite(f"plate_{i}.jpg", plate.image)
        print(f"Plate {i}: {plate.width}x{plate.height}, AR: {plate.aspect_ratio:.2f}")
    
    cv2.imwrite("detected_plates.jpg", img)
    print("Results saved to detected_plates.jpg")
