import logging
import sys
import os

def setup_logger(name: str, level: int = logging.INFO):
    """
    Sets up a standardized logger for the project.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers if setup is called multiple times
    if not logger.handlers:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler (optional, but good for local debug)
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_handler = logging.FileHandler(os.path.join(log_dir, "planner.log"))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

# Default logger for general use
logger = setup_logger("planner")
