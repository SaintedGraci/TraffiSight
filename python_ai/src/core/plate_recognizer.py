"""
License Plate Recognition Pipeline
Complete workflow for detecting and recognizing license plates
"""

import cv2
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

from ..models.plate_detector import PlateDetector, PlateRegion
from ..models.ocr_engine import OCREngine, OCRResult
from ..models.yolo_detector import Detection
from ..utils.logger import Logger
from ..utils.config_loader import Config


@dataclass
class VehiclePlate:
    """Vehicle with recognized plate"""
    vehicle: Detection
    plate_region: Optional[PlateRegion] = None
    ocr_result: Optional[OCRResult] = None
    frame_number: int = 0
    timestamp: float = 0.0
    
    @property
    def has_plate(self) -> bool:
        return self.plate_region is not None
    
    @property
    def has_text(self) -> bool:
        return self.ocr_result is not None and self.ocr_result.text
    
    @property
    def plate_text(self) -> str:
        return self.ocr_result.text if self.has_text else ""
    
    @property
    def plate_confidence(self) -> float:
        return self.ocr_result.confidence if self.has_text else 0.0


class PlateRecognizer:
    """Complete license plate recognition pipeline"""
    
    def __init__(
        self,
        use_simple_detection: bool = False,
        enable_caching: bool = True
    ):
        """
        Initialize plate recognizer
        
        Args:
            use_simple_detection: Use simplified plate detection
            enable_caching: Enable result caching
        """
        self.logger = Logger.get_logger("PlateRecognizer")
        
        # Load configuration
        config = Config()
        self.plate_config = config.get('plate_recognition', {})
        self.enabled = self.plate_config.get('enabled', True)
        
        if not self.enabled:
            self.logger.warning("Plate recognition is disabled in config")
            return
        
        # Initialize components
        self.logger.info("Initializing plate recognition components...")
        self.plate_detector = PlateDetector()
        self.ocr_engine = OCREngine()
        
        self.use_simple_detection = use_simple_detection
        self.enable_caching = enable_caching
        
        # Track plates by vehicle position (for caching)
        self.plate_cache = {}  # {vehicle_id: plate_text}
        self.plate_history = defaultdict(list)  # {track_id: [plate_texts]}
        
        self.logger.info("PlateRecognizer initialized")
    
    def process_vehicle(
        self,
        frame: np.ndarray,
        vehicle: Detection,
        frame_number: int = 0,
        timestamp: float = 0.0
    ) -> VehiclePlate:
        """
        Process single vehicle for plate recognition
        
        Args:
            frame: Video frame
            vehicle: Vehicle detection
            frame_number: Current frame number
            timestamp: Timestamp in video
            
        Returns:
            VehiclePlate with recognition results
        """
        if not self.enabled:
            return VehiclePlate(
                vehicle=vehicle,
                frame_number=frame_number,
                timestamp=timestamp
            )
        
        # Detect plate region
        if self.use_simple_detection:
            plates = self.plate_detector.detect_plates_simple(frame, vehicle.bbox)
        else:
            plates = self.plate_detector.detect_plates(frame, vehicle.bbox)
        
        if not plates:
            return VehiclePlate(
                vehicle=vehicle,
                frame_number=frame_number,
                timestamp=timestamp
            )
        
        # Use first (best) plate
        plate_region = plates[0]
        
        # Recognize text
        ocr_result = self.ocr_engine.recognize_text(plate_region.image)
        
        # Create result
        vehicle_plate = VehiclePlate(
            vehicle=vehicle,
            plate_region=plate_region,
            ocr_result=ocr_result,
            frame_number=frame_number,
            timestamp=timestamp
        )
        
        return vehicle_plate
    
    def process_frame(
        self,
        frame: np.ndarray,
        detections: List[Detection],
        frame_number: int = 0,
        timestamp: float = 0.0
    ) -> List[VehiclePlate]:
        """
        Process all vehicles in frame
        
        Args:
            frame: Video frame
            detections: List of vehicle detections
            frame_number: Current frame number
            timestamp: Timestamp in video
            
        Returns:
            List of VehiclePlate results
        """
        results = []
        
        for vehicle in detections:
            vehicle_plate = self.process_vehicle(
                frame,
                vehicle,
                frame_number,
                timestamp
            )
            results.append(vehicle_plate)
        
        return results
    
    def update_track_plate(
        self,
        track_id: int,
        plate_text: str
    ):
        """
        Update plate history for tracked vehicle
        
        Args:
            track_id: Vehicle track ID
            plate_text: Recognized plate text
        """
        if plate_text:
            self.plate_history[track_id].append(plate_text)
    
    def get_track_plate(
        self,
        track_id: int,
        use_consensus: bool = True
    ) -> Optional[str]:
        """
        Get plate text for tracked vehicle
        
        Args:
            track_id: Vehicle track ID
            use_consensus: Use most common plate text
            
        Returns:
            Plate text or None
        """
        history = self.plate_history.get(track_id, [])
        
        if not history:
            return None
        
        if use_consensus:
            # Return most common plate
            from collections import Counter
            counter = Counter(history)
            most_common = counter.most_common(1)
            return most_common[0][0] if most_common else None
        else:
            # Return latest plate
            return history[-1]
    
    def get_plate_statistics(self) -> Dict:
        """
        Get plate recognition statistics
        
        Returns:
            Dictionary with statistics
        """
        stats = {
            'total_tracks_with_plates': len(self.plate_history),
            'unique_plates': len(set(
                plate
                for plates in self.plate_history.values()
                for plate in plates
            )),
            'plates_by_track': {
                track_id: self.get_track_plate(track_id)
                for track_id in self.plate_history.keys()
            }
        }
        
        return stats
    
    def reset(self):
        """Reset caches and history"""
        self.plate_cache.clear()
        self.plate_history.clear()
        self.logger.info("PlateRecognizer reset")
    
    def save_plate_images(
        self,
        vehicle_plates: List[VehiclePlate],
        output_dir: str
    ):
        """
        Save detected plate images
        
        Args:
            vehicle_plates: List of VehiclePlate results
            output_dir: Output directory
        """
        from pathlib import Path
        import os
        
        output_path = Path(output_dir) / "plates"
        output_path.mkdir(parents=True, exist_ok=True)
        
        saved_count = 0
        for i, vp in enumerate(vehicle_plates):
            if not vp.has_plate:
                continue
            
            # Create filename
            plate_text = vp.plate_text if vp.has_text else "unknown"
            filename = f"frame_{vp.frame_number:06d}_plate_{i}_{plate_text}.jpg"
            filepath = output_path / filename
            
            # Save image
            cv2.imwrite(str(filepath), vp.plate_region.image)
            saved_count += 1
        
        self.logger.info(f"Saved {saved_count} plate images to {output_path}")
    
    def blur_plates_in_frame(
        self,
        frame: np.ndarray,
        vehicle_plates: List[VehiclePlate],
        blur_strength: int = 51
    ) -> np.ndarray:
        """
        Blur license plates in frame (privacy mode)
        
        Args:
            frame: Original frame
            vehicle_plates: List of VehiclePlate results
            blur_strength: Blur kernel size (must be odd)
            
        Returns:
            Frame with blurred plates
        """
        result = frame.copy()
        
        for vp in vehicle_plates:
            if not vp.has_plate:
                continue
            
            x1, y1, x2, y2 = vp.plate_region.bbox
            
            # Extract plate region
            plate_region = result[y1:y2, x1:x2]
            
            # Apply strong blur
            blurred = cv2.GaussianBlur(plate_region, (blur_strength, blur_strength), 0)
            
            # Replace in frame
            result[y1:y2, x1:x2] = blurred
        
        return result
    
    def export_plate_data(
        self,
        vehicle_plates: List[VehiclePlate]
    ) -> List[Dict]:
        """
        Export plate data as JSON-serializable format
        
        Args:
            vehicle_plates: List of VehiclePlate results
            
        Returns:
            List of plate data dictionaries
        """
        data = []
        
        for vp in vehicle_plates:
            if not vp.has_text:
                continue
            
            plate_data = {
                'frame_number': vp.frame_number,
                'timestamp': vp.timestamp,
                'vehicle_type': vp.vehicle.class_name,
                'vehicle_bbox': vp.vehicle.bbox,
                'vehicle_confidence': float(vp.vehicle.confidence),
                'plate': {
                    'text': vp.plate_text,
                    'confidence': float(vp.plate_confidence),
                    'bbox': vp.plate_region.bbox,
                    'validated': vp.ocr_result.validated
                }
            }
            
            data.append(plate_data)
        
        return data


# Example usage
if __name__ == "__main__":
    import sys
    from ..models.yolo_detector import YOLODetector
    
    if len(sys.argv) < 2:
        print("Usage: python plate_recognizer.py <video_path>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    # Create components
    detector = YOLODetector()
    recognizer = PlateRecognizer()
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    
    frame_num = 0
    total_plates = 0
    
    print("Processing video...")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect vehicles
        detections = detector.detect(frame)
        
        # Recognize plates
        vehicle_plates = recognizer.process_frame(frame, detections, frame_num)
        
        # Count plates with text
        plates_found = sum(1 for vp in vehicle_plates if vp.has_text)
        if plates_found > 0:
            total_plates += plates_found
            print(f"Frame {frame_num}: {plates_found} plates found")
            
            for vp in vehicle_plates:
                if vp.has_text:
                    print(f"  - {vp.plate_text} (conf: {vp.plate_confidence:.2f})")
        
        frame_num += 1
        
        # Process limited frames for testing
        if frame_num >= 100:
            break
    
    cap.release()
    
    print(f"\nTotal plates recognized: {total_plates}")
    print(f"Frames processed: {frame_num}")
