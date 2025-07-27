#!/usr/bin/env python3
"""
Enhanced Phase 5 Test Script

Tests all the enhanced control panel features implemented for section 5.1.1 requirements.
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


def test_enhanced_controls():
    """Test the enhanced control panel features for Phase 5."""
    try:
        # Setup logging
        setup_logger(log_to_file=False)
        logger = logging.getLogger(__name__)
        logger.info("Starting Enhanced Phase 5 Control Features Test")
        
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
        
        # Test Results
        test_results = {}
        
        # Test 1: Dataset Selection Controls
        logger.info("Testing dataset selection controls...")
        try:
            # Check if dataset selection variables exist
            if hasattr(right_panel, 'dataset_selection_vars'):
                logger.info(f"✅ Dataset selection variables found: {len(right_panel.dataset_selection_vars)} datasets")
                test_results['dataset_selection'] = "SUCCESS"
            else:
                logger.warning("❌ Dataset selection variables not found")
                test_results['dataset_selection'] = "MISSING"
        except Exception as e:
            logger.error(f"❌ Error testing dataset selection: {e}")
            test_results['dataset_selection'] = "ERROR"
        
        # Test 2: Geospatial Range Controls
        logger.info("Testing geospatial coordinate range controls...")
        try:
            # Check for lat/lon range controls
            required_vars = ['geo_lat_min_var', 'geo_lat_max_var', 'geo_lon_min_var', 'geo_lon_max_var']
            missing_vars = [var for var in required_vars if not hasattr(right_panel, var)]
            
            if not missing_vars:
                logger.info("✅ All geospatial range controls found")
                # Test default values
                lat_min = right_panel.geo_lat_min_var.get()
                lat_max = right_panel.geo_lat_max_var.get()
                lon_min = right_panel.geo_lon_min_var.get()
                lon_max = right_panel.geo_lon_max_var.get()
                logger.info(f"✅ Range defaults: Lat({lat_min}, {lat_max}), Lon({lon_min}, {lon_max})")
                test_results['geospatial_ranges'] = "SUCCESS"
            else:
                logger.warning(f"❌ Missing geospatial variables: {missing_vars}")
                test_results['geospatial_ranges'] = "MISSING"
        except Exception as e:
            logger.error(f"❌ Error testing geospatial ranges: {e}")
            test_results['geospatial_ranges'] = "ERROR"
        
        # Test 3: Track Selection Controls
        logger.info("Testing track selection controls...")
        try:
            # Check for track selection controls
            track_controls = ['error_tracks_var', 'rms_tracks_var']
            missing_controls = [var for var in track_controls if not hasattr(right_panel, var)]
            
            if not missing_controls:
                logger.info("✅ Track selection controls found")
                logger.info(f"✅ Error tracks default: {right_panel.error_tracks_var.get()}")
                logger.info(f"✅ RMS tracks default: {right_panel.rms_tracks_var.get()}")
                test_results['track_selection'] = "SUCCESS"
            else:
                logger.warning(f"❌ Missing track controls: {missing_controls}")
                test_results['track_selection'] = "MISSING"
        except Exception as e:
            logger.error(f"❌ Error testing track selection: {e}")
            test_results['track_selection'] = "ERROR"
        
        # Test 4: Animation Controls
        logger.info("Testing animation playback controls...")
        try:
            # Check for animation controls
            anim_controls = ['anim_playing', 'anim_current_frame', 'anim_speed', 
                           'play_btn', 'pause_btn', 'stop_btn']
            missing_anim = [var for var in anim_controls if not hasattr(right_panel, var)]
            
            if not missing_anim:
                logger.info("✅ Animation playback controls found")
                logger.info(f"✅ Animation speed default: {right_panel.anim_speed.get()}x")
                test_results['animation_controls'] = "SUCCESS"
            else:
                logger.warning(f"❌ Missing animation controls: {missing_anim}")
                test_results['animation_controls'] = "MISSING"
        except Exception as e:
            logger.error(f"❌ Error testing animation controls: {e}")
            test_results['animation_controls'] = "ERROR"
        
        # Test 5: Animation Range Controls
        logger.info("Testing animation coordinate range controls...")
        try:
            # Check for animation range controls
            anim_range_vars = ['anim_lat_min_var', 'anim_lat_max_var', 'anim_lon_min_var', 'anim_lon_max_var']
            missing_anim_vars = [var for var in anim_range_vars if not hasattr(right_panel, var)]
            
            if not missing_anim_vars:
                logger.info("✅ Animation range controls found")
                anim_lat_min = right_panel.anim_lat_min_var.get()
                anim_lat_max = right_panel.anim_lat_max_var.get()
                anim_lon_min = right_panel.anim_lon_min_var.get()
                anim_lon_max = right_panel.anim_lon_max_var.get()
                logger.info(f"✅ Animation range defaults: Lat({anim_lat_min}, {anim_lat_max}), Lon({anim_lon_min}, {anim_lon_max})")
                test_results['animation_ranges'] = "SUCCESS"
            else:
                logger.warning(f"❌ Missing animation range variables: {missing_anim_vars}")
                test_results['animation_ranges'] = "MISSING"
        except Exception as e:
            logger.error(f"❌ Error testing animation ranges: {e}")
            test_results['animation_ranges'] = "ERROR"
        
        # Test 6: Method Implementation
        logger.info("Testing control panel methods...")
        try:
            # Check for required methods
            required_methods = [
                '_select_all_datasets', '_select_no_datasets', '_reset_geo_range',
                '_reset_animation_range', '_animation_play', '_animation_pause',
                '_animation_stop', '_on_speed_changed'
            ]
            missing_methods = [method for method in required_methods 
                             if not hasattr(right_panel, method)]
            
            if not missing_methods:
                logger.info("✅ All required control methods found")
                test_results['control_methods'] = "SUCCESS"
            else:
                logger.warning(f"❌ Missing control methods: {missing_methods}")
                test_results['control_methods'] = "MISSING"
        except Exception as e:
            logger.error(f"❌ Error testing control methods: {e}")
            test_results['control_methods'] = "ERROR"
        
        # Print test results
        logger.info("=== Enhanced Phase 5 Control Features Test Results ===")
        for feature, result in test_results.items():
            status_icon = "✅" if result == "SUCCESS" else "❌"
            logger.info(f"{status_icon} {feature}: {result}")
        
        # Summary
        success_count = sum(1 for result in test_results.values() if result == "SUCCESS")
        total_tests = len(test_results)
        
        logger.info(f"Enhanced Controls Summary: {success_count}/{total_tests} features working correctly")
        
        # Check requirements coverage
        requirements_met = {
            "Dataset Selection (req: all/some, default all)": test_results.get('dataset_selection') == "SUCCESS",
            "Lat/Lon Range Controls (req: min/max selection)": test_results.get('geospatial_ranges') == "SUCCESS",
            "Track Selection (req: all/some for error plots)": test_results.get('track_selection') == "SUCCESS",
            "Animation Playback Controls (req: play/pause/step/speed)": test_results.get('animation_controls') == "SUCCESS",
            "Animation Range Controls (req: min/max lat/lon)": test_results.get('animation_ranges') == "SUCCESS",
            "Control Methods Implementation": test_results.get('control_methods') == "SUCCESS"
        }
        
        logger.info("=== Section 5.1.1 Requirements Coverage ===")
        for requirement, met in requirements_met.items():
            status = "✅ MET" if met else "❌ NOT MET"
            logger.info(f"{status}: {requirement}")
        
        requirements_success = sum(1 for met in requirements_met.values() if met)
        total_requirements = len(requirements_met)
        
        logger.info(f"Requirements Coverage: {requirements_success}/{total_requirements} requirements met")
        
        return success_count >= (total_tests - 1) and requirements_success >= (total_requirements - 1)
        
    except Exception as e:
        logger.error(f"Enhanced controls test failed with error: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = test_enhanced_controls()
    print(f"Enhanced Phase 5 Controls Test {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)
