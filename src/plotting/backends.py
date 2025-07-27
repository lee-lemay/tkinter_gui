"""
Abstract plot backend interfaces for supporting multiple plotting libraries.

This module defines the abstract interface that must be implemented by all
plot backends (matplotlib, plotly, etc.) to enable drop-in replacement.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, Tuple
import logging


class PlotResult:
    """Represents the result of a plot operation."""
    
    def __init__(self, success: bool, plot_object: Any = None, error: str = None):
        self.success = success
        self.plot_object = plot_object
        self.error = error


class PlotBackend(ABC):
    """
    Abstract base class for plot backends.
    
    This interface must be implemented by all plotting backends to ensure
    consistent behavior and enable drop-in replacement between backends.
    """
    
    def __init__(self, parent_widget=None):
        self.parent_widget = parent_widget
        self.logger = logging.getLogger(self.__class__.__name__)
        self.zoom_callback: Optional[Callable] = None
    
    @abstractmethod
    def create_plot(self, plot_type: str, data: Dict[str, Any], 
                   config: Optional[Dict[str, Any]] = None) -> PlotResult:
        """
        Create a plot of the specified type with given data.
        
        Args:
            plot_type: Type of plot to create (e.g., 'track_counts', 'lat_lon')
            data: Plot data dictionary
            config: Optional configuration parameters
            
        Returns:
            PlotResult indicating success/failure and containing plot object
        """
        pass
    
    @abstractmethod
    def set_axis_limits(self, x_range: Optional[Tuple[float, float]] = None,
                       y_range: Optional[Tuple[float, float]] = None) -> bool:
        """
        Set axis limits for the current plot.
        
        Args:
            x_range: X-axis range as (min, max) tuple
            y_range: Y-axis range as (min, max) tuple
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def clear_plot(self) -> bool:
        """
        Clear the current plot.
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def refresh(self) -> bool:
        """
        Refresh/redraw the plot.
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def export_plot(self, filename: str, format: str = 'png') -> bool:
        """
        Export the current plot to a file.
        
        Args:
            filename: Output file path
            format: Export format ('png', 'pdf', 'svg', etc.)
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_widget(self):
        """
        Get the widget that can be embedded in a tkinter interface.
        
        Returns:
            Widget object that can be packed/placed in tkinter
        """
        pass
    
    def set_zoom_callback(self, callback: Callable[[Tuple[float, float], Tuple[float, float]], None]):
        """
        Set callback function for zoom/pan events.
        
        Args:
            callback: Function to call with (xlim, ylim) when zoom/pan occurs
        """
        self.zoom_callback = callback
    
    def get_axis_limits(self) -> Tuple[Optional[Tuple[float, float]], Optional[Tuple[float, float]]]:
        """
        Get current axis limits.
        
        Returns:
            Tuple of (x_range, y_range) where each range is (min, max) or None
        """
        return None, None


class MatplotlibBackend(PlotBackend):
    """
    Matplotlib implementation of the PlotBackend interface.
    
    This backend wraps matplotlib functionality to conform to the abstract interface.
    """
    
    def __init__(self, parent_widget=None, figure_size: Tuple[int, int] = (8, 6)):
        super().__init__(parent_widget)
        self.figure_size = figure_size
        self._setup_matplotlib()
    
    def _setup_matplotlib(self):
        """Initialize matplotlib components."""
        import matplotlib
        matplotlib.use('TkAgg')
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from matplotlib.backends._backend_tk import NavigationToolbar2Tk
        from matplotlib.figure import Figure
        import tkinter as tk
        from tkinter import ttk
        
        # Store matplotlib imports for use in methods
        self.plt = plt
        self.Figure = Figure
        self.FigureCanvasTkAgg = FigureCanvasTkAgg
        self.NavigationToolbar2Tk = NavigationToolbar2Tk
        
        # Create matplotlib figure (or use existing one)
        if not hasattr(self, 'figure'):
            self.figure = Figure(figsize=self.figure_size, dpi=100)
            self.figure.patch.set_facecolor('white')
        
        if self.parent_widget:
            # Only create GUI components if we have a parent and don't already have them
            if not hasattr(self, 'frame'):
                # Create tkinter frame to hold everything
                self.frame = ttk.Frame(self.parent_widget)
                
                # Create canvas
                self.canvas = self.FigureCanvasTkAgg(self.figure, master=self.frame)
                self.canvas_widget = self.canvas.get_tk_widget()
                
                # Create toolbar
                self.toolbar_frame = ttk.Frame(self.frame)
                self.toolbar = self.NavigationToolbar2Tk(self.canvas, self.toolbar_frame)
                self.toolbar.update()
                
                # Layout
                self.toolbar_frame.pack(side=tk.TOP, fill=tk.X)
                self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
                
                # Setup event handling
                self._setup_event_handling()
                
                self.logger.debug("Matplotlib backend setup complete with GUI components")
    
    def _setup_event_handling(self):
        """Setup event handling for zoom/pan detection."""
        # Only set up events if we have a canvas (which requires a parent_widget)
        if hasattr(self, 'canvas') and self.canvas is not None:
            # Connect to matplotlib events
            self.canvas.mpl_connect('button_release_event', self._on_navigation_event)
            self.canvas.mpl_connect('key_release_event', self._on_navigation_event)
            self.canvas.mpl_connect('scroll_event', self._on_navigation_event)
            
            # Hook toolbar methods
            self._hook_toolbar_methods()
        else:
            self.logger.debug("No canvas available - event handling setup skipped (normal for headless backend)")
    
    def _hook_toolbar_methods(self):
        """Hook toolbar methods to detect navigation."""
        # Only hook if we have a toolbar
        if hasattr(self, 'toolbar') and self.toolbar is not None:
            original_methods = {}
            for method_name in ['home', 'back', 'forward', 'zoom', 'pan']:
                if hasattr(self.toolbar, method_name):
                    original_methods[method_name] = getattr(self.toolbar, method_name)
                    wrapped = self._wrap_toolbar_method(original_methods[method_name])
                    setattr(self.toolbar, method_name, wrapped)
        else:
            self.logger.debug("No toolbar available - method hooks skipped")
    
    def _wrap_toolbar_method(self, original_method):
        """Wrap toolbar method to trigger limit checking."""
        def wrapped(*args, **kwargs):
            result = original_method(*args, **kwargs)
            if hasattr(self, 'canvas_widget'):
                self.canvas_widget.after_idle(self._check_axis_limits)
            return result
        return wrapped
    
    def _on_navigation_event(self, event):
        """Handle navigation events."""
        if hasattr(self, 'canvas_widget') and self.canvas_widget is not None:
            self.canvas_widget.after_idle(self._check_axis_limits)
            self.canvas_widget.after(50, self._check_axis_limits)
    
    def _check_axis_limits(self):
        """Check if axis limits changed and notify callback."""
        if not self.zoom_callback:
            return
        
        try:
            axes = self.figure.get_axes()
            if axes:
                ax = axes[0]
                xlim = ax.get_xlim()
                ylim = ax.get_ylim()
                
                # Check if limits changed
                if not hasattr(self, '_last_xlim') or xlim != self._last_xlim or ylim != self._last_ylim:
                    self._last_xlim = xlim
                    self._last_ylim = ylim
                    self.zoom_callback(xlim, ylim)
        except Exception as e:
            self.logger.debug(f"Error checking axis limits: {e}")
    
    def create_plot(self, plot_type: str, data: Dict[str, Any], 
                   config: Optional[Dict[str, Any]] = None) -> PlotResult:
        """Create a matplotlib plot."""
        try:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            config = config or {}
            
            if plot_type == 'track_counts':
                self._plot_track_counts(ax, data, config)
            elif plot_type == 'demo':
                self._plot_demo(ax)
            else:
                raise ValueError(f"Unsupported plot type: {plot_type}")
            
            self.figure.tight_layout()
            
            # Debug logging for canvas availability
            canvas_available = hasattr(self, 'canvas') and self.canvas is not None
            self.logger.debug(f"create_plot: canvas available = {canvas_available}")
            
            if canvas_available:
                self.canvas.draw()
                self.canvas.flush_events()
                self.logger.debug("Plot drawn to canvas successfully")
            else:
                self.logger.debug("No canvas available - plot created in figure only (headless mode)")
            
            # Initialize limit tracking
            self._initialize_limit_tracking()
            
            return PlotResult(success=True, plot_object=self.figure)
            
        except Exception as e:
            self.logger.error(f"Error creating plot: {e}")
            self._show_error_plot(str(e))
            return PlotResult(success=False, error=str(e))
    
    def _plot_track_counts(self, ax, data: Dict[str, Any], config: Dict[str, Any]):
        """Plot track counts."""
        # Handle both old and new data formats
        if 'track_counts' in data:
            # Old format: {'track_counts': {'dataset_name': count}}
            track_data = data['track_counts']
            datasets = list(track_data.keys())
            counts = [track_data[dataset] for dataset in datasets]
        elif 'x' in data and 'y' in data:
            # New format: {'x': ['category1', 'category2'], 'y': [count1, count2]}
            datasets = data['x']
            counts = data['y']
        else:
            raise ValueError("No valid track count data provided")
        
        # Create the bar plot
        bars = ax.bar(datasets, counts, color='skyblue', alpha=0.7)
        
        # Set labels and title
        title = config.get('title', 'Track Counts by Dataset')
        xlabel = config.get('xlabel', 'Dataset')
        ylabel = config.get('ylabel', 'Number of Tracks')
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(counts)*0.01,
                   f'{int(count)}', ha='center', va='bottom', fontsize=10)
        
        # Rotate x-axis labels if needed
        if len(datasets) > 3:
            ax.tick_params(axis='x', rotation=45)
    
    def _plot_demo(self, ax):
        """Create a demo plot."""
        import numpy as np
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        ax.plot(x, y, 'b-', linewidth=2, label='sin(x)')
        ax.set_title('Demo Plot', fontsize=14, fontweight='bold')
        ax.set_xlabel('X', fontsize=12)
        ax.set_ylabel('Y', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()
    
    def _show_error_plot(self, error_message: str):
        """Show an error plot."""
        try:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, f'Error: {error_message}', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12, color='red')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            if hasattr(self, 'canvas'):
                self.canvas.draw()
        except Exception as e:
            self.logger.error(f"Error showing error plot: {e}")
    
    def _initialize_limit_tracking(self):
        """Initialize limit tracking."""
        try:
            axes = self.figure.get_axes()
            if axes:
                ax = axes[0]
                self._last_xlim = ax.get_xlim()
                self._last_ylim = ax.get_ylim()
        except Exception as e:
            self.logger.debug(f"Error initializing limit tracking: {e}")
    
    def set_axis_limits(self, x_range: Optional[Tuple[float, float]] = None,
                       y_range: Optional[Tuple[float, float]] = None) -> bool:
        """Set axis limits."""
        try:
            axes = self.figure.get_axes()
            if axes:
                ax = axes[0]
                if x_range:
                    ax.set_xlim(x_range)
                if y_range:
                    ax.set_ylim(y_range)
                if hasattr(self, 'canvas'):
                    self.canvas.draw()
                return True
        except Exception as e:
            self.logger.error(f"Error setting axis limits: {e}")
        return False
    
    def clear_plot(self) -> bool:
        """Clear the plot."""
        try:
            self.figure.clear()
            if hasattr(self, 'canvas'):
                self.canvas.draw()
            return True
        except Exception as e:
            self.logger.error(f"Error clearing plot: {e}")
            return False
    
    def refresh(self) -> bool:
        """Refresh the plot."""
        try:
            if hasattr(self, 'canvas') and self.canvas is not None:
                self.canvas.draw()
                self.canvas.flush_events()
                return True
            else:
                self.logger.debug("No canvas available for refresh - normal for headless backend")
                return False
        except Exception as e:
            self.logger.error(f"Error refreshing plot: {e}")
            return False
    
    def export_plot(self, filename: str, format: str = 'png') -> bool:
        """Export the plot."""
        try:
            self.figure.savefig(filename, format=format, dpi=300, bbox_inches='tight')
            return True
        except Exception as e:
            self.logger.error(f"Error exporting plot: {e}")
            return False
    
    def get_widget(self):
        """Get the tkinter widget."""
        return getattr(self, 'frame', None)
    
    def get_axis_limits(self) -> Tuple[Optional[Tuple[float, float]], Optional[Tuple[float, float]]]:
        """Get current axis limits."""
        try:
            axes = self.figure.get_axes()
            if axes:
                ax = axes[0]
                return ax.get_xlim(), ax.get_ylim()
        except Exception:
            pass
        return None, None
