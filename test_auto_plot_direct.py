#!/usr/bin/env python3
"""
Direct test of the geospatial auto-update functionality.
"""

import sys
import logging
from pathlib import Path
import pandas as pd

# Add the application directory to the Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

from src.models.application_state import ApplicationState, DatasetInfo, DatasetStatus
from src.components.right_panel import RightPanel
from src.controllers.application_controller import ApplicationController
from src.gui.main_window import MainWindow
from src.utils.logger import setup_logger
import tkinter as tk


def test_auto_geospatial_plot():
    """Test the automatic geospatial plot functionality directly."""
    try:
        # Setup logging
        setup_logger(log_to_file=False)
        logger = logging.getLogger(__name__)
        logger.info("Testing automatic geospatial plot functionality")
        
        # Create a minimal tkinter setup
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Create application state
        model = ApplicationState()
        
        # Create main window and controller
        view = MainWindow(root)
        controller = ApplicationController(model, view)
        view.set_controller(controller)
        
        # Get the right panel
        right_panel = view.right_panel
        
        # Create test dataset with sample data
        sample_tracks = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=10, freq='1S'),
            'lat': [40.712 + i*0.001 for i in range(10)],
            'lon': [-74.006 + i*0.001 for i in range(10)],
            'alt': [100.0 + i for i in range(10)],
            'track_id': ['TRACK_001'] * 10
        })
        
        sample_truth = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=10, freq='1S'),
            'lat': [40.713 + i*0.001 for i in range(10)],
            'lon': [-74.005 + i*0.001 for i in range(10)],
            'alt': [101.0 + i for i in range(10)],
            'id': ['TRUTH_001'] * 10
        })
        
        # Create dataset info
        dataset_info = DatasetInfo(
            name="test_dataset",
            path=Path("/test"),
            status=DatasetStatus.LOADED,
            tracks_df=sample_tracks,
            truth_df=sample_truth
        )
        
        # Add dataset to model
        model.add_dataset(dataset_info)
        model.focus_dataset = "test_dataset"
        
        logger.info("Setup complete, calling auto-update method")
        
        # Test the automatic geospatial plot method directly
        result = right_panel._auto_update_geospatial_plot()
        
        logger.info("Auto-update method completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        return False
    finally:
        try:
            root.destroy()
        except:
            pass


if __name__ == "__main__":
    success = test_auto_geospatial_plot()
    print(f"Direct test {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)
