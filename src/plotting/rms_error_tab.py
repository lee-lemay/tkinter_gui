"""
RMS Error tab widget for the data analysis application.

This module provides the RMS Error tab widget that extends the base PlotTabWidget
with RMS error calculation and visualization functionality.
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Any, Dict
import logging

from .widgets import PlotTabWidget
from .backends import PlotBackend
from .control_widgets import TrackSelectionWidget


class RMSErrorTabWidget(PlotTabWidget):
    """
    RMS Error tab widget for calculating and visualizing RMS errors.
    
    This widget provides controls for track selection, time window settings,
    and various RMS error analysis options.
    """
    
    def __init__(self, parent: tk.Widget, backend: PlotBackend):
        """
        Initialize the RMS error tab widget.
        
        Args:
            parent: Parent widget
            backend: Plot backend to use
        """
        
        # Initialize control widgets
        self.track_selection_widget = None
        self.dataset_selection_widget = None
        
        super().__init__(parent, backend, "RMS Error")
        
        # Show initial plot following template pattern
        self._show_initial_plot()
    
    def _create_controls(self):
        """Create RMS error-specific control widgets."""
        
        # Add track selection widget
        self.track_selection_widget = TrackSelectionWidget(self.control_frame)
        self.track_selection_widget.pack(fill="x", padx=5, pady=5)
        self.track_selection_widget.set_selection_callback(self._on_track_selection_changed)

    def _propagate_controller_to_widgets(self):
        """Propagate controller to child widgets."""
        if hasattr(self, 'track_selection_widget') and self.controller:
            if self.track_selection_widget:
                self.track_selection_widget.set_controller(self.controller)  
    
    def _on_track_selection_changed(self, selection: Any):
        """Handle track selection changes."""
        self.logger.debug(f"Track selection changed: {selection}")
        self._on_calculate_rms()
    
    def _on_dataset_selection_changed(self, selection: List[str]):
        """Handle dataset selection changes."""
        self.logger.debug(f"Dataset selection changed: {selection}")
        self._on_calculate_rms()

    def on_focus_dataset_changed(self):
        """Handle focus dataset changes by updating track selection widget."""
        try:
            # Call parent method to update common widgets
            super().on_focus_dataset_changed()
            
        except Exception as e:
            self.logger.error(f"Error handling focus dataset change in RMS error tab: {e}")
    
    def _on_calculate_rms(self):
        """Calculate RMS errors and update the plot."""
        try:
            # Try to get data through multiple paths for maximum compatibility
            plot_data = None

            if self.plot_manager and self.controller:
                 app_state = self.controller.get_state()
                 
                 # Build configuration with track selection
                 config = self._build_plot_config()

                 plot_data = self.plot_manager.prepare_plot_data('rms_error_3d', app_state, config)
            
            # Update the plot if we have data
            if plot_data and 'error' not in plot_data:
                config = {
                    'title': f'RMS Error',
                    'xlabel': 'Time (s)',
                    'ylabel': f'RMS Error'
                }
                self.update_plot('rms_error_3d', plot_data, config)
                self.logger.debug("RMS error plot generated successfully")
            else:
                self.logger.debug("No valid data for RMS error plot")
                self.clear_plot()
                
        except Exception as e:
            self.logger.error(f"Error calculating RMS errors: {e}")
            self.clear_plot()

    def _build_plot_config(self) -> Dict[str, Any]:
        """
        Build the configuration dictionary for plot generation.
        
        Returns:
            Configuration dictionary with track selection
        """
        config: Dict[str, Any] = {}
        
        # Get selected tracks from the track selection widget
        if hasattr(self, 'track_selection_widget') and self.track_selection_widget:
            selected_tracks = self.track_selection_widget.get_selected_tracks()
            if selected_tracks:
                config['tracks'] = selected_tracks
            else:
                config['tracks'] = "None"
        else:
            config['tracks'] = "All"  # Default to all tracks if no widget
        
        return config
    
    def auto_update(self):
        """Auto-update the plot when data changes."""
        self.logger.debug("Auto-updating RMS error plot")
        
        self.on_focus_dataset_changed()
        
        self._on_calculate_rms()
    
    def should_auto_update(self, focus_info: Any) -> bool:
        """
        Check if this tab should auto-update.
        
        RMS error tab should auto-update when datasets with tracking data change.
        """
        return True
    
    def _show_initial_plot(self):
        """Show initial plot when tab is first displayed."""
        self._on_calculate_rms() 
