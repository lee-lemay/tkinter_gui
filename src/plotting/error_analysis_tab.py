"""
Error Analysis tab widget for the data analysis application.

This module provides the Error Analysis tab widget that extends the base PlotTabWidget
with error analysis-specific functionality and controls.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Any, Dict, List
import logging

from .widgets import PlotTabWidget
from .backends import PlotBackend
from .control_widgets import TrackSelectionWidget


class ErrorAnalysisTabWidget(PlotTabWidget):
    """
    Error Analysis tab widget for analyzing tracking errors.
    
    This widget provides controls for track selection, error metric selection,
    and various error analysis visualization options.
    """
    
    def __init__(self, parent: tk.Widget, backend: PlotBackend):
        """
        Initialize the error analysis tab widget.
        
        Args:
            parent: Parent widget
            backend: Plot backend to use
        """        
        # Initialize control widgets
        self.track_selection_widget = None
        self.dataset_selection_widget = None
        
        super().__init__(parent, backend, "Error Analysis")
        
        # Auto-show initial plot if data is available
        self._show_initial_plot()
    
    def _create_controls(self):
        """Create error analysis-specific control widgets."""
                
        # Add track selection widget
        self.track_selection_widget = TrackSelectionWidget(self.control_frame)
        self.track_selection_widget.pack(fill="x", padx=5, pady=5)
        self.track_selection_widget.set_selection_callback(self._on_track_selection_changed)  

    def _propagate_controller_to_widgets(self):
        """Propagate controller to child widgets."""
        if hasattr(self, 'track_selection_widget') and self.controller:
            if self.track_selection_widget:
                self.track_selection_widget.set_controller(self.controller)          
    
    def _show_initial_plot(self):
        """Show initial plot if data is available (following statistics_tab template)."""
        try:
            self._on_analyze_errors()
        except Exception as e:
            self.logger.debug(f"Could not show initial plot: {e}")    
    
    def _on_track_selection_changed(self, selection: Any):
        """Handle track selection changes."""
        self.logger.debug(f"Track selection changed: {selection}")
        self._on_analyze_errors()
    
    def _on_dataset_selection_changed(self, selection: List[str]):
        """Handle dataset selection changes."""
        self.logger.debug(f"Dataset selection changed: {selection}")
        self._on_analyze_errors()
    
    def _on_analyze_errors(self):
        """Perform error analysis and update the plot."""
        try:
            # Try to get data through multiple paths for maximum compatibility
            plot_data = None
            
            # Path 1: Use plot_manager if available (legacy compatibility)
            if self.plot_manager and self.controller:
                app_state = self.controller.get_state()
                plot_data = self.plot_manager.prepare_plot_data('north_east_error', app_state)
            
            # Update the plot if we have data
            if plot_data and 'error' not in plot_data:
                config = {
                    'title': f'Error Analysis',
                    'xlabel': "Seconds",
                    'ylabel': "Seconds",
                }
                self.update_plot('north_east_error', plot_data, config)
                self.logger.debug("Error analysis plot generated successfully")
            else:
                self.logger.debug("No valid data for error analysis plot")
                self.clear_plot()
                
        except Exception as e:
            self.logger.error(f"Error performing error analysis: {e}")
            self.clear_plot()
    
    def auto_update(self):
        """Auto-update the plot when data changes."""
        self.logger.debug("Auto-updating error analysis plot")
        self._on_analyze_errors()
    
    def should_auto_update(self, focus_info: Any) -> bool:
        """
        Check if this tab should auto-update.
        
        Error analysis tab should auto-update when datasets with tracking data change.
        """
        return True
