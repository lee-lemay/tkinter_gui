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
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
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
        
        # Export button
        export_btn = ttk.Button(
            self.toolbar_frame,
            text="Export Plot",
            command=self.export_plot
        )
        export_btn.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        clear_btn = ttk.Button(
            self.toolbar_frame,
            text="Clear",
            command=self.clear_plot
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
    
    def get_frame(self) -> ttk.Frame:
        """Get the main frame containing the canvas."""
        return self.frame
    
    def get_figure(self) -> Figure:
        """Get the matplotlib figure object."""
        return self.figure
    
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
    
    def create_simple_plot(self, data: Dict[str, Any], plot_config: Dict[str, Any] = None):
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
            else:
                # Default demo plot
                self._plot_demo(ax)
            
            # Apply common styling
            self.figure.tight_layout()
            self.canvas.draw()
            
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
        
        # Styling
        ax.set_title('Latitude vs Longitude', fontsize=14, fontweight='bold')
        ax.set_xlabel('Longitude', fontsize=12)
        ax.set_ylabel('Latitude', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
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
