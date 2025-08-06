"""
Lifetime tab widget for the data analysis application.

This module provides the Lifetime tab widget that extends the base PlotTabWidget
with track lifetime analysis functionality and controls.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Any, Dict, List
import logging

from .widgets import PlotTabWidget
from .backends import PlotBackend
from .control_widgets import TrackSelectionWidget


class LifetimeTabWidget(PlotTabWidget):
    """
    Lifetime tab widget for analyzing track lifetimes and duration statistics.
    
    This widget provides controls for track selection, lifetime calculation methods,
    and various lifetime analysis visualization options.
    """
    
    def __init__(self, parent: tk.Widget, backend: PlotBackend):
        """
        Initialize the lifetime tab widget.
        
        Args:
            parent: Parent widget
            backend: Plot backend to use
        """        
        # Initialize control widgets
        self.track_selection_widget = None
        self.dataset_selection_widget = None
        
        super().__init__(parent, backend, "Lifetime")
        
        # Show initial plot following template pattern
        self._show_initial_plot()
    
    def _create_controls(self):
        """Create lifetime analysis-specific control widgets."""
        
        # Add track selection widget (collapsed by default to save space)
        self.track_selection_widget = TrackSelectionWidget(self.control_frame, collapsed=True)
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
        self._on_analyze_lifetimes()
    
    def _on_dataset_selection_changed(self, selection: List[str]):
        """Handle dataset selection changes."""
        self.logger.debug(f"Dataset selection changed: {selection}")
        self._on_analyze_lifetimes()
    
    def _on_export_results(self):
        """Handle export results button click."""
        try:
            from tkinter import filedialog, messagebox
            filename = filedialog.asksaveasfilename(
                title="Export Lifetime Analysis Results",
                defaultextension=".csv",
                filetypes=[
                    ("CSV files", "*.csv"),
                    ("Excel files", "*.xlsx"),
                    ("MATLAB files", "*.mat"),
                    ("JSON files", "*.json"),
                    ("All files", "*.*")
                ]
            )
            if filename:
                # Here we would export the lifetime analysis results
                # For now, just show a placeholder message
                messagebox.showinfo("Export", f"Lifetime analysis results would be exported to:\\n{filename}")
                self.logger.info(f"Lifetime analysis results exported to: {filename}")
                
        except Exception as e:
            self.logger.error(f"Error exporting results: {e}")
    
    def _on_analyze_lifetimes(self):
        """Perform lifetime analysis and update the plot."""
        try:
            # Try to get data through multiple paths for maximum compatibility
            plot_data = None
            
            # Path 1: Use plot_manager if available (legacy compatibility)
            if self.plot_manager and self.controller:
                app_state = self.controller.get_state()
                plot_data = self.plot_manager.prepare_plot_data('track_truth_lifetime', app_state)
            
            # Update the plot if we have data
            if plot_data and 'error' not in plot_data:
                config = {
                    'title': f'Lifetime Analysis',
                    'xlabel': "Seconds",
                    'ylabel': "Seconds"
                }
                self.update_plot('track_truth_lifetime', plot_data, config)
                self.logger.debug("Lifetime analysis plot generated successfully")
            else:
                self.logger.debug("No valid data for lifetime analysis plot")
                self.clear_plot()
                
        except Exception as e:
            self.logger.error(f"Error performing lifetime analysis: {e}")
            self.clear_plot()

    def auto_update(self):
        """Auto-update the plot when data changes."""
        self.logger.debug("Auto-updating lifetime analysis plot")
        self._on_analyze_lifetimes()
    
    def should_auto_update(self, focus_info: Any) -> bool:
        """
        Check if this tab should auto-update.
        
        Lifetime tab should auto-update when datasets with tracking data change.
        """
        return True
    
    def _show_initial_plot(self):
        """Show initial plot when tab is first displayed."""
        self._on_analyze_lifetimes() 
