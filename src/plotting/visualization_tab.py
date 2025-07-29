"""
Visualization tab widget for the data analysis application.

This module provides the Visualization tab widget that extends the base PlotTabWidget
with visualization-specific functionality and controls.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Any, Dict
import logging

from .widgets import PlotTabWidget
from .backends import PlotBackend
from .control_widgets import DataSelectionWidget, CoordinateRangeWidget


class VisualizationTabWidget(PlotTabWidget):
    """
    Visualization tab widget for creating scatter plots and other visualizations.
    
    This widget provides controls for selecting data types, coordinate ranges,
    and various visualization options.
    """
    
    def __init__(self, parent: tk.Widget, backend: PlotBackend):
        """
        Initialize the visualization tab widget.
        
        Args:
            parent: Parent widget
            backend: Plot backend to use
        """
        # Initialize control variables BEFORE calling super().__init__
        # because super().__init__ calls _create_controls() which needs these variables
        self.plot_type_var = tk.StringVar(value="scatter")
        self.show_detections_var = tk.BooleanVar(value=True)
        self.show_tracks_var = tk.BooleanVar(value=True)
        self.show_truth_var = tk.BooleanVar(value=True)
        
        # Initialize control widgets
        self.data_selection_widget = None
        self.coord_range_widget = None
        
        super().__init__(parent, backend, "Visualization")
        
        # Show initial plot following template pattern
        self._show_initial_plot()
    
    def _create_controls(self):
        """Create visualization-specific control widgets."""
        # Plot type selection
        plot_type_frame = ttk.Frame(self.control_frame)
        plot_type_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(plot_type_frame, text="Plot Type:").pack(side="left")
        plot_type_combo = ttk.Combobox(
            plot_type_frame,
            textvariable=self.plot_type_var,
            values=["scatter", "line", "trajectory", "heatmap"],
            state="readonly",
            width=15
        )
        plot_type_combo.pack(side="left", padx=(5, 0))
        plot_type_combo.bind("<<ComboboxSelected>>", self._on_plot_type_changed)
        
        # Data type selection checkboxes
        data_types_frame = ttk.Frame(self.control_frame)
        data_types_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(data_types_frame, text="Show:").pack(side="left")
        
        detection_cb = ttk.Checkbutton(
            data_types_frame,
            text="Detections",
            variable=self.show_detections_var,
            command=self._on_data_type_changed
        )
        detection_cb.pack(side="left", padx=(10, 0))
        
        tracks_cb = ttk.Checkbutton(
            data_types_frame,
            text="Tracks",
            variable=self.show_tracks_var,
            command=self._on_data_type_changed
        )
        tracks_cb.pack(side="left", padx=(10, 0))
        
        truth_cb = ttk.Checkbutton(
            data_types_frame,
            text="Truth",
            variable=self.show_truth_var,
            command=self._on_data_type_changed
        )
        truth_cb.pack(side="left", padx=(10, 0))
        
        # Add coordinate range widget
        self.coord_range_widget = CoordinateRangeWidget(
            self.control_frame,
            title="Coordinate Range"
        )
        self.coord_range_widget.pack(fill="x", padx=5, pady=5)
        self.coord_range_widget.set_range_callback(self._on_coord_range_changed)
        
        # Visualization options
        viz_options_frame = ttk.Frame(self.control_frame)
        viz_options_frame.pack(fill="x", padx=5, pady=5)
        
        # Color scheme selection
        ttk.Label(viz_options_frame, text="Color Scheme:").pack(side="left")
        color_scheme_combo = ttk.Combobox(
            viz_options_frame,
            values=["default", "viridis", "plasma", "jet", "grayscale"],
            state="readonly",
            width=12
        )
        color_scheme_combo.pack(side="left", padx=(5, 0))
        color_scheme_combo.set("default")
        color_scheme_combo.bind("<<ComboboxSelected>>", self._on_color_scheme_changed)
        
        # Marker size
        ttk.Label(viz_options_frame, text="Marker Size:").pack(side="left", padx=(10, 0))
        marker_size_scale = tk.Scale(
            viz_options_frame,
            from_=1,
            to=20,
            orient="horizontal",
            length=100,
            command=self._on_marker_size_changed
        )
        marker_size_scale.pack(side="left", padx=(5, 0))
        marker_size_scale.set(5)
        
        # Plot button
        plot_btn = ttk.Button(
            self.control_frame,
            text="Generate Plot",
            command=self._on_generate_plot
        )
        plot_btn.pack(pady=10)
    
    def _on_plot_type_changed(self, event=None):
        """Handle plot type selection change."""
        self.logger.debug(f"Plot type changed to: {self.plot_type_var.get()}")
        self._on_generate_plot()
    
    def _on_data_type_changed(self):
        """Handle data type checkbox changes."""
        self.logger.debug(f"Data types changed - Detections: {self.show_detections_var.get()}, "
                         f"Tracks: {self.show_tracks_var.get()}, Truth: {self.show_truth_var.get()}")
        self._on_generate_plot()
    
    def _on_coord_range_changed(self, ranges: Dict[str, tuple]):
        """Handle coordinate range changes."""
        self.logger.debug(f"Coordinate ranges changed: {ranges}")
        self._on_generate_plot()
    
    def _on_color_scheme_changed(self, event=None):
        """Handle color scheme selection change."""
        if event and hasattr(event, 'widget'):
            combo = event.widget
            self.logger.debug(f"Color scheme changed to: {combo.get()}")
        self._on_generate_plot()
    
    def _on_marker_size_changed(self, value):
        """Handle marker size change."""
        self.logger.debug(f"Marker size changed to: {value}")
        self._on_generate_plot()
    
    def _on_generate_plot(self):
        """Generate the visualization plot."""
        try:
            # Try to get data through multiple paths for maximum compatibility
            plot_data = None
            
            # Path 1: Use plot_manager if available (legacy compatibility)
            if self.plot_manager and self.controller:
                app_state = self.controller.get_state()
                plot_data = self.plot_manager.prepare_plot_data('visualization', app_state) 
            
            # Update the plot if we have data
            if plot_data and 'error' not in plot_data:
                config = {
                    'title': f'{self.plot_type_var.get().title()} Plot',
                    'xlabel': 'X Coordinate',
                    'ylabel': 'Y Coordinate'
                }
                self.update_plot('visualization', plot_data, config)
                self.logger.debug("Visualization plot generated successfully")
            else:
                self.logger.debug("No valid data for visualization plot")
                self.clear_plot()
                
        except Exception as e:
            self.logger.error(f"Error generating visualization plot: {e}")
            self.clear_plot()
    
    def auto_update(self):
        """Auto-update the plot when data changes."""
        self.logger.debug("Auto-updating visualization plot")
        self._on_generate_plot()
    
    def should_auto_update(self, focus_info: Any) -> bool:
        """
        Check if this tab should auto-update.
        
        Visualization tab should auto-update when datasets or selections change.
        """
        return True
    
    def _show_initial_plot(self):
        """Show initial plot when tab is first displayed."""
        self._on_generate_plot()
