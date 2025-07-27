"""
Matplotlib Canvas Component

This module provides a reusable matplotlib canvas component that can be
embedded in tkinter applications with navigation toolbar support.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging
from typing import Optional, Any, Dict, List
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np


class MatplotlibCanvas:
    """
    A reusable matplotlib canvas component for tkinter applications.
    
    Provides matplotlib figure embedding with navigation toolbar and export functionality.
    """
    
    def __init__(self, parent: tk.Widget, figure_size: tuple = (8, 6)):
        """
        Initialize the matplotlib canvas.
        
        Args:
            parent: The parent tkinter widget
            figure_size: Tuple of (width, height) for the figure in inches
        """
        self.parent = parent
        self.logger = logging.getLogger(__name__)
        
        # Create matplotlib figure
        self.figure = Figure(figsize=figure_size, dpi=100)
        self.figure.patch.set_facecolor('white')
        
        # Create the main frame
        self.frame = ttk.Frame(parent)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        
        # Create toolbar frame and navigation toolbar
        self.toolbar_frame = ttk.Frame(self.frame)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbar_frame)
        self.toolbar.update()
        
        # Hook into navigation toolbar methods to ensure we catch all navigation events
        self._setup_toolbar_hooks()
        
        # Zoom/pan event callback
        self.zoom_callback = None
        
        # Connect to multiple matplotlib events for comprehensive navigation detection
        self.canvas.mpl_connect('button_release_event', self._on_navigation_event)
        self.canvas.mpl_connect('key_release_event', self._on_navigation_event)
        self.canvas.mpl_connect('scroll_event', self._on_navigation_event)
        
        # Note: xlim_changed and ylim_changed are not valid mpl events
        # We rely on toolbar hooks and user interaction events instead
        
        # Track last known limits to prevent duplicate updates
        self.last_xlim = None
        self.last_ylim = None
        
        # Create custom toolbar with export button
        self._create_custom_toolbar()
        
        # Layout
        self._setup_layout()
        
        # Initialize with empty plot
        self.clear_plot()
        
        self.logger.debug("Matplotlib canvas initialized")
    
    def _setup_layout(self):
        """Setup the layout of canvas and toolbar."""
        # Pack toolbar at top
        self.toolbar_frame.pack(side=tk.TOP, fill=tk.X)
        
        # Pack canvas below toolbar
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Configure frame to expand
        self.frame.pack_propagate(False)
    
    def _create_custom_toolbar(self):
        """Create custom toolbar buttons."""
        # Add separator
        separator = ttk.Separator(self.toolbar_frame, orient='vertical')
        separator.pack(side=tk.LEFT, padx=5, fill=tk.Y)
    
    def _setup_toolbar_hooks(self):
        """Setup hooks into navigation toolbar methods to catch all navigation."""
        if not hasattr(self, 'toolbar') or not self.toolbar:
            return
            
        # Store original toolbar methods
        self._original_home = getattr(self.toolbar, 'home', None)
        self._original_back = getattr(self.toolbar, 'back', None)
        self._original_forward = getattr(self.toolbar, 'forward', None)
        self._original_zoom = getattr(self.toolbar, 'zoom', None)
        self._original_pan = getattr(self.toolbar, 'pan', None)
        
        # Replace with wrapped versions
        if self._original_home:
            self.toolbar.home = self._wrap_toolbar_method(self._original_home)
        if self._original_back:
            self.toolbar.back = self._wrap_toolbar_method(self._original_back)
        if self._original_forward:
            self.toolbar.forward = self._wrap_toolbar_method(self._original_forward)
        if self._original_zoom:
            self.toolbar.zoom = self._wrap_toolbar_method(self._original_zoom)
        if self._original_pan:
            self.toolbar.pan = self._wrap_toolbar_method(self._original_pan)
    
    def _wrap_toolbar_method(self, original_method):
        """Wrap a toolbar method to trigger limit checking."""
        def wrapped_method(*args, **kwargs):
            # Call original method
            result = original_method(*args, **kwargs)
            # Schedule limit check
            if hasattr(self, 'canvas_widget') and self.canvas_widget:
                self.canvas_widget.after_idle(self._check_axes_limits)
            return result
        return wrapped_method
    
    def get_frame(self) -> ttk.Frame:
        """Get the main frame containing the canvas."""
        return self.frame
    
    def get_figure(self) -> Figure:
        """Get the matplotlib figure object."""
        return self.figure
    
    def set_zoom_callback(self, callback):
        """Set callback function to be called when zoom/pan events occur."""
        self.zoom_callback = callback
    
    def _on_navigation_event(self, event):
        """Handle general navigation events (button, key, scroll)."""
        # Use a small delay to ensure axes have been updated
        if hasattr(self, 'canvas_widget') and self.canvas_widget:
            # Check immediately and also after a short delay to catch all updates
            self.canvas_widget.after_idle(self._check_axes_limits)
            self.canvas_widget.after(50, self._check_axes_limits)  # Additional check after 50ms
    
    def _check_axes_limits(self):
        """Check if axes limits have changed and notify callback."""
        if not self.zoom_callback:
            return
            
        try:
            # Get the current axes (assumes single subplot)
            axes = self.figure.get_axes()
            if not axes:
                return
                
            ax = axes[0]  # Get first (and typically only) axes
            
            # Get current limits
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            
            # Check if limits have actually changed
            if (xlim != self.last_xlim or ylim != self.last_ylim):
                self.last_xlim = xlim
                self.last_ylim = ylim
                
                # Notify callback with new ranges
                self.zoom_callback(xlim, ylim)
                
        except Exception as e:
            self.logger.debug(f"Error checking axes limits: {e}")
    
    def _initialize_limit_tracking(self):
        """Initialize limit tracking for a new plot."""
        try:
            axes = self.figure.get_axes()
            if axes:
                ax = axes[0]
                self.last_xlim = ax.get_xlim()
                self.last_ylim = ax.get_ylim()
                self.logger.debug(f"Initialized limit tracking: xlim={self.last_xlim}, ylim={self.last_ylim}")
        except Exception as e:
            self.logger.debug(f"Error initializing limit tracking: {e}")
    
    def _on_zoom_pan(self, event):
        """Legacy method - redirect to new handler."""
        self._on_navigation_event(event)
    
    def clear_plot(self):
        """Clear the current plot and show empty axes."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, 'No plot selected\\nSelect a dataset and plot type to begin',
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=12, color='gray')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xticks([])
        ax.set_yticks([])
        self.canvas.draw()
    
    def create_simple_plot(self, data: Dict[str, Any], plot_config: Optional[Dict[str, Any]] = None):
        """
        Create a simple plot based on provided data.
        
        Args:
            data: Dictionary containing plot data
            plot_config: Optional plot configuration
        """
        try:
            self.figure.clear()
            
            if plot_config is None:
                plot_config = {}
            
            # Create subplot
            ax = self.figure.add_subplot(111)
            
            # Determine plot type based on data
            if 'track_counts' in data:
                self._plot_track_counts(ax, data, plot_config)
            elif 'lat_lon_data' in data:
                self._plot_lat_lon(ax, data, plot_config)
            elif 'error_data' in data:
                self._plot_north_east_error(ax, data, plot_config)
            elif 'rms_data' in data:
                self._plot_rms_error_3d(ax, data, plot_config)
            elif 'lifetime_data' in data:
                self._plot_lifetime(ax, data, plot_config)
            elif 'animation_data' in data:
                self._plot_animation(ax, data, plot_config)
            else:
                # Default demo plot
                self._plot_demo(ax)
            
            # Apply common styling
            self.figure.tight_layout()
            self.canvas.draw()
            
            # Initialize limit tracking for new plot
            self._initialize_limit_tracking()
            
            self.logger.debug("Plot created successfully")
            
        except Exception as e:
            self.logger.error(f"Error creating plot: {e}")
            self._show_error_plot(str(e))
    
    def _plot_track_counts(self, ax, data: Dict[str, Any], config: Dict[str, Any]):
        """Plot track counts for datasets."""
        track_counts = data['track_counts']
        
        if not track_counts:
            ax.text(0.5, 0.5, 'No track count data available',
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12, color='gray')
            return
        
        # Prepare data
        datasets = list(track_counts.keys())
        counts = list(track_counts.values())
        
        # Create bar plot
        bars = ax.bar(datasets, counts, color='steelblue', alpha=0.7)
        
        # Styling
        ax.set_title('Track Counts by Dataset', fontsize=14, fontweight='bold')
        ax.set_xlabel('Dataset', fontsize=12)
        ax.set_ylabel('Number of Tracks', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(counts) * 0.01,
                   f'{count}', ha='center', va='bottom', fontsize=10)
        
        # Rotate x-axis labels if there are many datasets
        if len(datasets) > 3:
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    
    def _plot_lat_lon(self, ax, data: Dict[str, Any], config: Dict[str, Any]):
        """Plot latitude/longitude data."""
        lat_lon_data = data['lat_lon_data']
        
        if not lat_lon_data:
            ax.text(0.5, 0.5, 'No lat/lon data available',
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12, color='gray')
            return
        
        # Plot tracks if available
        if 'tracks' in lat_lon_data and not lat_lon_data['tracks'].empty:
            tracks_df = lat_lon_data['tracks']
            ax.scatter(tracks_df['lon'], tracks_df['lat'], 
                      c='blue', alpha=0.6, s=20, label='Tracks')
        
        # Plot truth if available
        if 'truth' in lat_lon_data and not lat_lon_data['truth'].empty:
            truth_df = lat_lon_data['truth']
            ax.scatter(truth_df['lon'], truth_df['lat'], 
                      c='red', alpha=0.6, s=20, marker='^', label='Truth')
        
        # Apply coordinate ranges if provided
        if 'lat_range' in data:
            lat_min, lat_max = data['lat_range']
            ax.set_ylim(lat_min, lat_max)
        
        if 'lon_range' in data:
            lon_min, lon_max = data['lon_range']
            ax.set_xlim(lon_min, lon_max)
        
        # Styling
        ax.set_title('Latitude vs Longitude', fontsize=14, fontweight='bold')
        ax.set_xlabel('Longitude', fontsize=12)
        ax.set_ylabel('Latitude', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()
    
        # Fix axis formatting for geographic coordinates
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
        
        # Equal aspect ratio for geographic data
        ax.set_aspect('equal', adjustable='box')
    
    def _plot_demo(self, ax):
        """Create a demo plot when no specific data is provided."""
        # Generate sample data
        x = np.linspace(0, 10, 100)
        y1 = np.sin(x)
        y2 = np.cos(x)
        
        # Create plot
        ax.plot(x, y1, 'b-', label='sin(x)', linewidth=2)
        ax.plot(x, y2, 'r--', label='cos(x)', linewidth=2)
        
        # Styling
        ax.set_title('Demo Plot - Sine and Cosine Functions', fontsize=14, fontweight='bold')
        ax.set_xlabel('X Value', fontsize=12)
        ax.set_ylabel('Y Value', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()
    
    def _show_error_plot(self, error_message: str):
        """Show an error message in the plot area."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, f'Error creating plot:\\n{error_message}',
               horizontalalignment='center', verticalalignment='center',
               transform=ax.transAxes, fontsize=12, color='red')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xticks([])
        ax.set_yticks([])
        self.canvas.draw()
    
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
        
        if not rms_data['rms_error']:
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
        ax.plot(relative_times, rms_data['rms_error'], 
                'o-', color='blue', linewidth=2, markersize=4, alpha=0.7)
        
        # Add trend line if there are enough points
        if len(relative_times) > 1:
            z = np.polyfit(relative_times, rms_data['rms_error'], 1)
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
    
    def _plot_animation(self, ax, data: Dict[str, Any], config: Dict[str, Any]):
        """Plot animated lat/lon data (static frame for now)."""
        animation_data = data['animation_data']
        
        if (len(animation_data['tracks']) == 0 and len(animation_data['truth']) == 0):
            ax.text(0.5, 0.5, 'No animation data available',
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12, color='gray')
            return
        
        # For Phase 5, show static plot with trajectory paths
        # (Animation controls will be added in enhanced version)
        
        # Plot track trajectories
        if len(animation_data['tracks']) > 0:
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
        if len(animation_data['truth']) > 0:
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
        ax.set_title('Trajectory Animation (Static View)', fontsize=14, fontweight='bold')
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
    
    def create_animation_frame(self, filtered_data: Dict[str, Any], current_frame: int, max_frames: int):
        """Create an animation frame showing data up to current timestamp."""
        try:
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
                title = f'Animation - Frame {current_frame + 1}/{max_frames} - Time: {current_time}'
            else:
                title = f'Animation - Frame {current_frame + 1}/{max_frames}'
                
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
    
    def export_plot(self):
        """Export the current plot to a file."""
        try:
            # Get file path from user
            file_path = filedialog.asksaveasfilename(
                title="Export Plot",
                defaultextension=".png",
                filetypes=[
                    ("PNG files", "*.png"),
                    ("PDF files", "*.pdf"),
                    ("SVG files", "*.svg"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                # Save the figure
                self.figure.savefig(file_path, dpi=300, bbox_inches='tight')
                self.logger.info(f"Plot exported to: {file_path}")
                messagebox.showinfo("Export Successful", f"Plot saved to:\\n{file_path}")
            
        except Exception as e:
            self.logger.error(f"Error exporting plot: {e}")
            messagebox.showerror("Export Error", f"Failed to export plot:\\n{e}")
    
    def refresh(self):
        """Refresh the canvas display."""
        self.canvas.draw()
    
    def configure_size(self, width: int, height: int):
        """Configure the canvas size."""
        self.canvas_widget.configure(width=width, height=height)
        self.refresh()
