"""
YOLOv8 Vehicle Detector
Detect vehicles (cars, motorcycles, buses, trucks) in video frames
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional
from ultralytics import YOLO

from ..utils.logger import Logger
from ..utils.config_loader import get_config


class Detection:
    """Single detection result"""
    
    def __init__(
        self,
        bbox: Tuple[int, int, int, int],
        confidence: float,
        class_id: int,
        class_name: str
    ):
        """
        Initialize detection
        
        Args:
            bbox: Bounding box (x1, y1, x2, y2)
            confidence: Detection confidence (0-1)
            class_id: COCO class ID
            class_name: Class name (e.g., 'car', 'motorcycle')
        """
        self.bbox = bbox
        self.confidence = confidence
        self.class_id = class_id
        self.class_name = class_name
        
        # Calculate center point
        x1, y1, x2, y2 = bbox
        self.center_x = (x1 + x2) // 2
        self.center_y = (y1 + y2) // 2
        self.width = x2 - x1
        self.height = y2 - y1
    
    def __repr__(self) -> str:
        return (f"Detection({self.class_name}, "
                f"conf={self.confidence:.2f}, "
                f"bbox={self.bbox})")


class YOLODetector:
    """YOLOv8-based vehicle detector"""
    
    # COCO dataset vehicle class IDs
    VEHICLE_CLASSES = {
        2: 'car',
        3: 'motorcycle',
        5: 'bus',
        7: 'truck'
    }
    
    def __init__(
        self,
        model_name: str = "yolov8n.pt",
        confidence_threshold: float = 0.5,
        iou_threshold: float = 0.45,
        device: str = "cpu"
    ):
        """
        Initialize YOLOv8 detector
        
        Args:
            model_name: YOLO model name (n/s/m/l/x)
            confidence_threshold: Minimum confidence for detection
            iou_threshold: IOU threshold for NMS
            device: Device to run on ('cpu', 'cuda', or 'mps')
        """
        self.logger = Logger.get_logger("YOLODetector")
        self.config = get_config()
        
        self.model_name = model_name
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.device = device
        
        self.model: Optional[YOLO] = None
        self._load_model()
    
    def _load_model(self):
        """Load YOLOv8 model"""
        try:
            self.logger.info(f"Loading YOLO model: {self.model_name}")
            
            # Get model path
            models_dir = self.config.get_path('paths.models_dir')
            model_path = models_dir / self.model_name
            
            # Download model if it doesn't exist
            if not model_path.exists():
                self.logger.info(f"Downloading {self.model_name}...")
                self.model = YOLO(self.model_name)
                # Save to models directory
                self.logger.info(f"Model saved to {models_dir}")
            else:
                self.logger.info(f"Loading model from {model_path}")
                self.model = YOLO(str(model_path))
            
            # Move model to device
            if self.device != "cpu":
                self.model.to(self.device)
            
            self.logger.info(f"Model loaded successfully on {self.device}")
            self.logger.info(f"Confidence threshold: {self.confidence_threshold}")
            self.logger.info(f"IOU threshold: {self.iou_threshold}")
            
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            raise
    
    def detect(self, frame: np.ndarray) -> List[Detection]:
        """
        Detect vehicles in a frame
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            List of Detection objects
        """
        if self.model is None:
            self.logger.error("Model not loaded")
            return []
        
        try:
            # Run inference
            results = self.model(
                frame,
                conf=self.confidence_threshold,
                iou=self.iou_threshold,
                verbose=False
            )[0]
            
            detections = []
            
            # Process each detection
            for box in results.boxes:
                class_id = int(box.cls[0])
                
                # Filter for vehicles only
                if class_id in self.VEHICLE_CLASSES:
                    # Get bounding box coordinates
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    confidence = float(box.conf[0])
                    class_name = self.VEHICLE_CLASSES[class_id]
                    
                    detection = Detection(
                        bbox=(x1, y1, x2, y2),
                        confidence=confidence,
                        class_id=class_id,
                        class_name=class_name
                    )
                    detections.append(detection)
            
            return detections
        
        except Exception as e:
            self.logger.error(f"Detection failed: {e}")
            return []
    
    def detect_batch(
        self,
        frames: List[np.ndarray],
        batch_size: int = 32
    ) -> List[List[Detection]]:
        """
        Detect vehicles in multiple frames (batch processing)
        
        Args:
            frames: List of frames
            batch_size: Batch size for inference
            
        Returns:
            List of detection lists (one per frame)
        """
        all_detections = []
        
        for i in range(0, len(frames), batch_size):
            batch = frames[i:i + batch_size]
            
            for frame in batch:
                detections = self.detect(frame)
                all_detections.append(detections)
        
        return all_detections
    
    def get_vehicle_count(self, detections: List[Detection]) -> dict:
        """
        Count vehicles by type
        
        Args:
            detections: List of detections
            
        Returns:
            Dictionary with counts per vehicle type
        """
        counts = {
            'car': 0,
            'motorcycle': 0,
            'bus': 0,
            'truck': 0,
            'total': len(detections)
        }
        
        for detection in detections:
            if detection.class_name in counts:
                counts[detection.class_name] += 1
        
        return counts
    
    def filter_by_confidence(
        self,
        detections: List[Detection],
        min_confidence: float
    ) -> List[Detection]:
        """
        Filter detections by confidence threshold
        
        Args:
            detections: List of detections
            min_confidence: Minimum confidence
            
        Returns:
            Filtered detections
        """
        return [d for d in detections if d.confidence >= min_confidence]
    
    def filter_by_class(
        self,
        detections: List[Detection],
        vehicle_types: List[str]
    ) -> List[Detection]:
        """
        Filter detections by vehicle type
        
        Args:
            detections: List of detections
            vehicle_types: List of vehicle types to keep
            
        Returns:
            Filtered detections
        """
        return [d for d in detections if d.class_name in vehicle_types]
    
    def get_model_info(self) -> dict:
        """Get model information"""
        return {
            'model_name': self.model_name,
            'device': self.device,
            'confidence_threshold': self.confidence_threshold,
            'iou_threshold': self.iou_threshold,
            'vehicle_classes': list(self.VEHICLE_CLASSES.values()),
        }


# Example usage
if __name__ == "__main__":
    import sys
    from ..core.video_loader import VideoLoader
    
    if len(sys.argv) < 2:
        print("Usage: python yolo_detector.py <video_path>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    # Initialize detector
    detector = YOLODetector(model_name="yolov8n.pt")
    
    # Load video
    with VideoLoader(video_path) as loader:
        print(f"\nProcessing: {loader.video_path.name}")
        print(f"Model: {detector.model_name}")
        print("-" * 60)
        
        # Process first 30 frames
        for i in range(min(30, loader.frame_count)):
            success, frame = loader.read_frame()
            if not success:
                break
            
            # Detect vehicles
            detections = detector.detect(frame)
            
            if detections:
                counts = detector.get_vehicle_count(detections)
                print(f"Frame {i}: {counts['total']} vehicles "
                      f"(Cars: {counts['car']}, "
                      f"Motorcycles: {counts['motorcycle']}, "
                      f"Buses: {counts['bus']}, "
                      f"Trucks: {counts['truck']})")
