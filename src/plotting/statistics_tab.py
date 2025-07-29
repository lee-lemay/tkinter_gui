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
    Statistics tab widget for displaying track count and other statistical plots.
    
    This widget demonstrates the component-based architecture by extending
    the base PlotTabWidget with statistics-specific functionality.
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
        # Control panel layout
        controls_container = ttk.Frame(self.control_frame)
        controls_container.pack(fill="x", padx=5, pady=5)
        
        # Plot type selection
        plot_type_frame = ttk.Frame(controls_container)
        plot_type_frame.pack(side="left", padx=5)
        
        ttk.Label(plot_type_frame, text="Plot Type:").pack(anchor="w")
        self.plot_type_var = tk.StringVar(value="track_counts")
        plot_type_combo = ttk.Combobox(
            plot_type_frame,
            textvariable=self.plot_type_var,
            values=["track_counts", "dataset_summary", "data_quality"],
            state="readonly",
            width=15
        )
        plot_type_combo.pack()
        plot_type_combo.bind("<<ComboboxSelected>>", self._on_plot_type_changed)
        
        # Refresh button
        button_frame = ttk.Frame(controls_container)
        button_frame.pack(side="right", padx=5)
        
        refresh_btn = ttk.Button(
            button_frame,
            text="Refresh",
            command=self._on_refresh_plot
        )
        refresh_btn.pack()
        
        # Export button
        export_btn = ttk.Button(
            button_frame,
            text="Export",
            command=self._on_export_plot
        )
        export_btn.pack(pady=(5, 0))
    
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
    
    def _on_export_plot(self):
        """Handle export button click."""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                title="Export Plot",
                defaultextension=".png",
                filetypes=[
                    ("PNG files", "*.png"),
                    ("PDF files", "*.pdf"),
                    ("SVG files", "*.svg"),
                    ("All files", "*.*")
                ]
            )
            if filename:
                if self.plot_canvas.export_plot(filename):
                    messagebox.showinfo("Export Successful", f"Plot saved to:\\n{filename}")
                else:
                    messagebox.showerror("Export Failed", "Failed to export plot")
        except Exception as e:
            self.logger.error(f"Error exporting plot: {e}")
            messagebox.showerror("Export Error", f"Export failed: {e}")
    
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
            if plot_type == 'track_counts':
                # Count data in each dataset type
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


class ControlPanelWidget(ttk.LabelFrame):
    """
    Reusable control panel widget for common plot controls.
    
    This widget provides standardized control elements that can be used
    across different plot tabs.
    """
    
    def __init__(self, parent: tk.Widget, title: str = "Controls"):
        """
        Initialize the control panel.
        
        Args:
            parent: Parent widget
            title: Title for the control panel
        """
        super().__init__(parent, text=title, padding=5)
        self.logger = logging.getLogger(__name__)
        self._callbacks = {}
    
    def add_combobox_control(self, label: str, var: tk.StringVar, values: list,
                            callback: Optional[Callable] = None, width: int = 15):
        """
        Add a combobox control to the panel.
        
        Args:
            label: Label text
            var: StringVar to bind to
            values: List of combobox values
            callback: Optional callback for selection changes
            width: Width of the combobox
        """
        frame = ttk.Frame(self)
        frame.pack(fill="x", padx=5, pady=2)
        
        ttk.Label(frame, text=label).pack(side="left")
        combo = ttk.Combobox(frame, textvariable=var, values=values, 
                           state="readonly", width=width)
        combo.pack(side="right")
        
        if callback:
            combo.bind("<<ComboboxSelected>>", callback)
        
        return combo
    
    def add_button_control(self, text: str, callback: Callable, side: str = "left"):
        """
        Add a button control to the panel.
        
        Args:
            text: Button text
            callback: Button click callback
            side: Pack side ("left", "right", "top", "bottom")
        """
        button = ttk.Button(self, text=text, command=callback)
        # Use string literals to satisfy type checker
        if side == "left":
            button.pack(side="left", padx=5, pady=2)
        elif side == "right":
            button.pack(side="right", padx=5, pady=2)
        elif side == "top":
            button.pack(side="top", padx=5, pady=2)
        elif side == "bottom":
            button.pack(side="bottom", padx=5, pady=2)
        else:
            button.pack(side="left", padx=5, pady=2)  # Default
        return button
