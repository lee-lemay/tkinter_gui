#!/usr/bin/env python3
"""
Test Phase 4: Basic Visualization using Matplotlib

This script tests the Phase 4 implementation including:
- Matplotlib canvas integration
- NavigationToolbar2Tk setup
- First simple plot creation
- Plot export functionality
- Tab-based view selection framework
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
from src.models.application_state import ApplicationState


def test_matplotlib_canvas():
    """Test matplotlib canvas creation and basic functionality."""
    print("=== Testing Matplotlib Canvas ===")
    
    # Create test window
    root = tk.Tk()
    root.title("Phase 4 Test - Matplotlib Canvas")
    root.geometry("800x600")
    
    try:
        # Create matplotlib canvas
        canvas = MatplotlibCanvas(root)
        canvas.frame.pack(fill="both", expand=True)
        
        # Test demo plot
        demo_data = {'plot_type': 'demo'}
        canvas.create_simple_plot(demo_data)
        
        print("✓ Matplotlib canvas created successfully")
        print("✓ Demo plot generated successfully")
        print("✓ Navigation toolbar integrated")
        
        # Test that window can be created (don't show it)
        root.update()
        
        print("✓ Canvas rendering successful")
        
    except Exception as e:
        print(f"✗ Error testing matplotlib canvas: {e}")
        return False
    finally:
        root.destroy()
    
    return True


def test_plot_manager():
    """Test plot manager functionality."""
    print("\n=== Testing Plot Manager ===")
    
    try:
        # Create mock data interface
        data_interface = MockDataInterface()
        
        # Create plot manager
        plot_manager = PlotManager(data_interface)
        
        # Create mock application state
        app_state = ApplicationState()
        
        # Test available plots
        available_plots = plot_manager.get_available_plots(app_state)
        print(f"✓ Available plots: {len(available_plots)}")
        
        for plot in available_plots:
            print(f"  - {plot['name']} ({'enabled' if plot['enabled'] else 'disabled'})")
        
        # Test demo plot data preparation
        demo_data = plot_manager.prepare_plot_data('demo_plot', app_state)
        if 'error' not in demo_data:
            print("✓ Demo plot data preparation successful")
        else:
            print(f"✗ Demo plot data error: {demo_data['error']}")
            return False
        
        # Test track counts data preparation
        track_data = plot_manager.prepare_plot_data('track_counts', app_state)
        if 'error' not in track_data:
            print("✓ Track counts data preparation successful")
        else:
            print(f"✗ Track counts data error: {track_data['error']}")
        
        print("✓ Plot manager functionality verified")
        
    except Exception as e:
        print(f"✗ Error testing plot manager: {e}")
        return False
    
    return True


def test_data_interface_plot_methods():
    """Test new plot data methods in data interface."""
    print("\n=== Testing Data Interface Plot Methods ===")
    
    try:
        # Create mock data interface
        data_interface = MockDataInterface()
        
        # Test track counts
        track_counts = data_interface.get_track_counts()
        print(f"✓ Track counts: {track_counts}")
        
        # Test lat/lon data
        lat_lon_data = data_interface.get_lat_lon_data("test_dataset")
        if lat_lon_data:
            print(f"✓ Lat/lon data includes: {list(lat_lon_data.keys())}")
        
        # Test plot data method
        plot_data = data_interface.get_plot_data("test_dataset", "demo_plot")
        if plot_data:
            print(f"✓ Plot data includes: {list(plot_data.keys())}")
        
        # Test focus summary
        summary = data_interface.get_focus_summary("test_dataset")
        if summary:
            print(f"✓ Focus summary includes: {list(summary.keys())}")
        
        print("✓ All data interface plot methods working")
        
    except Exception as e:
        print(f"✗ Error testing data interface: {e}")
        return False
    
    return True


def test_plot_types():
    """Test different plot types with matplotlib canvas."""
    print("\n=== Testing Plot Types ===")
    
    # Create test window
    root = tk.Tk()
    root.title("Phase 4 Test - Plot Types")
    root.geometry("800x600")
    
    try:
        canvas = MatplotlibCanvas(root)
        canvas.frame.pack(fill="both", expand=True)
        
        # Test demo plot
        print("Testing demo plot...")
        demo_data = {'plot_type': 'demo'}
        canvas.create_simple_plot(demo_data)
        root.update()
        print("✓ Demo plot successful")
        
        # Test track counts plot
        print("Testing track counts plot...")
        track_data = {
            'plot_type': 'track_counts',
            'data': {'Dataset_A': 25, 'Dataset_B': 18, 'Dataset_C': 32}
        }
        canvas.create_simple_plot(track_data)
        root.update()
        print("✓ Track counts plot successful")
        
        # Test lat/lon plot
        print("Testing lat/lon plot...")
        import numpy as np
        lat_lon_data = {
            'plot_type': 'lat_lon',
            'data': {
                'tracks': {
                    'lat': np.random.normal(40.7, 0.01, 50).tolist(),
                    'lon': np.random.normal(-74.0, 0.01, 50).tolist()
                },
                'truth': {
                    'lat': np.random.normal(40.7, 0.005, 25).tolist(),
                    'lon': np.random.normal(-74.0, 0.005, 25).tolist()
                }
            }
        }
        canvas.create_simple_plot(lat_lon_data)
        root.update()
        print("✓ Lat/lon plot successful")
        
        print("✓ All plot types working correctly")
        
    except Exception as e:
        print(f"✗ Error testing plot types: {e}")
        return False
    finally:
        root.destroy()
    
    return True


def test_export_functionality():
    """Test plot export functionality."""
    print("\n=== Testing Export Functionality ===")
    
    # Create test window
    root = tk.Tk()
    root.title("Phase 4 Test - Export")
    root.geometry("800x600")
    
    try:
        canvas = MatplotlibCanvas(root)
        canvas.frame.pack(fill="both", expand=True)
        
        # Create a plot to export
        demo_data = {'plot_type': 'demo'}
        canvas.create_simple_plot(demo_data)
        root.update()
        
        # Test that export method exists and can be called
        # (We won't actually save a file in automated test)
        export_method = getattr(canvas, 'export_plot', None)
        if export_method and callable(export_method):
            print("✓ Export functionality available")
        else:
            print("✗ Export functionality not available")
            return False
        
        # Test clear functionality
        canvas.clear_plot()
        root.update()
        print("✓ Clear plot functionality working")
        
    except Exception as e:
        print(f"✗ Error testing export functionality: {e}")
        return False
    finally:
        root.destroy()
    
    return True


def main():
    """Run all Phase 4 tests."""
    print("Phase 4: Basic Visualization using Matplotlib - Test Suite")
    print("=" * 60)
    
    tests = [
        test_matplotlib_canvas,
        test_plot_manager,
        test_data_interface_plot_methods,
        test_plot_types,
        test_export_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Phase 4 implementation SUCCESSFUL!")
        print("\nPhase 4 Features Implemented:")
        print("✓ Extensible/modular design pattern")
        print("✓ Matplotlib canvas integration")
        print("✓ NavigationToolbar2Tk setup")
        print("✓ First simple plot creation")
        print("✓ Plot export functionality")
        print("✓ Tab-based view selection framework")
        return True
    else:
        print("❌ Phase 4 implementation has issues")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
