"""
Base geospatial tab widget for the data analysis application.

This module provides the base GeospatialTabWidget that can be extended by
specific geospatial implementations like scatter plots and animations.
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Any, Dict
import logging

from .widgets import PlotTabWidget
from .backends import PlotBackend
from .control_widgets import DataSelectionWidget, CoordinateRangeWidget


class BaseGeospatialTabWidget(PlotTabWidget):
    """
    Base geospatial tab widget for creating geographic visualizations.
    
    This base class provides common functionality for geospatial plotting including:
    - Data selection (tracks/truth)
    - Coordinate range controls
    - Zoom/pan integration
    - Common event handling
    """
    
    def __init__(self, parent: tk.Widget, backend: PlotBackend, tab_name: str):
        """
        Initialize the base geospatial tab widget.
        
        Args:
            parent: Parent widget
            backend: Plot backend to use
            tab_name: Name for this tab instance
        """
        # Initialize common state variables
        self.track_selection_var = ["All"]
        self.truth_selection_var = ["All"]
        self.lat_range = None
        self.lon_range = None
        
        # Initialize common control widgets
        self.data_selection_widget = None
        self.coord_range_widget = None
        
        # Locks to prevent multiple plot generations
        self._plot_generation_locked = False
        self._pending_plot_generation = False
        
        super().__init__(parent, backend, tab_name)
        
        # Show initial plot
        self._show_initial_plot()
    
    def _create_controls(self):
        """Create common geospatial control widgets."""
        # Add data selection widget (collapsed by default to save space)
        self.data_selection_widget = DataSelectionWidget(self.control_frame, collapsed=True)
        self.data_selection_widget.pack(fill="x", padx=5, pady=5)
        self.data_selection_widget.set_tracks_callback(self._on_track_data_selection_changed)
        self.data_selection_widget.set_truth_callback(self._on_truth_data_selection_changed)
        
        # Add coordinate range widget (collapsed by default to save space)
        self.coord_range_widget = CoordinateRangeWidget(
            self.control_frame,
            title=self._get_coordinate_widget_title(),
            collapsed=True
        )
        self.coord_range_widget.pack(fill="x", padx=5, pady=5)
        self.coord_range_widget.set_range_callback(self._on_coord_range_changed)
        self.coord_range_widget.set_reset_callback(self._on_reset_bounds)

        # Setup zoom callback connection
        self._setup_zoom_callback_connection()
        
        # Allow subclasses to add additional controls
        self._create_additional_controls()
    
    def _create_additional_controls(self):
        """
        Hook for subclasses to add additional controls.
        Override this method to add tab-specific controls.
        """
        pass
    
    def _get_coordinate_widget_title(self) -> str:
        """
        Get the title for the coordinate range widget.
        Override this method to customize the title.
        """
        return "Geographic Bounds"
    
    def _propagate_controller_to_widgets(self):
        """Propagate controller to child widgets."""
        if hasattr(self, 'data_selection_widget') and self.controller:
            if self.data_selection_widget:
                self.data_selection_widget.set_controller(self.controller)
    
    def _show_initial_plot(self):
        """Show initial plot if data is available."""
        try:
            self._generate_plot()
        except Exception as e:
            self.logger.debug(f"Could not show initial plot: {e}")
    
    def _on_track_data_selection_changed(self, selection: List[str]):
        """Handle track selection changes."""
        self.track_selection_var = selection
        self._generate_plot()

    def _on_truth_data_selection_changed(self, selection: List[str]):
        """Handle truth selection changes."""
        self.truth_selection_var = selection
        self._generate_plot()
    
    def _on_coord_range_changed(self, ranges: Dict[str, tuple]):
        """Handle coordinate range changes."""
        self.logger.debug(f"Coordinate ranges changed: {ranges}")
        lat_range = ranges.get('lat_range', None)
        lon_range = ranges.get('lon_range', None)
        
        if lat_range and lon_range:
            if lat_range != self.lat_range or lon_range != self.lon_range:
                self.lat_range = lat_range
                self.lon_range = lon_range
                self._on_coordinate_ranges_updated()

    def _on_coordinate_ranges_updated(self):
        """
        Called when coordinate ranges are updated.
        Override this method to handle coordinate range updates.
        """
        self._generate_plot()

    def _on_reset_bounds(self):
        """Handle reset bounds button click."""
        self.logger.debug("Resetting geographic bounds")
        if hasattr(self, 'coord_range_widget') and self.coord_range_widget:
            # Set to default values to trigger recalculation
            self.coord_range_widget.set_ranges((-1.0, 1.0), (-1.0, 1.0))
        self._generate_plot()
    
    def _setup_zoom_callback_connection(self):
        """Setup connection between plot backend zoom events and coordinate range widget."""
        if self.backend and hasattr(self.backend, 'set_zoom_callback'):
            self.backend.set_zoom_callback(self._on_plot_zoom_changed)
            self.logger.debug("Connected zoom callback to coordinate range widget")

    def _on_plot_zoom_changed(self, xlim: tuple, ylim: tuple):
        """Handle zoom/pan changes from the plot backend."""
        try:
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
    
    def _build_plot_config(self) -> Dict[str, Any]:
        """
        Build the configuration dictionary for plot generation.
        
        Returns:
            Configuration dictionary with common settings
        """
        config: Dict[str, Any] = {
            'tracks': self.track_selection_var,
            'truth': self.truth_selection_var,
            # Plot mode directives for downstream rendering logic
            'tracks_plot_mode': 'trajectory',
            'truth_plot_mode': 'scatter',
        }
        
        # Get coordinate ranges from widget
        if hasattr(self, 'coord_range_widget') and self.coord_range_widget:
            ranges = self.coord_range_widget.get_ranges()
            if ranges:
                lat_range = ranges.get('lat_range', None)
                lon_range = ranges.get('lon_range', None)
                
                # Only include if explicitly set (not default values)
                if lat_range is not None and lat_range != (-1.0, 1.0):
                    config['lat_range'] = lat_range
                if lon_range is not None and lon_range != (-1.0, 1.0):
                    config['lon_range'] = lon_range
        
        return config
    
    def _update_coordinate_ranges_from_plot_data(self, plot_data: Dict[str, Any]):
        """
        Update coordinate range widgets with data from plot.
        
        Args:
            plot_data: Plot data containing coordinate ranges
        """
        self.lat_range = plot_data.get('lat_range')
        self.lon_range = plot_data.get('lon_range')
        
        if self.lat_range and self.lon_range and self.coord_range_widget:
            # Temporarily disable the range callback to prevent circular updates
            original_callback = self.coord_range_widget.range_callback
            self.coord_range_widget.range_callback = None
            
            # Update the widget values
            self.coord_range_widget.set_ranges(self.lat_range, self.lon_range)
            
            # Restore the callback
            self.coord_range_widget.range_callback = original_callback
    
    def _generate_plot(self):
        """
        Generate the geospatial plot.
        This method should be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _generate_plot()")
    
    def auto_update(self):
        """Auto-update the plot when data changes."""
        self.logger.debug("Auto-updating geospatial plot")
        
        self.on_focus_dataset_changed()
        
        self._generate_plot()
    
    def should_auto_update(self, focus_info: Any) -> bool:
        """
        Check if this tab should auto-update.
        
        Base implementation allows auto-update for all geospatial tabs.
        Override this method to customize auto-update behavior.
        """
        return True