"""
Configuration loader for TraffiSight AI
Handles loading and parsing of configuration files
"""

import yaml
import os
from pathlib import Path
from typing import Any, Dict
from dotenv import load_dotenv


class ConfigLoader:
    """Load and manage configuration settings"""
    
    def __init__(self, config_path: str = "./config/config.yaml"):
        """
        Initialize configuration loader
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self._load_env()
        self._load_yaml()
    
    def _load_env(self):
        """Load environment variables from .env file"""
        env_path = Path(__file__).parent.parent.parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)
    
    def _load_yaml(self):
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        
        Args:
            key: Configuration key (e.g., 'video.frame_extraction.skip_frames')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_path(self, key: str) -> Path:
        """
        Get path configuration and convert to absolute path
        
        Args:
            key: Configuration key for path
            
        Returns:
            Absolute path
        """
        path_str = self.get(key)
        if path_str is None:
            raise ValueError(f"Path configuration not found: {key}")
        
        path = Path(path_str)
        if not path.is_absolute():
            # Make relative to project root
            project_root = Path(__file__).parent.parent.parent
            path = project_root / path
        
        return path.resolve()
    
    def ensure_directories(self):
        """Create all configured directories if they don't exist"""
        paths_config = self.get('paths', {})
        
        for key, path_str in paths_config.items():
            if 'dir' in key.lower():
                path = self.get_path(f'paths.{key}')
                path.mkdir(parents=True, exist_ok=True)
    
    def reload(self):
        """Reload configuration from file"""
        self._load_yaml()
    
    def __repr__(self) -> str:
        return f"ConfigLoader(config_path='{self.config_path}')"


# Global configuration instance
_config = None


def get_config(config_path: str = None) -> ConfigLoader:
    """
    Get global configuration instance
    
    Args:
        config_path: Path to configuration file (only used on first call)
        
    Returns:
        ConfigLoader instance
    """
    global _config
    
    if _config is None:
        if config_path is None:
            config_path = "./config/config.yaml"
        _config = ConfigLoader(config_path)
    
    return _config


# Example usage
if __name__ == "__main__":
    # Load configuration
    config = ConfigLoader("./config/config.yaml")
    
    # Get values
    print(f"App Name: {config.get('app.name')}")
    print(f"Environment: {config.get('app.environment')}")
    print(f"Skip Frames: {config.get('video.frame_extraction.skip_frames')}")
    print(f"YOLO Model: {config.get('detection.model_name')}")
    
    # Get paths
    print(f"Videos Directory: {config.get_path('paths.videos_dir')}")
    print(f"Output Directory: {config.get_path('paths.output_dir')}")
    
    # Create directories
    config.ensure_directories()
    print("All directories created!")
