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
from ..plotting.lifetime_tab import LifetimeTabWidget
from ..plotting.animation_tab import AnimationTabWidget
from ..plotting.xy_plot_tab import XYPlotTabWidget
from ..plotting.xy_config_formatters import (
    example_tracks_lat_lon_over_time,
    error_north_east_over_time,
    rms_error_3d_over_time,
)


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
            # Lat/Lon Scatter Tab
            self._create_geospatial_tab()
            # (Removed) Legacy bespoke North/East Errors and RMS Error tabs replaced by generic XY equivalents
            # Generic XY RMS Error mirror tab
            self._create_xy_rms_error_tab(include_track_selection=True)
            # Track lifetime tab
            self._create_lifetime_tab()
            # Animation Tab
            self._create_animation_tab()
            # Generic XY Tab (with optional data selection widgets enabled)
            self._create_xy_plot_tab(include_data_selection=True)
            # Generic XY Error Analysis mirror tab (uses formatter to replicate errors)
            self._create_xy_error_tab(include_data_selection=True)
    
    def _create_overview_tab(self):
        """Create the overview tab using modular widget architecture."""
        # Create backend for this tab
        overview_backend = MatplotlibBackend()
        
        # Create the overview tab widget
        self.overview_tab = OverviewTabWidget(self.notebook, overview_backend)
        self.notebook.add(self.overview_tab, text="Overview")
        
        # Set dependencies
        if hasattr(self, 'controller'):
            self.overview_tab.set_controller(self.controller)
        if hasattr(self, 'plot_manager'):
            self.overview_tab.set_plot_manager(self.plot_manager)
        
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
    
    
    def _create_lifetime_tab(self):
        """Create the lifetime tab using modular widget architecture."""
        # Create backend for this tab
        lifetime_backend = MatplotlibBackend()
        
        # Create the lifetime tab widget
        self.lifetime_tab = LifetimeTabWidget(self.notebook, lifetime_backend)
        self.notebook.add(self.lifetime_tab, text="Lifetime")
        
        # Set dependencies
        if hasattr(self, 'controller'):
            self.lifetime_tab.set_controller(self.controller)
        if hasattr(self, 'plot_manager'):
            self.lifetime_tab.set_plot_manager(self.plot_manager)
        
        # Store reference in the tab widgets dict
        if not hasattr(self, 'tab_widgets'):
            self.tab_widgets = {}
        self.tab_widgets['lifetime'] = self.lifetime_tab
    
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

    def _create_xy_plot_tab(self, include_data_selection: bool = True):
        """Create the generic XY plot tab."""
        xy_backend = MatplotlibBackend()
        # Pass a default/example formatter; callers can later replace it via controller interaction if desired
        self.xy_tab = XYPlotTabWidget(
            self.notebook,
            xy_backend,
            include_data_selection=include_data_selection,
            config_formatter=example_tracks_lat_lon_over_time,
            formatter_widgets=[],
        )
        self.notebook.add(self.xy_tab, text="XY Plot")

        if hasattr(self, 'controller'):
            self.xy_tab.set_controller(self.controller)
        if hasattr(self, 'plot_manager'):
            self.xy_tab.set_plot_manager(self.plot_manager)

        if not hasattr(self, 'tab_widgets'):
            self.tab_widgets = {}
        self.tab_widgets['xy_plot'] = self.xy_tab

    def _create_xy_error_tab(self, include_data_selection: bool = True):
        """Create a generic XY tab instance replicating the Error Analysis (north/east error) plot."""
        xy_backend = MatplotlibBackend()
        self.xy_error_tab = XYPlotTabWidget(
            self.notebook,
            xy_backend,
            include_data_selection=False,  
            include_track_selection=True,
            config_formatter=error_north_east_over_time,
            formatter_widgets=[],
            title="XY Errors"
        )
        self.notebook.add(self.xy_error_tab, text="XY Errors")

        if hasattr(self, 'controller'):
            self.xy_error_tab.set_controller(self.controller)
        if hasattr(self, 'plot_manager'):
            self.xy_error_tab.set_plot_manager(self.plot_manager)

        if not hasattr(self, 'tab_widgets'):
            self.tab_widgets = {}
        self.tab_widgets['xy_errors'] = self.xy_error_tab

    def _create_xy_rms_error_tab(self, include_track_selection: bool = True):
        """Create a generic XY tab instance replicating the RMS Error plot (time vs 3D RMS)."""
        xy_backend = MatplotlibBackend()
        self.xy_rms_error_tab = XYPlotTabWidget(
            self.notebook,
            xy_backend,
            include_data_selection=False,
            include_track_selection=include_track_selection,
            config_formatter=rms_error_3d_over_time,
            formatter_widgets=[],
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