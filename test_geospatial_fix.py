#!/usr/bin/env python3
"""
Test script to verify the geospatial plot fix.

This script tests whether the lat/lon plot appears automatically when datasets are loaded.
"""

import sys
import logging
from pathlib import Path
import time

# Add the application directory to the Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

from src.application import DataAnalysisApp
from src.utils.logger import setup_logger


def test_geospatial_auto_plot():
    """Test that geospatial plot appears automatically when data is loaded."""
    try:
        # Setup logging
        setup_logger(log_to_file=False)
        logger = logging.getLogger(__name__)
        logger.info("Starting geospatial plot test")
        
        # Create the application
        app = DataAnalysisApp()
        
        # Get access to components
        controller = app.controller
        model = app.model
        right_panel = app.view.right_panel
        
        # Set dataset directory to our test data
        data_dir = Path(__file__).parent / "data"
        logger.info(f"Setting dataset directory to: {data_dir}")
        controller.load_dataset_directory(str(data_dir))
        
        # Wait for datasets to be discovered
        time.sleep(2)
        
        # Check if datasets were found
        datasets = model.datasets
        logger.info(f"Found {len(datasets)} datasets: {list(datasets.keys())}")
        
        if not datasets:
            logger.error("No datasets found!")
            return False
        
        # Load the first dataset
        dataset_name = list(datasets.keys())[0]
        logger.info(f"Loading dataset: {dataset_name}")
        controller.load_single_dataset(dataset_name)
        
        # Wait for dataset to load
        time.sleep(3)
        
        # Set as focus dataset
        logger.info(f"Setting focus dataset to: {dataset_name}")
        controller.set_focus_dataset(dataset_name)
        
        # Check if the dataset is loaded
        focus_info = model.get_focus_dataset_info()
        if focus_info and focus_info.status.value == "loaded":
            logger.info(f"Dataset loaded successfully. Status: {focus_info.status.value}")
            logger.info(f"Tracks data: {focus_info.tracks_df is not None and not focus_info.tracks_df.empty if focus_info.tracks_df is not None else False}")
            logger.info(f"Truth data: {focus_info.truth_df is not None and not focus_info.truth_df.empty if focus_info.truth_df is not None else False}")
            
            # Check if geospatial plot was automatically created
            if 'geospatial' in right_panel.canvas_widgets:
                canvas = right_panel.canvas_widgets['geospatial']
                # The plot should have been created automatically
                logger.info("Geospatial canvas is available")
                return True
            else:
                logger.error("Geospatial canvas not found!")
                return False
        else:
            logger.error(f"Dataset not loaded properly. Status: {focus_info.status.value if focus_info else 'None'}")
            return False
            
    except Exception as e:
        logger.error(f"Test failed with error: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = test_geospatial_auto_plot()
    print(f"Test {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)
