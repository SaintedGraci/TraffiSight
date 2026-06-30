"""
Traffic Violation Detection
Detect various traffic violations including red light running, wrong lane usage, speeding, etc.
"""

import cv2
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from ..models.traffic_light_detector import TrafficLight, TrafficLightState
from ..models.byte_tracker import Track
from ..utils.logger import Logger
from ..utils.config_loader import Config


class ViolationType(Enum):
    """Types of traffic violations"""
    RED_LIGHT = "red_light_violation"
    WRONG_LANE = "wrong_lane_usage"
    STOP_LINE = "stop_line_violation"
    SPEEDING = "speeding_violation"
    ILLEGAL_TURN = "illegal_turn"
    NO_PLATE = "no_license_plate"


@dataclass
class Violation:
    """Traffic violation record"""
    violation_type: ViolationType
    track_id: int
    vehicle_type: str
    plate_number: Optional[str]
    frame_number: int
    timestamp: float
    confidence: float
    evidence_bbox: Tuple[int, int, int, int]
    description: str
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'violation_type': self.violation_type.value,
            'track_id': self.track_id,
            'vehicle_type': self.vehicle_type,
            'plate_number': self.plate_number,
            'frame_number': self.frame_number,
            'timestamp': self.timestamp,
            'confidence': self.confidence,
            'evidence_bbox': self.evidence_bbox,
            'description': self.description,
            'metadata': self.metadata
        }


class ViolationDetector:
    """Detect traffic violations"""
    
    def __init__(self):
        """Initialize violation detector"""
        self.logger = Logger.get_logger("ViolationDetector")
        
        # Load configuration
        config = Config()
        self.violation_config = config.get('violation', {})
        
        # Stop line parameters
        self.stop_line_buffer = self.violation_config.get('stop_line_buffer', 10)
        
        # Speed parameters
        self.fps_default = self.violation_config.get('fps_default', 30)
        self.pixel_to_meter_ratio = self.violation_config.get('pixel_to_meter_ratio', 0.05)
        self.speed_limit_kmh = 50  # Default speed limit
        
        # Tracking
        self.violations = []
        self.vehicle_states = {}  # Track vehicle states
        
        self.logger.info("ViolationDetector initialized")
    
    def detect_violations(
        self,
        frame: np.ndarray,
        tracks: List[Track],
        traffic_lights: List[TrafficLight],
        stop_line: Optional[Tuple[int, int, int, int]] = None,
        frame_number: int = 0,
        timestamp: float = 0.0,
        fps: float = 30.0
    ) -> List[Violation]:
        """
        Detect violations in current frame
        
        Args:
            frame: Current frame
            tracks: Vehicle tracks
            traffic_lights: Detected traffic lights
            stop_line: Stop line coordinates (x1, y1, x2, y2)
            frame_number: Current frame number
            timestamp: Timestamp in video
            fps: Video FPS
            
        Returns:
            List of detected violations
        """
        frame_violations = []
        
        # Get dominant traffic light
        from ..models.traffic_light_detector import TrafficLightDetector
        detector = TrafficLightDetector()
        dominant_light = detector.get_dominant_light(traffic_lights)
        
        for track in tracks:
            vehicle_id = track.track_id
            
            # Initialize vehicle state if needed
            if vehicle_id not in self.vehicle_states:
                self.vehicle_states[vehicle_id] = {
                    'last_position': track.get_center(),
                    'last_frame': frame_number,
                    'red_light_frames': 0,
                    'crossed_stop_line': False
                }
            
            # Red light violation
            if dominant_light and dominant_light.is_red and stop_line:
                violation = self._check_red_light_violation(
                    track,
                    stop_line,
                    frame_number,
                    timestamp
                )
                if violation:
                    frame_violations.append(violation)
            
            # Speeding violation
            if frame_number > 0:
                violation = self._check_speeding_violation(
                    track,
                    vehicle_id,
                    frame_number,
                    timestamp,
                    fps
                )
                if violation:
                    frame_violations.append(violation)
            
            # Update vehicle state
            self.vehicle_states[vehicle_id]['last_position'] = track.get_center()
            self.vehicle_states[vehicle_id]['last_frame'] = frame_number
        
        # Add to total violations
        self.violations.extend(frame_violations)
        
        return frame_violations
    
    def _check_red_light_violation(
        self,
        track: Track,
        stop_line: Tuple[int, int, int, int],
        frame_number: int,
        timestamp: float
    ) -> Optional[Violation]:
        """
        Check for red light violation
        
        Args:
            track: Vehicle track
            stop_line: Stop line coordinates
            frame_number: Current frame
            timestamp: Timestamp
            
        Returns:
            Violation if detected, None otherwise
        """
        vehicle_id = track.track_id
        vehicle_center = track.get_center()
        
        # Check if vehicle crossed stop line
        x1_line, y1_line, x2_line, y2_line = stop_line
        
        # For horizontal stop line, check y coordinate
        if abs(y2_line - y1_line) < 50:  # Horizontal line
            crossed = vehicle_center[1] > y1_line + self.stop_line_buffer
        else:  # Vertical line
            crossed = vehicle_center[0] > x1_line + self.stop_line_buffer
        
        # Check if this is a new violation
        if crossed and not self.vehicle_states[vehicle_id].get('crossed_stop_line', False):
            self.vehicle_states[vehicle_id]['crossed_stop_line'] = True
            self.vehicle_states[vehicle_id]['red_light_frames'] += 1
            
            # Only record if crossed during red light
            if self.vehicle_states[vehicle_id]['red_light_frames'] >= 3:
                return Violation(
                    violation_type=ViolationType.RED_LIGHT,
                    track_id=vehicle_id,
                    vehicle_type=track.class_name,
                    plate_number=None,  # To be filled by plate recognizer
                    frame_number=frame_number,
                    timestamp=timestamp,
                    confidence=0.9,
                    evidence_bbox=track.bbox,
                    description=f"{track.class_name.capitalize()} ran red light",
                    metadata={'stop_line': stop_line}
                )
        
        return None
    
    def _check_speeding_violation(
        self,
        track: Track,
        vehicle_id: int,
        frame_number: int,
        timestamp: float,
        fps: float
    ) -> Optional[Violation]:
        """
        Check for speeding violation
        
        Args:
            track: Vehicle track
            vehicle_id: Vehicle ID
            frame_number: Current frame
            timestamp: Timestamp
            fps: Video FPS
            
        Returns:
            Violation if detected, None otherwise
        """
        if vehicle_id not in self.vehicle_states:
            return None
        
        state = self.vehicle_states[vehicle_id]
        current_pos = track.get_center()
        last_pos = state['last_position']
        frame_diff = frame_number - state['last_frame']
        
        if frame_diff == 0:
            return None
        
        # Calculate distance in pixels
        distance_pixels = np.sqrt(
            (current_pos[0] - last_pos[0])**2 +
            (current_pos[1] - last_pos[1])**2
        )
        
        # Convert to meters
        distance_meters = distance_pixels * self.pixel_to_meter_ratio
        
        # Calculate time
        time_seconds = frame_diff / fps
        
        if time_seconds == 0:
            return None
        
        # Calculate speed
        speed_mps = distance_meters / time_seconds
        speed_kmh = speed_mps * 3.6
        
        # Check if speeding
        if speed_kmh > self.speed_limit_kmh:
            return Violation(
                violation_type=ViolationType.SPEEDING,
                track_id=vehicle_id,
                vehicle_type=track.class_name,
                plate_number=None,
                frame_number=frame_number,
                timestamp=timestamp,
                confidence=0.7,
                evidence_bbox=track.bbox,
                description=f"{track.class_name.capitalize()} speeding at {speed_kmh:.1f} km/h",
                metadata={
                    'speed_kmh': speed_kmh,
                    'speed_limit': self.speed_limit_kmh,
                    'over_limit': speed_kmh - self.speed_limit_kmh
                }
            )
        
        return None
    
    def set_speed_limit(self, speed_limit_kmh: float):
        """Set speed limit"""
        self.speed_limit_kmh = speed_limit_kmh
        self.logger.info(f"Speed limit set to {speed_limit_kmh} km/h")
    
    def set_calibration(self, pixel_to_meter_ratio: float):
        """Set pixel to meter calibration"""
        self.pixel_to_meter_ratio = pixel_to_meter_ratio
        self.logger.info(f"Calibration set: 1px = {pixel_to_meter_ratio}m")
    
    def get_violations(
        self,
        violation_type: Optional[ViolationType] = None
    ) -> List[Violation]:
        """
        Get all violations, optionally filtered by type
        
        Args:
            violation_type: Filter by violation type
            
        Returns:
            List of violations
        """
        if violation_type:
            return [v for v in self.violations if v.violation_type == violation_type]
        return self.violations
    
    def get_violation_summary(self) -> Dict:
        """
        Get violation statistics
        
        Returns:
            Dictionary with violation statistics
        """
        summary = {
            'total_violations': len(self.violations),
            'by_type': {},
            'by_vehicle_type': {},
            'unique_vehicles': len(set(v.track_id for v in self.violations))
        }
        
        # Count by violation type
        for violation_type in ViolationType:
            count = len([v for v in self.violations if v.violation_type == violation_type])
            if count > 0:
                summary['by_type'][violation_type.value] = count
        
        # Count by vehicle type
        for violation in self.violations:
            vehicle_type = violation.vehicle_type
            if vehicle_type not in summary['by_vehicle_type']:
                summary['by_vehicle_type'][vehicle_type] = 0
            summary['by_vehicle_type'][vehicle_type] += 1
        
        return summary
    
    def export_violations(self) -> List[Dict]:
        """
        Export violations as JSON-serializable format
        
        Returns:
            List of violation dictionaries
        """
        return [v.to_dict() for v in self.violations]
    
    def reset(self):
        """Reset detector state"""
        self.violations.clear()
        self.vehicle_states.clear()
        self.logger.info("ViolationDetector reset")


# Example usage
if __name__ == "__main__":
    from ..models.byte_tracker import Track, Detection
    from ..models.traffic_light_detector import TrafficLight, TrafficLightState
    
    # Create detector
    detector = ViolationDetector()
    
    # Simulate violations
    print("Simulating traffic violations...")
    
    # Create dummy track
    from dataclasses import dataclass
    
    @dataclass
    class DummyTrack:
        track_id: int
        class_name: str
        bbox: Tuple[int, int, int, int]
        
        def get_center(self):
            x1, y1, x2, y2 = self.bbox
            return ((x1 + x2) // 2, (y1 + y2) // 2)
    
    track = DummyTrack(1, 'car', (100, 100, 200, 200))
    
    # Simulate red light
    red_light = TrafficLight(
        bbox=(50, 50, 80, 80),
        state=TrafficLightState.RED,
        confidence=0.95,
        color_intensity=0.9
    )
    
    # Define stop line
    stop_line = (0, 150, 640, 150)  # Horizontal line at y=150
    
    # Check violations
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    violations = detector.detect_violations(
        frame,
        [track],
        [red_light],
        stop_line,
        frame_number=10,
        timestamp=0.33
    )
    
    print(f"Violations detected: {len(violations)}")
    for v in violations:
        print(f"  {v.violation_type.value}: {v.description}")
    
    # Get summary
    summary = detector.get_violation_summary()
    print(f"\nSummary: {summary}")
