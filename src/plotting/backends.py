"""
Abstract plot backend interfaces for supporting multiple plotting libraries.

This module defines the abstract interface that must be implemented by all
plot backends (matplotlib, plotly, etc.) to enable drop-in replacement.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, Tuple
import logging
import pandas as pd

from src import data


class PlotResult:
    """Represents the result of a plot operation."""
    
    def __init__(self, success: bool, plot_object: Any = None, error: Optional[str] = None):
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
                config['plot_mode'] = 'scatter'
                self._plot_geospatial_data(ax, data, config)

            elif plot_type == 'lat_lon_animation':
                config['plot_mode'] = 'trajectory'
                self._plot_geospatial_data(ax, data, config)

            elif plot_type == 'animation_frame':
                config['plot_mode'] = 'trajectory'
                self._plot_geospatial_data(ax, data, config)
            
            elif plot_type == 'generic_xy':
                self._plot_generic_xy(ax, data, config)
            elif plot_type == 'histogram':
                self._plot_histogram(ax, data, config)
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
    
            
    def _plot_tracks_data(self, ax, tracks_df: pd.DataFrame, plot_mode: str, config: Dict[str, Any]):
        """Plot tracks data in specified mode."""
        
        if plot_mode == 'scatter':
            # Scatter mode: plot individual points grouped by track ID
            for track_id, track_data in tracks_df.groupby('track_id'):
                lat = track_data['lat'].values
                lon = track_data['lon'].values
                if len(lat) != len(lon):
                    raise ValueError(f"Track {track_id} has mismatched lat/lon lengths")
                ax.scatter(lon, lat, s=10, alpha=0.5, label=f'Track {track_id}')
        
        elif plot_mode == 'trajectory':
            # Trajectory mode: plot connected lines with markers
            for track_id in tracks_df['track_id'].unique():
                track_data = tracks_df[tracks_df['track_id'] == track_id]
                ax.plot(track_data['lon'], track_data['lat'], 
                    'b-', alpha=0.6, linewidth=2, 
                    label='Track Trajectory' if track_id == tracks_df['track_id'].iloc[0] else "")
                
                # Mark start and end points
                ax.scatter(track_data['lon'].iloc[0], track_data['lat'].iloc[0], 
                        c='green', s=100, marker='o', 
                        label='Start' if track_id == tracks_df['track_id'].iloc[0] else "")
                ax.scatter(track_data['lon'].iloc[-1], track_data['lat'].iloc[-1], 
                        c='red', s=100, marker='s', 
                        label='End' if track_id == tracks_df['track_id'].iloc[0] else "")
                
    def _plot_truth_data(self, ax, truth_df: pd.DataFrame, plot_mode: str, config: Dict[str, Any]):
        """Plot truth data in specified mode."""
        
        if plot_mode == 'scatter':
            # Scatter mode: plot individual points grouped by truth ID
            for truth_id, truth_data in truth_df.groupby('id'):
                lat = truth_data['lat'].values
                lon = truth_data['lon'].values
                if len(lat) != len(lon):
                    raise ValueError("Truth data has mismatched lat/lon lengths")
                ax.scatter(lon, lat, s=10, alpha=0.5, c='red', label=f'Truth {truth_id}')
        
        elif plot_mode == 'trajectory':
            # Trajectory mode: plot connected lines
            for truth_id in truth_df['id'].unique():
                truth_data = truth_df[truth_df['id'] == truth_id]
                ax.plot(truth_data['lon'], truth_data['lat'], 
                    'r--', alpha=0.6, linewidth=2, 
                    label='Truth Trajectory' if truth_id == truth_df['id'].iloc[0] else "")
    
    def _apply_geospatial_styling(self, ax, config: Dict[str, Any]):
        """Apply common styling to geospatial plots."""
        
        # Set axis labels and title
        ax.set_xlabel('Longitude', fontsize=12)
        ax.set_ylabel('Latitude', fontsize=12)
        ax.set_title(config.get('title', 'Geospatial Plot'), fontsize=14, fontweight='bold')
        
        # Set grid if specified
        if config.get('show_grid', True):
            ax.grid(True, alpha=0.3)
        
        # Add legend
        ax.legend()
        
        # Set equal aspect ratio for geographic data
        ax.set_aspect('equal', adjustable='box')
        
        # Fix axis formatting for geographic coordinates
        ax.ticklabel_format(style='plain', useOffset=False)
        
        # Format ticks for small coordinate ranges
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        
        if abs(xlim[1] - xlim[0]) < 1.0:  # Less than 1 degree
            import numpy as np
            x_ticks = np.linspace(xlim[0], xlim[1], 6)
            ax.set_xticks(x_ticks)
            ax.set_xticklabels([f'{tick:.4f}' for tick in x_ticks])
        
        if abs(ylim[1] - ylim[0]) < 1.0:  # Less than 1 degree
            import numpy as np
            y_ticks = np.linspace(ylim[0], ylim[1], 6)
            ax.set_yticks(y_ticks)
            ax.set_yticklabels([f'{tick:.4f}' for tick in y_ticks])

    def _plot_geospatial_data(self, ax, data: Dict[str, Any], config: Dict[str, Any]):
        """Plot geospatial data in either scatter or trajectory mode."""
        
        # Extract data based on structure
        tracks_df = data.get('tracks_df', None)
        truth_df = data.get('truth_df', None)
        
        # Check for empty data
        if ((tracks_df is None or tracks_df.empty) and 
            (truth_df is None or truth_df.empty)):
            ax.text(0.5, 0.5, 'No geospatial data available',
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=12, color='gray')
            return
        
        # Plot tracks    
        # Determine plot mode from config or data structure
        plot_mode = config.get('tracks_plot_mode', 'auto')
        
        # Auto-detect mode if not specified
        if plot_mode == 'auto':
            if 'animation_data' in data:
                plot_mode = 'trajectory'
            else:
                plot_mode = 'scatter'
        if tracks_df is not None and not tracks_df.empty:
            self._plot_tracks_data(ax, tracks_df, plot_mode, config)
        
        # Plot truth
        # Determine plot mode from config or data structure
        plot_mode = config.get('truth_plot_mode', 'auto')
        
        # Auto-detect mode if not specified
        if plot_mode == 'auto':
            if 'animation_data' in data:
                plot_mode = 'trajectory'
            else:
                plot_mode = 'scatter'
        if truth_df is not None and not truth_df.empty:
            self._plot_truth_data(ax, truth_df, plot_mode, config)
        
        # Check for ranges in data (animation format)
        lat_range = data.get('lat_range', None)
        lon_range = data.get('lon_range', None)
        
        # Apply ranges if found
        if lat_range is not None:
            ax.set_ylim(lat_range)
        
        if lon_range is not None:
            ax.set_xlim(lon_range)
        
        # Apply styling
        self._apply_geospatial_styling(ax, config)

    
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

    def _plot_generic_xy(self, ax, data: Dict[str, Any], config: Dict[str, Any]):
        """Render generic XY series passed from PlotManager."""
        series = data.get('series', {})
        if not series or 'x' not in series:
            ax.text(0.5, 0.5, 'No data', ha='center', va='center', transform=ax.transAxes, color='gray')
            return

        x = series['x']
        default_style = (config or {}).get('style', 'line')
        series_styles = (data or {}).get('series_styles') or (config or {}).get('series_styles') or {}

        for key, values in series.items():
            if key == 'x':
                continue
            sconf       = series_styles.get(key, {}) if isinstance(series_styles, dict) else {}
            ptype       = sconf.get('type', default_style)  # 'line' | 'scatter'
            color       = sconf.get('color')
            marker      = sconf.get('marker')  # e.g., 'o', '^', 's'
            linestyle   = sconf.get('linestyle', '-') if ptype == 'line' else 'None'
            linewidth   = sconf.get('linewidth', 2)
            alpha       = sconf.get('alpha', 0.9)
            label       = sconf.get('label', key)
            markersize  = sconf.get('markersize', 36 if ptype == 'scatter' else 6)

            if ptype == 'scatter':
                ax.scatter(x, values, s=markersize, alpha=alpha, label=label, c=color, marker=marker)
            else:
                ax.plot(x, values, linestyle, linewidth=linewidth, alpha=alpha, label=label, color=color, marker=marker)

        # Titles and labels
        ax.set_title((config or {}).get('title', data.get('title', 'XY Plot')), fontsize=14, fontweight='bold')
        ax.set_xlabel((config or {}).get('xlabel', data.get('xlabel', 'X')), fontsize=12)
        ax.set_ylabel((config or {}).get('ylabel', data.get('ylabel', 'Y')), fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()
        # Custom y ticks (e.g., track lifetime) if provided
        y_ticks_meta = (config or {}).get('y_ticks') or data.get('y_ticks')
        if isinstance(y_ticks_meta, dict) and 'positions' in y_ticks_meta and 'labels' in y_ticks_meta:
            try:
                positions = y_ticks_meta['positions']
                labels = y_ticks_meta['labels']
                ax.set_yticks(positions)
                ax.set_yticklabels(labels)
                pad = y_ticks_meta.get('padding', 0)
                if positions:
                    ymin = min(positions) - pad
                    ymax = max(positions) + pad
                    ax.set_ylim(ymin, ymax)
            except Exception as e:
                self.logger.debug(f"Custom y ticks failed: {e}")

    def _plot_histogram(self, ax, data: Dict[str, Any], config: Dict[str, Any]):
        import numpy as np
        histograms = data.get('histograms') or []
        overlays = data.get('overlays') or []
        if not histograms:
            ax.text(0.5, 0.5, 'No histogram data', ha='center', va='center', transform=ax.transAxes, color='gray')
            return
        global_ymax = 0
        # Draw each histogram in order
        for h in histograms:
            values = np.array(h.get('values') or [], dtype=float)
            if values.size == 0:
                continue
            mean = h.get('mean') or 0.0
            std = h.get('std') or 1.0
            if std == 0: std = 1.0
            edges = h.get('edges')
            if not edges:
                edges = [mean + k*std for k in (-3,-2,-1,0,1,2,3)]
            counts, _ = np.histogram(values, bins=edges)
            style = h.get('style', {})
            # Sigma bands unless disabled
            if style.get('sigma_bands', True):
                bands = h.get('bands')
                if not bands:
                    # Default: fixed 1σ-wide bands around mean, independent of bin edges
                    # Use up to ±3σ (classic). Colors mirror previous scheme.
                    bands = [
                        (mean-3*std, mean-2*std, (1.0,0.6,0.6,0.5)),
                        (mean-2*std, mean-1*std, (0.6,0.8,1.0,0.5)),
                        (mean-1*std, mean,         (0.7,1.0,0.7,0.5)),
                        (mean,        mean+1*std, (0.7,1.0,0.7,0.5)),
                        (mean+1*std, mean+2*std, (0.6,0.8,1.0,0.5)),
                        (mean+2*std, mean+3*std, (1.0,0.6,0.6,0.5)),
                    ]
                for left, right, color in bands:
                    if left < right:
                        ax.axvspan(left, right, facecolor=color, edgecolor='none', zorder=0)
            # Outline bars or filled
            outline_only = style.get('outline_only', True)
            bar_color = style.get('color', 'black')
            lw = style.get('linewidth', 1.5)
            for i in range(len(counts)):
                left = edges[i]; right = edges[i+1]; height = counts[i]
                global_ymax = max(global_ymax, height)
                if outline_only:
                    ax.plot([left,left,right,right,left],[0,height,height,0,0], color=bar_color, linewidth=lw, zorder=2)
                else:
                    ax.bar([ (left+right)/2.0 ], [height], width=(right-left)*0.95, color=bar_color, alpha=style.get('alpha',0.6), zorder=2, edgecolor='black')
            if style.get('mean_line', True):
                ax.axvline(mean, color=style.get('mean_color','black'), linestyle=style.get('mean_linestyle','--'), linewidth=1.2, label=style.get('mean_label','Mean'))
        # Overlays
        # Overlays (support optional secondary y)
        secondary_ax = None
        for ov in overlays:
            x = ov.get('x'); y = ov.get('y')
            if not x or not y: continue
            st = ov.get('style', {})
            use_secondary = st.get('secondary_y', False)
            target_ax = ax
            if use_secondary:
                if secondary_ax is None:
                    secondary_ax = ax.twinx()
                target_ax = secondary_ax
            ptype = st.get('type','line')
            if ptype == 'scatter':
                target_ax.scatter(x,y, label=st.get('label'), c=st.get('color'), marker=st.get('marker','o'), alpha=st.get('alpha',0.8), zorder=3)
            else:
                target_ax.plot(x,y, st.get('linestyle','-'), label=st.get('label'), color=st.get('color'), linewidth=st.get('linewidth',2), alpha=st.get('alpha',0.9), zorder=3)
        if secondary_ax:
            # Label secondary axis if any overlay supplies label text
            sec_label = None
            for ov in overlays:
                st = ov.get('style', {})
                if st.get('secondary_y') and st.get('secondary_ylabel'):
                    sec_label = st.get('secondary_ylabel')
                    break
            if sec_label:
                secondary_ax.set_ylabel(sec_label)
            try:
                secondary_ax.legend(loc='upper right')
            except Exception:
                pass
        # Final styling
        title = config.get('title', data.get('title','Histogram'))
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(config.get('xlabel', data.get('metric','value')))
        ax.set_ylabel('Count')
        ax.set_ylim(0, global_ymax * 1.15 if global_ymax else 1)
        ax.grid(True, axis='y', alpha=0.3)
        try:
            # Place primary legend in upper right to avoid overlapping stats box (upper left)
            ax.legend(loc='upper right')
        except Exception:
            pass
        # Primary stats box (from first histogram if present)
        first = histograms[0]
        try:
            # Compute datapoint count for first histogram (fallback to length of values)
            n_values = first.get('count')
            if n_values is None:
                try:
                    vals = first.get('values') or []
                    n_values = len(vals)
                except Exception:
                    n_values = 0
            stats_text = (f"μ={first.get('mean',0):.2f}\n"
                          f"σ={first.get('std',1):.2f}\n"
                          f"N={n_values}")
            ax.text(0.02, 0.95, stats_text, transform=ax.transAxes, va='top', ha='left', fontsize=10,
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.7, edgecolor='gray'))
        except Exception:
            pass
