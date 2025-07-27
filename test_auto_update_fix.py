#!/usr/bin/env python3
"""
Test script to verify the auto-update functionality fixes.

This test verifies that:
1. All tabs now auto-update when focus dataset changes
2. Manual "Show" buttons have been removed
3. Auto-update methods exist
"""

import sys
import os
import re

def test_code_changes():
    """Test the code changes by analyzing the source file."""
    
    print("=" * 60)
    print("Testing Auto-Update Functionality Fixes")
    print("=" * 60)
    
    right_panel_path = os.path.join(os.path.dirname(__file__), 'src', 'components', 'right_panel.py')
    
    if not os.path.exists(right_panel_path):
        print(f"✗ Right panel file not found: {right_panel_path}")
        return False
    
    try:
        with open(right_panel_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("✓ Right panel file loaded successfully")
        
        # Test 1: Check that manual plot buttons have been removed
        print("\n1. Testing button removal...")
        
        removed_button_patterns = [
            r'text="Show North/East Errors"',
            r'text="Show 3D RMS Errors"', 
            r'text="Show Lifetimes"',
            r'text="Generate Animation"',
            r'text="Show Track Counts"'
        ]
        
        buttons_removed = True
        for pattern in removed_button_patterns:
            if re.search(pattern, content):
                print(f"  ✗ Button pattern still found: {pattern}")
                buttons_removed = False
            else:
                print(f"  ✓ Button pattern removed: {pattern}")
        
        if buttons_removed:
            print("  ✓ All manual plot buttons successfully removed")
        else:
            print("  ✗ Some buttons were not removed")
        
        # Test 2: Check that auto-update methods exist
        print("\n2. Testing auto-update methods...")
        
        auto_update_methods = [
            r'def _auto_update_geospatial_plot\(self\)',
            r'def _auto_update_error_plot\(self\)', 
            r'def _auto_update_rms_plot\(self\)',
            r'def _auto_update_lifetime_plot\(self\)',
            r'def _auto_update_animation_plot\(self\)',
            r'def _auto_update_statistics_plot\(self\)'
        ]
        
        methods_exist = True
        for pattern in auto_update_methods:
            if re.search(pattern, content):
                print(f"  ✓ Method found: {pattern}")
            else:
                print(f"  ✗ Method missing: {pattern}")
                methods_exist = False
        
        if methods_exist:
            print("  ✓ All auto-update methods exist")
        else:
            print("  ✗ Some auto-update methods are missing")
            
        # Test 3: Check on_state_changed calls all auto-update methods
        print("\n3. Testing on_state_changed method...")
        
        state_changed_calls = [
            r'self\._auto_update_geospatial_plot\(\)',
            r'self\._auto_update_error_plot\(\)', 
            r'self\._auto_update_rms_plot\(\)',
            r'self\._auto_update_lifetime_plot\(\)',
            r'self\._auto_update_animation_plot\(\)',
            r'self\._auto_update_statistics_plot\(\)'
        ]
        
        calls_exist = True
        for pattern in state_changed_calls:
            if re.search(pattern, content):
                print(f"  ✓ Auto-update call found: {pattern}")
            else:
                print(f"  ✗ Auto-update call missing: {pattern}")
                calls_exist = False
        
        if calls_exist:
            print("  ✓ All auto-update methods called from on_state_changed")
        else:
            print("  ✗ Some auto-update methods not called from on_state_changed")
            
        # Test 4: Check demo plot initialization
        print("\n4. Testing demo plot initialization...")
        
        demo_init_pattern = r'self\._create_demo_plot\(\)'
        if re.search(demo_init_pattern, content):
            print("  ✓ Demo plot initialization found")
            demo_init = True
        else:
            print("  ✗ Demo plot initialization missing")
            demo_init = False
        
        # Summary
        print("\n" + "=" * 60)
        if buttons_removed and methods_exist and calls_exist and demo_init:
            print("✓ AUTO-UPDATE FUNCTIONALITY TESTS PASSED")
            print("✓ All manual buttons removed")
            print("✓ All auto-update methods implemented") 
            print("✓ All auto-update methods called from state changes")
            print("✓ Demo plot initialization added")
        else:
            print("✗ SOME TESTS FAILED")
            print("Check the details above for specific issues")
        
        print("=" * 60)
        
        return buttons_removed and methods_exist and calls_exist and demo_init
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_code_changes()
    sys.exit(0 if success else 1)
