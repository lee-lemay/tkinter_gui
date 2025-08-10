"""
Geospatial tab widget for the data analysis application.

This module provides the Geospatial tab widget that extends the base BaseGeospatialTabWidget
with scatter plot functionality.
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Any, Dict
import logging

from .base_geospatial_tab import BaseGeospatialTabWidget
from .backends import PlotBackend


class GeospatialTabWidget(BaseGeospatialTabWidget):
    """
    Geospatial tab widget for creating geographic scatter plot visualizations.
    
    This widget provides controls for coordinate range selection and
    scatter plot visualization options.
    """
    
    def __init__(self, parent: tk.Widget, backend: PlotBackend):
        """
        Initialize the geospatial tab widget.
        
        Args:
            parent: Parent widget
            backend: Plot backend to use
        """
        # Initialize geospatial-specific variables
        self.map_type_var = tk.StringVar(value="scatter")
        self.show_grid_var = tk.BooleanVar(value=True)
        self.show_coastlines_var = tk.BooleanVar(value=True)
        self.projection_var = tk.StringVar(value="mercator")
        
        super().__init__(parent, backend, "Geospatial")
    
    def _get_coordinate_widget_title(self) -> str:
        """Get the title for the coordinate range widget."""
        return "Geographic Bounds"
    
    def _generate_plot(self):
        """Generate the geospatial scatter plot."""
        try:            
            plot_data = None
            
            if self.plot_manager and self.controller:
                config = self._build_plot_config()
                app_state = self.controller.get_state()
                plot_data = self.plot_manager.prepare_plot_data('lat_lon_scatter', app_state, config)
            
            # Update the plot if we have data
            if plot_data and 'error' not in plot_data:
                # Update coordinate ranges from calculated data
                self._update_coordinate_ranges_from_plot_data(plot_data)

                # Create plot configuration
                plot_config = {
                    'title': f'Geospatial {self.map_type_var.get().title()} Map',
                    'show_grid': self.show_grid_var.get(),
                    # Explicit plot modes for renderer/backends
                    'tracks_plot_mode': 'trajectory',
                    'truth_plot_mode': 'scatter',
                }
                
                self.update_plot('lat_lon_scatter', plot_data, plot_config)
                self.logger.debug("Geospatial plot generated successfully")
            else:
                self.logger.debug("No valid data for geospatial plot")
                self.clear_plot()
                
        except Exception as e:
            self.logger.error(f"Error generating geospatial plot: {e}")
            self.clear_plot()