#!/usr/bin/env python3
"""
Data Analysis Application - Main Entry Point

This is the main entry point for the tkinter-based data analysis application.
It initializes and starts the application following the MVC pattern.
"""

import sys
import logging
from pathlib import Path

# Add the application directory to the Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

from src.application import DataAnalysisApp
from src.utils.logger import setup_logger


def main():
    """Main entry point for the application."""
    try:
        # Setup logging
        setup_logger()
        logger = logging.getLogger(__name__)
        logger.info("Starting Data Analysis Application")
        
        # Create and run the application
        app = DataAnalysisApp()
        app.run()
        
    except Exception as e:
        logging.error(f"Failed to start application: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
