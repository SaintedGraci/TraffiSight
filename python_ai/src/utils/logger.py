"""
Logging utility for TraffiSight AI
Provides consistent logging across all modules
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler
import colorlog


class Logger:
    """Custom logger for TraffiSight AI"""
    
    _loggers = {}
    
    @staticmethod
    def get_logger(name: str, log_dir: str = "./logs", level: str = "INFO") -> logging.Logger:
        """
        Get or create a logger instance
        
        Args:
            name: Logger name
            log_dir: Directory to store log files
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            
        Returns:
            logging.Logger: Configured logger instance
        """
        if name in Logger._loggers:
            return Logger._loggers[name]
        
        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper()))
        
        # Prevent duplicate handlers
        if logger.handlers:
            return logger
        
        # Create logs directory
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        
        # Console handler with colors
        console_handler = colorlog.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_format = colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s%(reset)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
        
        # File handler with rotation
        log_file = log_path / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
        
        # Store logger
        Logger._loggers[name] = logger
        
        return logger
    
    @staticmethod
    def log_exception(logger: logging.Logger, exception: Exception, context: str = ""):
        """
        Log an exception with full traceback
        
        Args:
            logger: Logger instance
            exception: Exception to log
            context: Additional context information
        """
        import traceback
        
        error_msg = f"{context}\n" if context else ""
        error_msg += f"Exception: {type(exception).__name__}: {str(exception)}\n"
        error_msg += f"Traceback:\n{traceback.format_exc()}"
        
        logger.error(error_msg)


# Example usage
if __name__ == "__main__":
    # Create logger
    logger = Logger.get_logger("test", level="DEBUG")
    
    # Test different log levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    # Test exception logging
    try:
        1 / 0
    except Exception as e:
        Logger.log_exception(logger, e, "Testing exception logging")
