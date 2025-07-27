#!/usr/bin/env python3
"""
Test script to verify Phase 10.1 implementation works correctly.
"""

import sys
from pathlib import Path

# Add the application directory to the Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

def test_imports():
    """Test that all modules can be imported successfully."""
    print("Testing imports...")
    
    try:
        from src.utils.logger import setup_logger, get_logger
        print("✓ Logger utilities imported successfully")
        
        from src.models.application_state import ApplicationState, DatasetInfo, DatasetStatus
        print("✓ Application state models imported successfully")
        
        from src.controllers.application_controller import ApplicationController
        print("✓ Application controller imported successfully")
        
        from src.components.menu_bar import MenuBar
        print("✓ Menu bar component imported successfully")
        
        from src.components.status_bar import StatusBar
        print("✓ Status bar component imported successfully")
        
        from src.components.left_panel import LeftPanel
        print("✓ Left panel component imported successfully")
        
        from src.components.right_panel import RightPanel
        print("✓ Right panel component imported successfully")
        
        from src.gui.main_window import MainWindow
        print("✓ Main window imported successfully")
        
        from src.application import DataAnalysisApp
        print("✓ Main application class imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality without creating GUI."""
    print("\nTesting basic functionality...")
    
    try:
        # Test logger setup
        from src.utils.logger import setup_logger
        setup_logger(log_to_file=False)  # Don't create log files for test
        print("✓ Logger setup successful")
        
        # Test application state
        from src.models.application_state import ApplicationState, DatasetInfo, DatasetStatus
        state = ApplicationState()
        
        # Test adding a dataset
        dataset = DatasetInfo(
            name="test_dataset",
            path=Path("test/path"),
            status=DatasetStatus.AVAILABLE
        )
        state.add_dataset(dataset)
        assert len(state.datasets) == 1
        print("✓ Application state functionality working")
        
        return True
        
    except Exception as e:
        print(f"✗ Functionality test error: {e}")
        return False

def test_gui_creation():
    """Test GUI creation without showing it."""
    print("\nTesting GUI creation...")
    
    try:
        import tkinter as tk
        from src.models.application_state import ApplicationState
        from src.controllers.application_controller import ApplicationController
        from src.gui.main_window import MainWindow
        
        # Create a hidden root window for testing
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Test component creation
        state = ApplicationState()
        view = MainWindow(root)
        controller = ApplicationController(state, view)
        view.set_controller(controller)
        
        print("✓ GUI components created successfully")
        
        # Cleanup
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"✗ GUI creation error: {e}")
        return False

def main():
    """Run all tests."""
    print("Phase 10.1 Implementation Test")
    print("=" * 40)
    
    success = True
    
    # Test imports
    success &= test_imports()
    
    # Test basic functionality
    success &= test_basic_functionality()
    
    # Test GUI creation
    success &= test_gui_creation()
    
    print("\n" + "=" * 40)
    if success:
        print("✓ All tests passed! Phase 10.1 implementation is working correctly.")
        print("\nTo run the full application, use: python main.py")
    else:
        print("✗ Some tests failed. Please check the implementation.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
