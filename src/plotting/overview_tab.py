"""
Overview tab widget for the data analysis application.

This module provides the Overview tab widget that extends the base PlotTabWidget
with overview-specific functionality and controls.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Any, Dict
import logging

from .widgets import PlotTabWidget
from .backends import PlotBackend


class OverviewTabWidget(PlotTabWidget):
    """
    Overview tab widget for displaying welcome information and demo plots.
    
    This widget provides a simple overview of the application with welcome
    text and instructions for getting started.
    """
    
    def __init__(self, parent: tk.Widget, backend: PlotBackend):
        """
        Initialize the overview tab widget.
        
        Args:
            parent: Parent widget
            backend: Plot backend to use
        """
        # Initialize with empty controls first (following statistics_tab template)
        super().__init__(parent, backend, "Overview")
        
        # Create header content before the standard controls/canvas
        self._create_header_content()
        
        # Auto-show initial plot if data is available (following statistics_tab template)
        self._show_initial_plot()
    
    def _create_header_content(self):
        """Create header content with welcome message."""
        # Insert header frame before the control frame
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", padx=10, pady=10, before=self.control_frame)
        
        # Welcome message
        welcome_label = ttk.Label(
            header_frame,
            text="Data Analysis Application",
            font=("TkDefaultFont", 12, "bold")
        )
        welcome_label.pack(anchor="w")
        
        # Feature description
        feature_label = ttk.Label(
            header_frame,
            text="Extended matplotlib visualization capabilities",
            font=("TkDefaultFont", 10, "italic")
        )
        feature_label.pack(anchor="w", pady=(5, 0))
    
    def _create_controls(self):
        """Create overview-specific control widgets."""
        # For overview tab, we don't need complex controls
        # Just add some instructions
        instructions_frame = ttk.Frame(self.control_frame)
        instructions_frame.pack(fill="x", padx=5, pady=5)
        
        instructions_label = ttk.Label(
            instructions_frame,
            text="Load datasets using the File menu to enable additional visualization options.",
            font=("TkDefaultFont", 9, "italic")
        )
        instructions_label.pack(anchor="w")
    
    def _show_initial_plot(self):
        """Show initial demo plot."""
        try:
            self._create_demo_plot()
        except Exception as e:
            self.logger.debug(f"Could not show initial demo plot: {e}")
    
    def _on_show_demo(self):
        """Handle demo plot button click."""
        self._create_demo_plot()
    
    def _on_refresh_plot(self):
        """Handle refresh button click (following statistics_tab template)."""
        self._create_demo_plot()
    
    def _create_demo_plot(self):
        """Create a demo plot."""
        try:
            # Create demo plot data
            demo_data = {
                'plot_type': 'demo'
            }
            
            config = {
                'title': 'Welcome to Data Analysis Application',
                'subtitle': 'Demo mathematical functions'
            }
            
            self.update_plot('demo_plot', demo_data, config)
            self.logger.debug("Demo plot created successfully")
            
        except Exception as e:
            self.logger.error(f"Error creating demo plot: {e}")
    
    def auto_update(self):
        """Auto-update the plot when data changes."""
        # For overview tab, we typically don't auto-update
        # but we could refresh the demo plot
        self.logger.debug("Auto-update called for Overview tab")
        pass
    
    def should_auto_update(self, focus_info: Any) -> bool:
        """
        Check if this tab should auto-update.
        
        For overview tab, we don't typically auto-update based on data changes.
        """
        return False
