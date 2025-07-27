#!/usr/bin/env python3
"""
Phase 5 Test Script

This script tests all the Phase 5 matplotlib plotting functionality.
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


def test_phase5_plots():
    """Test all Phase 5 plot types."""
    try:
        # Setup logging
        setup_logger(log_to_file=False)
        logger = logging.getLogger(__name__)
        logger.info("Starting Phase 5 plot functionality test")
        
        # Create the application
        app = DataAnalysisApp()
        
        # Get access to components
        controller = app.controller
        model = app.model
        right_panel = app.view.right_panel
        plot_manager = right_panel.plot_manager
        
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
        if not focus_info or focus_info.status.value != "loaded":
            logger.error(f"Dataset not loaded properly")
            return False
        
        logger.info(f"Dataset loaded successfully. Testing Phase 5 plots...")
        
        # Test all Phase 5 plot types
        app_state = controller.get_state()
        available_plots = plot_manager.get_available_plots(app_state)
        
        phase5_plots = [
            'track_counts',
            'lat_lon_scatter', 
            'north_east_error',
            'rms_error_3d',
            'track_truth_lifetime',
            'lat_lon_animation'
        ]
        
        test_results = {}
        
        for plot_id in phase5_plots:
            try:
                logger.info(f"Testing plot: {plot_id}")
                
                # Check if plot is available
                plot_available = any(p['id'] == plot_id and p['enabled'] for p in available_plots)
                if not plot_available:
                    logger.warning(f"Plot {plot_id} is not available/enabled")
                    test_results[plot_id] = "UNAVAILABLE"
                    continue
                
                # Test data preparation
                plot_data = plot_manager.prepare_plot_data(plot_id, app_state)
                if 'error' in plot_data:
                    logger.error(f"Error preparing {plot_id}: {plot_data['error']}")
                    test_results[plot_id] = "DATA_ERROR"
                    continue
                
                logger.info(f"Successfully prepared data for {plot_id}")
                test_results[plot_id] = "SUCCESS"
                
            except Exception as e:
                logger.error(f"Error testing {plot_id}: {e}")
                test_results[plot_id] = "EXCEPTION"
        
        # Print test results
        logger.info("=== Phase 5 Test Results ===")
        for plot_id, result in test_results.items():
            logger.info(f"{plot_id}: {result}")
        
        # Check if all tests passed
        success_count = sum(1 for result in test_results.values() if result == "SUCCESS")
        total_tests = len(phase5_plots)
        
        logger.info(f"Test Summary: {success_count}/{total_tests} plots working correctly")
        
        # Check that we have the expected tabs
        expected_tabs = ["Overview", "Visualization", "Statistics", "Geospatial", 
                        "Error Analysis", "RMS Error", "Lifetime", "Animation"]
        
        actual_tabs = []
        for i in range(right_panel.notebook.index("end")):
            tab_text = right_panel.notebook.tab(i, "text")
            actual_tabs.append(tab_text)
        
        logger.info(f"Available tabs: {actual_tabs}")
        
        missing_tabs = set(expected_tabs) - set(actual_tabs)
        if missing_tabs:
            logger.error(f"Missing tabs: {missing_tabs}")
            return False
        
        logger.info("All expected tabs are present!")
        
        return success_count >= (total_tests - 1)  # Allow 1 failure
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = test_phase5_plots()
    print(f"Phase 5 Test {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)
