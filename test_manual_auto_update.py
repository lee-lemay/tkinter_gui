#!/usr/bin/env python3
"""
Quick manual test to verify the auto-update functionality by running the application.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.application import DataAnalysisApp

def main():
    """Run the application to test auto-update functionality."""
    print("Testing Auto-Update Functionality")
    print("=" * 40)
    print("1. Launch the application")
    print("2. Navigate to different tabs")
    print("3. Load dataset using File > Load Dataset")
    print("4. Check that all tabs auto-update without button clicks")
    print("5. Verify no 'Show' buttons exist (except dataset controls)")
    print("=" * 40)
    
    try:
        app = DataAnalysisApp()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
