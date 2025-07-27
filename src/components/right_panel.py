"""
Right Panel Component

This module contains the right panel component that displays
analysis views and visualizations.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Optional, Any


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
        
        # Create the main frame
        self.frame = ttk.Frame(parent)
        
        # Create panel content
        self._create_content()
        
        self.logger.debug("Right panel initialized")
    
    def set_controller(self, controller: Any):
        """
        Set the controller for this component.
        
        Args:
            controller: The application controller
        """
        self.controller = controller
        self.logger.debug("Controller set for right panel")
    
    def _create_content(self):
        """Create the right panel content."""
        # Title
        title_label = ttk.Label(
            self.frame,
            text="Analysis Views",
            font=("TkDefaultFont", 10, "bold")
        )
        title_label.pack(fill="x", padx=10, pady=(10, 5))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create tabs
        self._create_tabs()
    
    def _create_tabs(self):
        """Create the analysis view tabs."""
        # Overview Tab
        self._create_overview_tab()
        
        # Statistics Tab (placeholder)
        self._create_statistics_tab()
        
        # Geospatial Tab (placeholder)
        self._create_geospatial_tab()
        
        # Animation Tab (placeholder)
        self._create_animation_tab()
        
        # Custom Tab (placeholder)
        self._create_custom_tab()
    
    def _create_overview_tab(self):
        """Create the overview tab."""
        overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(overview_frame, text="Overview")
        
        # Welcome message
        welcome_label = ttk.Label(
            overview_frame,
            text="Welcome to the Data Analysis Application",
            font=("TkDefaultFont", 12, "bold")
        )
        welcome_label.pack(pady=(50, 20))
        
        # Information text
        info_text = """This is Phase 1 of the application development.

Current features:
• Basic application window with menu system
• Left panel for dataset management
• Right panel for analysis views
• Status bar with progress indication
• Modular, extensible architecture

Next phases will add:
• Dataset loading and management
• Data visualization with matplotlib
• Interactive plots and analysis tools
• Animation capabilities"""
        
        info_label = ttk.Label(
            overview_frame,
            text=info_text,
            justify="left",
            font=("TkDefaultFont", 10)
        )
        info_label.pack(padx=50, pady=20)
        
        # Instructions
        instructions_label = ttk.Label(
            overview_frame,
            text="Use the File menu to begin working with datasets.",
            font=("TkDefaultFont", 10, "italic")
        )
        instructions_label.pack(pady=(20, 0))
    
    def _create_statistics_tab(self):
        """Create the statistics tab (placeholder)."""
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="Statistics", state="disabled")
        
        # Placeholder content
        placeholder_label = ttk.Label(
            stats_frame,
            text="Statistical Analysis Views\\n\\nThis tab will contain:\\n• Dataset summary statistics\\n• Distribution plots\\n• Error analysis\\n• Track/truth lifetime analysis",
            justify="center",
            font=("TkDefaultFont", 10)
        )
        placeholder_label.pack(expand=True)
    
    def _create_geospatial_tab(self):
        """Create the geospatial tab (placeholder)."""
        geo_frame = ttk.Frame(self.notebook)
        self.notebook.add(geo_frame, text="Geospatial", state="disabled")
        
        # Placeholder content
        placeholder_label = ttk.Label(
            geo_frame,
            text="Geospatial Analysis Views\\n\\nThis tab will contain:\\n• Latitude/longitude scatter plots\\n• Track trajectory overlays\\n• Truth vs detection comparisons\\n• Geographic data visualization",
            justify="center",
            font=("TkDefaultFont", 10)
        )
        placeholder_label.pack(expand=True)
    
    def _create_animation_tab(self):
        """Create the animation tab (placeholder)."""
        anim_frame = ttk.Frame(self.notebook)
        self.notebook.add(anim_frame, text="Animation", state="disabled")
        
        # Placeholder content
        placeholder_label = ttk.Label(
            anim_frame,
            text="Animation Views\\n\\nThis tab will contain:\\n• Time-based track animations\\n• Truth vs track temporal alignment\\n• Playback controls (play, pause, step)\\n• Speed adjustment",
            justify="center",
            font=("TkDefaultFont", 10)
        )
        placeholder_label.pack(expand=True)
    
    def _create_custom_tab(self):
        """Create the custom analysis tab (placeholder)."""
        custom_frame = ttk.Frame(self.notebook)
        self.notebook.add(custom_frame, text="Custom", state="disabled")
        
        # Placeholder content
        placeholder_label = ttk.Label(
            custom_frame,
            text="Custom Analysis Views\\n\\nThis tab will contain:\\n• User-defined plotting tools\\n• Field selection for X/Y axes\\n• Multiple plot types (scatter, line, bar)\\n• Filtering and customization options",
            justify="center",
            font=("TkDefaultFont", 10)
        )
        placeholder_label.pack(expand=True)
    
    def enable_tab(self, tab_name: str, enabled: bool = True):
        """
        Enable or disable a specific tab.
        
        Args:
            tab_name: Name of the tab to enable/disable
            enabled: Whether to enable or disable the tab
        """
        try:
            tab_count = self.notebook.index("end")
            for i in range(tab_count):
                if self.notebook.tab(i, "text") == tab_name:
                    state = "normal" if enabled else "disabled"
                    self.notebook.tab(i, state=state)
                    self.logger.debug(f"Tab '{tab_name}' set to: {state}")
                    break
        except Exception as e:
            self.logger.error(f"Error setting tab state: {e}")
    
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
                # Enable/disable tabs based on available datasets
                has_datasets = len(state.datasets) > 0
                
                # For now, keep tabs disabled until Phase 2+
                # In future phases, we'll enable them based on data availability
                self.logger.debug(f"Datasets available: {has_datasets}")
            
            elif event == "view_changed":
                # Select the appropriate tab based on current view
                current_view = state.current_view
                if current_view == "overview":
                    self.select_tab("Overview")
                elif current_view == "statistics":
                    self.select_tab("Statistics")
                elif current_view == "geospatial":
                    self.select_tab("Geospatial")
                elif current_view == "animation":
                    self.select_tab("Animation")
                elif current_view == "custom":
                    self.select_tab("Custom")
            
        except Exception as e:
            self.logger.error(f"Error handling state change '{event}': {e}")
    
    # Utility Methods
    def add_view_tab(self, name: str, content_widget: tk.Widget):
        """
        Add a new view tab with custom content.
        
        Args:
            name: Name of the new tab
            content_widget: Widget to display in the tab
        """
        try:
            self.notebook.add(content_widget, text=name)
            self.logger.debug(f"Added new tab: {name}")
        except Exception as e:
            self.logger.error(f"Error adding tab: {e}")
    
    def remove_view_tab(self, name: str):
        """
        Remove a view tab.
        
        Args:
            name: Name of the tab to remove
        """
        try:
            tab_count = self.notebook.index("end")
            for i in range(tab_count):
                if self.notebook.tab(i, "text") == name:
                    self.notebook.forget(i)
                    self.logger.debug(f"Removed tab: {name}")
                    break
        except Exception as e:
            self.logger.error(f"Error removing tab: {e}")
    
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
