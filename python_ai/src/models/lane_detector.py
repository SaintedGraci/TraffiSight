"""
Lane Detection Module
Detect lane markings and classify vehicle positions in lanes
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from ..utils.logger import Logger
from ..utils.config_loader import ConfigLoader as Config


class LanePosition(Enum):
    """Vehicle position relative to lanes"""
    LEFT_LANE = "left"
    CENTER_LANE = "center"
    RIGHT_LANE = "right"
    BETWEEN_LANES = "between"
    UNKNOWN = "unknown"


@dataclass
class Lane:
    """Single lane line"""
    x1: int
    y1: int
    x2: int
    y2: int
    slope: float
    intercept: float
    side: str  # 'left' or 'right'
    
    def draw(self, image: np.ndarray, color: Tuple[int, int, int] = (0, 255, 0), thickness: int = 5):
        """Draw lane line on image"""
        cv2.line(image, (self.x1, self.y1), (self.x2, self.y2), color, thickness)


@dataclass
class LaneInfo:
    """Complete lane detection information"""
    left_lane: Optional[Lane] = None
    right_lane: Optional[Lane] = None
    center_x: Optional[int] = None
    lane_width: Optional[int] = None
    detected: bool = False
    
    @property
    def has_both_lanes(self) -> bool:
        return self.left_lane is not None and self.right_lane is not None


class LaneDetector:
    """Detect road lane markings using Hough Transform"""
    
    def __init__(self):
        """Initialize lane detector"""
        self.logger = Logger.get_logger("LaneDetector")
        
        # Load configuration
        config = Config()
        lane_config = config.get('lane_detection', {})
        
        self.canny_low = lane_config.get('canny_low', 50)
        self.canny_high = lane_config.get('canny_high', 150)
        self.hough_threshold = lane_config.get('hough_threshold', 100)
        self.min_line_length = lane_config.get('min_line_length', 50)
        self.max_line_gap = lane_config.get('max_line_gap', 10)
        
        # Region of interest (ROI) - focus on bottom portion of frame
        self.roi_height_ratio = 0.6  # Top 60% ignored, bottom 40% processed
        
        self.logger.info("LaneDetector initialized")
    
    def detect_lanes(self, frame: np.ndarray) -> LaneInfo:
        """
        Detect lane markings in frame
        
        Args:
            frame: Input frame
            
        Returns:
            LaneInfo with detected lanes
        """
        h, w = frame.shape[:2]
        
        # Pre-process frame
        processed = self._preprocess_frame(frame)
        
        # Apply region of interest
        roi_mask = self._get_roi_mask(frame.shape)
        masked = cv2.bitwise_and(processed, roi_mask)
        
        # Detect lines using Hough Transform
        lines = cv2.HoughLinesP(
            masked,
            rho=1,
            theta=np.pi / 180,
            threshold=self.hough_threshold,
            minLineLength=self.min_line_length,
            maxLineGap=self.max_line_gap
        )
        
        if lines is None or len(lines) == 0:
            return LaneInfo(detected=False)
        
        # Classify lines as left or right lanes
        left_lines, right_lines = self._classify_lines(lines, w)
        
        # Average lines to get single left and right lane
        left_lane = self._average_lines(left_lines, h) if left_lines else None
        right_lane = self._average_lines(right_lines, h) if right_lines else None
        
        # Calculate lane info
        lane_info = LaneInfo(
            left_lane=left_lane,
            right_lane=right_lane,
            detected=left_lane is not None or right_lane is not None
        )
        
        if lane_info.has_both_lanes:
            # Calculate center and width
            center_bottom_x = (left_lane.x2 + right_lane.x2) // 2
            lane_info.center_x = center_bottom_x
            lane_info.lane_width = abs(right_lane.x2 - left_lane.x2)
        
        return lane_info
    
    def _preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Pre-process frame for lane detection
        
        Args:
            frame: Input frame
            
        Returns:
            Processed grayscale edge-detected image
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Canny edge detection
        edges = cv2.Canny(blurred, self.canny_low, self.canny_high)
        
        return edges
    
    def _get_roi_mask(self, shape: Tuple[int, int, int]) -> np.ndarray:
        """
        Create region of interest mask (trapezoid shape)
        
        Args:
            shape: Frame shape (height, width, channels)
            
        Returns:
            Binary mask
        """
        h, w = shape[:2]
        
        # Define trapezoid vertices (focus on bottom portion)
        top_offset = int(h * self.roi_height_ratio)
        
        vertices = np.array([[
            (0, h),                          # Bottom left
            (w // 2 - w // 8, top_offset),  # Top left
            (w // 2 + w // 8, top_offset),  # Top right
            (w, h)                           # Bottom right
        ]], dtype=np.int32)
        
        # Create mask
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.fillPoly(mask, vertices, 255)
        
        return mask
    
    def _classify_lines(
        self,
        lines: np.ndarray,
        frame_width: int
    ) -> Tuple[List, List]:
        """
        Classify lines as left or right lane based on slope and position
        
        Args:
            lines: Detected lines from HoughLinesP
            frame_width: Width of frame
            
        Returns:
            Tuple of (left_lines, right_lines)
        """
        left_lines = []
        right_lines = []
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            
            # Calculate slope
            if x2 - x1 == 0:  # Vertical line, skip
                continue
            
            slope = (y2 - y1) / (x2 - x1)
            
            # Filter by slope (lanes should be somewhat diagonal)
            if abs(slope) < 0.3:  # Too horizontal
                continue
            
            # Classify by slope and position
            if slope < 0:  # Negative slope = left lane
                left_lines.append((slope, x1, y1, x2, y2))
            else:  # Positive slope = right lane
                right_lines.append((slope, x1, y1, x2, y2))
        
        return left_lines, right_lines
    
    def _average_lines(
        self,
        lines: List[Tuple],
        frame_height: int
    ) -> Optional[Lane]:
        """
        Average multiple lines into single lane line
        
        Args:
            lines: List of (slope, x1, y1, x2, y2)
            frame_height: Height of frame
            
        Returns:
            Single averaged Lane or None
        """
        if not lines:
            return None
        
        # Extract slopes and intercepts
        slopes = []
        intercepts = []
        
        for slope, x1, y1, x2, y2 in lines:
            intercept = y1 - slope * x1
            slopes.append(slope)
            intercepts.append(intercept)
        
        # Average
        avg_slope = np.mean(slopes)
        avg_intercept = np.mean(intercepts)
        
        # Calculate line endpoints (extend to frame edges)
        # Bottom of frame
        y1 = frame_height
        x1 = int((y1 - avg_intercept) / avg_slope)
        
        # Top of ROI
        y2 = int(frame_height * self.roi_height_ratio)
        x2 = int((y2 - avg_intercept) / avg_slope)
        
        side = 'left' if avg_slope < 0 else 'right'
        
        return Lane(x1, y1, x2, y2, avg_slope, avg_intercept, side)
    
    def get_vehicle_lane_position(
        self,
        vehicle_center_x: int,
        lane_info: LaneInfo
    ) -> LanePosition:
        """
        Determine which lane a vehicle is in
        
        Args:
            vehicle_center_x: X coordinate of vehicle center
            lane_info: Detected lane information
            
        Returns:
            Lane position enum
        """
        if not lane_info.detected:
            return LanePosition.UNKNOWN
        
        # If we only have one lane, basic left/right determination
        if lane_info.left_lane and not lane_info.right_lane:
            return LanePosition.RIGHT_LANE if vehicle_center_x > lane_info.left_lane.x2 else LanePosition.LEFT_LANE
        
        if lane_info.right_lane and not lane_info.left_lane:
            return LanePosition.LEFT_LANE if vehicle_center_x < lane_info.right_lane.x2 else LanePosition.RIGHT_LANE
        
        # Both lanes detected
        if lane_info.has_both_lanes:
            left_x = lane_info.left_lane.x2
            right_x = lane_info.right_lane.x2
            
            # Calculate lane boundaries (with some tolerance)
            lane_width = right_x - left_x
            tolerance = lane_width * 0.15  # 15% tolerance
            
            if vehicle_center_x < left_x - tolerance:
                return LanePosition.LEFT_LANE
            elif vehicle_center_x > right_x + tolerance:
                return LanePosition.RIGHT_LANE
            elif left_x + tolerance < vehicle_center_x < right_x - tolerance:
                return LanePosition.CENTER_LANE
            else:
                return LanePosition.BETWEEN_LANES
        
        return LanePosition.UNKNOWN
    
    def draw_lanes(
        self,
        frame: np.ndarray,
        lane_info: LaneInfo,
        show_roi: bool = False
    ) -> np.ndarray:
        """
        Draw detected lanes on frame
        
        Args:
            frame: Input frame
            lane_info: Lane information
            show_roi: Show region of interest
            
        Returns:
            Frame with lanes drawn
        """
        result = frame.copy()
        
        # Draw ROI if requested
        if show_roi:
            roi_mask = self._get_roi_mask(frame.shape)
            roi_overlay = cv2.cvtColor(roi_mask, cv2.COLOR_GRAY2BGR)
            roi_overlay[:, :, 1] = 0  # Remove green channel
            roi_overlay[:, :, 2] = 0  # Remove red channel
            result = cv2.addWeighted(result, 1.0, roi_overlay, 0.2, 0)
        
        # Draw lanes
        if lane_info.left_lane:
            lane_info.left_lane.draw(result, color=(255, 0, 0), thickness=5)  # Blue
        
        if lane_info.right_lane:
            lane_info.right_lane.draw(result, color=(0, 0, 255), thickness=5)  # Red
        
        # Draw center line if both lanes detected
        if lane_info.has_both_lanes and lane_info.center_x:
            h = frame.shape[0]
            top_y = int(h * self.roi_height_ratio)
            cv2.line(result, (lane_info.center_x, h), (lane_info.center_x, top_y), (0, 255, 0), 3)
        
        # Draw lane fill (between lanes)
        if lane_info.has_both_lanes:
            pts = np.array([
                [lane_info.left_lane.x1, lane_info.left_lane.y1],
                [lane_info.left_lane.x2, lane_info.left_lane.y2],
                [lane_info.right_lane.x2, lane_info.right_lane.y2],
                [lane_info.right_lane.x1, lane_info.right_lane.y1]
            ], dtype=np.int32)
            
            overlay = result.copy()
            cv2.fillPoly(overlay, [pts], (0, 255, 0))
            result = cv2.addWeighted(result, 0.8, overlay, 0.2, 0)
        
        return result
    
    def draw_vehicle_lane_position(
        self,
        frame: np.ndarray,
        vehicle_center: Tuple[int, int],
        lane_position: LanePosition
    ) -> np.ndarray:
        """
        Draw vehicle position indicator
        
        Args:
            frame: Input frame
            vehicle_center: Vehicle center point (x, y)
            lane_position: Lane position enum
            
        Returns:
            Frame with position indicator
        """
        result = frame.copy()
        
        # Color based on position
        color_map = {
            LanePosition.LEFT_LANE: (255, 0, 0),      # Blue
            LanePosition.CENTER_LANE: (0, 255, 0),    # Green
            LanePosition.RIGHT_LANE: (0, 0, 255),     # Red
            LanePosition.BETWEEN_LANES: (0, 255, 255),  # Yellow
            LanePosition.UNKNOWN: (128, 128, 128)     # Gray
        }
        
        color = color_map.get(lane_position, (255, 255, 255))
        
        # Draw marker at vehicle center
        cv2.circle(result, vehicle_center, 8, color, -1)
        cv2.circle(result, vehicle_center, 10, (255, 255, 255), 2)
        
        # Draw label
        label = lane_position.value.upper()
        label_pos = (vehicle_center[0] - 30, vehicle_center[1] - 20)
        
        cv2.putText(
            result,
            label,
            label_pos,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            2,
            cv2.LINE_AA
        )
        
        return result


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python lane_detector.py <image_or_video_path>")
        sys.exit(1)
    
    path = sys.argv[1]
    detector = LaneDetector()
    
    # Check if video or image
    if path.lower().endswith(('.mp4', '.avi', '.mov')):
        # Process video
        cap = cv2.VideoCapture(path)
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect lanes
            lane_info = detector.detect_lanes(frame)
            
            # Draw lanes
            result = detector.draw_lanes(frame, lane_info, show_roi=True)
            
            # Display
            cv2.imshow('Lane Detection', result)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
    else:
        # Process image
        frame = cv2.imread(path)
        
        # Detect lanes
        lane_info = detector.detect_lanes(frame)
        
        print(f"Lanes detected: {lane_info.detected}")
        if lane_info.left_lane:
            print(f"Left lane: slope={lane_info.left_lane.slope:.2f}")
        if lane_info.right_lane:
            print(f"Right lane: slope={lane_info.right_lane.slope:.2f}")
        if lane_info.has_both_lanes:
            print(f"Lane width: {lane_info.lane_width} pixels")
        
        # Draw lanes
        result = detector.draw_lanes(frame, lane_info, show_roi=True)
        
        # Save result
        cv2.imwrite('lane_detection_result.jpg', result)
        print("Result saved to lane_detection_result.jpg")
