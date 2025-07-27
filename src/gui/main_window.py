"""
Main Window GUI Component

This module contains the main window class that manages the overall
application layout and coordinates the different panels.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Optional, Any

from matplotlib import style

from ..components.menu_bar import MenuBar
from ..components.status_bar import StatusBar
from ..components.left_panel import LeftPanel
from ..components.right_panel import RightPanel


class MainWindow:
    """
    Main application window that coordinates all GUI components.
    
    This class manages the overall layout and acts as the main View
    component in the MVC pattern.
    """
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the main window.
        
        Args:
            root: The root tkinter window
        """
        self.root = root
        self.logger = logging.getLogger(__name__)
        self.controller: Optional[Any] = None
        
        # GUI Components
        self.menu_bar: Optional[MenuBar] = None
        self.status_bar: Optional[StatusBar] = None
        self.left_panel: Optional[LeftPanel] = None
        self.right_panel: Optional[RightPanel] = None
        
        # Layout frames
        self.main_frame: Optional[ttk.Frame] = None
        self.content_frame: Optional[ttk.Frame] = None
        self.panels_frame: Optional[ttk.Frame] = None
        
        # Panel management
        self.left_panel_visible = True
        self.right_panel_visible = True
        
        # Initialize the window
        self._setup_window()
        self._create_layout()
        self._create_components()
        
        self.logger.info("Main window initialized")
    
    def set_controller(self, controller: Any):
        """
        Set the controller for this view.
        
        Args:
            controller: The application controller
        """
        self.controller = controller
        
        # Pass controller to child components
        if self.menu_bar:
            self.menu_bar.set_controller(controller)
        if self.status_bar:
            self.status_bar.set_controller(controller)
        if self.left_panel:
            self.left_panel.set_controller(controller)
        if self.right_panel:
            self.right_panel.set_controller(controller)
        
        self.logger.debug("Controller set for main window and child components")
    
    def _setup_window(self):
        """Setup the main window properties."""
        # Window properties
        self.root.title("Data Analysis Application")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Configure window closing
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
        
        # Configure grid weights for responsive design
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
    
    def _create_layout(self):
        """Create the main layout structure."""
        # Main frame that contains everything
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        # Style:
        style = ttk.Style()
        style.theme_use('clam')   # <— this theme shows the sash handle
        style.configure('Sash', sashthickness=6, gripcount=300)

        
        # Configure main frame grid
        self.main_frame.grid_rowconfigure(1, weight=1)  # Content area
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Content frame (below menu, above status)
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.grid(row=1, column=0, sticky="nsew", pady=(2, 0))
        
        # Configure content frame grid
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Create a paned window for resizable panels with divider
        self.paned_window = ttk.PanedWindow(self.content_frame, 
                                            orient="horizontal"

                                            # sashwidth=8,  # Increase sash width from default 3px to 8px
                                            # sashrelief=tk.RAISED,  # Add raised relief for 3D effect
                                            # sashpad=2  # Add padding around the sash
        )
        self.paned_window.grid(row=0, column=0, sticky="nsew")
        
        # Configure content frame grid
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
    
    def _create_components(self):
        """Create all GUI components."""
        try:
            # Create menu bar
            self.menu_bar = MenuBar(self.main_frame)
            self.menu_bar.frame.grid(row=0, column=0, sticky="ew")
            
            # Create status bar
            self.status_bar = StatusBar(self.main_frame)
            self.status_bar.frame.grid(row=2, column=0, sticky="ew")
            
            # Create left panel
            self.left_panel = LeftPanel(self.paned_window)
            self.paned_window.add(self.left_panel.frame, weight=1)
            
            # Create right panel
            self.right_panel = RightPanel(self.paned_window)
            self.paned_window.add(self.right_panel.frame, weight=3)  # Right panel gets more space initially
            
            self.logger.debug("All GUI components created")
            
        except Exception as e:
            self.logger.error(f"Error creating GUI components: {e}")
            raise
    
    def _on_window_close(self):
        """Handle window close event."""
        try:
            self.logger.info("Window close requested")
            
            # Ask controller to handle shutdown
            if self.controller and hasattr(self.controller, 'on_window_close'):
                self.controller.on_window_close()
            else:
                # Fallback: just quit
                self.root.quit()
                
        except Exception as e:
            self.logger.error(f"Error during window close: {e}")
            self.root.quit()
    
    # Panel Visibility Management
    def set_left_panel_visible(self, visible: bool):
        """
        Set the visibility of the left panel.
        
        Args:
            visible: Whether the left panel should be visible
        """
        if visible != self.left_panel_visible and self.left_panel:
            self.left_panel_visible = visible
            
            if visible:
                # Re-add the left panel to the paned window
                if self.left_panel.frame not in self.paned_window.panes():
                    self.paned_window.insert(0, self.left_panel.frame, weight=1)
            else:
                # Remove the left panel from the paned window
                if self.left_panel.frame in self.paned_window.panes():
                    self.paned_window.remove(self.left_panel.frame)
            
            self.logger.debug(f"Left panel visibility: {visible}")
    
    def set_right_panel_visible(self, visible: bool):
        """
        Set the visibility of the right panel.
        
        Args:
            visible: Whether the right panel should be visible
        """
        if visible != self.right_panel_visible and self.right_panel:
            self.right_panel_visible = visible
            
            if visible:
                # Re-add the right panel to the paned window
                if self.right_panel.frame not in self.paned_window.panes():
                    self.paned_window.add(self.right_panel.frame, weight=3)
            else:
                # Remove the right panel from the paned window
                if self.right_panel.frame in self.paned_window.panes():
                    self.paned_window.remove(self.right_panel.frame)
            
            self.logger.debug(f"Right panel visibility: {visible}")
    
    # State Update Methods (called by controller)
    def on_state_changed(self, event: str):
        """
        Handle state changes from the application state.
        
        Args:
            event: The type of state change event
        """
        try:
            if event == "panel_visibility_changed":
                # Update panel visibility based on state
                if self.controller:
                    state = self.controller.get_state()
                    self.set_left_panel_visible(state.left_panel_visible)
                    self.set_right_panel_visible(state.right_panel_visible)
            
            # Forward event to child components
            components = [self.menu_bar, self.status_bar, self.left_panel, self.right_panel]
            for component in components:
                if component and hasattr(component, 'on_state_changed'):
                    component.on_state_changed(event)
            
        except Exception as e:
            self.logger.error(f"Error handling state change '{event}': {e}")
    
    # Utility Methods
    def show_error(self, title: str, message: str):
        """Show an error dialog."""
        messagebox.showerror(title, message, parent=self.root)
    
    def show_info(self, title: str, message: str):
        """Show an info dialog."""
        messagebox.showinfo(title, message, parent=self.root)
    
    def show_warning(self, title: str, message: str):
        """Show a warning dialog."""
        messagebox.showwarning(title, message, parent=self.root)
    
    def ask_yes_no(self, title: str, message: str) -> bool:
        """
        Show a yes/no dialog.
        
        Returns:
            True if user clicked Yes, False otherwise
        """
        return messagebox.askyesno(title, message, parent=self.root)
    
    def get_root(self) -> tk.Tk:
        """Get the root tkinter window."""
        return self.root
