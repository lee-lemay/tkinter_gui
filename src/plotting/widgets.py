"""
Widget components for modular plot tab architecture.

This module provides reusable widget components that can work with any
plot backend, enabling clean separation of UI and plotting concerns.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Any, Dict, Callable
import logging
from .backends import PlotBackend


class PlotCanvasWidget(ttk.Frame):
    """
    Generic plot canvas widget that can host any plot backend.
    
    This widget provides a standardized interface for embedding different
    plot backends (matplotlib, plotly, etc.) in tkinter applications.
    """
    
    def __init__(self, parent: tk.Widget, backend: PlotBackend):
        """
        Initialize the plot canvas widget.
        
        Args:
            parent: Parent tkinter widget
            backend: Plot backend instance to use for rendering
        """
        super().__init__(parent)
        self.backend = backend
        self.logger = logging.getLogger(__name__)
        
        # Setup the backend widget
        self._setup_backend_widget()
    
    def _setup_backend_widget(self):
        """Setup the backend widget in this frame."""
        try:
            # If backend doesn't have a parent widget yet, set this frame as its parent
            if not hasattr(self.backend, 'parent_widget') or self.backend.parent_widget is None:
                self.logger.debug(f"Setting parent widget for backend: {type(self.backend).__name__}")
                self.backend.parent_widget = self
                # Re-initialize the backend with the parent for matplotlib backend
                try:
                    if hasattr(self.backend, '_setup_matplotlib'):
                        self.logger.debug("Re-initializing backend with parent widget")
                        # Use getattr to safely call the method
                        setup_method = getattr(self.backend, '_setup_matplotlib')
                        setup_method()
                except AttributeError:
                    # Method doesn't exist on this backend type
                    pass
                except Exception as e:
                    self.logger.error(f"Error re-initializing backend: {e}")
            
            backend_widget = self.backend.get_widget()
            if backend_widget:
                backend_widget.pack(fill="both", expand=True)
                self.logger.debug(f"Backend widget setup complete: {type(self.backend).__name__}")
                
                # Debug: Check if canvas was created
                if hasattr(self.backend, 'canvas'):
                    self.logger.debug("✓ Backend has canvas after setup")
                else:
                    self.logger.warning("✗ Backend still missing canvas after setup")
            else:
                self.logger.debug("Backend did not provide a widget - may be operating in headless mode")
        except Exception as e:
            self.logger.error(f"Error setting up backend widget: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
    
    def create_plot(self, plot_type: str, data: Dict[str, Any], 
                   config: Optional[Dict[str, Any]] = None):
        """
        Create a plot using the configured backend.
        
        Args:
            plot_type: Type of plot to create
            data: Plot data
            config: Optional configuration parameters
        """
        try:
            result = self.backend.create_plot(plot_type, data, config)
            if not result.success:
                self.logger.error(f"Plot creation failed: {result.error}")
        except Exception as e:
            self.logger.error(f"Error creating plot: {e}")
    
    def set_axis_limits(self, x_range: Optional[tuple] = None, y_range: Optional[tuple] = None):
        """Set axis limits for the current plot."""
        self.backend.set_axis_limits(x_range, y_range)
    
    def clear_plot(self):
        """Clear the current plot."""
        self.backend.clear_plot()
    
    def refresh(self):
        """Refresh the plot display."""
        self.backend.refresh()
    
    def export_plot(self, filename: str, format: str = 'png'):
        """Export the current plot to a file."""
        return self.backend.export_plot(filename, format)
    
    def set_zoom_callback(self, callback: Callable):
        """Set callback for zoom/pan events."""
        self.backend.set_zoom_callback(callback)


class PlotTabWidget(ttk.Frame):
    """
    Base class for plot tab widgets.
    
    Provides common functionality for all plot tabs including:
    - Plot canvas management
    - Control panel structure
    - Data update handling
    - Auto-update interface for data changes
    """
    
    def __init__(self, parent: tk.Widget, backend: PlotBackend, tab_name: str):
        """
        Initialize the plot tab widget.
        
        Args:
            parent: Parent widget (typically a notebook)
            backend: Plot backend to use
            tab_name: Name of this tab
        """
        super().__init__(parent)
        self.backend = backend
        self.tab_name = tab_name
        self.logger = logging.getLogger(f"{__name__}.{tab_name}")
        
        # Data and state management
        self.controller: Optional[Any] = None
        self.plot_manager: Optional[Any] = None
        
        # Create the tab structure
        self._create_tab_structure()
        self._create_controls()
        self._create_plot_canvas()
        
        self.logger.debug(f"Plot tab '{tab_name}' initialized")
    
    def set_controller(self, controller: Any):
        """Set the application controller."""
        self.controller = controller
    
    def set_plot_manager(self, plot_manager: Any):
        """Set the plot manager."""
        self.plot_manager = plot_manager
    
    def _create_tab_structure(self):
        """Create the basic tab structure with control and canvas areas."""
        # Control panel at top
        self.control_frame = ttk.LabelFrame(self, text=f"{self.tab_name} Controls")
        self.control_frame.pack(fill="x", padx=10, pady=10)
        
        # Canvas area below
        self.canvas_frame = ttk.Frame(self)
        self.canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    def _create_controls(self):
        """Create control widgets. Override in subclasses."""
        # Base implementation - override in subclasses
        ttk.Label(self.control_frame, text="No controls defined").pack(padx=5, pady=5)
    
    def _create_plot_canvas(self):
        """Create the plot canvas using the configured backend."""
        self.plot_canvas = PlotCanvasWidget(self.canvas_frame, self.backend)
        self.plot_canvas.pack(fill="both", expand=True)
    
    def update_plot(self, plot_type: str, data: Dict[str, Any], 
                   config: Optional[Dict[str, Any]] = None):
        """
        Update the plot with new data.
        
        Args:
            plot_type: Type of plot to create
            data: Plot data
            config: Optional configuration
        """
        try:
            self.plot_canvas.create_plot(plot_type, data, config)
            self.logger.debug(f"Plot updated: {plot_type}")
        except Exception as e:
            self.logger.error(f"Error updating plot: {e}")
    
    def clear_plot(self):
        """Clear the current plot."""
        self.plot_canvas.clear_plot()
    
    def refresh_plot(self):
        """Refresh the plot display."""
        self.plot_canvas.refresh()
    
    def auto_update(self):
        """
        Auto-update the plot when data changes.
        
        This method should be overridden in subclasses to implement
        tab-specific update logic. Called automatically when:
        - Datasets are loaded/changed
        - Focus dataset changes
        - Data is modified
        """
        self.logger.debug(f"Auto-update called for {self.tab_name} tab")
        # Default implementation - override in subclasses
        pass
    
    def should_auto_update(self, focus_info: Any) -> bool:
        """
        Check if this tab should auto-update for the given focus dataset.
        
        Args:
            focus_info: DatasetInfo for the focus dataset
            
        Returns:
            True if the tab should update, False otherwise
        """
        # Default implementation - checks if focus dataset is loaded with data
        if not focus_info or focus_info.status.value != "loaded":
            return False
        
        # Check if there's any data to display
        has_data = (
            (focus_info.tracks_df is not None and not focus_info.tracks_df.empty) or
            (focus_info.truth_df is not None and not focus_info.truth_df.empty) or
            (focus_info.detections_df is not None and not focus_info.detections_df.empty)
        )
        
        return has_data


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
            
            # Path 2: Generate data directly from controller state (new approach)
            elif self.controller:
                app_state = self.controller.get_state()
                focus_info = app_state.get_focus_dataset_info()
                
                if focus_info and focus_info.status.value == "loaded":
                    plot_data = self._generate_plot_data_direct(focus_info, plot_type)
            
            # Path 3: Show demo data if no real data available
            else:
                plot_data = self._generate_demo_data(plot_type)
            
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
    
    def _generate_demo_data(self, plot_type: str) -> Dict[str, Any]:
        """Generate demo data when no real data is available."""
        if plot_type == 'track_counts':
            return {
                'track_counts': {'Demo Dataset': 100},
                'x': ['Demo Tracks', 'Demo Truth', 'Demo Detections'],
                'y': [50, 30, 20]
            }
        return {'error': 'No demo data available'}
    
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
