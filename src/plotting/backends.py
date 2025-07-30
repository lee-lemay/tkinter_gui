"""
Abstract plot backend interfaces for supporting multiple plotting libraries.

This module defines the abstract interface that must be implemented by all
plot backends (matplotlib, plotly, etc.) to enable drop-in replacement.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, Tuple
import logging
import pandas as pd


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
            
            elif plot_type == 'lat_lon_scatter':
                self._plot_lat_lon_scatter(ax, data, config)
            
            elif plot_type == 'north_east_error':
                self._plot_north_east_error(ax, data, config)
            
            elif plot_type == 'rms_error_3d':
                self._plot_rms_error_3d(ax, data, config)
            
            elif plot_type == 'track_truth_lifetime':
                self._plot_lifetime(ax, data, config)
            
            elif plot_type == 'lat_lon_animation':
                self._plot_animation(ax, data, config)
            
            elif plot_type == 'animation_frame':
                self._plot_animation(ax, data, config)
                #self.create_animation_frame(ax, data, config)
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
    
    def _plot_north_east_error(self, ax, data: Dict[str, Any], config: Dict[str, Any]):
        """Plot North/East error data."""
        error_data = data['error_data']
        
        if not error_data['north_errors'] or not error_data['east_errors']:
            ax.text(0.5, 0.5, 'No error data available',
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12, color='gray')
            return
        
        # Create time array for x-axis
        timestamps = error_data['timestamps']
        time_seconds = [(t - timestamps[0]).total_seconds() for t in timestamps]
        
        # Plot North and East errors
        ax.plot(time_seconds, error_data['north_errors'], 'b-', label='North Error', linewidth=2)
        ax.plot(time_seconds, error_data['east_errors'], 'r-', label='East Error', linewidth=2)
        
        # Styling
        ax.set_title('North/East Position Errors', fontsize=14, fontweight='bold')
        ax.set_xlabel('Time (seconds)', fontsize=12)
        ax.set_ylabel('Error (meters)', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.axhline(y=0, color='k', linestyle='--', alpha=0.5)
    
    def _plot_rms_error_3d(self, ax, data: Dict[str, Any], config: Dict[str, Any]):
        """Plot 3D RMS error data with time on X-axis and error on Y-axis."""
        rms_data = data['rms_data']
        
        if not rms_data['rms_error_3d']:
            ax.text(0.5, 0.5, 'No RMS error data available',
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12, color='gray')
            return
        
        # Convert timestamps to relative time (seconds from start)
        import numpy as np
        import pandas as pd
        
        timestamps = pd.to_datetime(rms_data['timestamps'])
        start_time = timestamps.min()
        relative_times = [(t - start_time).total_seconds() for t in timestamps]
        
        # Create line plot with time on X-axis and RMS error on Y-axis
        ax.plot(relative_times, rms_data['rms_error_3d'], 
                'o-', color='blue', linewidth=2, markersize=4, alpha=0.7)
        
        # Add trend line if there are enough points
        if len(relative_times) > 1:
            z = np.polyfit(relative_times, rms_data['rms_error_3d'], 1)
            p = np.poly1d(z)
            ax.plot(relative_times, p(relative_times), 
                   '--', color='red', alpha=0.8, linewidth=1, label='Trend')
            ax.legend()
        
        # Styling
        ax.set_title('3D RMS Position Error vs Time', fontsize=14, fontweight='bold')
        ax.set_xlabel('Time (seconds)', fontsize=12)
        ax.set_ylabel('RMS Error (meters)', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Format y-axis to show error values nicely
        from matplotlib.ticker import FuncFormatter
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:.2f}'))
    
    
    def _plot_lifetime(self, ax, data: Dict[str, Any], config: Dict[str, Any]):
        """Plot track/truth lifetime data."""
        lifetime_data = data['lifetime_data']
        
        if not lifetime_data['track_lifetimes'] and not lifetime_data['truth_lifetimes']:
            ax.text(0.5, 0.5, 'No lifetime data available',
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12, color='gray')
            return
        
        # Prepare data for histogram
        data_to_plot = []
        labels = []
        
        if lifetime_data['track_lifetimes']:
            data_to_plot.append(lifetime_data['track_lifetimes'])
            labels.append('Tracks')
        
        if lifetime_data['truth_lifetimes']:
            data_to_plot.append(lifetime_data['truth_lifetimes'])
            labels.append('Truth')
        
        # Create histogram
        ax.hist(data_to_plot, bins=20, alpha=0.7, label=labels, edgecolor='black')
        
        # Styling
        ax.set_title('Track/Truth Lifetime Distribution', fontsize=14, fontweight='bold')
        ax.set_xlabel('Lifetime (seconds)', fontsize=12)
        ax.set_ylabel('Count', fontsize=12)
        ax.grid(True, alpha=0.3)
        if len(labels) > 1:
            ax.legend()

    def _plot_lat_lon_scatter(self, ax, data: Dict[str, Any], config: Dict[str, Any]):
        """Plot latitude/longitude scatter plot."""
        try:
            # Check if 'lat_lon_data' is in the data dataframe
            if 'lat_lon_data' in data:
                lat_lon_data = data['lat_lon_data']
                # Check if 'tracks' is in lat_lon_data
                if 'tracks' in lat_lon_data:
                    tracks_df = lat_lon_data['tracks']
                    if isinstance(tracks_df, pd.DataFrame):
                        # iterate through the track ids and add lat lon for each of them to the plot
                        for track_id, track_data in tracks_df.groupby('track_id'):
                            lat = track_data['lat'].values
                            lon = track_data['lon'].values
                            if len(lat) != len(lon):
                                raise ValueError(f"Track {track_id} has mismatched lat/lon lengths")
                            ax.scatter(lon, lat, s=10, alpha=0.5, label=f'Track {track_id}')
                # Check if 'truth' is in lat_lon_data
                if 'truth' in lat_lon_data:
                    truth_df = lat_lon_data['truth']
                    if isinstance(truth_df, pd.DataFrame):
                        for truth_id, truth_data in truth_df.groupby('id'):
                            lat = truth_data['lat'].values
                            lon = truth_data['lon'].values
                            if len(lat) != len(lon):
                                raise ValueError("Truth data has mismatched lat/lon lengths")
                            ax.scatter(lon, lat, s=10, alpha=0.5, c='red', label='Truth {truth_id}')
            
            # Set axis labels and title
            ax.set_xlabel('Longitude', fontsize=12)
            ax.set_ylabel('Latitude', fontsize=12)
            ax.set_title(config.get('title', 'Geospatial Scatter Plot'), fontsize=14, fontweight='bold')
            
            # Set grid if specified
            if config.get('show_grid', True):
                ax.grid(True, alpha=0.3)
            
        except Exception as e:
            self.logger.error(f"Error plotting lat/lon scatter: {e}")
    
    def _plot_track_counts(self, ax, data: Dict[str, Any], config: Dict[str, Any]):
        """Plot track counts."""

        if not 'track_counts' in data:
            ax.text(0.5, 0.5, 'No track count data available',
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12, color='gray')
            return
        
        track_counts = data['track_counts']
        
        # Prepare data
        datasets = list(track_counts.keys())
        counts = list(track_counts.values())
        
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
    
    def _plot_animation(self, ax, data: Dict[str, Any], config: Dict[str, Any]):
        """Plot animated lat/lon data (static frame for now)."""
        animation_data = data['animation_data']
        
        if ((animation_data['tracks'] is None or animation_data['tracks'].empty) and 
             (animation_data['truth'] is None or animation_data['truth'].empty)):
            ax.text(0.5, 0.5, 'No animation data available',
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12, color='gray')
            return
                
        # Plot track trajectories
        if animation_data['tracks'] is not None and not animation_data['tracks'].empty:
            tracks_df = animation_data['tracks']
            for track_id in tracks_df['track_id'].unique():
                track_data = tracks_df[tracks_df['track_id'] == track_id]
                ax.plot(track_data['lon'], track_data['lat'], 
                       'b-', alpha=0.6, linewidth=2, label='Track Trajectory' if track_id == tracks_df['track_id'].iloc[0] else "")
                # Mark start and end points
                ax.scatter(track_data['lon'].iloc[0], track_data['lat'].iloc[0], 
                          c='green', s=100, marker='o', label='Start' if track_id == tracks_df['track_id'].iloc[0] else "")
                ax.scatter(track_data['lon'].iloc[-1], track_data['lat'].iloc[-1], 
                          c='red', s=100, marker='s', label='End' if track_id == tracks_df['track_id'].iloc[0] else "")
        
        # Plot truth trajectories
        if animation_data['truth'] is not None and not animation_data['truth'].empty:
            truth_df = animation_data['truth']
            for truth_id in truth_df['id'].unique():
                truth_data = truth_df[truth_df['id'] == truth_id]
                ax.plot(truth_data['lon'], truth_data['lat'], 
                       'r--', alpha=0.6, linewidth=2, label='Truth Trajectory' if truth_id == truth_df['id'].iloc[0] else "")
        
        # Apply coordinate ranges if provided
        if 'lat_range' in data and data['lat_range'] is not None:
            lat_min, lat_max = data['lat_range']
            ax.set_ylim(lat_min, lat_max)
        
        if 'lon_range' in data and data['lon_range'] is not None:
            lon_min, lon_max = data['lon_range']
            ax.set_xlim(lon_min, lon_max)
        
        # Styling
        ax.set_title(config['title'], fontsize=14, fontweight='bold')
        ax.set_xlabel('Longitude', fontsize=12)
        ax.set_ylabel('Latitude', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_aspect('equal', adjustable='box')
        
        # Fix axis formatting for geographic coordinates (same as geospatial plot)
        # Disable scientific notation and offset formatting
        ax.ticklabel_format(style='plain', useOffset=False)
    
        # For very small coordinate ranges, use fixed decimal places
        from matplotlib.ticker import FixedFormatter, FixedLocator
        import numpy as np
        
        # Get current axis limits
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        
        # If the range is small (typical for local geographic data), format nicely
        if abs(xlim[1] - xlim[0]) < 1.0:  # Less than 1 degree
            # Create custom tick formatters for longitude
            x_ticks = np.linspace(xlim[0], xlim[1], 6)
            ax.set_xticks(x_ticks)
            ax.set_xticklabels([f'{tick:.4f}' for tick in x_ticks])
        
        if abs(ylim[1] - ylim[0]) < 1.0:  # Less than 1 degree
            # Create custom tick formatters for latitude
            y_ticks = np.linspace(ylim[0], ylim[1], 6)
            ax.set_yticks(y_ticks)
            ax.set_yticklabels([f'{tick:.4f}' for tick in y_ticks])
    
    def create_animation_frame(self, ax, data: Dict[str, Any], config: Dict[str, Any]):
        """Create an animation frame showing data up to current timestamp."""
        try:
            filtered_data   = data
            current_frame   = config["current_frame"]
            total_frames      = config["total_frames"]
            
            # Clear the current plot and create new axes
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            # Get coordinate ranges
            lat_range = filtered_data.get('lat_range')
            lon_range = filtered_data.get('lon_range')
            current_time = filtered_data.get('current_time')
            
            # Plot tracks data up to current time
            if filtered_data.get('tracks') is not None and len(filtered_data['tracks']) > 0:
                tracks_df = filtered_data['tracks']
                for track_id in tracks_df['track_id'].unique():
                    track_data = tracks_df[tracks_df['track_id'] == track_id]
                    if len(track_data) > 0:
                        # Plot trajectory path
                        ax.plot(track_data['lon'], track_data['lat'], 
                               'b-', alpha=0.7, linewidth=2, 
                               label='Track' if track_id == tracks_df['track_id'].iloc[0] else "")
                        # Mark current position
                        current_pos = track_data.iloc[-1]
                        ax.scatter(current_pos['lon'], current_pos['lat'], 
                                  c='blue', s=100, marker='o', zorder=5)
            
            # Plot truth data up to current time
            if filtered_data.get('truth') is not None and len(filtered_data['truth']) > 0:
                truth_df = filtered_data['truth']
                for truth_id in truth_df['id'].unique():
                    truth_data = truth_df[truth_df['id'] == truth_id]
                    if len(truth_data) > 0:
                        # Plot trajectory path
                        ax.plot(truth_data['lon'], truth_data['lat'], 
                               'r--', alpha=0.7, linewidth=2,
                               label='Truth' if truth_id == truth_df['id'].iloc[0] else "")
                        # Mark current position
                        current_pos = truth_data.iloc[-1]
                        ax.scatter(current_pos['lon'], current_pos['lat'], 
                                  c='red', s=100, marker='s', zorder=5)
            
            # Set coordinate ranges
            if lat_range:
                ax.set_ylim(lat_range)
            if lon_range:
                ax.set_xlim(lon_range)
            
            # Styling and labels
            if current_time:
                title = f'Animation - Frame {current_frame + 1}/{total_frames} - Time: {current_time}'
            else:
                title = f'Animation - Frame {current_frame + 1}/{total_frames}'
                
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_xlabel('Longitude', fontsize=12)
            ax.set_ylabel('Latitude', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.set_aspect('equal', adjustable='box')
            
            # Add legend if there's data
            if (filtered_data.get('tracks') is not None and len(filtered_data['tracks']) > 0) or \
               (filtered_data.get('truth') is not None and len(filtered_data['truth']) > 0):
                ax.legend()
            
            # Fix axis formatting
            ax.ticklabel_format(style='plain', useOffset=False)
            
            # Format ticks for small coordinate ranges
            if lat_range and abs(lat_range[1] - lat_range[0]) < 1.0:
                import numpy as np
                y_ticks = np.linspace(lat_range[0], lat_range[1], 6)
                ax.set_yticks(y_ticks)
                ax.set_yticklabels([f'{tick:.4f}' for tick in y_ticks])
                
            if lon_range and abs(lon_range[1] - lon_range[0]) < 1.0:
                import numpy as np
                x_ticks = np.linspace(lon_range[0], lon_range[1], 6)
                ax.set_xticks(x_ticks)
                ax.set_xticklabels([f'{tick:.4f}' for tick in x_ticks])
            
            # Update canvas
            self.figure.tight_layout()
            self.canvas.draw()
            self.canvas.flush_events()  # Ensure all drawing events are processed
            
            # Initialize limit tracking for animation frame
            self._initialize_limit_tracking()
            
        except Exception as e:
            self.logger.error(f"Error creating animation frame: {e}")
            self._show_error_plot(f"Animation Error: {str(e)}")
    
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
