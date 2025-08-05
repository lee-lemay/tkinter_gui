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
from ..plotting.backends import MatplotlibBackend
from ..plotting.statistics_tab import StatisticsTabWidget
from ..plotting.overview_tab import OverviewTabWidget
from ..plotting.geospatial_tab import GeospatialTabWidget
from ..plotting.error_analysis_tab import ErrorAnalysisTabWidget
from ..plotting.rms_error_tab import RMSErrorTabWidget
from ..plotting.lifetime_tab import LifetimeTabWidget
from ..plotting.animation_tab import AnimationTabWidget


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

        # North/East Errors Tab
        self._create_error_analysis_tab()

        # RMS Error Tab
        self._create_rms_error_tab()

        # Track lifetime tab
        self._create_lifetime_tab()

        # Animation Tab
        self._create_animation_tab()
    
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
    
    def _create_error_analysis_tab(self):
        """Create the error analysis tab using modular widget architecture."""
        # Create backend for this tab
        error_analysis_backend = MatplotlibBackend()
        
        # Create the error analysis tab widget
        self.error_analysis_tab = ErrorAnalysisTabWidget(self.notebook, error_analysis_backend)
        self.notebook.add(self.error_analysis_tab, text="North/East Errors")
        
        # Set dependencies
        if hasattr(self, 'controller'):
            self.error_analysis_tab.set_controller(self.controller)
        if hasattr(self, 'plot_manager'):
            self.error_analysis_tab.set_plot_manager(self.plot_manager)
        
        # Store reference in the tab widgets dict
        if not hasattr(self, 'tab_widgets'):
            self.tab_widgets = {}
        self.tab_widgets['error_analysis'] = self.error_analysis_tab
    
    def _create_rms_error_tab(self):
        """Create the RMS error tab using modular widget architecture."""
        # Create backend for this tab
        rms_error_backend = MatplotlibBackend()
        
        # Create the RMS error tab widget
        self.rms_error_tab = RMSErrorTabWidget(self.notebook, rms_error_backend)
        self.notebook.add(self.rms_error_tab, text="RMS Error")
        
        # Set dependencies
        if hasattr(self, 'controller'):
            self.rms_error_tab.set_controller(self.controller)
        if hasattr(self, 'plot_manager'):
            self.rms_error_tab.set_plot_manager(self.plot_manager)
        
        # Store reference in the tab widgets dict
        if not hasattr(self, 'tab_widgets'):
            self.tab_widgets = {}
        self.tab_widgets['rms_error_3d'] = self.rms_error_tab
    
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
            
            if event == "datasets_changed":
                
                # Check if focus dataset is loaded and auto-update all plots
                focus_info = state.get_focus_dataset_info()
                if focus_info and focus_info.status.value == "loaded":
                    for tab_name, tab_widget in self.tab_widgets.items():
                        if hasattr(tab_widget, 'auto_update'):
                            tab_widget.auto_update()
                
                self.logger.debug(f"Datasets changed, all plots refreshed")
            
            elif event == "focus_changed":
                
                # Auto-update all plots if focus dataset is loaded
                focus_info = state.get_focus_dataset_info()
                if focus_info and focus_info.status.value == "loaded":
                    for tab_name, tab_widget in self.tab_widgets.items():
                        if hasattr(tab_widget, 'auto_update'):
                            tab_widget.auto_update()
                
                self.logger.debug(f"Focus changed, all plots refreshed")
            
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
    
    def _notify_tabs_focus_changed(self):
        """Notify all tabs that the focus dataset has changed."""
        try:
            # Notify geospatial-based tabs that have the focus change handler
            if hasattr(self, 'geospatial_tab') and hasattr(self.geospatial_tab, 'on_focus_dataset_changed'):
                self.geospatial_tab.on_focus_dataset_changed()
                
            if hasattr(self, 'animation_tab') and hasattr(self.animation_tab, 'on_focus_dataset_changed'):
                self.animation_tab.on_focus_dataset_changed()

            if hasattr(self, 'error_analysis_tab') and hasattr(self.error_analysis_tab, 'on_focus_dataset_changed'):
                self.error_analysis_tab.on_focus_dataset_changed()

            if hasattr(self, 'rms_error_tab') and hasattr(self.rms_error_tab, 'on_focus_dataset_changed'):
                self.rms_error_tab.on_focus_dataset_changed()

            if hasattr(self, 'lifetime_tab') and hasattr(self.lifetime_tab, 'on_focus_dataset_changed'):
                self.lifetime_tab.on_focus_dataset_changed()

            if hasattr(self, 'statistics_tab') and hasattr(self.statistics_tab, 'on_focus_dataset_changed'):
                self.statistics_tab.on_focus_dataset_changed()
                
            if hasattr(self, 'overview_tab') and hasattr(self.overview_tab, 'on_focus_dataset_changed'):
                self.overview_tab.on_focus_dataset_changed()
            
            
            self.logger.debug("All tabs notified of focus dataset change")
            
        except Exception as e:
            self.logger.error(f"Error notifying tabs of focus change: {e}")
    