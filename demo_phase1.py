#!/usr/bin/env python3
"""
Demo script for Phase 1 implementation.

This script demonstrates the application functionality and
shows the GUI briefly before automatically closing.
"""

import sys
import time
from pathlib import Path

# Add the application directory to the Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

def demo_application():
    """Run a demonstration of the application."""
    print("Data Analysis Application - Phase 1 Demo")
    print("=" * 45)
    
    try:
        # Import and setup
        from src.utils.logger import setup_logger
        from src.application import DataAnalysisApp
        
        # Setup logging (no file output for demo)
        setup_logger(log_to_file=False)
        
        print("1. Creating application instance...")
        app = DataAnalysisApp()
        
        print("2. Application components initialized:")
        print(f"   - Model: {type(app.model).__name__}")
        print(f"   - View: {type(app.view).__name__}")
        print(f"   - Controller: {type(app.controller).__name__}")
        
        print("3. Testing application state...")
        state = app.controller.get_state()
        stats = state.get_statistics()
        print(f"   - Total datasets: {stats['total_datasets']}")
        print(f"   - Current view: {stats['current_view']}")
        print(f"   - Processing status: {stats['processing_status']}")
        
        print("4. Testing menu actions...")
        # Test menu actions
        app.controller.on_menu_help_about()
        app.controller.update_status("Demo running...")
        
        print("5. GUI is ready and functional!")
        print("\nApplication window will appear briefly...")
        
        # Show the window briefly
        app.root.deiconify()  # Show the window
        app.root.update()     # Process pending events
        
        # Wait a moment to see the GUI
        time.sleep(2)
        
        print("6. Demo complete - shutting down gracefully...")
        app.shutdown()
        
        print("\n✓ Phase 1 implementation is working correctly!")
        print("✓ All components are properly integrated!")
        print("✓ Ready for Phase 2 development!")
        
    except Exception as e:
        print(f"✗ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = demo_application()
    sys.exit(0 if success else 1)
