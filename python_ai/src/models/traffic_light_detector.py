"""
Traffic Light Detection
Detect traffic lights and their states (red, yellow, green) using color detection
"""

import cv2
import numpy as np
from typing import List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from ..utils.logger import Logger
from ..utils.config_loader import ConfigLoader as Config


class TrafficLightState(Enum):
    """Traffic light states"""
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"
    UNKNOWN = "unknown"


@dataclass
class TrafficLight:
    """Detected traffic light"""
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    state: TrafficLightState
    confidence: float
    color_intensity: float  # 0-1
    
    @property
    def center(self) -> Tuple[int, int]:
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) // 2, (y1 + y2) // 2)
    
    @property
    def is_red(self) -> bool:
        return self.state == TrafficLightState.RED
    
    @property
    def is_yellow(self) -> bool:
        return self.state == TrafficLightState.YELLOW
    
    @property
    def is_green(self) -> bool:
        return self.state == TrafficLightState.GREEN


class TrafficLightDetector:
    """Detect traffic lights using color-based detection"""
    
    def __init__(self):
        """Initialize traffic light detector"""
        self.logger = Logger.get_logger("TrafficLightDetector")
        
        # Load configuration
        config = Config()
        tl_config = config.get('traffic_light', {})
        
        # HSV color ranges
        self.red_lower = np.array(tl_config.get('red_lower', [0, 100, 100]))
        self.red_upper = np.array(tl_config.get('red_upper', [10, 255, 255]))
        self.yellow_lower = np.array(tl_config.get('yellow_lower', [20, 100, 100]))
        self.yellow_upper = np.array(tl_config.get('yellow_upper', [30, 255, 255]))
        self.green_lower = np.array(tl_config.get('green_lower', [40, 50, 50]))
        self.green_upper = np.array(tl_config.get('green_upper', [80, 255, 255]))
        
        # Detection parameters
        self.min_area = 100
        self.min_circularity = 0.6
        
        self.logger.info("TrafficLightDetector initialized")
    
    def detect(
        self,
        frame: np.ndarray,
        roi: Optional[Tuple[int, int, int, int]] = None
    ) -> List[TrafficLight]:
        """
        Detect traffic lights in frame
        
        Args:
            frame: Input frame
            roi: Region of interest (x1, y1, x2, y2) to search in
            
        Returns:
            List of detected traffic lights
        """
        # Apply ROI if specified
        if roi:
            x1, y1, x2, y2 = roi
            search_region = frame[y1:y2, x1:x2].copy()
            offset_x, offset_y = x1, y1
        else:
            search_region = frame.copy()
            offset_x, offset_y = 0, 0
        
        # Convert to HSV
        hsv = cv2.cvtColor(search_region, cv2.COLOR_BGR2HSV)
        
        traffic_lights = []
        
        # Detect red lights
        red_lights = self._detect_color(
            hsv,
            self.red_lower,
            self.red_upper,
            TrafficLightState.RED,
            offset_x,
            offset_y
        )
        traffic_lights.extend(red_lights)
        
        # Detect yellow lights
        yellow_lights = self._detect_color(
            hsv,
            self.yellow_lower,
            self.yellow_upper,
            TrafficLightState.YELLOW,
            offset_x,
            offset_y
        )
        traffic_lights.extend(yellow_lights)
        
        # Detect green lights
        green_lights = self._detect_color(
            hsv,
            self.green_lower,
            self.green_upper,
            TrafficLightState.GREEN,
            offset_x,
            offset_y
        )
        traffic_lights.extend(green_lights)
        
        return traffic_lights
    
    def _detect_color(
        self,
        hsv_image: np.ndarray,
        lower_bound: np.ndarray,
        upper_bound: np.ndarray,
        state: TrafficLightState,
        offset_x: int,
        offset_y: int
    ) -> List[TrafficLight]:
        """
        Detect specific color in HSV image
        
        Args:
            hsv_image: HSV image
            lower_bound: Lower HSV bound
            upper_bound: Upper HSV bound
            state: Traffic light state
            offset_x: X offset for ROI
            offset_y: Y offset for ROI
            
        Returns:
            List of traffic lights
        """
        # Create mask for color
        mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
        
        # Morphological operations to clean up mask
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        lights = []
        for contour in contours:
            # Filter by area
            area = cv2.contourArea(contour)
            if area < self.min_area:
                continue
            
            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)
            
            # Check circularity
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue
            
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            if circularity < self.min_circularity:
                continue
            
            # Calculate intensity
            roi_mask = mask[y:y+h, x:x+w]
            intensity = np.mean(roi_mask) / 255.0
            
            # Create traffic light object
            light = TrafficLight(
                bbox=(offset_x + x, offset_y + y, offset_x + x + w, offset_y + y + h),
                state=state,
                confidence=min(circularity, intensity),
                color_intensity=intensity
            )
            
            lights.append(light)
        
        return lights
    
    def get_dominant_light(
        self,
        traffic_lights: List[TrafficLight]
    ) -> Optional[TrafficLight]:
        """
        Get most prominent traffic light
        
        Args:
            traffic_lights: List of detected lights
            
        Returns:
            Most confident traffic light or None
        """
        if not traffic_lights:
            return None
        
        # Prioritize red lights
        red_lights = [tl for tl in traffic_lights if tl.is_red]
        if red_lights:
            return max(red_lights, key=lambda tl: tl.confidence)
        
        # Then yellow lights
        yellow_lights = [tl for tl in traffic_lights if tl.is_yellow]
        if yellow_lights:
            return max(yellow_lights, key=lambda tl: tl.confidence)
        
        # Then green lights
        green_lights = [tl for tl in traffic_lights if tl.is_green]
        if green_lights:
            return max(green_lights, key=lambda tl: tl.confidence)
        
        return None


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python traffic_light_detector.py <image_path>")
        sys.exit(1)
    
    # Load image
    img = cv2.imread(sys.argv[1])
    
    # Create detector
    detector = TrafficLightDetector()
    
    # Detect lights
    lights = detector.detect(img)
    
    print(f"Found {len(lights)} traffic lights")
    
    # Draw results
    for light in lights:
        x1, y1, x2, y2 = light.bbox
        
        # Color based on state
        if light.is_red:
            color = (0, 0, 255)
        elif light.is_yellow:
            color = (0, 255, 255)
        else:
            color = (0, 255, 0)
        
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            img,
            f"{light.state.value} {light.confidence:.2f}",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            2
        )
        
        print(f"{light.state.value}: confidence={light.confidence:.2f}")
    
    cv2.imwrite("traffic_lights_detected.jpg", img)
    print("Results saved to traffic_lights_detected.jpg")
