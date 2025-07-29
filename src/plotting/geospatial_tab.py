"""
Geospatial tab widget for the data analysis application.

This module provides the Geospatial tab widget that extends the base PlotTabWidget
with geospatial-specific functionality and controls.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Any, Dict
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
        
        super().__init__(parent, backend, "Geospatial")
        
        # Auto-show initial plot if data is available (following statistics_tab template)
        self._show_initial_plot()
    
    def _create_controls(self):
        """Create geospatial-specific control widgets."""
        
        # Add data selection widget
        self.data_selection_widget = DataSelectionWidget(self.control_frame)
        self.data_selection_widget.pack(fill="x", padx=5, pady=5)
        self.data_selection_widget.set_tracks_callback(self._on_data_selection_changed)
        self.data_selection_widget.set_truth_callback(self._on_data_selection_changed)
        
        # Add coordinate range widget
        self.coord_range_widget = CoordinateRangeWidget(
            self.control_frame,
            title="Geographic Bounds"
        )
        self.coord_range_widget.pack(fill="x", padx=5, pady=5)
        self.coord_range_widget.set_range_callback(self._on_coord_range_changed)
        self.coord_range_widget.set_reset_callback(self._on_reset_bounds)

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
    
    def _on_data_selection_changed(self, selection: str):
        """Handle data selection changes."""
        self.logger.debug(f"Data selection changed: {selection}")
        self._on_generate_plot()
    
    def _on_coord_range_changed(self, ranges: Dict[str, tuple]):
        """Handle coordinate range changes."""
        self.logger.debug(f"Coordinate ranges changed: {ranges}")
        self._on_generate_plot()
    
    def _on_reset_bounds(self):
        """Handle reset bounds button click."""
        self.logger.debug("Resetting geographic bounds")
        # Reset to default bounds
        self.coord_range_widget.set_ranges((-1.0, 1.0), (-1.0, 1.0))
        self._on_generate_plot()
    
    def _calculate_data_bounds(self, dataset_info: Any) -> Optional[Dict[str, tuple]]:
        """Calculate geographic bounds from dataset."""
        try:
            lat_values = []
            lon_values = []
            
            # Collect coordinates from available datasets
            for df_name in ['tracks_df', 'truth_df', 'detections_df']:
                df = getattr(dataset_info, df_name, None)
                if df is not None and not df.empty:
                    # Look for common coordinate column names
                    lat_cols = [col for col in df.columns if 'lat' in col.lower()]
                    lon_cols = [col for col in df.columns if 'lon' in col.lower()]
                    
                    if lat_cols and lon_cols:
                        lat_values.extend(df[lat_cols[0]].dropna().tolist())
                        lon_values.extend(df[lon_cols[0]].dropna().tolist())
            
            if lat_values and lon_values:
                # Add some padding around the data bounds
                lat_min, lat_max = min(lat_values), max(lat_values)
                lon_min, lon_max = min(lon_values), max(lon_values)
                
                lat_padding = (lat_max - lat_min) * 0.1
                lon_padding = (lon_max - lon_min) * 0.1
                
                return {
                    'lat_range': (lat_min - lat_padding, lat_max + lat_padding),
                    'lon_range': (lon_min - lon_padding, lon_max + lon_padding)
                }
            
        except Exception as e:
            self.logger.error(f"Error calculating data bounds: {e}")
        
        return None
    
    def _on_generate_plot(self):
        """Generate the geospatial plot."""
        try:
            # Try to get data through multiple paths for maximum compatibility
            plot_data = None
            
            # Path 1: Use plot_manager if available (legacy compatibility)
            if self.plot_manager and self.controller:
                 app_state = self.controller.get_state()
                 plot_data = self.plot_manager.prepare_plot_data('lat_lon_scatter', app_state)
            
            # Update the plot if we have data
            if plot_data and 'error' not in plot_data:
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
