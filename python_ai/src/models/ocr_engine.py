"""
OCR Engine for License Plate Recognition
Extract text from license plate images using EasyOCR
"""

import re
import numpy as np
from typing import List, Optional, Tuple
from dataclasses import dataclass

from ..utils.logger import Logger
from ..utils.config_loader import ConfigLoader as Config


@dataclass
class OCRResult:
    """OCR recognition result"""
    text: str
    confidence: float
    raw_text: str  # Original text before cleaning
    validated: bool  # Whether text matches expected format
    bbox: Optional[Tuple[int, int, int, int]] = None


class OCREngine:
    """OCR engine for reading license plate text"""
    
    def __init__(self):
        """Initialize OCR engine"""
        self.logger = Logger.get_logger("OCREngine")
        
        # Load configuration
        config = Config()
        plate_config = config.get('plate_recognition', {})
        
        self.confidence_threshold = plate_config.get('confidence_threshold', 0.6)
        self.languages = plate_config.get('languages', ['en'])
        self.use_gpu = plate_config.get('use_gpu', False)
        self.validate_format = plate_config.get('validate_format', True)
        self.allowed_patterns = plate_config.get('allowed_patterns', [])
        
        # Initialize reader (lazy loading)
        self._reader = None
        self._reader_initialized = False
        
        self.logger.info("OCREngine initialized")
    
    def _initialize_reader(self):
        """Initialize EasyOCR reader (lazy loading)"""
        if self._reader_initialized:
            return
        
        try:
            import easyocr
            self.logger.info(f"Loading EasyOCR with languages: {self.languages}")
            self._reader = easyocr.Reader(
                self.languages,
                gpu=self.use_gpu,
                verbose=False
            )
            self._reader_initialized = True
            self.logger.info("EasyOCR reader loaded successfully")
        except ImportError:
            self.logger.error("EasyOCR not installed. Install with: pip install easyocr")
            raise
        except Exception as e:
            self.logger.error(f"Failed to initialize EasyOCR: {e}")
            raise
    
    def recognize_text(
        self,
        plate_image: np.ndarray,
        return_all: bool = False
    ) -> Optional[OCRResult]:
        """
        Recognize text from plate image
        
        Args:
            plate_image: Plate image (grayscale or color)
            return_all: Return all detections instead of best one
            
        Returns:
            OCRResult or None if no text detected
        """
        # Initialize reader if needed
        self._initialize_reader()
        
        if self._reader is None:
            self.logger.error("OCR reader not initialized")
            return None
        
        try:
            # Run OCR
            results = self._reader.readtext(
                plate_image,
                detail=1,
                paragraph=False
            )
            
            if not results:
                return None
            
            # Process results
            ocr_results = []
            for bbox, text, confidence in results:
                # Clean text
                cleaned_text = self._clean_text(text)
                
                if not cleaned_text:
                    continue
                
                # Validate format
                validated = self._validate_text(cleaned_text)
                
                # Create result
                ocr_result = OCRResult(
                    text=cleaned_text,
                    confidence=confidence,
                    raw_text=text,
                    validated=validated,
                    bbox=self._extract_bbox(bbox)
                )
                
                ocr_results.append(ocr_result)
            
            if not ocr_results:
                return None
            
            # Return all or best result
            if return_all:
                return ocr_results
            
            # Return best result (prioritize validated, then confidence)
            best_result = max(
                ocr_results,
                key=lambda r: (r.validated, r.confidence)
            )
            
            return best_result
            
        except Exception as e:
            self.logger.error(f"OCR recognition failed: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """
        Clean OCR text
        
        Args:
            text: Raw OCR text
            
        Returns:
            Cleaned text
        """
        # Remove whitespace
        text = text.strip()
        
        # Convert to uppercase
        text = text.upper()
        
        # Remove invalid characters (keep alphanumeric and dash)
        text = re.sub(r'[^A-Z0-9-]', '', text)
        
        # Common OCR corrections
        corrections = {
            'O': '0',  # O to zero in numeric positions
            'I': '1',  # I to one in numeric positions
            'S': '5',  # S to five in numeric positions
            'B': '8',  # B to eight in numeric positions
        }
        
        # Apply corrections cautiously (only for ambiguous cases)
        # This is simplified - in production, use position-based logic
        
        return text
    
    def _validate_text(self, text: str) -> bool:
        """
        Validate text against allowed patterns
        
        Args:
            text: Cleaned text
            
        Returns:
            True if text matches any allowed pattern
        """
        if not self.validate_format or not self.allowed_patterns:
            return True
        
        # Check each pattern
        for pattern in self.allowed_patterns:
            if re.match(pattern, text):
                return True
        
        # Additional basic validation
        # Plate should have reasonable length
        if 5 <= len(text) <= 10:
            # Should have both letters and numbers
            has_letters = bool(re.search(r'[A-Z]', text))
            has_numbers = bool(re.search(r'[0-9]', text))
            if has_letters and has_numbers:
                return True
        
        return False
    
    def _extract_bbox(self, bbox_points) -> Tuple[int, int, int, int]:
        """
        Extract bounding box from EasyOCR bbox format
        
        Args:
            bbox_points: EasyOCR bbox (4 points)
            
        Returns:
            (x1, y1, x2, y2) format
        """
        # EasyOCR returns 4 corner points
        points = np.array(bbox_points)
        x_coords = points[:, 0]
        y_coords = points[:, 1]
        
        x1 = int(np.min(x_coords))
        y1 = int(np.min(y_coords))
        x2 = int(np.max(x_coords))
        y2 = int(np.max(y_coords))
        
        return (x1, y1, x2, y2)
    
    def recognize_multiple_images(
        self,
        plate_images: List[np.ndarray]
    ) -> List[Optional[OCRResult]]:
        """
        Recognize text from multiple plate images
        
        Args:
            plate_images: List of plate images
            
        Returns:
            List of OCR results
        """
        results = []
        for plate_img in plate_images:
            result = self.recognize_text(plate_img)
            results.append(result)
        
        return results
    
    def get_consensus(
        self,
        ocr_results: List[OCRResult],
        min_occurrences: int = 2
    ) -> Optional[OCRResult]:
        """
        Get consensus text from multiple OCR results
        
        Args:
            ocr_results: List of OCR results
            min_occurrences: Minimum times text must appear
            
        Returns:
            Consensus result or None
        """
        if not ocr_results:
            return None
        
        # Count occurrences of each text
        text_counts = {}
        text_to_result = {}
        
        for result in ocr_results:
            if result is None:
                continue
            
            text = result.text
            if text not in text_counts:
                text_counts[text] = 0
                text_to_result[text] = result
            
            text_counts[text] += 1
        
        if not text_counts:
            return None
        
        # Find most common text
        most_common = max(text_counts.items(), key=lambda x: x[1])
        text, count = most_common
        
        # Check minimum occurrences
        if count < min_occurrences:
            return None
        
        return text_to_result[text]
    
    def format_plate_text(self, text: str, format_style: str = "default") -> str:
        """
        Format plate text according to style
        
        Args:
            text: Raw plate text
            format_style: Format style (default, spaced, dashed)
            
        Returns:
            Formatted text
        """
        if format_style == "spaced":
            # ABC1234 -> ABC 1234
            if len(text) >= 6:
                letters = re.match(r'^[A-Z]+', text)
                if letters:
                    letter_part = letters.group()
                    number_part = text[len(letter_part):]
                    return f"{letter_part} {number_part}"
        
        elif format_style == "dashed":
            # ABC1234 -> ABC-1234
            if len(text) >= 6:
                letters = re.match(r'^[A-Z]+', text)
                if letters:
                    letter_part = letters.group()
                    number_part = text[len(letter_part):]
                    return f"{letter_part}-{number_part}"
        
        return text


# Example usage
if __name__ == "__main__":
    import sys
    import cv2
    
    if len(sys.argv) < 2:
        print("Usage: python ocr_engine.py <plate_image_path>")
        sys.exit(1)
    
    # Load plate image
    plate_img = cv2.imread(sys.argv[1])
    
    # Create OCR engine
    ocr = OCREngine()
    
    # Recognize text
    print("Recognizing text...")
    result = ocr.recognize_text(plate_img)
    
    if result:
        print(f"\nRecognized Text: {result.text}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Raw Text: {result.raw_text}")
        print(f"Validated: {result.validated}")
        print(f"Formatted: {ocr.format_plate_text(result.text, 'dashed')}")
    else:
        print("No text detected")
