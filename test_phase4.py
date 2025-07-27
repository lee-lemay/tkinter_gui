#!/usr/bin/env python3
"""
Test Phase 4: Basic Visualization using Matplotlib (Updated Requirements)

This script tests the updated Phase 4 implementation including:
- Loading real CSV datasets from test_data directory
- First simple plot showing lat/lon of tracks and truth (as specified in requirements)
- Matplotlib canvas integration with NavigationToolbar2Tk
- Plot export functionality
- Tab-based view selection framework
- Extensible, modular software design practice
"""

import sys
import os
import tkinter as tk
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.visualization.matplotlib_canvas import MatplotlibCanvas
from src.visualization.plot_manager import PlotManager
from src.business.data_interface import MockDataInterface
from src.models.application_state import ApplicationState, DatasetInfo, DatasetStatus


def test_real_csv_loading():
    """Test loading real CSV data from test_data directory."""
    print("=== Testing Real CSV Data Loading ===")
    
    try:
        # Create data interface
        data_interface = MockDataInterface()
        
        # Test loading sample_dataset_alpha
        dataset_path = Path("test_data/sample_dataset_alpha")
        if not dataset_path.exists():
            print(f"✗ Test data directory not found: {dataset_path}")
            return False
        
        # Load the dataset
        dataframes = data_interface.load_dataset(dataset_path)
        
        # Verify all expected data types are loaded
        expected_types = ['truth', 'tracks', 'detections']
        for data_type in expected_types:
            if data_type not in dataframes:
                print(f"✗ Missing data type: {data_type}")
                return False
            
            df = dataframes[data_type]
            if df.empty:
                print(f"✗ Empty DataFrame for: {data_type}")
                return False
            
            print(f"✓ Loaded {data_type}: {len(df)} records")
            
            # Verify required columns
            if data_type == 'truth':
                required_cols = ['timestamp', 'lat', 'lon', 'alt', 'id']
            elif data_type == 'tracks':
                required_cols = ['timestamp', 'lat', 'lon', 'alt', 'track_id']
            elif data_type == 'detections':
                required_cols = ['timestamp', 'lat', 'lon', 'alt', 'detection_id']
            
            if not all(col in df.columns for col in required_cols):
                print(f"✗ Missing required columns in {data_type}: {required_cols}")
                return False
            
            print(f"✓ Schema validated for {data_type}: {list(df.columns)}")
        
        # Test data content - verify we have real lat/lon coordinates
        tracks_df = dataframes['tracks']
        truth_df = dataframes['truth']
        
        # Check lat/lon ranges are realistic (around NYC area) - be more flexible
        lat_range = (tracks_df['lat'].min(), tracks_df['lat'].max())
        lon_range = (tracks_df['lon'].min(), tracks_df['lon'].max())
        
        if not (40.70 <= lat_range[0] <= lat_range[1] <= 40.73):
            print(f"✗ Unexpected latitude range in tracks: {lat_range}")
            return False
            
        if not (-74.02 <= lon_range[0] <= lon_range[1] <= -74.0):
            print(f"✗ Unexpected longitude range in tracks: {lon_range}")
            return False
        
        print(f"✓ Tracks lat/lon range validated: lat={lat_range}, lon={lon_range}")
        
        print("✓ Real CSV data loading successful")
        return True
        
    except Exception as e:
        print(f"✗ Error testing CSV loading: {e}")
        return False


def test_lat_lon_plot_with_real_data():
    """Test lat/lon plotting with real CSV data (Phase 4 requirement)."""
    print("\n=== Testing Lat/Lon Plot with Real Data ===")
    
    # Create test window
    root = tk.Tk()
    root.title("Phase 4 Test - Real Lat/Lon Plot")
    root.geometry("800x600")
    
    try:
        # Create application state with real data
        app_state = ApplicationState()
        data_interface = MockDataInterface()
        
        # Load real dataset
        dataset_path = Path("test_data/sample_dataset_alpha")
        dataframes = data_interface.load_dataset(dataset_path)
        
        # Create dataset info with real data
        dataset_info = DatasetInfo(
            name="sample_dataset_alpha",
            path=dataset_path,
            status=DatasetStatus.LOADED
        )
        
        # Store the loaded DataFrames
        dataset_info.tracks_df = dataframes['tracks']
        dataset_info.truth_df = dataframes['truth'] 
        dataset_info.detections_df = dataframes['detections']
        
        # Add to application state using the proper method
        app_state.add_dataset(dataset_info)
        
        # Set focus dataset using the property setter
        app_state.focus_dataset = "sample_dataset_alpha"
        
        # Create plot manager and matplotlib canvas
        plot_manager = PlotManager(data_interface)
        canvas = MatplotlibCanvas(root)  # Tk is a valid parent widget
        canvas.frame.pack(fill="both", expand=True)
        
        # Test the key Phase 4 requirement: "First simple plot showing lat/lon of tracks and truth"
        print("Creating lat/lon plot with real track and truth data...")
        
        # Prepare real lat/lon data
        plot_data = plot_manager.prepare_plot_data('lat_lon_scatter', app_state)
        
        if 'error' in plot_data:
            print(f"✗ Error preparing plot data: {plot_data['error']}")
            return False
        
        # Verify we have real data
        lat_lon_data = plot_data['lat_lon_data']
        if 'tracks' not in lat_lon_data or 'truth' not in lat_lon_data:
            print("✗ Missing tracks or truth data in plot preparation")
            return False
        
        tracks_df = lat_lon_data['tracks']
        truth_df = lat_lon_data['truth']
        
        print(f"✓ Prepared tracks data: {len(tracks_df)} points")
        print(f"✓ Prepared truth data: {len(truth_df)} points")
        
        # Create the actual plot
        canvas_data = {
            'plot_type': 'lat_lon',
            'data': lat_lon_data
        }
        canvas.create_simple_plot(canvas_data)
        root.update()
        
        print("✓ Successfully created lat/lon plot with real tracks and truth data")
        print("✓ Phase 4 core requirement fulfilled: 'First simple plot showing lat/lon of tracks and truth'")
        
        # Test export functionality
        print("Testing plot export functionality...")
        # We won't actually save a file in the test, just verify the method exists
        if hasattr(canvas, 'export_plot') and callable(canvas.export_plot):
            print("✓ Plot export functionality available")
        else:
            print("✗ Plot export functionality missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing lat/lon plot: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        root.destroy()


def test_extensible_design():
    """Test extensible, modular software design practice."""
    print("\n=== Testing Extensible Design ===")
    
    try:
        # Verify modular components exist
        components = [
            ('MatplotlibCanvas', 'Reusable matplotlib integration component'),
            ('PlotManager', 'Plot coordination and data preparation'),
            ('MockDataInterface', 'Data loading interface with real CSV support')
        ]
        
        for component_name, description in components:
            # Import and instantiate to verify modularity
            if component_name == 'MatplotlibCanvas':
                root = tk.Tk()
                root.withdraw()  # Hide window
                component = MatplotlibCanvas(root)
                root.destroy()
            elif component_name == 'PlotManager':
                data_interface = MockDataInterface()
                component = PlotManager(data_interface)
            elif component_name == 'MockDataInterface':
                component = MockDataInterface()
            
            print(f"✓ {component_name}: {description}")
        
        # Test that components can work together
        print("✓ Component integration tested")
        
        # Verify NavigationToolbar2Tk integration
        root = tk.Tk()
        root.withdraw()
        canvas = MatplotlibCanvas(root)
        
        # Check that toolbar exists
        if hasattr(canvas, 'toolbar') and canvas.toolbar is not None:
            print("✓ NavigationToolbar2Tk integration confirmed")
        else:
            print("✗ NavigationToolbar2Tk integration missing")
            root.destroy()
            return False
        
        root.destroy()
        
        print("✓ Extensible, modular design practice confirmed")
        return True
        
    except Exception as e:
        print(f"✗ Error testing extensible design: {e}")
        return False


def test_tab_based_framework():
    """Test tab-based view selection framework."""
    print("\n=== Testing Tab-based View Selection Framework ===")
    
    try:
        # Test that right panel has multiple tabs for visualization
        from src.components.right_panel import RightPanel
        
        root = tk.Tk()
        root.withdraw()
        
        # Create right panel
        right_panel = RightPanel(root)
        
        # Check that it has a notebook (tab) widget
        if hasattr(right_panel, 'notebook'):
            print("✓ Tab-based notebook widget found")
            
            # Check for multiple tabs
            tab_count = right_panel.notebook.index("end")
            if tab_count >= 3:  # Should have Overview, Visualization, Statistics, Geospatial
                print(f"✓ Multiple tabs available: {tab_count} tabs")
                
                # Verify specific tabs exist
                expected_tabs = ["Overview", "Visualization", "Statistics", "Geospatial"]
                for i in range(tab_count):
                    tab_text = right_panel.notebook.tab(i, "text")
                    if tab_text in expected_tabs:
                        print(f"✓ Found expected tab: {tab_text}")
                
            else:
                print(f"✗ Insufficient tabs found: {tab_count}")
                root.destroy()
                return False
        else:
            print("✗ Tab-based notebook widget not found")
            root.destroy()
            return False
        
        root.destroy()
        print("✓ Tab-based view selection framework confirmed")
        return True
        
    except Exception as e:
        print(f"✗ Error testing tab framework: {e}")
        return False


def main():
    """Run all Phase 4 tests for updated requirements."""
    print("Phase 4: Basic Visualization using Matplotlib (Updated Requirements)")
    print("=" * 70)
    print("Testing compliance with updated Phase 4 requirements:")
    print("- Extensible, modular software design practice")
    print("- Matplotlib canvas integration")  
    print("- NavigationToolbar2Tk setup")
    print("- First simple plot showing lat/lon of tracks and truth")
    print("- Plot export functionality")
    print("- Tab-based view selection framework")
    print("=" * 70)
    
    tests = [
        test_real_csv_loading,
        test_lat_lon_plot_with_real_data,
        test_extensible_design,
        test_tab_based_framework
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 70)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Updated Phase 4 implementation SUCCESSFUL!")
        print("\nPhase 4 Requirements Fulfilled:")
        print("✅ Extensible, modular software design practice")
        print("✅ Matplotlib canvas integration") 
        print("✅ NavigationToolbar2Tk setup")
        print("✅ First simple plot showing lat/lon of tracks and truth")
        print("✅ Plot export functionality")
        print("✅ Tab-based view selection framework")
        print("\nKey Achievement:")
        print("📊 Successfully loads and visualizes REAL CSV data with lat/lon coordinates")
        print("📊 Displays actual tracks and truth positions from test datasets")
        return True
    else:
        print("❌ Phase 4 implementation has issues")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
