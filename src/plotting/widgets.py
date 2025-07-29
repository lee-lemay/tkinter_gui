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
        # Propagate to child control widgets
        self._propagate_controller_to_widgets()

    def _propagate_controller_to_widgets(self):
        """Propagate controller to child control widgets."""
        # Override in subclasses to pass controller to specific widgets
        pass
    
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