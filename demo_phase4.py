#!/usr/bin/env python3
"""
Phase 4 Demo: Basic Visualization using Matplotlib (Updated Requirements)

This demo showcases the updated Phase 4 implementation features:
- Extensible, modular software design practice for reusable components
- Matplotlib canvas integration with NavigationToolbar2Tk
- First simple plot showing lat/lon of tracks and truth (from real CSV data)
- Plot export functionality
- Tab-based view selection framework
- Loading and visualizing REAL CSV datasets

Usage: python demo_phase4_updated.py
"""

import sys
import time
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.visualization.matplotlib_canvas import MatplotlibCanvas
from src.visualization.plot_manager import PlotManager
from src.business.data_interface import MockDataInterface
from src.models.application_state import ApplicationState, DatasetInfo, DatasetStatus


class Phase4UpdatedDemo:
    """Updated Phase 4 demonstration application with real CSV data."""
    
    def __init__(self):
        """Initialize the demo application."""
        self.root = tk.Tk()
        self.root.title("Phase 4 Demo: Real CSV Data Visualization")
        self.root.geometry("1200x800")
        
        # Initialize components
        self.data_interface = MockDataInterface()
        self.plot_manager = PlotManager(self.data_interface)
        self.app_state = ApplicationState()
        
        # Load real datasets from test_data directory
        self._load_real_datasets()
        
        # Create GUI
        self._create_gui()
        
        # Create initial lat/lon plot with real data
        self._create_initial_plot()
    
    def _load_real_datasets(self):
        """Load real CSV datasets from test_data directory."""
        test_data_dir = Path("test_data")
        
        if not test_data_dir.exists():
            messagebox.showerror("Error", "test_data directory not found!")
            return
        
        # Load both sample datasets
        for dataset_dir in test_data_dir.iterdir():
            if dataset_dir.is_dir():
                try:
                    # Load the CSV files
                    dataframes = self.data_interface.load_dataset(dataset_dir)
                    
                    # Create dataset info
                    dataset_info = DatasetInfo(
                        name=dataset_dir.name,
                        path=dataset_dir,
                        status=DatasetStatus.LOADED
                    )
                    
                    # Store the loaded DataFrames
                    dataset_info.tracks_df = dataframes['tracks']
                    dataset_info.truth_df = dataframes['truth']
                    dataset_info.detections_df = dataframes['detections']
                    
                    # Add to application state
                    self.app_state.add_dataset(dataset_info)
                    
                    print(f"Loaded dataset: {dataset_dir.name}")
                    print(f"  - Tracks: {len(dataframes['tracks'])} records")
                    print(f"  - Truth: {len(dataframes['truth'])} records")
                    print(f"  - Detections: {len(dataframes['detections'])} records")
                    
                except Exception as e:
                    print(f"Error loading {dataset_dir.name}: {e}")
        
        # Set focus to first loaded dataset
        datasets = list(self.app_state.datasets.keys())
        if datasets:
            self.app_state.focus_dataset = datasets[0]
            print(f"Focus dataset set to: {datasets[0]}")
    
    def _create_gui(self):
        """Create the demonstration GUI."""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Phase 4: Basic Visualization with Real CSV Data",
            font=("TkDefaultFont", 16, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Description
        desc_text = """This demo showcases Phase 4 implementation with REAL CSV datasets loaded from test_data directory.
Key Achievement: "First simple plot showing lat/lon of tracks and truth" using actual data."""
        
        desc_label = ttk.Label(
            main_frame,
            text=desc_text,
            font=("TkDefaultFont", 11),
            justify="center"
        )
        desc_label.pack(pady=(0, 15))
        
        # Dataset info frame
        info_frame = ttk.LabelFrame(main_frame, text="Loaded Dataset Information")
        info_frame.pack(fill="x", pady=(0, 10))
        
        # Dataset selection
        dataset_frame = ttk.Frame(info_frame)
        dataset_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(dataset_frame, text="Focus Dataset:").pack(side="left", padx=(0, 5))
        
        self.dataset_var = tk.StringVar()
        self.dataset_combo = ttk.Combobox(
            dataset_frame,
            textvariable=self.dataset_var,
            state="readonly",
            width=25
        )
        self.dataset_combo.pack(side="left", padx=5)
        self.dataset_combo.bind("<<ComboboxSelected>>", self._on_dataset_changed)
        
        # Populate dataset list
        datasets = list(self.app_state.datasets.keys())
        if datasets:
            self.dataset_combo['values'] = datasets
            self.dataset_var.set(datasets[0])
        
        # Dataset statistics
        self.stats_label = ttk.Label(
            info_frame,
            text="",
            font=("TkDefaultFont", 9)
        )
        self.stats_label.pack(pady=5)
        
        # Controls frame
        controls_frame = ttk.LabelFrame(main_frame, text="Plot Controls")
        controls_frame.pack(fill="x", pady=(0, 10))
        
        # Plot type selection
        ttk.Label(controls_frame, text="Plot Type:").pack(side="left", padx=5)
        
        self.plot_type_var = tk.StringVar(value="lat_lon")
        plot_types = [
            ("Lat/Lon (Real Data)", "lat_lon"),
            ("Track Counts", "track_counts"),
            ("Demo Plot", "demo")
        ]
        
        for text, value in plot_types:
            ttk.Radiobutton(
                controls_frame,
                text=text,
                variable=self.plot_type_var,
                value=value,
                command=self._update_plot
            ).pack(side="left", padx=5)
        
        # Options for lat/lon plot
        options_frame = ttk.Frame(controls_frame)
        options_frame.pack(side="left", padx=20)
        
        self.include_tracks_var = tk.BooleanVar(value=True)
        self.include_truth_var = tk.BooleanVar(value=True)
        
        tracks_cb = ttk.Checkbutton(
            options_frame,
            text="Show Tracks",
            variable=self.include_tracks_var,
            command=self._update_plot
        )
        tracks_cb.pack(side="left", padx=5)
        
        truth_cb = ttk.Checkbutton(
            options_frame,
            text="Show Truth",
            variable=self.include_truth_var,
            command=self._update_plot
        )
        truth_cb.pack(side="left", padx=5)
        
        # Action buttons
        button_frame = ttk.Frame(controls_frame)
        button_frame.pack(side="right", padx=10)
        
        ttk.Button(
            button_frame,
            text="Refresh Plot",
            command=self._update_plot
        ).pack(side="left", padx=2)
        
        ttk.Button(
            button_frame,
            text="Clear Plot",
            command=self._clear_plot
        ).pack(side="left", padx=2)
        
        ttk.Button(
            button_frame,
            text="Export Plot",
            command=self._export_plot
        ).pack(side="left", padx=2)
        
        ttk.Button(
            button_frame,
            text="Show Info",
            command=self._show_info
        ).pack(side="left", padx=2)
        
        # Create matplotlib canvas
        canvas_frame = ttk.LabelFrame(main_frame, text="Matplotlib Canvas with NavigationToolbar2Tk")
        canvas_frame.pack(fill="both", expand=True)
        
        self.canvas = MatplotlibCanvas(canvas_frame)
        self.canvas.frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill="x", pady=(10, 0))
        
        self.status_label = ttk.Label(
            status_frame,
            text="Ready - Loaded real CSV datasets with track and truth data",
            font=("TkDefaultFont", 9, "italic")
        )
        self.status_label.pack(side="left")
        
        # Close button
        ttk.Button(
            status_frame,
            text="Close Demo",
            command=self.root.quit
        ).pack(side="right")
        
        # Update dataset stats
        self._update_dataset_stats()
    
    def _create_initial_plot(self):
        """Create initial lat/lon plot with real data."""
        self._update_plot()
    
    def _on_dataset_changed(self, event=None):
        """Handle dataset selection change."""
        selected_dataset = self.dataset_var.get()
        if selected_dataset:
            self.app_state.focus_dataset = selected_dataset
            self._update_dataset_stats()
            self._update_plot()
    
    def _update_dataset_stats(self):
        """Update dataset statistics display."""
        focus_dataset = self.app_state.get_focus_dataset_info()
        if focus_dataset:
            tracks_count = len(focus_dataset.tracks_df) if focus_dataset.tracks_df is not None else 0
            truth_count = len(focus_dataset.truth_df) if focus_dataset.truth_df is not None else 0
            detections_count = len(focus_dataset.detections_df) if focus_dataset.detections_df is not None else 0
            
            # Get lat/lon ranges
            if focus_dataset.tracks_df is not None and not focus_dataset.tracks_df.empty:
                lat_range = (focus_dataset.tracks_df['lat'].min(), focus_dataset.tracks_df['lat'].max())
                lon_range = (focus_dataset.tracks_df['lon'].min(), focus_dataset.tracks_df['lon'].max())
                
                stats_text = f"""Dataset: {focus_dataset.name} | Tracks: {tracks_count} | Truth: {truth_count} | Detections: {detections_count}
Lat Range: {lat_range[0]:.4f} to {lat_range[1]:.4f} | Lon Range: {lon_range[0]:.4f} to {lon_range[1]:.4f}"""
            else:
                stats_text = f"Dataset: {focus_dataset.name} | Tracks: {tracks_count} | Truth: {truth_count} | Detections: {detections_count}"
            
            self.stats_label.config(text=stats_text)
    
    def _update_plot(self):
        """Update the plot based on selected type and options."""
        plot_type = self.plot_type_var.get()
        
        try:
            if plot_type == "lat_lon":
                # This is the key Phase 4 requirement: "First simple plot showing lat/lon of tracks and truth"
                config = {
                    'include_tracks': self.include_tracks_var.get(),
                    'include_truth': self.include_truth_var.get()
                }
                
                plot_data = self.plot_manager.prepare_plot_data('lat_lon_scatter', self.app_state, config)
                
                if 'error' in plot_data:
                    self.status_label.config(text=f"Error: {plot_data['error']}")
                    return
                
                data = {
                    'plot_type': 'lat_lon',
                    'data': plot_data['lat_lon_data']
                }
                
                # Count actual data points
                tracks_count = len(plot_data['lat_lon_data'].get('tracks', [])) if 'tracks' in plot_data['lat_lon_data'] else 0
                truth_count = len(plot_data['lat_lon_data'].get('truth', [])) if 'truth' in plot_data['lat_lon_data'] else 0
                
                self.status_label.config(text=f"Displaying REAL lat/lon data - Tracks: {tracks_count}, Truth: {truth_count} points")
                
            elif plot_type == "track_counts":
                plot_data = self.plot_manager.prepare_plot_data('track_counts', self.app_state)
                
                data = {
                    'plot_type': 'track_counts',
                    'data': plot_data['track_counts']
                }
                self.status_label.config(text=f"Displaying track counts for {len(plot_data['track_counts'])} datasets")
                
            elif plot_type == "demo":
                data = {'plot_type': 'demo'}
                self.status_label.config(text="Displaying demo plot with mathematical functions")
            
            # Create the plot
            self.canvas.create_simple_plot(data)
            
        except Exception as e:
            self.status_label.config(text=f"Error creating plot: {e}")
            print(f"Plot error: {e}")
    
    def _clear_plot(self):
        """Clear the current plot."""
        self.canvas.clear_plot()
        self.status_label.config(text="Plot cleared")
    
    def _export_plot(self):
        """Export the current plot."""
        try:
            self.canvas.export_plot()
            self.status_label.config(text="Plot export dialog opened")
        except Exception as e:
            self.status_label.config(text=f"Export error: {e}")
    
    def _show_info(self):
        """Show information about Updated Phase 4 implementation."""
        info_text = """Updated Phase 4: Basic Visualization using Matplotlib

🎯 KEY ACHIEVEMENT: Real CSV Data Visualization
The application now loads and visualizes ACTUAL track and truth data from CSV files!

📊 Phase 4 Requirements Fulfilled:
✅ Extensible, modular software design practice for reusable components
✅ Matplotlib canvas integration with Figure and FigureCanvasTkAgg
✅ NavigationToolbar2Tk setup for professional plot interaction
✅ First simple plot showing lat/lon of tracks and truth (REAL DATA!)
✅ Plot export functionality with multiple format support
✅ Tab-based view selection framework in main application

🔧 Technical Implementation:
• Real CSV loading from test_data directory with proper schema validation
• Data schema compliance: tracks[timestamp,lat,lon,alt,track_id], truth[timestamp,lat,lon,alt,id]
• Actual coordinate visualization around NYC area (40.7°N, -74.0°W)
• Integration between MockDataInterface, PlotManager, and MatplotlibCanvas
• Proper focus dataset management and state coordination

📂 Data Sources:
• sample_dataset_alpha: 100 track points, 100 truth points
• sample_dataset_beta: 100 track points, 100 truth points
• All data loaded from CSV files with realistic coordinates and timestamps

This establishes the foundation for real-world data analysis capabilities
while maintaining clean separation between visualization and business logic."""
        
        messagebox.showinfo("Updated Phase 4 Information", info_text)
    
    def run(self):
        """Run the demo application."""
        print("Starting Updated Phase 4 Demo...")
        print("Features: Real CSV data loading, lat/lon visualization, matplotlib integration")
        self.root.mainloop()


def main():
    """Main entry point for updated Phase 4 demo."""
    print("Updated Phase 4 Demo: Basic Visualization using Matplotlib")
    print("=" * 60)
    print("Key Feature: Real CSV data visualization with lat/lon plots")
    
    try:
        demo = Phase4UpdatedDemo()
        demo.run()
        
        print("Demo completed successfully!")
        
    except Exception as e:
        print(f"Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
