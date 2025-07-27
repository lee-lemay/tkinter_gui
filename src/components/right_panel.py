"""
Right Panel Component

This module contains the right panel component that displays
analysis views and visualizations using matplotlib integration.
Phase 4: Basic Visualization using Matplotlib
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Optional, Any, Dict, List

from ..visualization.matplotlib_canvas import MatplotlibCanvas
from ..visualization.plot_manager import PlotManager


class RightPanel:
    """
    Right panel component that provides analysis views and visualizations.
    
    Phase 4 implementation with matplotlib integration and extensible design.
    """
    
    def __init__(self, parent: tk.Widget):
        """
        Initialize the right panel.
        
        Args:
            parent: The parent widget
        """
        self.parent = parent
        self.logger = logging.getLogger(__name__)
        self.controller: Optional[Any] = None
        self.plot_manager: Optional[PlotManager] = None
        
        # Store matplotlib canvases for each tab
        self.canvas_widgets: Dict[str, MatplotlibCanvas] = {}
        
        # Create the main frame
        self.frame = ttk.Frame(parent)
        
        # Create panel content
        self._create_content()
        
        self.logger.debug("Right panel initialized with matplotlib integration")
    
    def set_controller(self, controller: Any):
        """
        Set the controller for this component.
        
        Args:
            controller: The application controller
        """
        self.controller = controller
        
        # Initialize plot manager with business logic interface
        if hasattr(controller, 'data_interface'):
            self.plot_manager = PlotManager(controller.data_interface)
        
        self.logger.debug("Controller set for right panel")
    
    def _create_content(self):
        """Create the right panel content."""
        # Title
        title_label = ttk.Label(
            self.frame,
            text="Visualization & Analysis",
            font=("TkDefaultFont", 10, "bold")
        )
        title_label.pack(fill="x", padx=10, pady=(10, 5))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Bind tab selection events
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        
        # Create tabs with matplotlib integration
        self._create_tabs()
    
    def _create_tabs(self):
        """Create the analysis view tabs with matplotlib integration."""
        # Overview Tab (with basic plot)
        self._create_overview_tab()
        
        # Visualization Tab (main plotting area)
        self._create_visualization_tab()
        
        # Statistics Tab (with statistical plots)
        self._create_statistics_tab()
        
        # Geospatial Tab (for lat/lon plots)
        self._create_geospatial_tab()
    
    def _create_overview_tab(self):
        """Create the overview tab with demo plot."""
        overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(overview_frame, text="Overview")
        
        # Create header frame
        header_frame = ttk.Frame(overview_frame)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        # Welcome message
        welcome_label = ttk.Label(
            header_frame,
            text="Data Analysis Application - Phase 4",
            font=("TkDefaultFont", 12, "bold")
        )
        welcome_label.pack(anchor="w")
        
        # Feature description
        feature_label = ttk.Label(
            header_frame,
            text="Matplotlib visualization capabilities enabled",
            font=("TkDefaultFont", 10, "italic")
        )
        feature_label.pack(anchor="w", pady=(5, 0))
        
        # Create matplotlib canvas for demo plot
        canvas_frame = ttk.Frame(overview_frame)
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.canvas_widgets['overview'] = MatplotlibCanvas(canvas_frame)
        self.canvas_widgets['overview'].frame.pack(fill="both", expand=True)
        
        # Instructions frame
        instructions_frame = ttk.Frame(overview_frame)
        instructions_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        instructions_label = ttk.Label(
            instructions_frame,
            text="Load datasets using the File menu to enable additional visualization options.",
            font=("TkDefaultFont", 9, "italic")
        )
        instructions_label.pack(anchor="w")
    
    def _create_visualization_tab(self):
        """Create the main visualization tab."""
        viz_frame = ttk.Frame(self.notebook)
        self.notebook.add(viz_frame, text="Visualization")
        
        # Create control panel
        control_frame = ttk.LabelFrame(viz_frame, text="Plot Controls")
        control_frame.pack(fill="x", padx=10, pady=10)
        
        # Plot selection
        self.plot_type_var = tk.StringVar(value="Select Plot Type")
        self.plot_type_combo = ttk.Combobox(
            control_frame,
            textvariable=self.plot_type_var,
            state="readonly",
            width=30
        )
        self.plot_type_combo.pack(side="left", padx=5, pady=5)
        
        # Create plot button
        self.create_plot_btn = ttk.Button(
            control_frame,
            text="Create Plot",
            command=self._create_selected_plot
        )
        self.create_plot_btn.pack(side="left", padx=5, pady=5)
        
        # Refresh plots button
        self.refresh_btn = ttk.Button(
            control_frame,
            text="Refresh",
            command=self._refresh_available_plots
        )
        self.refresh_btn.pack(side="left", padx=5, pady=5)
        
        # Create matplotlib canvas
        canvas_frame = ttk.Frame(viz_frame)
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.canvas_widgets['visualization'] = MatplotlibCanvas(canvas_frame)
        self.canvas_widgets['visualization'].frame.pack(fill="both", expand=True)
        
        # Initialize available plots
        self._refresh_available_plots()
    
    def _create_statistics_tab(self):
        """Create the statistics tab."""
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="Statistics")
        
        # Control panel for statistics
        control_frame = ttk.LabelFrame(stats_frame, text="Statistics Controls")
        control_frame.pack(fill="x", padx=10, pady=10)
        
        # Dataset summary button
        self.summary_btn = ttk.Button(
            control_frame,
            text="Show Track Counts",
            command=self._show_track_counts
        )
        self.summary_btn.pack(side="left", padx=5, pady=5)
        
        # Create matplotlib canvas
        canvas_frame = ttk.Frame(stats_frame)
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.canvas_widgets['statistics'] = MatplotlibCanvas(canvas_frame)
        self.canvas_widgets['statistics'].frame.pack(fill="both", expand=True)
        
        # Show initial track counts if data is available
        self._show_track_counts()
    
    def _create_geospatial_tab(self):
        """Create the geospatial analysis tab."""
        geo_frame = ttk.Frame(self.notebook)
        self.notebook.add(geo_frame, text="Geospatial")
        
        # Control panel
        control_frame = ttk.LabelFrame(geo_frame, text="Geospatial Controls")
        control_frame.pack(fill="x", padx=10, pady=10)
        
        # Lat/Lon plot button
        self.latlon_btn = ttk.Button(
            control_frame,
            text="Show Lat/Lon Plot",
            command=self._show_lat_lon_plot
        )
        self.latlon_btn.pack(side="left", padx=5, pady=5)
        
        # Options frame
        options_frame = ttk.Frame(control_frame)
        options_frame.pack(side="left", padx=10)
        
        self.include_tracks_var = tk.BooleanVar(value=True)
        self.include_truth_var = tk.BooleanVar(value=True)
        
        tracks_cb = ttk.Checkbutton(
            options_frame,
            text="Include Tracks",
            variable=self.include_tracks_var
        )
        tracks_cb.pack(side="left", padx=5)
        
        truth_cb = ttk.Checkbutton(
            options_frame,
            text="Include Truth",
            variable=self.include_truth_var
        )
        truth_cb.pack(side="left", padx=5)
        
        # Create matplotlib canvas
        canvas_frame = ttk.Frame(geo_frame)
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.canvas_widgets['geospatial'] = MatplotlibCanvas(canvas_frame)
        self.canvas_widgets['geospatial'].frame.pack(fill="both", expand=True)
    
    def _create_demo_plot(self):
        """Create a demo plot for the overview tab."""
        if 'overview' in self.canvas_widgets:
            # Create demo plot data
            demo_data = {
                'plot_type': 'demo'
            }
            self.canvas_widgets['overview'].create_simple_plot(demo_data)
    
    def _refresh_available_plots(self):
        """Refresh the list of available plots based on current state."""
        if not self.plot_manager or not self.controller:
            self.plot_type_combo['values'] = ["No data available"]
            return
        
        try:
            app_state = self.controller.get_state()
            available_plots = self.plot_manager.get_available_plots(app_state)
            
            # Create combo box values with enabled status
            combo_values = []
            for plot in available_plots:
                if plot['enabled']:
                    combo_values.append(f"{plot['name']} ({plot['id']})")
                else:
                    combo_values.append(f"{plot['name']} - {plot['reason']}")
            
            if not combo_values:
                combo_values = ["No plots available"]
            
            self.plot_type_combo['values'] = combo_values
            
            # Select first enabled plot if available
            enabled_plots = [p for p in available_plots if p['enabled']]
            if enabled_plots:
                self.plot_type_var.set(f"{enabled_plots[0]['name']} ({enabled_plots[0]['id']})")
            else:
                self.plot_type_var.set("No plots available")
        
        except Exception as e:
            self.logger.error(f"Error refreshing available plots: {e}")
            self.plot_type_combo['values'] = ["Error loading plots"]
    
    def _create_selected_plot(self):
        """Create the selected plot in the visualization tab."""
        if not self.plot_manager or not self.controller:
            return
        
        try:
            # Extract plot ID from selected value
            selected = self.plot_type_var.get()
            if '(' not in selected or ')' not in selected:
                return
            
            plot_id = selected.split('(')[-1].split(')')[0]
            
            # Get current application state
            app_state = self.controller.get_state()
            
            # Validate plot requirements
            validation = self.plot_manager.validate_plot_requirements(plot_id, app_state)
            if not validation['valid']:
                self.logger.warning(f"Cannot create plot: {validation['reason']}")
                return
            
            # Prepare plot data
            plot_data = self.plot_manager.prepare_plot_data(plot_id, app_state)
            if 'error' in plot_data:
                self.logger.error(f"Plot data error: {plot_data['error']}")
                return
            
            # Create the plot
            canvas = self.canvas_widgets['visualization']
            
            if plot_id == 'track_counts':
                canvas.create_simple_plot({'track_counts': plot_data['track_counts']})
            elif plot_id == 'lat_lon_scatter':
                canvas.create_simple_plot({'lat_lon_data': plot_data['lat_lon_data']})
            elif plot_id == 'demo_plot':
                canvas.create_simple_plot({})
            
            self.logger.info(f"Created plot: {plot_id}")
        
        except Exception as e:
            self.logger.error(f"Error creating plot: {e}")
    
    def _show_track_counts(self):
        """Show track counts in the statistics tab."""
        if not self.plot_manager or not self.controller:
            return
        
        try:
            app_state = self.controller.get_state()
            plot_data = self.plot_manager.prepare_plot_data('track_counts', app_state)
            
            if 'error' not in plot_data:
                canvas = self.canvas_widgets['statistics']
                canvas.create_simple_plot({'track_counts': plot_data['track_counts']})
            
        except Exception as e:
            self.logger.error(f"Error showing track counts: {e}")
    
    def _show_lat_lon_plot(self):
        """Show lat/lon plot in the geospatial tab."""
        if not self.plot_manager or not self.controller:
            return
        
        try:
            app_state = self.controller.get_state()
            
            # Get plot configuration from UI
            config = {
                'include_tracks': self.include_tracks_var.get(),
                'include_truth': self.include_truth_var.get()
            }
            
            plot_data = self.plot_manager.prepare_plot_data('lat_lon_scatter', app_state, config)
            
            if 'error' not in plot_data:
                canvas = self.canvas_widgets['geospatial']
                canvas.create_simple_plot({'lat_lon_data': plot_data['lat_lon_data']})
            
        except Exception as e:
            self.logger.error(f"Error showing lat/lon plot: {e}")
    
    def _auto_update_geospatial_plot(self):
        """Automatically update the geospatial plot when focus dataset changes."""
        try:
            if not self.plot_manager or not self.controller:
                return
            
            app_state = self.controller.get_state()
            focus_info = app_state.get_focus_dataset_info()
            
            # Only auto-update if we have a loaded focus dataset with data
            if (focus_info and 
                focus_info.status.value == "loaded" and 
                ((focus_info.tracks_df is not None and not focus_info.tracks_df.empty) or
                 (focus_info.truth_df is not None and not focus_info.truth_df.empty))):
                
                # Get plot configuration from UI (use defaults if UI controls not available)
                config = {
                    'include_tracks': getattr(self, 'include_tracks_var', tk.BooleanVar(value=True)).get(),
                    'include_truth': getattr(self, 'include_truth_var', tk.BooleanVar(value=True)).get()
                }
                
                plot_data = self.plot_manager.prepare_plot_data('lat_lon_scatter', app_state, config)
                
                if 'error' not in plot_data and 'geospatial' in self.canvas_widgets:
                    canvas = self.canvas_widgets['geospatial']
                    canvas.create_simple_plot({'lat_lon_data': plot_data['lat_lon_data']})
                    self.logger.debug(f"Auto-updated geospatial plot for dataset: {focus_info.name}")
            
        except Exception as e:
            self.logger.error(f"Error auto-updating geospatial plot: {e}")
    
    def _on_tab_changed(self, event):
        """Handle tab change events."""
        try:
            current_tab = self.get_current_tab()
            self.logger.debug(f"Tab changed to: {current_tab}")
            
            # Refresh data when switching to certain tabs
            if current_tab == "Visualization":
                self._refresh_available_plots()
        
        except Exception as e:
            self.logger.error(f"Error handling tab change: {e}")
    
    # State Management
    def on_state_changed(self, event: str):
        """
        Handle state changes from the application.
        
        Args:
            event: The type of state change event
        """
        try:
            if not self.controller:
                return
            
            state = self.controller.get_state()
            
            if event == "datasets_changed":
                # Refresh available plots when datasets change
                self._refresh_available_plots()
                
                # Update track counts display
                self._show_track_counts()
                
                # Check if focus dataset is loaded and auto-update geospatial plot
                focus_info = state.get_focus_dataset_info()
                if focus_info and focus_info.status.value == "loaded":
                    self._auto_update_geospatial_plot()
                
                self.logger.debug(f"Datasets changed, plots refreshed")
            
            elif event == "focus_changed":
                # Refresh plots when focus dataset changes
                self._refresh_available_plots()
                
                # Auto-update geospatial plot if focus dataset is loaded
                focus_info = state.get_focus_dataset_info()
                if focus_info and focus_info.status.value == "loaded":
                    self._auto_update_geospatial_plot()
                
                self.logger.debug(f"Focus changed, plots refreshed")
            
        except Exception as e:
            self.logger.error(f"Error handling state change '{event}': {e}")
    
    # Utility Methods
    def get_current_tab(self) -> str:
        """
        Get the name of the currently selected tab.
        
        Returns:
            Name of the current tab, or empty string if none selected
        """
        try:
            current_index = self.notebook.index(self.notebook.select())
            return self.notebook.tab(current_index, "text")
        except Exception as e:
            self.logger.error(f"Error getting current tab: {e}")
            return ""
    
    def select_tab(self, tab_name: str):
        """
        Select a specific tab.
        
        Args:
            tab_name: Name of the tab to select
        """
        try:
            tab_count = self.notebook.index("end")
            for i in range(tab_count):
                if self.notebook.tab(i, "text") == tab_name:
                    self.notebook.select(i)
                    self.logger.debug(f"Selected tab: {tab_name}")
                    break
        except Exception as e:
            self.logger.error(f"Error selecting tab: {e}")
    
    def export_current_plot(self):
        """
        Export the current tab's plot to a file (opens file dialog).
        """
        try:
            current_tab = self.get_current_tab().lower()
            if current_tab in self.canvas_widgets:
                # Call export_plot without parameters (it opens a file dialog)
                self.canvas_widgets[current_tab].export_plot()
                self.logger.info(f"Exported plot from {current_tab} tab")
        except Exception as e:
            self.logger.error(f"Error exporting plot: {e}")
    
    def clear_current_plot(self):
        """Clear the current tab's plot."""
        try:
            current_tab = self.get_current_tab().lower()
            if current_tab in self.canvas_widgets:
                self.canvas_widgets[current_tab].clear_plot()
                self.logger.info(f"Cleared plot in {current_tab} tab")
        except Exception as e:
            self.logger.error(f"Error clearing plot: {e}")
