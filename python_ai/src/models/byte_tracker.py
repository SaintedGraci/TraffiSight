"""
ByteTrack Vehicle Tracker
Track detected vehicles across video frames with unique IDs
Based on ByteTrack algorithm for multi-object tracking
"""

import numpy as np
from typing import List, Optional, Tuple
from collections import deque

from ..utils.logger import Logger
from .yolo_detector import Detection


class Track:
    """Single vehicle track with unique ID"""
    
    _id_counter = 0  # Global track ID counter
    
    def __init__(self, detection: Detection, frame_number: int):
        """
        Initialize a new track
        
        Args:
            detection: Initial detection
            frame_number: Frame where track started
        """
        # Assign unique ID
        Track._id_counter += 1
        self.track_id = Track._id_counter
        
        # Track properties
        self.class_name = detection.class_name
        self.class_id = detection.class_id
        self.bbox = detection.bbox
        self.confidence = detection.confidence
        
        # Track history
        self.history = deque(maxlen=30)  # Keep last 30 positions
        self.history.append((frame_number, detection.bbox, detection.center_x, detection.center_y))
        
        # Track state
        self.hits = 1  # Number of consecutive detections
        self.age = 0  # Frames since first detection
        self.time_since_update = 0  # Frames since last update
        self.state = 'tentative'  # tentative, confirmed, deleted
        
        # Start frame
        self.start_frame = frame_number
        self.last_frame = frame_number
    
    def update(self, detection: Detection, frame_number: int):
        """
        Update track with new detection
        
        Args:
            detection: New detection
            frame_number: Current frame number
        """
        self.bbox = detection.bbox
        self.confidence = detection.confidence
        self.hits += 1
        self.time_since_update = 0
        self.last_frame = frame_number
        
        # Update history
        self.history.append((frame_number, detection.bbox, detection.center_x, detection.center_y))
        
        # Confirm track after minimum hits
        if self.hits >= 3 and self.state == 'tentative':
            self.state = 'confirmed'
    
    def predict(self):
        """
        Predict next position (simple linear prediction)
        """
        self.age += 1
        self.time_since_update += 1
    
    def mark_missed(self):
        """Mark track as missed in current frame"""
        self.time_since_update += 1
        
        # Mark for deletion if too old
        if self.time_since_update > 30:
            self.state = 'deleted'
    
    def get_trajectory(self) -> List[Tuple[int, int]]:
        """
        Get track trajectory (center points)
        
        Returns:
            List of (x, y) center points
        """
        return [(x, y) for _, _, x, y in self.history]
    
    def get_center(self) -> Tuple[int, int]:
        """Get current center point"""
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) // 2, (y1 + y2) // 2)
    
    def get_velocity(self) -> Tuple[float, float]:
        """
        Estimate velocity from last two positions
        
        Returns:
            (vx, vy) velocity in pixels per frame
        """
        if len(self.history) < 2:
            return (0.0, 0.0)
        
        # Get last two positions
        _, _, x2, y2 = self.history[-1]
        _, _, x1, y1 = self.history[-2]
        
        return (float(x2 - x1), float(y2 - y1))
    
    def __repr__(self) -> str:
        return (f"Track(id={self.track_id}, {self.class_name}, "
                f"state={self.state}, hits={self.hits})")


class ByteTracker:
    """
    ByteTrack algorithm for multi-object tracking
    Simplified implementation for vehicle tracking
    """
    
    def __init__(
        self,
        max_age: int = 30,
        min_hits: int = 3,
        iou_threshold: float = 0.3
    ):
        """
        Initialize ByteTracker
        
        Args:
            max_age: Maximum frames to keep track without update
            min_hits: Minimum detections before confirming track
            iou_threshold: IOU threshold for matching
        """
        self.logger = Logger.get_logger("ByteTracker")
        
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        
        self.tracks: List[Track] = []
        self.frame_count = 0
        
        self.logger.info("ByteTracker initialized")
        self.logger.info(f"Parameters: max_age={max_age}, min_hits={min_hits}, iou_threshold={iou_threshold}")
    
    def update(self, detections: List[Detection]) -> List[Track]:
        """
        Update tracks with new detections
        
        Args:
            detections: List of detections in current frame
            
        Returns:
            List of active tracks
        """
        self.frame_count += 1
        
        # Predict new locations for existing tracks
        for track in self.tracks:
            track.predict()
        
        # Match detections to existing tracks
        matched_indices = self._match_detections_to_tracks(detections)
        
        # Update matched tracks
        unmatched_detections = set(range(len(detections)))
        matched_tracks = set()
        
        for det_idx, track_idx in matched_indices:
            self.tracks[track_idx].update(detections[det_idx], self.frame_count)
            unmatched_detections.discard(det_idx)
            matched_tracks.add(track_idx)
        
        # Mark unmatched tracks as missed
        for i, track in enumerate(self.tracks):
            if i not in matched_tracks:
                track.mark_missed()
        
        # Create new tracks for unmatched detections
        for det_idx in unmatched_detections:
            new_track = Track(detections[det_idx], self.frame_count)
            self.tracks.append(new_track)
        
        # Remove dead tracks
        self.tracks = [t for t in self.tracks if t.state != 'deleted']
        
        # Return confirmed tracks only
        return [t for t in self.tracks if t.state == 'confirmed']
    
    def _match_detections_to_tracks(
        self,
        detections: List[Detection]
    ) -> List[Tuple[int, int]]:
        """
        Match detections to existing tracks using IOU
        
        Args:
            detections: List of detections
            
        Returns:
            List of (detection_index, track_index) pairs
        """
        if not self.tracks or not detections:
            return []
        
        # Compute IOU matrix
        iou_matrix = np.zeros((len(detections), len(self.tracks)))
        
        for d, detection in enumerate(detections):
            det_box = detection.bbox
            for t, track in enumerate(self.tracks):
                track_box = track.bbox
                iou_matrix[d, t] = self._compute_iou(det_box, track_box)
        
        # Match using greedy algorithm
        matches = []
        
        while True:
            # Find best match
            if iou_matrix.size == 0:
                break
            
            best_match = np.unravel_index(iou_matrix.argmax(), iou_matrix.shape)
            best_iou = iou_matrix[best_match]
            
            if best_iou < self.iou_threshold:
                break
            
            det_idx, track_idx = best_match
            matches.append((det_idx, track_idx))
            
            # Remove matched detection and track
            iou_matrix[det_idx, :] = 0
            iou_matrix[:, track_idx] = 0
        
        return matches
    
    @staticmethod
    def _compute_iou(box1: Tuple[int, int, int, int], box2: Tuple[int, int, int, int]) -> float:
        """
        Compute Intersection over Union (IOU)
        
        Args:
            box1: First bounding box (x1, y1, x2, y2)
            box2: Second bounding box (x1, y1, x2, y2)
            
        Returns:
            IOU score (0-1)
        """
        x1_1, y1_1, x2_1, y2_1 = box1
        x1_2, y1_2, x2_2, y2_2 = box2
        
        # Intersection area
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i < x1_i or y2_i < y1_i:
            return 0.0
        
        intersection = (x2_i - x1_i) * (y2_i - y1_i)
        
        # Union area
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def get_active_tracks(self) -> List[Track]:
        """
        Get all active confirmed tracks
        
        Returns:
            List of confirmed tracks
        """
        return [t for t in self.tracks if t.state == 'confirmed']
    
    def get_all_tracks(self) -> List[Track]:
        """
        Get all tracks (including tentative)
        
        Returns:
            List of all tracks
        """
        return self.tracks
    
    def get_track_count(self) -> int:
        """Get number of active tracks"""
        return len([t for t in self.tracks if t.state == 'confirmed'])
    
    def reset(self):
        """Reset tracker state"""
        self.tracks = []
        self.frame_count = 0
        Track._id_counter = 0
        self.logger.info("ByteTracker reset")
    
    def get_statistics(self) -> dict:
        """
        Get tracking statistics
        
        Returns:
            Dictionary with tracking stats
        """
        confirmed = [t for t in self.tracks if t.state == 'confirmed']
        tentative = [t for t in self.tracks if t.state == 'tentative']
        
        return {
            'total_tracks': len(self.tracks),
            'confirmed_tracks': len(confirmed),
            'tentative_tracks': len(tentative),
            'frame_count': self.frame_count,
            'max_track_id': Track._id_counter
        }