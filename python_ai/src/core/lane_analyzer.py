"""
Lane Analysis Module
Analyze vehicle positions in lanes and detect lane violations
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

from ..models.lane_detector import LaneDetector, LaneInfo, LanePosition
from ..models.yolo_detector import Detection
from ..models.byte_tracker import Track
from ..utils.logger import Logger


@dataclass
class VehicleLaneInfo:
    """Vehicle with lane position information"""
    vehicle: Detection
    lane_position: LanePosition
    track_id: Optional[int] = None
    center_point: Tuple[int, int] = (0, 0)
    distance_from_center: Optional[float] = None
    
    @property
    def in_lane(self) -> bool:
        """Check if vehicle is properly in a lane"""
        return self.lane_position in [
            LanePosition.LEFT_LANE,
            LanePosition.CENTER_LANE,
            LanePosition.RIGHT_LANE
        ]
    
    @property
    def between_lanes(self) -> bool:
        """Check if vehicle is between lanes"""
        return self.lane_position == LanePosition.BETWEEN_LANES


class LaneAnalyzer:
    """Analyze vehicle positions in lanes"""
    
    def __init__(self):
        """Initialize lane analyzer"""
        self.logger = Logger.get_logger("LaneAnalyzer")
        
        # Initialize lane detector
        self.lane_detector = LaneDetector()
        
        # Track history
        self.vehicle_lane_history = defaultdict(list)  # {track_id: [lane_positions]}
        self.lane_change_events = []  # List of lane change events
        
        self.logger.info("LaneAnalyzer initialized")
    
    def analyze_frame(
        self,
        frame: np.ndarray,
        detections: List[Detection],
        tracks: Optional[List[Track]] = None
    ) -> Tuple[LaneInfo, List[VehicleLaneInfo]]:
        """
        Analyze frame for lanes and vehicle positions
        
        Args:
            frame: Input frame
            detections: List of vehicle detections
            tracks: Optional list of tracks (for history tracking)
            
        Returns:
            Tuple of (LaneInfo, List of VehicleLaneInfo)
        """
        # Detect lanes
        lane_info = self.lane_detector.detect_lanes(frame)
        
        # Analyze each vehicle
        vehicle_lane_infos = []
        
        for i, detection in enumerate(detections):
            # Get vehicle center
            center_x = detection.center_x
            center_y = detection.center_y
            
            # Determine lane position
            lane_position = self.lane_detector.get_vehicle_lane_position(
                center_x,
                lane_info
            )
            
            # Get track ID if available
            track_id = None
            if tracks and i < len(tracks):
                track_id = tracks[i].track_id
            
            # Calculate distance from lane center
            distance_from_center = None
            if lane_info.center_x:
                distance_from_center = abs(center_x - lane_info.center_x)
            
            # Create vehicle lane info
            vli = VehicleLaneInfo(
                vehicle=detection,
                lane_position=lane_position,
                track_id=track_id,
                center_point=(center_x, center_y),
                distance_from_center=distance_from_center
            )
            
            vehicle_lane_infos.append(vli)
            
            # Update history if tracking
            if track_id is not None:
                self._update_lane_history(track_id, lane_position)
        
        return lane_info, vehicle_lane_infos
    
    def _update_lane_history(
        self,
        track_id: int,
        lane_position: LanePosition
    ):
        """
        Update lane position history for tracked vehicle
        
        Args:
            track_id: Vehicle track ID
            lane_position: Current lane position
        """
        history = self.vehicle_lane_history[track_id]
        history.append(lane_position)
        
        # Detect lane changes
        if len(history) >= 2:
            prev_position = history[-2]
            curr_position = history[-1]
            
            # Check if valid lane change occurred
            if self._is_lane_change(prev_position, curr_position):
                self.lane_change_events.append({
                    'track_id': track_id,
                    'from_lane': prev_position.value,
                    'to_lane': curr_position.value,
                    'frame_count': len(history)
                })
                self.logger.info(
                    f"Lane change detected: Track {track_id} "
                    f"{prev_position.value} -> {curr_position.value}"
                )
    
    def _is_lane_change(
        self,
        prev_position: LanePosition,
        curr_position: LanePosition
    ) -> bool:
        """
        Determine if a lane change occurred
        
        Args:
            prev_position: Previous lane position
            curr_position: Current lane position
            
        Returns:
            True if lane change detected
        """
        # Define valid lane positions
        valid_lanes = {
            LanePosition.LEFT_LANE,
            LanePosition.CENTER_LANE,
            LanePosition.RIGHT_LANE
        }
        
        # Both must be valid lanes
        if prev_position not in valid_lanes or curr_position not in valid_lanes:
            return False
        
        # Must be different
        if prev_position == curr_position:
            return False
        
        return True
    
    def get_lane_statistics(self) -> Dict:
        """
        Get lane analysis statistics
        
        Returns:
            Dictionary with statistics
        """
        stats = {
            'total_tracked_vehicles': len(self.vehicle_lane_history),
            'total_lane_changes': len(self.lane_change_events),
            'lane_changes_by_track': defaultdict(int)
        }
        
        # Count lane changes per track
        for event in self.lane_change_events:
            track_id = event['track_id']
            stats['lane_changes_by_track'][track_id] += 1
        
        return stats
    
    def get_track_lane_history(
        self,
        track_id: int
    ) -> List[LanePosition]:
        """
        Get lane position history for specific track
        
        Args:
            track_id: Vehicle track ID
            
        Returns:
            List of lane positions over time
        """
        return self.vehicle_lane_history.get(track_id, [])
    
    def get_current_lane_distribution(
        self,
        vehicle_lane_infos: List[VehicleLaneInfo]
    ) -> Dict[str, int]:
        """
        Get distribution of vehicles across lanes
        
        Args:
            vehicle_lane_infos: List of vehicle lane information
            
        Returns:
            Dictionary with counts per lane
        """
        distribution = {
            'left_lane': 0,
            'center_lane': 0,
            'right_lane': 0,
            'between_lanes': 0,
            'unknown': 0
        }
        
        for vli in vehicle_lane_infos:
            if vli.lane_position == LanePosition.LEFT_LANE:
                distribution['left_lane'] += 1
            elif vli.lane_position == LanePosition.CENTER_LANE:
                distribution['center_lane'] += 1
            elif vli.lane_position == LanePosition.RIGHT_LANE:
                distribution['right_lane'] += 1
            elif vli.lane_position == LanePosition.BETWEEN_LANES:
                distribution['between_lanes'] += 1
            else:
                distribution['unknown'] += 1
        
        return distribution
    
    def detect_improper_lane_usage(
        self,
        vehicle_lane_infos: List[VehicleLaneInfo]
    ) -> List[VehicleLaneInfo]:
        """
        Detect vehicles between lanes (improper positioning)
        
        Args:
            vehicle_lane_infos: List of vehicle lane information
            
        Returns:
            List of vehicles with improper lane usage
        """
        return [vli for vli in vehicle_lane_infos if vli.between_lanes]
    
    def reset(self):
        """Reset analyzer state"""
        self.vehicle_lane_history.clear()
        self.lane_change_events.clear()
        self.logger.info("LaneAnalyzer reset")
    
    def export_lane_data(
        self,
        vehicle_lane_infos: List[VehicleLaneInfo],
        frame_number: int,
        timestamp: float
    ) -> Dict:
        """
        Export lane analysis data
        
        Args:
            vehicle_lane_infos: List of vehicle lane information
            frame_number: Current frame number
            timestamp: Timestamp in video
            
        Returns:
            Dictionary with lane data
        """
        data = {
            'frame_number': frame_number,
            'timestamp': timestamp,
            'vehicles': [],
            'lane_distribution': self.get_current_lane_distribution(vehicle_lane_infos)
        }
        
        for vli in vehicle_lane_infos:
            vehicle_data = {
                'type': vli.vehicle.class_name,
                'lane_position': vli.lane_position.value,
                'center': vli.center_point,
                'in_lane': vli.in_lane,
                'between_lanes': vli.between_lanes
            }
            
            if vli.track_id is not None:
                vehicle_data['track_id'] = vli.track_id
            
            if vli.distance_from_center is not None:
                vehicle_data['distance_from_center'] = float(vli.distance_from_center)
            
            data['vehicles'].append(vehicle_data)
        
        return data


# Example usage
if __name__ == "__main__":
    import sys
    import cv2
    from ..models.yolo_detector import YOLODetector
    
    if len(sys.argv) < 2:
        print("Usage: python lane_analyzer.py <video_path>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    # Create components
    detector = YOLODetector()
    analyzer = LaneAnalyzer()
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    
    frame_num = 0
    
    print("Analyzing video...")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect vehicles
        detections = detector.detect(frame)
        
        # Analyze lanes
        lane_info, vehicle_lane_infos = analyzer.analyze_frame(frame, detections)
        
        # Draw lanes
        result = analyzer.lane_detector.draw_lanes(frame, lane_info)
        
        # Draw vehicle positions
        for vli in vehicle_lane_infos:
            result = analyzer.lane_detector.draw_vehicle_lane_position(
                result,
                vli.center_point,
                vli.lane_position
            )
        
        # Display
        cv2.imshow('Lane Analysis', result)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        frame_num += 1
        
        # Limit for testing
        if frame_num >= 100:
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    # Print statistics
    stats = analyzer.get_lane_statistics()
    print(f"\nStatistics:")
    print(f"Total vehicles tracked: {stats['total_tracked_vehicles']}")
    print(f"Lane changes detected: {stats['total_lane_changes']}")
