"""
Laravel API Client
Communicate with Laravel backend to send analysis results
"""

import requests
import json
from typing import Dict, List, Optional
from pathlib import Path

from ..utils.logger import Logger
from ..utils.config_loader import Config


class LaravelClient:
    """Client for Laravel API communication"""
    
    def __init__(self):
        """Initialize Laravel client"""
        self.logger = Logger.get_logger("LaravelClient")
        
        # Load configuration
        config = Config()
        api_config = config.get('api', {})
        
        self.base_url = api_config.get('base_url', 'http://localhost:8000')
        self.endpoint = api_config.get('endpoint', '/api/analysis/results')
        self.timeout = api_config.get('timeout', 30)
        self.retry_attempts = api_config.get('retry_attempts', 3)
        
        # API token (if needed)
        self.api_token = None
        
        self.logger.info(f"LaravelClient initialized: {self.base_url}")
    
    def set_token(self, token: str):
        """Set API authentication token"""
        self.api_token = token
        self.logger.info("API token set")
    
    def send_analysis_results(
        self,
        video_id: int,
        results: Dict
    ) -> Dict:
        """
        Send analysis results to Laravel
        
        Args:
            video_id: Video ID in database
            results: Analysis results dictionary
            
        Returns:
            API response
        """
        url = f"{self.base_url}{self.endpoint}"
        
        payload = {
            'video_id': video_id,
            'results': results,
            'processed_at': results.get('timestamp', None)
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if self.api_token:
            headers['Authorization'] = f'Bearer {self.api_token}'
        
        # Retry logic
        for attempt in range(self.retry_attempts):
            try:
                self.logger.info(f"Sending results to Laravel (attempt {attempt + 1}/{self.retry_attempts})...")
                
                response = requests.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout
                )
                
                response.raise_for_status()
                
                self.logger.info("Results sent successfully")
                return response.json()
                
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Request failed (attempt {attempt + 1}): {e}")
                
                if attempt == self.retry_attempts - 1:
                    self.logger.error("All retry attempts failed")
                    raise
        
        return {}
    
    def send_detection_results(
        self,
        video_id: int,
        detections: List[Dict]
    ) -> Dict:
        """Send vehicle detection results"""
        return self.send_analysis_results(video_id, {
            'type': 'detection',
            'detections': detections
        })
    
    def send_tracking_results(
        self,
        video_id: int,
        tracks: List[Dict]
    ) -> Dict:
        """Send vehicle tracking results"""
        return self.send_analysis_results(video_id, {
            'type': 'tracking',
            'tracks': tracks
        })
    
    def send_plate_results(
        self,
        video_id: int,
        plates: List[Dict]
    ) -> Dict:
        """Send license plate recognition results"""
        return self.send_analysis_results(video_id, {
            'type': 'plates',
            'plates': plates
        })
    
    def send_violation_results(
        self,
        video_id: int,
        violations: List[Dict]
    ) -> Dict:
        """Send violation detection results"""
        return self.send_analysis_results(video_id, {
            'type': 'violations',
            'violations': violations
        })
    
    def update_video_status(
        self,
        video_id: int,
        status: str,
        progress: int = 0
    ) -> Dict:
        """
        Update video processing status
        
        Args:
            video_id: Video ID
            status: Status (processing, completed, failed)
            progress: Progress percentage (0-100)
            
        Returns:
            API response
        """
        url = f"{self.base_url}/api/videos/{video_id}/status"
        
        payload = {
            'status': status,
            'progress': progress
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if self.api_token:
            headers['Authorization'] = f'Bearer {self.api_token}'
        
        try:
            response = requests.put(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to update video status: {e}")
            return {}
    
    def upload_evidence_image(
        self,
        video_id: int,
        image_path: str,
        violation_id: Optional[int] = None
    ) -> Dict:
        """
        Upload evidence image to Laravel
        
        Args:
            video_id: Video ID
            image_path: Path to image file
            violation_id: Associated violation ID
            
        Returns:
            API response with uploaded file info
        """
        url = f"{self.base_url}/api/videos/{video_id}/evidence"
        
        files = {
            'image': open(image_path, 'rb')
        }
        
        data = {}
        if violation_id:
            data['violation_id'] = violation_id
        
        headers = {}
        if self.api_token:
            headers['Authorization'] = f'Bearer {self.api_token}'
        
        try:
            response = requests.post(
                url,
                files=files,
                data=data,
                headers=headers,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to upload evidence: {e}")
            return {}
    
    def get_video_info(self, video_id: int) -> Dict:
        """
        Get video information from Laravel
        
        Args:
            video_id: Video ID
            
        Returns:
            Video information
        """
        url = f"{self.base_url}/api/videos/{video_id}"
        
        headers = {'Accept': 'application/json'}
        if self.api_token:
            headers['Authorization'] = f'Bearer {self.api_token}'
        
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get video info: {e}")
            return {}
    
    def health_check(self) -> bool:
        """
        Check if Laravel API is accessible
        
        Returns:
            True if API is accessible
        """
        url = f"{self.base_url}/api/health"
        
        try:
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False


# Example usage
if __name__ == "__main__":
    # Create client
    client = LaravelClient()
    
    # Health check
    if client.health_check():
        print("✓ Laravel API is accessible")
    else:
        print("✗ Laravel API is not accessible")
    
    # Example: Send detection results
    results = {
        'video_id': 1,
        'total_vehicles': 150,
        'detections_by_frame': [
            {
                'frame': 0,
                'vehicles': [
                    {'type': 'car', 'confidence': 0.95}
                ]
            }
        ]
    }
    
    try:
        response = client.send_detection_results(1, results)
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")
