"""
Detection Visualizer
Draw detection results on frames
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict, TYPE_CHECKING

from ..models.yolo_detector import Detection

if TYPE_CHECKING:
    from ..models.byte_tracker import Track


class DetectionVisualizer:
    """Visualize detection results on frames"""
    
    # Color scheme for different vehicle types (BGR format)
    COLORS = {
        'car': (0, 255, 0),         # Green
        'motorcycle': (255, 0, 0),   # Blue
        'bus': (0, 165, 255),        # Orange
        'truck': (0, 0, 255),        # Red
        'default': (255, 255, 0)     # Cyan
    }
    
    def __init__(
        self,
        line_thickness: int = 2,
        font_scale: float = 0.6,
        font_thickness: int = 2
    ):
        """
        Initialize visualizer
        
        Args:
            line_thickness: Thickness of bounding box lines
            font_scale: Font scale for text
            font_thickness: Thickness of text
        """
        self.line_thickness = line_thickness
        self.font_scale = font_scale
        self.font_thickness = font_thickness
        self.font = cv2.FONT_HERSHEY_SIMPLEX
    
    def draw_detection(
        self,
        frame: np.ndarray,
        detection: Detection,
        show_confidence: bool = True,
        show_class: bool = True
    ) -> np.ndarray:
        """
        Draw a single detection on frame
        
        Args:
            frame: Input frame
            detection: Detection object
            show_confidence: Show confidence score
            show_class: Show class name
            
        Returns:
            Frame with detection drawn
        """
        # Get color for vehicle type
        color = self.COLORS.get(detection.class_name, self.COLORS['default'])
        
        # Draw bounding box
        x1, y1, x2, y2 = detection.bbox
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, self.line_thickness)
        
        # Prepare label text
        label_parts = []
        if show_class:
            label_parts.append(detection.class_name.capitalize())
        if show_confidence:
            label_parts.append(f"{detection.confidence:.2f}")
        
        label = " ".join(label_parts) if label_parts else ""
        
        if label:
            # Calculate label background size
            (label_width, label_height), baseline = cv2.getTextSize(
                label,
                self.font,
                self.font_scale,
                self.font_thickness
            )
            
            # Draw label background
            label_y = max(y1 - 10, label_height + 10)
            cv2.rectangle(
                frame,
                (x1, label_y - label_height - baseline - 5),
                (x1 + label_width + 10, label_y + baseline),
                color,
                -1  # Filled
            )
            
            # Draw label text
            cv2.putText(
                frame,
                label,
                (x1 + 5, label_y - 5),
                self.font,
                self.font_scale,
                (255, 255, 255),  # White text
                self.font_thickness,
                cv2.LINE_AA
            )
        
        # Draw center point
        cv2.circle(frame, (detection.center_x, detection.center_y), 3, color, -1)
        
        return frame
    
    def draw_detections(
        self,
        frame: np.ndarray,
        detections: List[Detection],
        show_confidence: bool = True,
        show_class: bool = True
    ) -> np.ndarray:
        """
        Draw multiple detections on frame
        
        Args:
            frame: Input frame
            detections: List of detections
            show_confidence: Show confidence scores
            show_class: Show class names
            
        Returns:
            Frame with all detections drawn
        """
        result = frame.copy()
        
        for detection in detections:
            result = self.draw_detection(
                result,
                detection,
                show_confidence=show_confidence,
                show_class=show_class
            )
        
        return result
    
    def draw_statistics(
        self,
        frame: np.ndarray,
        detections: List[Detection],
        position: Tuple[int, int] = (10, 30)
    ) -> np.ndarray:
        """
        Draw detection statistics on frame
        
        Args:
            frame: Input frame
            detections: List of detections
            position: Top-left position for stats
            
        Returns:
            Frame with statistics
        """
        result = frame.copy()
        
        # Count vehicles by type
        counts = {
            'car': 0,
            'motorcycle': 0,
            'bus': 0,
            'truck': 0
        }
        
        for detection in detections:
            if detection.class_name in counts:
                counts[detection.class_name] += 1
        
        # Draw background panel
        panel_height = 140
        panel_width = 250
        overlay = result.copy()
        cv2.rectangle(
            overlay,
            (position[0] - 5, position[1] - 25),
            (position[0] + panel_width, position[1] + panel_height),
            (0, 0, 0),
            -1
        )
        cv2.addWeighted(overlay, 0.6, result, 0.4, 0, result)
        
        # Draw statistics
        x, y = position
        line_height = 25
        
        # Title
        cv2.putText(
            result,
            "Vehicle Detection",
            (x, y),
            self.font,
            0.7,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )
        
        y += line_height + 5
        
        # Total
        cv2.putText(
            result,
            f"Total: {len(detections)}",
            (x, y),
            self.font,
            0.6,
            (255, 255, 255),
            1,
            cv2.LINE_AA
        )
        
        # Individual counts with colors
        y += line_height
        for vehicle_type, count in counts.items():
            if count > 0:
                color = self.COLORS[vehicle_type]
                cv2.putText(
                    result,
                    f"{vehicle_type.capitalize()}: {count}",
                    (x, y),
                    self.font,
                    0.5,
                    color,
                    1,
                    cv2.LINE_AA
                )
                y += line_height
        
        return result
    
    def create_detection_frame(
        self,
        frame: np.ndarray,
        detections: List[Detection],
        show_stats: bool = True,
        show_confidence: bool = True,
        show_class: bool = True
    ) -> np.ndarray:
        """
        Create complete visualization with detections and statistics
        
        Args:
            frame: Input frame
            detections: List of detections
            show_stats: Show statistics panel
            show_confidence: Show confidence scores
            show_class: Show class names
            
        Returns:
            Fully annotated frame
        """
        # Draw detections
        result = self.draw_detections(
            frame,
            detections,
            show_confidence=show_confidence,
            show_class=show_class
        )
        
        # Draw statistics
        if show_stats:
            result = self.draw_statistics(result, detections)
        
        return result
    
    def draw_fps(
        self,
        frame: np.ndarray,
        fps: float,
        position: Tuple[int, int] = None
    ) -> np.ndarray:
        """
        Draw FPS counter on frame
        
        Args:
            frame: Input frame
            fps: Frames per second
            position: Position for FPS text (None = bottom right)
            
        Returns:
            Frame with FPS counter
        """
        result = frame.copy()
        
        if position is None:
            # Bottom right corner
            position = (frame.shape[1] - 150, frame.shape[0] - 20)
        
        # Draw background
        overlay = result.copy()
        cv2.rectangle(
            overlay,
            (position[0] - 5, position[1] - 25),
            (position[0] + 140, position[1] + 5),
            (0, 0, 0),
            -1
        )
        cv2.addWeighted(overlay, 0.6, result, 0.4, 0, result)
        
        # Draw FPS text
        fps_text = f"FPS: {fps:.1f}"
        cv2.putText(
            result,
            fps_text,
            position,
            self.font,
            0.6,
            (0, 255, 0),
            2,
            cv2.LINE_AA
        )
        
        return result
    
    def draw_tracks(
        self,
        frame: np.ndarray,
        tracks: List['Track'],
        show_trajectory: bool = True,
        trajectory_length: int = 30
    ) -> np.ndarray:
        """
        Draw tracked vehicles with IDs and trajectories
        
        Args:
            frame: Input frame
            tracks: List of Track objects
            show_trajectory: Draw trajectory path
            trajectory_length: Number of trajectory points to show
            
        Returns:
            Frame with tracks drawn
        """
        result = frame.copy()
        
        for track in tracks:
            # Get color for vehicle type
            color = self.COLORS.get(track.class_name, self.COLORS['default'])
            
            # Draw bounding box
            x1, y1, x2, y2 = track.bbox
            cv2.rectangle(result, (x1, y1), (x2, y2), color, self.line_thickness)
            
            # Draw track ID
            label = f"ID:{track.track_id} {track.class_name.capitalize()} {track.confidence:.2f}"
            
            # Calculate label background size
            (label_width, label_height), baseline = cv2.getTextSize(
                label,
                self.font,
                self.font_scale,
                self.font_thickness
            )
            
            # Draw label background
            label_y = max(y1 - 10, label_height + 10)
            cv2.rectangle(
                result,
                (x1, label_y - label_height - baseline - 5),
                (x1 + label_width + 10, label_y + baseline),
                color,
                -1
            )
            
            # Draw label text
            cv2.putText(
                result,
                label,
                (x1 + 5, label_y - 5),
                self.font,
                self.font_scale,
                (255, 255, 255),
                self.font_thickness,
                cv2.LINE_AA
            )
            
            # Draw trajectory if enabled
            if show_trajectory:
                trajectory = track.get_trajectory()
                if len(trajectory) > 1:
                    # Limit trajectory length
                    trajectory = trajectory[-trajectory_length:]
                    
                    # Draw trajectory lines
                    for i in range(1, len(trajectory)):
                        pt1 = trajectory[i - 1]
                        pt2 = trajectory[i]
                        
                        # Fade effect: older points are more transparent
                        alpha = i / len(trajectory)
                        thickness = max(1, int(self.line_thickness * alpha))
                        
                        cv2.line(result, pt1, pt2, color, thickness, cv2.LINE_AA)
                    
                    # Draw current position marker
                    current_pos = track.get_center()
                    cv2.circle(result, current_pos, 5, color, -1)
        
        # Draw tracking statistics
        result = self.draw_tracking_stats(result, tracks)
        
        return result
    
    def draw_tracking_stats(
        self,
        frame: np.ndarray,
        tracks: List['Track'],
        position: Tuple[int, int] = (10, 30)
    ) -> np.ndarray:
        """
        Draw tracking statistics on frame
        
        Args:
            frame: Input frame
            tracks: List of Track objects
            position: Top-left position for stats
            
        Returns:
            Frame with tracking statistics
        """
        result = frame.copy()
        
        # Count vehicles by type
        counts = {
            'car': 0,
            'motorcycle': 0,
            'bus': 0,
            'truck': 0
        }
        
        for track in tracks:
            if track.class_name in counts:
                counts[track.class_name] += 1
        
        # Draw background panel
        panel_height = 140
        panel_width = 250
        overlay = result.copy()
        cv2.rectangle(
            overlay,
            (position[0] - 5, position[1] - 25),
            (position[0] + panel_width, position[1] + panel_height),
            (0, 0, 0),
            -1
        )
        cv2.addWeighted(overlay, 0.6, result, 0.4, 0, result)
        
        # Draw statistics
        x, y = position
        line_height = 25
        
        # Title
        cv2.putText(
            result,
            "Vehicle Tracking",
            (x, y),
            self.font,
            0.7,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )
        
        y += line_height + 5
        
        # Total tracked vehicles
        cv2.putText(
            result,
            f"Tracked: {len(tracks)}",
            (x, y),
            self.font,
            0.6,
            (0, 255, 0),
            1,
            cv2.LINE_AA
        )
        
        # Individual counts with colors
        y += line_height
        for vehicle_type, count in counts.items():
            if count > 0:
                color = self.COLORS[vehicle_type]
                cv2.putText(
                    result,
                    f"{vehicle_type.capitalize()}: {count}",
                    (x, y),
                    self.font,
                    0.5,
                    color,
                    1,
                    cv2.LINE_AA
                )
                y += line_height
        
        return result
    
    def draw_plate_region(
        self,
        frame: np.ndarray,
        plate_bbox: Tuple[int, int, int, int],
        color: Tuple[int, int, int] = (255, 255, 0)
    ) -> np.ndarray:
        """
        Draw license plate bounding box
        
        Args:
            frame: Input frame
            plate_bbox: Plate bounding box (x1, y1, x2, y2)
            color: Box color (default: cyan)
            
        Returns:
            Frame with plate box drawn
        """
        result = frame.copy()
        x1, y1, x2, y2 = plate_bbox
        
        # Draw thicker box for plate
        cv2.rectangle(result, (x1, y1), (x2, y2), color, 3)
        
        return result
    
    def draw_plate_text(
        self,
        frame: np.ndarray,
        plate_text: str,
        position: Tuple[int, int],
        confidence: float,
        validated: bool = False
    ) -> np.ndarray:
        """
        Draw recognized plate text
        
        Args:
            frame: Input frame
            plate_text: Recognized text
            position: Text position (x, y)
            confidence: OCR confidence
            validated: Whether text format is validated
            
        Returns:
            Frame with text drawn
        """
        result = frame.copy()
        x, y = position
        
        # Choose color based on validation
        text_color = (0, 255, 0) if validated else (0, 255, 255)  # Green if valid, yellow if not
        
        # Format text with confidence
        display_text = f"{plate_text} ({confidence:.2f})"
        
        # Get text size for background
        (text_width, text_height), baseline = cv2.getTextSize(
            display_text,
            self.font,
            0.7,
            2
        )
        
        # Draw background
        overlay = result.copy()
        cv2.rectangle(
            overlay,
            (x - 5, y - text_height - 5),
            (x + text_width + 5, y + baseline + 5),
            (0, 0, 0),
            -1
        )
        cv2.addWeighted(overlay, 0.7, result, 0.3, 0, result)
        
        # Draw text
        cv2.putText(
            result,
            display_text,
            (x, y),
            self.font,
            0.7,
            text_color,
            2,
            cv2.LINE_AA
        )
        
        return result
    
    def draw_vehicle_with_plate(
        self,
        frame: np.ndarray,
        vehicle_plate  # VehiclePlate object
    ) -> np.ndarray:
        """
        Draw vehicle with plate information
        
        Args:
            frame: Input frame
            vehicle_plate: VehiclePlate object
            
        Returns:
            Frame with vehicle and plate drawn
        """
        result = frame.copy()
        
        # Draw vehicle detection
        result = self.draw_detection(result, vehicle_plate.vehicle)
        
        # Draw plate region if detected
        if vehicle_plate.has_plate:
            result = self.draw_plate_region(
                result,
                vehicle_plate.plate_region.bbox,
                color=(255, 255, 0)
            )
            
            # Draw plate text if recognized
            if vehicle_plate.has_text:
                # Position text above plate box
                x1, y1, _, _ = vehicle_plate.plate_region.bbox
                text_pos = (x1, y1 - 10)
                
                result = self.draw_plate_text(
                    result,
                    vehicle_plate.plate_text,
                    text_pos,
                    vehicle_plate.plate_confidence,
                    vehicle_plate.ocr_result.validated
                )
        
        return result
    
    def create_plate_visualization(
        self,
        frame: np.ndarray,
        vehicle_plates: List,  # List[VehiclePlate]
        show_stats: bool = True
    ) -> np.ndarray:
        """
        Create complete visualization with plates
        
        Args:
            frame: Input frame
            vehicle_plates: List of VehiclePlate objects
            show_stats: Show statistics panel
            
        Returns:
            Annotated frame
        """
        result = frame.copy()
        
        # Draw each vehicle with plate
        for vp in vehicle_plates:
            result = self.draw_vehicle_with_plate(result, vp)
        
        # Draw statistics if enabled
        if show_stats:
            plates_detected = sum(1 for vp in vehicle_plates if vp.has_plate)
            plates_recognized = sum(1 for vp in vehicle_plates if vp.has_text)
            
            # Draw stats panel
            result = self._draw_plate_stats(
                result,
                len(vehicle_plates),
                plates_detected,
                plates_recognized
            )
        
        return result
    
    def _draw_plate_stats(
        self,
        frame: np.ndarray,
        total_vehicles: int,
        plates_detected: int,
        plates_recognized: int,
        position: Tuple[int, int] = (10, 30)
    ) -> np.ndarray:
        """Draw plate recognition statistics panel"""
        result = frame.copy()
        
        # Draw background panel
        panel_height = 110
        panel_width = 280
        overlay = result.copy()
        cv2.rectangle(
            overlay,
            (position[0] - 5, position[1] - 25),
            (position[0] + panel_width, position[1] + panel_height),
            (0, 0, 0),
            -1
        )
        cv2.addWeighted(overlay, 0.6, result, 0.4, 0, result)
        
        # Draw statistics
        x, y = position
        line_height = 28
        
        # Title
        cv2.putText(
            result,
            "Plate Recognition",
            (x, y),
            self.font,
            0.7,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )
        
        y += line_height
        
        # Vehicles
        cv2.putText(
            result,
            f"Vehicles: {total_vehicles}",
            (x, y),
            self.font,
            0.6,
            (255, 255, 255),
            1,
            cv2.LINE_AA
        )
        
        y += line_height
        
        # Plates detected
        cv2.putText(
            result,
            f"Plates Detected: {plates_detected}",
            (x, y),
            self.font,
            0.6,
            (255, 255, 0),
            1,
            cv2.LINE_AA
        )
        
        y += line_height
        
        # Plates recognized
        cv2.putText(
            result,
            f"Text Recognized: {plates_recognized}",
            (x, y),
            self.font,
            0.6,
            (0, 255, 0),
            1,
            cv2.LINE_AA
        )
        
        return result
    
    def draw_lane_statistics(
        self,
        frame: np.ndarray,
        lane_distribution: Dict[str, int],
        position: Tuple[int, int] = (10, 180)
    ) -> np.ndarray:
        """
        Draw lane distribution statistics
        
        Args:
            frame: Input frame
            lane_distribution: Dictionary with lane counts
            position: Position for stats panel
            
        Returns:
            Frame with statistics
        """
        result = frame.copy()
        
        # Draw background panel
        panel_height = 150
        panel_width = 250
        overlay = result.copy()
        cv2.rectangle(
            overlay,
            (position[0] - 5, position[1] - 25),
            (position[0] + panel_width, position[1] + panel_height),
            (0, 0, 0),
            -1
        )
        cv2.addWeighted(overlay, 0.6, result, 0.4, 0, result)
        
        # Draw statistics
        x, y = position
        line_height = 28
        
        # Title
        cv2.putText(
            result,
            "Lane Distribution",
            (x, y),
            self.font,
            0.7,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )
        
        y += line_height
        
        # Lane counts with colors
        lane_colors = {
            'left_lane': (255, 0, 0),      # Blue
            'center_lane': (0, 255, 0),    # Green
            'right_lane': (0, 0, 255),     # Red
            'between_lanes': (0, 255, 255),  # Yellow
            'unknown': (128, 128, 128)     # Gray
        }
        
        lane_labels = {
            'left_lane': 'Left Lane',
            'center_lane': 'Center Lane',
            'right_lane': 'Right Lane',
            'between_lanes': 'Between Lanes',
            'unknown': 'Unknown'
        }
        
        for lane_key, count in lane_distribution.items():
            if count > 0:
                color = lane_colors.get(lane_key, (255, 255, 255))
                label = lane_labels.get(lane_key, lane_key)
                
                cv2.putText(
                    result,
                    f"{label}: {count}",
                    (x, y),
                    self.font,
                    0.5,
                    color,
                    1,
                    cv2.LINE_AA
                )
                y += line_height
        
        return result


# Example usage
if __name__ == "__main__":
    # Create test frame
    frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    
    # Create dummy detections
    from ..models.yolo_detector import Detection
    
    detections = [
        Detection((100, 100, 300, 300), 0.95, 2, 'car'),
        Detection((400, 150, 600, 350), 0.87, 2, 'car'),
        Detection((800, 200, 950, 400), 0.92, 3, 'motorcycle'),
        Detection((200, 400, 500, 650), 0.78, 5, 'bus'),
    ]
    
    # Create visualizer
    visualizer = DetectionVisualizer()
    
    # Draw detections
    result = visualizer.create_detection_frame(frame, detections)
    
    # Save result
    cv2.imwrite("test_visualization.jpg", result)
    print("Test visualization saved to test_visualization.jpg")
