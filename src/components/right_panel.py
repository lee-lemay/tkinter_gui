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

from ..visualization.plot_manager import PlotManager
from ..plotting.backends import MatplotlibBackend
from ..plotting.statistics_tab import StatisticsTabWidget
from ..plotting.overview_tab import OverviewTabWidget
from ..plotting.geospatial_tab import GeospatialTabWidget
from ..plotting.animation_tab import AnimationTabWidget
from ..plotting.xy_plot_tab import XYPlotTabWidget
from ..plotting.histogram_plot_tab import HistogramPlotTabWidget
from ..plotting import histogram_config_formatters  # noqa: F401 ensure registry
# Importing formatter names via registry lookup (functions kept for backward compatibility if needed)
from ..plotting import xy_config_formatters  # noqa: F401  (ensures registry side-effects)


class RightPanel:
    """
    Right panel component that provides analysis views and visualizations.
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
        
        # Pass controller and plot manager to all modular widgets
        if hasattr(self, 'tab_widgets'):
            for tab_name, tab_widget in self.tab_widgets.items():
                tab_widget.set_controller(controller)
                if hasattr(tab_widget, 'set_plot_manager'):
                    if hasattr(self, 'plot_manager'):
                        tab_widget.set_plot_manager(self.plot_manager)
        
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
            """Create the analysis view tabs with matplotlib integration for Phase 5."""
            # Overview Tab
            self._create_overview_tab()
            # Statistics Tab
            self._create_statistics_tab()
            # Track existence (lifetime) tab 
            self._create_xy_lifetime_tab()
            # Lat/Lon Scatter Tab
            self._create_geospatial_tab()
            # Generic XY RMS Error mirror tab
            self._create_xy_rms_error_tab()
            # Animation Tab
            self._create_animation_tab()
            # North / East error tabs
            self._create_xy_north_error_tab()
            self._create_xy_east_error_tab()
            # Histograms
            self._create_histogram_tabs()
    
    def _create_overview_tab(self):
        """Create the overview tab"""
        self.overview_tab = OverviewTabWidget(self.notebook)
        self.notebook.add(self.overview_tab, text="Overview")
        
        # Set dependencies
        if hasattr(self, 'controller'):
            self.overview_tab.set_controller(self.controller)
        
        # Store reference in the tab widgets dict
        if not hasattr(self, 'tab_widgets'):
            self.tab_widgets = {}
        self.tab_widgets['overview'] = self.overview_tab
        
    def _create_statistics_tab(self):
        """Create the statistics tab using modular widget architecture."""
        # Create backend for this tab
        stats_backend = MatplotlibBackend()
        
        # Create the statistics tab widget
        self.statistics_tab = StatisticsTabWidget(self.notebook, stats_backend)
        self.notebook.add(self.statistics_tab, text="Statistics")
        
        # Set dependencies
        if hasattr(self, 'controller'):
            self.statistics_tab.set_controller(self.controller)
        if hasattr(self, 'plot_manager'):
            self.statistics_tab.set_plot_manager(self.plot_manager)
        
        # Store reference in a separate dict for the new modular widgets
        if not hasattr(self, 'tab_widgets'):
            self.tab_widgets = {}
        self.tab_widgets['statistics'] = self.statistics_tab
    
    def _create_geospatial_tab(self):
        """Create the geospatial tab using modular widget architecture."""
        # Create backend for this tab
        geospatial_backend = MatplotlibBackend()
        
        # Create the geospatial tab widget
        self.geospatial_tab = GeospatialTabWidget(self.notebook, geospatial_backend)
        self.notebook.add(self.geospatial_tab, text="Lat/Lon Scatter")
        
        # Set dependencies
        if hasattr(self, 'controller'):
            self.geospatial_tab.set_controller(self.controller)
        if hasattr(self, 'plot_manager'):
            self.geospatial_tab.set_plot_manager(self.plot_manager)
        
        # Store reference in the tab widgets dict
        if not hasattr(self, 'tab_widgets'):
            self.tab_widgets = {}
        self.tab_widgets['geospatial'] = self.geospatial_tab
    
    
    def _create_xy_lifetime_tab(self):
        """Create the lifetime (existence) tab as an XY plot (track duration lines)."""
        xy_backend = MatplotlibBackend()
        self.xy_lifetime_tab = XYPlotTabWidget(
            self.notebook,
            xy_backend,
            include_data_selection=False,
            include_track_selection=True,
            formatter_name="track_existence_over_time",
            title="Track Lifetimes"
        )
        self.notebook.add(self.xy_lifetime_tab, text="Track Lifetimes")

        if hasattr(self, 'controller'):
            self.xy_lifetime_tab.set_controller(self.controller)
        if hasattr(self, 'plot_manager'):
            self.xy_lifetime_tab.set_plot_manager(self.plot_manager)

        if not hasattr(self, 'tab_widgets'):
            self.tab_widgets = {}
        self.tab_widgets['xy_lifetimes'] = self.xy_lifetime_tab
    
    def _create_animation_tab(self):
        """Create the animation tab using modular widget architecture."""
        # Create backend for this tab
        animation_backend = MatplotlibBackend()
        
        # Create the animation tab widget
        self.animation_tab = AnimationTabWidget(self.notebook, animation_backend)
        self.notebook.add(self.animation_tab, text="Animation")
        
        # Set dependencies
        if hasattr(self, 'controller'):
            self.animation_tab.set_controller(self.controller)
        if hasattr(self, 'plot_manager'):
            self.animation_tab.set_plot_manager(self.plot_manager)
        
        # Store reference in the tab widgets dict
        if not hasattr(self, 'tab_widgets'):
            self.tab_widgets = {}
        self.tab_widgets['animation'] = self.animation_tab

    def _create_xy_north_error_tab(self):
        """Create a generic XY tab for North (latitudinal) error vs time."""
        xy_backend = MatplotlibBackend()
        self.xy_north_error_tab = XYPlotTabWidget(
            self.notebook,
            xy_backend,
            include_data_selection=False,
            include_track_selection=True,
            formatter_name="north_error_over_time",
            title="North Error"
        )
        self.notebook.add(self.xy_north_error_tab, text="North Error")

        if hasattr(self, 'controller'):
            self.xy_north_error_tab.set_controller(self.controller)
        if hasattr(self, 'plot_manager'):
            self.xy_north_error_tab.set_plot_manager(self.plot_manager)

        if not hasattr(self, 'tab_widgets'):
            self.tab_widgets = {}
        self.tab_widgets['xy_north_error'] = self.xy_north_error_tab

    def _create_xy_east_error_tab(self):
        """Create a generic XY tab for East (longitudinal) error vs time."""
        xy_backend = MatplotlibBackend()
        self.xy_east_error_tab = XYPlotTabWidget(
            self.notebook,
            xy_backend,
            include_data_selection=False,
            include_track_selection=True,
            formatter_name="east_error_over_time",
            title="East Error"
        )
        self.notebook.add(self.xy_east_error_tab, text="East Error")

        if hasattr(self, 'controller'):
            self.xy_east_error_tab.set_controller(self.controller)
        if hasattr(self, 'plot_manager'):
            self.xy_east_error_tab.set_plot_manager(self.plot_manager)

        if not hasattr(self, 'tab_widgets'):
            self.tab_widgets = {}
        self.tab_widgets['xy_east_error'] = self.xy_east_error_tab

    def _create_xy_rms_error_tab(self):
        """Create a generic XY tab instance replicating the RMS Error plot (time vs 3D RMS)."""
        xy_backend = MatplotlibBackend()
        self.xy_rms_error_tab = XYPlotTabWidget(
            self.notebook,
            xy_backend,
            include_data_selection=False,
            include_track_selection=True,
            formatter_name="rms_error_3d_over_time",
            title="XY RMS Error"
        )
        self.notebook.add(self.xy_rms_error_tab, text="XY RMS Error")

        if hasattr(self, 'controller'):
            self.xy_rms_error_tab.set_controller(self.controller)
        if hasattr(self, 'plot_manager'):
            self.xy_rms_error_tab.set_plot_manager(self.plot_manager)

        if not hasattr(self, 'tab_widgets'):
            self.tab_widgets = {}
        self.tab_widgets['xy_rms_error'] = self.xy_rms_error_tab

    def _create_histogram_tabs(self):
        """Create histogram tabs for north and east error distributions."""
        north_backend = MatplotlibBackend()
        self.north_error_hist_tab = HistogramPlotTabWidget(
            self.notebook,
            north_backend,
            include_data_selection=False,
            include_track_selection=True,
            formatter_name='north_error_histogram',
            title='North Error Histogram'
        )
        self.notebook.add(self.north_error_hist_tab, text='North Err Hist')

        east_backend = MatplotlibBackend()
        self.east_error_hist_tab = HistogramPlotTabWidget(
            self.notebook,
            east_backend,
            include_data_selection=False,
            include_track_selection=True,
            formatter_name='east_error_histogram',
            title='East Error Histogram'
        )
        self.notebook.add(self.east_error_hist_tab, text='East Err Hist')

        if hasattr(self, 'controller') and self.controller:
            self.north_error_hist_tab.set_controller(self.controller)
            self.east_error_hist_tab.set_controller(self.controller)
        if hasattr(self, 'plot_manager') and self.plot_manager:
            self.north_error_hist_tab.set_plot_manager(self.plot_manager)
            self.east_error_hist_tab.set_plot_manager(self.plot_manager)

        if not hasattr(self, 'tab_widgets'):
            self.tab_widgets = {}
        self.tab_widgets['north_error_hist'] = self.north_error_hist_tab
        self.tab_widgets['east_error_hist'] = self.east_error_hist_tab
    
    def _on_tab_changed(self, event):
        """Handle tab change events."""
        try:
            current_tab = self.get_current_tab()
            self.logger.debug(f"Tab changed to: {current_tab}")
        
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
            
            if event in ("datasets_changed", "focus_changed"):
                focus_info = state.get_focus_dataset_info()
                if focus_info and focus_info.status.value == "loaded":
                    # Auto-update all tabs when we have a loaded focus dataset
                    for _, tab_widget in self.tab_widgets.items():
                        if hasattr(tab_widget, 'auto_update'):
                            tab_widget.auto_update()
                    self.logger.debug(f"{event}: plots refreshed for loaded focus dataset")
                else:
                    # No focus or not loaded: clear all plots and reset tab widgets
                    for _, tab_widget in self.tab_widgets.items():
                        if hasattr(tab_widget, 'clear_plot'):
                            try:
                                tab_widget.clear_plot()
                            except Exception:
                                pass
                        # Also trigger focus-change handling to reset control widgets if available
                        if hasattr(tab_widget, 'on_focus_dataset_changed'):
                            try:
                                tab_widget.on_focus_dataset_changed()
                            except Exception:
                                pass
                    self.logger.debug(f"{event}: no focus or not loaded; plots cleared and widgets reset")
            
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
            return str(self.notebook.tab(current_index, "text") or "")
        except Exception as e:
            self.logger.error(f"Error getting current tab: {e}")
            return ""