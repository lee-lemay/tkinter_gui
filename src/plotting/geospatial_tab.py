"""
Geospatial tab widget for the data analysis application.

This module provides the Geospatial tab widget that extends the base PlotTabWidget
with geospatial-specific functionality and controls.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional, Any, Dict
import logging

from .widgets import PlotTabWidget
from .backends import PlotBackend
from .control_widgets import DataSelectionWidget, CoordinateRangeWidget


class GeospatialTabWidget(PlotTabWidget):
    """
    Geospatial tab widget for creating geographic visualizations.
    
    This widget provides controls for coordinate range selection,
    map type selection, and various geospatial visualization options.
    """
    
    def __init__(self, parent: tk.Widget, backend: PlotBackend):
        """
        Initialize the geospatial tab widget.
        
        Args:
            parent: Parent widget
            backend: Plot backend to use
        """
        # Initialize control variables BEFORE calling super().__init__
        # because super().__init__ calls _create_controls() which needs these variables
        self.map_type_var = tk.StringVar(value="scatter")
        self.show_grid_var = tk.BooleanVar(value=True)
        self.show_coastlines_var = tk.BooleanVar(value=True)
        self.projection_var = tk.StringVar(value="mercator")
        self.track_selection_var = ["All"]
        self.truth_selection_var = ["All"]
        
        super().__init__(parent, backend, "Geospatial")
        
        # Auto-show initial plot if data is available (following statistics_tab template)
        self._show_initial_plot()
    
    def _create_controls(self):
        """Create geospatial-specific control widgets."""
        
        # Add data selection widget
        self.data_selection_widget = DataSelectionWidget(self.control_frame)
        self.data_selection_widget.pack(fill="x", padx=5, pady=5)
        self.data_selection_widget.set_tracks_callback(self._on_track_data_selection_changed)
        self.data_selection_widget.set_truth_callback(self._on_truth_data_selection_changed)
        
        # Add coordinate range widget
        self.coord_range_widget = CoordinateRangeWidget(
            self.control_frame,
            title="Geographic Bounds"
        )
        self.coord_range_widget.pack(fill="x", padx=5, pady=5)
        self.coord_range_widget.set_range_callback(self._on_coord_range_changed)
        self.coord_range_widget.set_reset_callback(self._on_reset_bounds)

        # This will trigger when the matplotlib canvas is zoomed or panned
        self._setup_zoom_callback_connection()

    def _propagate_controller_to_widgets(self):
        """Propagate controller to child widgets."""
        if hasattr(self, 'data_selection_widget') and self.controller:
            if self.data_selection_widget:
                self.data_selection_widget.set_controller(self.controller)  
        
    
    def _show_initial_plot(self):
        """Show initial plot if data is available (following statistics_tab template)."""
        try:
            self._on_generate_plot()
        except Exception as e:
            self.logger.debug(f"Could not show initial plot: {e}")
    def _on_track_data_selection_changed(self, selection: List[str]):
        """Handle track selection changes."""
        self.track_selection_var = selection
        self._on_generate_plot()

    def _on_truth_data_selection_changed(self, selection: List[str]):
        """Handle truth selection changes."""
        self.truth_selection_var = selection
        self._on_generate_plot()
    
    def _on_coord_range_changed(self, ranges: Dict[str, tuple]):
        """Handle coordinate range changes."""
        self.logger.debug(f"Coordinate ranges changed: {ranges}")
        # When user manually changes ranges, regenerate plot with new ranges
        lat_range = ranges.get('lat_range', None)
        lon_range = ranges.get('lon_range', None)
        if lat_range and lon_range:
            if lat_range != self.lat_range or lon_range != self.lon_range:
                self.lat_range = lat_range
                self.lon_range = lon_range
                self._on_generate_plot()

    def _on_reset_bounds(self):
        """Handle reset bounds button click."""
        self.logger.debug("Resetting geographic bounds")
        # Reset by clearing current ranges and regenerating plot 
        # This will cause the plot manager to recalculate bounds from data
        if hasattr(self, 'coord_range_widget') and self.coord_range_widget:
            # Set to default values temporarily to trigger recalculation
            self.coord_range_widget.set_ranges((-1.0, 1.0), (-1.0, 1.0))
        self._on_generate_plot()
    
    def _setup_zoom_callback_connection(self):
        """Setup connection between plot backend zoom events and coordinate range widget."""
        if self.backend and hasattr(self.backend, 'set_zoom_callback'):
            self.backend.set_zoom_callback(self._on_plot_zoom_changed)
            self.logger.debug("Connected zoom callback to coordinate range widget")

    def _on_plot_zoom_changed(self, xlim: tuple, ylim: tuple):
        """Handle zoom/pan changes from the plot backend."""
        try:
            # Update coordinate range widget to reflect new plot limits
            if self.coord_range_widget:
                # Note: xlim is longitude, ylim is latitude for geographic plots
                lon_range = xlim
                lat_range = ylim
                
                # Temporarily disable the range callback to prevent circular updates
                original_callback = self.coord_range_widget.range_callback
                self.coord_range_widget.range_callback = None
                
                # Update the widget values
                self.coord_range_widget.set_ranges(lat_range, lon_range)
                
                # Restore the callback
                self.coord_range_widget.range_callback = original_callback
                
                self.logger.debug(f"Updated coordinate ranges from zoom: lat={lat_range}, lon={lon_range}")
        except Exception as e:
            self.logger.error(f"Error updating coordinate ranges from zoom: {e}")
    
    def _on_generate_plot(self):
        """Generate the geospatial plot."""
        try:            
            plot_data = None
            
            if self.plot_manager and self.controller:
                # Get coordinate ranges from widget
                coordinate_ranges = {}
                if hasattr(self, 'coord_range_widget') and self.coord_range_widget:
                    ranges = self.coord_range_widget.get_ranges()
                    if ranges:
                        coordinate_ranges = ranges
                
                # Build config with track/truth selections and coordinate ranges
                config = {
                    'tracks': getattr(self, 'track_selection_var', ["All"]),
                    'truth': getattr(self, 'truth_selection_var', ["All"]),
                }
                
                # Only include coordinate ranges in config if user has explicitly set them
                if coordinate_ranges:
                    lat_range = coordinate_ranges.get('lat_range', None)
                    lon_range = coordinate_ranges.get('lon_range', None)
                    if lat_range is not None and lat_range != (-1.0, 1.0):
                        config['lat_range'] = lat_range
                    if lon_range is not None and lon_range != (-1.0, 1.0):
                        config['lon_range'] = lon_range
                app_state = self.controller.get_state()
                plot_data = self.plot_manager.prepare_plot_data('lat_lon_scatter', app_state, config)
            
            # Update the plot if we have data
            if plot_data and 'error' not in plot_data:
                # Set coordinate ranges from calculated data bounds
                self.lat_range = plot_data.get('lat_range')
                self.lon_range = plot_data.get('lon_range')                
                
                if self.lat_range and self.lon_range and hasattr(self, 'coord_range_widget'):
                    if self.coord_range_widget:
                        self.coord_range_widget.set_ranges(self.lat_range, self.lon_range)

                config = {
                    'title': f'Geospatial {self.map_type_var.get().title()} Map',
                    'show_grid': self.show_grid_var.get()
                }
                self.update_plot('lat_lon_scatter', plot_data, config)
                self.logger.debug("Geospatial plot generated successfully")
            else:
                self.logger.debug("No valid data for geospatial plot")
                self.clear_plot()
                
        except Exception as e:
            self.logger.error(f"Error generating geospatial plot: {e}")
            self.clear_plot()
    
    def auto_update(self):
        """Auto-update the plot when data changes."""
        self.logger.debug("Auto-updating geospatial plot")
        self._on_generate_plot()
    
    def should_auto_update(self, focus_info: Any) -> bool:
        """
        Check if this tab should auto-update.
        
        Geospatial tab should auto-update when datasets with geographic data change.
        """
        return True
