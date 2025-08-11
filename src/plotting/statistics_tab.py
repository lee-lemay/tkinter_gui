"""
Statistics tab widget for the data analysis application.

This module provides the Statistics tab widget that extends the base PlotTabWidget
with statistics-specific functionality and controls.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Any, Dict
import logging
from typing import Callable

from .widgets import PlotTabWidget
from .backends import PlotBackend


class StatisticsTabWidget(PlotTabWidget):
    """
    Statistics tab widget for displaying track count.
    """
    
    def __init__(self, parent: tk.Widget, backend: PlotBackend):
        """
        Initialize the statistics tab widget.
        
        Args:
            parent: Parent widget
            backend: Plot backend to use
        """
        # Initialize with empty controls first
        super().__init__(parent, backend, "Statistics")
        
        # Auto-show initial plot if data is available
        self._show_initial_plot()
    
    def _create_controls(self):
        """Create statistics-specific control widgets."""
        return
    
    def _show_initial_plot(self):
        """Show initial plot if data is available."""
        try:
            self._update_statistics_plot()
        except Exception as e:
            self.logger.debug(f"Could not show initial plot: {e}")
    
    def _on_plot_type_changed(self, event=None):
        """Handle plot type selection change."""
        self._update_statistics_plot()
    
    def _on_refresh_plot(self):
        """Handle refresh button click."""
        self._update_statistics_plot()
    
    def _update_statistics_plot(self):
        """Update the statistics plot based on current settings."""
        try:
            # Get current plot type
            plot_type = getattr(self, 'plot_type_var', None)
            if plot_type:
                plot_type = plot_type.get()
            else:
                plot_type = 'track_counts'  # Default fallback
            
            # Try to get data through multiple paths for maximum compatibility
            plot_data = None
            
            # Path 1: Use plot_manager if available (legacy compatibility)
            if self.plot_manager and self.controller:
                app_state = self.controller.get_state()
                plot_data = self.plot_manager.prepare_plot_data(plot_type, app_state)
            
            # Update the plot if we have data
            if plot_data and 'error' not in plot_data:
                config = {
                    'title': f'Dataset Statistics - {plot_type}',
                    'xlabel': 'Category',
                    'ylabel': 'Count'
                }
                self.update_plot(plot_type, plot_data, config)
                self.logger.debug(f"Statistics plot updated: {plot_type}")
            else:
                self.logger.debug(f"No valid data for statistics plot: {plot_type}")
                self.clear_plot()
                
        except Exception as e:
            self.logger.error(f"Error updating statistics plot: {e}")
            self.clear_plot()
    
    def _generate_plot_data_direct(self, dataset_info: Any, plot_type: str) -> Dict[str, Any]:
        """
        Generate plot data directly from dataset info (independent approach).
        
        Args:
            dataset_info: DatasetInfo object
            plot_type: Type of plot to generate
            
        Returns:
            Dictionary with plot data
        """
        try:
            counts = {}
            
            if dataset_info.tracks_df is not None and not dataset_info.tracks_df.empty:
                counts['Tracks'] = len(dataset_info.tracks_df)
            
            if dataset_info.truth_df is not None and not dataset_info.truth_df.empty:
                counts['Truth'] = len(dataset_info.truth_df)
            
            if dataset_info.detections_df is not None and not dataset_info.detections_df.empty:
                counts['Detections'] = len(dataset_info.detections_df)
            
            if counts:
                return {
                    'track_counts': {dataset_info.name: sum(counts.values())},
                    'x': list(counts.keys()),
                    'y': list(counts.values())
                }
            
            return {'error': 'No data available'}
            
        except Exception as e:
            self.logger.error(f"Error generating direct plot data: {e}")
            return {'error': str(e)}
    
    def auto_update(self):
        """Auto-update the plot when data changes."""
        self._update_statistics_plot()