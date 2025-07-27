#!/usr/bin/env python3
"""
Phase 4 Demo: Basic Visualization using Matplotlib

This demo showcases the Phase 4 implementation features:
- Matplotlib canvas integration with NavigationToolbar2Tk
- Multiple plot types (demo, track counts, lat/lon scatter)
- Plot export functionality
- Tab-based visualization framework
- Extensible design patterns

Usage: python demo_phase4.py
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


class Phase4Demo:
    """Phase 4 demonstration application."""
    
    def __init__(self):
        """Initialize the demo application."""
        self.root = tk.Tk()
        self.root.title("Phase 4 Demo: Basic Visualization using Matplotlib")
        self.root.geometry("1000x700")
        
        # Initialize components
        self.data_interface = MockDataInterface()
        self.plot_manager = PlotManager(self.data_interface)
        self.app_state = ApplicationState()
        
        # Create mock datasets for demonstration
        self._setup_mock_datasets()
        
        # Create GUI
        self._create_gui()
        
        # Initial plot
        self._create_initial_demo()
    
    def _setup_mock_datasets(self):
        """Setup mock datasets in application state."""
        # Add some mock datasets
        datasets = ['Radar_Dataset_A', 'Sonar_Dataset_B', 'Multi_Sensor_C']
        
        for dataset_name in datasets:
            dataset_info = DatasetInfo(
                name=dataset_name,
                path=Path(f"/mock/path/{dataset_name}"),
                status=DatasetStatus.LOADED
            )
            
            # Add mock dataframes
            import pandas as pd
            import numpy as np
            
            # Create mock tracks data
            n_tracks = np.random.randint(15, 35)
            base_lat, base_lon = 40.7128, -74.0060  # NYC coordinates
            
            tracks_data = {
                'track_id': list(range(n_tracks)),
                'lat': base_lat + np.random.normal(0, 0.01, n_tracks),
                'lon': base_lon + np.random.normal(0, 0.01, n_tracks),
                'timestamp': np.linspace(0, 600, n_tracks)
            }
            dataset_info.tracks_df = pd.DataFrame(tracks_data)
            
            # Create mock truth data
            n_truth = np.random.randint(10, 20)
            truth_data = {
                'id': list(range(n_truth)),
                'lat': base_lat + np.random.normal(0, 0.005, n_truth),
                'lon': base_lon + np.random.normal(0, 0.005, n_truth),
                'timestamp': np.linspace(0, 600, n_truth)
            }
            dataset_info.truth_df = pd.DataFrame(truth_data)
            
            self.app_state.datasets[dataset_name] = dataset_info
        
        # Set focus dataset
        if 'Radar_Dataset_A' in self.app_state.datasets:
            self.app_state.focus_dataset = 'Radar_Dataset_A'
    
    def _create_gui(self):
        """Create the demonstration GUI."""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Phase 4: Basic Visualization using Matplotlib",
            font=("TkDefaultFont", 14, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Description
        desc_text = """This demo showcases Phase 4 matplotlib integration with extensible design patterns.
Features: NavigationToolbar2Tk, multiple plot types, export functionality, and tab-based framework."""
        
        desc_label = ttk.Label(
            main_frame,
            text=desc_text,
            font=("TkDefaultFont", 10),
            justify="center"
        )
        desc_label.pack(pady=(0, 15))
        
        # Controls frame
        controls_frame = ttk.LabelFrame(main_frame, text="Demo Controls")
        controls_frame.pack(fill="x", pady=(0, 10))
        
        # Plot type selection
        ttk.Label(controls_frame, text="Plot Type:").pack(side="left", padx=5)
        
        self.plot_type_var = tk.StringVar(value="demo")
        plot_types = [
            ("Demo Plot", "demo"),
            ("Track Counts", "track_counts"), 
            ("Lat/Lon Scatter", "lat_lon")
        ]
        
        for text, value in plot_types:
            ttk.Radiobutton(
                controls_frame,
                text=text,
                variable=self.plot_type_var,
                value=value,
                command=self._update_plot
            ).pack(side="left", padx=5)
        
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
            text="Ready - Use controls above to explore different plot types",
            font=("TkDefaultFont", 9, "italic")
        )
        self.status_label.pack(side="left")
        
        # Close button
        ttk.Button(
            status_frame,
            text="Close Demo",
            command=self.root.quit
        ).pack(side="right")
    
    def _create_initial_demo(self):
        """Create initial demo plot."""
        self._update_plot()
    
    def _update_plot(self):
        """Update the plot based on selected type."""
        plot_type = self.plot_type_var.get()
        data = None
        
        try:
            if plot_type == "demo":
                data = {'plot_type': 'demo'}
                self.status_label.config(text="Displaying demo plot with mathematical functions")
                
            elif plot_type == "track_counts":
                # Get track counts from datasets
                track_counts = {}
                for name, dataset in self.app_state.datasets.items():
                    if dataset.tracks_df is not None:
                        track_counts[name] = len(dataset.tracks_df['track_id'].unique())
                
                data = {
                    'plot_type': 'track_counts',
                    'data': track_counts
                }
                self.status_label.config(text=f"Displaying track counts for {len(track_counts)} datasets")
                
            elif plot_type == "lat_lon":
                # Get lat/lon data from focus dataset
                focus_dataset = self.app_state.get_focus_dataset_info()
                if focus_dataset and focus_dataset.tracks_df is not None:
                    lat_lon_data = {
                        'tracks': {
                            'lat': focus_dataset.tracks_df['lat'].tolist(),
                            'lon': focus_dataset.tracks_df['lon'].tolist()
                        }
                    }
                    
                    if focus_dataset.truth_df is not None:
                        lat_lon_data['truth'] = {
                            'lat': focus_dataset.truth_df['lat'].tolist(),
                            'lon': focus_dataset.truth_df['lon'].tolist()
                        }
                    
                    data = {
                        'plot_type': 'lat_lon',
                        'data': lat_lon_data
                    }
                    self.status_label.config(text=f"Displaying lat/lon scatter plot for {focus_dataset.name}")
                else:
                    self.status_label.config(text="No focus dataset available for lat/lon plot")
                    return
            
            # Create the plot if data is available
            if data:
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
        """Show information about Phase 4 implementation."""
        info_text = """Phase 4: Basic Visualization using Matplotlib

Key Features Implemented:
• Extensible/modular design with matplotlib integration
• MatplotlibCanvas class with Figure and FigureCanvasTkAgg
• NavigationToolbar2Tk for pan, zoom, and navigation
• Multiple plot types: demo, track counts, lat/lon scatter
• Plot export functionality with file format support
• Tab-based view selection framework in main application
• Plot manager for data preparation and coordination
• Enhanced business logic interface with plot data methods

Architecture:
• src/visualization/matplotlib_canvas.py - Reusable canvas component
• src/visualization/plot_manager.py - Plot coordination and data prep
• Enhanced data interface with plot data methods
• Updated right panel with matplotlib integration

This establishes the foundation for advanced plotting capabilities
while maintaining clean separation between visualization and business logic."""
        
        messagebox.showinfo("Phase 4 Information", info_text)
    
    def run(self):
        """Run the demo application."""
        print("Starting Phase 4 Demo...")
        print("Features: Matplotlib integration, NavigationToolbar2Tk, multiple plot types")
        self.root.mainloop()


def main():
    """Main entry point for Phase 4 demo."""
    print("Phase 4 Demo: Basic Visualization using Matplotlib")
    print("=" * 55)
    
    try:
        demo = Phase4Demo()
        demo.run()
        
        print("Demo completed successfully!")
        
    except Exception as e:
        print(f"Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
