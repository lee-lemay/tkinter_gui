"""
Menu Bar Component

This module contains the menu bar component that provides
the main application menu system.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Optional, Any


class MenuBar:
    """
    Menu bar component that provides the main application menu system.
    """
    
    def __init__(self, parent: tk.Widget):
        """
        Initialize the menu bar.
        
        Args:
            parent: The parent widget
        """
        self.parent = parent
        self.logger = logging.getLogger(__name__)
        self.controller: Optional[Any] = None
        
        # Create the menu bar frame
        self.frame = ttk.Frame(parent)
        
        # Create the menu bar
        self.menubar = tk.Menu(parent)
        
        # Create menus
        self._create_menus()
        
        # Configure the parent to use this menu bar
        if hasattr(parent, 'master') and parent.master:
            parent.master.config(menu=self.menubar)
        elif hasattr(parent, 'config'):
            try:
                parent.config(menu=self.menubar)
            except tk.TclError:
                # If we can't set the menu directly, we'll create a frame-based menu
                self._create_frame_menu()
        
        self.logger.debug("Menu bar initialized")
    
    def set_controller(self, controller: Any):
        """
        Set the controller for this component.
        
        Args:
            controller: The application controller
        """
        self.controller = controller
        self.logger.debug("Controller set for menu bar")
    
    def _create_menus(self):
        """Create all menu items."""
        # File Menu
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.file_menu.add_command(
            label="Open Dataset Directory...",
            command=self._on_file_open,
            accelerator="Ctrl+O"
        )
        self.file_menu.add_separator()
        self.file_menu.add_command(
            label="Recent Directories",
            state="disabled"  # Placeholder for future implementation
        )
        self.file_menu.add_separator()
        self.file_menu.add_command(
            label="Exit",
            command=self._on_file_exit,
            accelerator="Ctrl+Q"
        )
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        
        # View Menu
        self.view_menu = tk.Menu(self.menubar, tearoff=0)
        self.view_menu.add_command(
            label="Toggle Left Panel",
            command=self._on_view_toggle_left_panel,
            accelerator="F9"
        )
        self.view_menu.add_command(
            label="Toggle Right Panel",
            command=self._on_view_toggle_right_panel,
            accelerator="F10"
        )
        self.view_menu.add_separator()
        self.view_menu.add_command(
            label="Zoom In",
            state="disabled",  # Placeholder
            accelerator="Ctrl++"
        )
        self.view_menu.add_command(
            label="Zoom Out",
            state="disabled",  # Placeholder
            accelerator="Ctrl+-"
        )
        self.view_menu.add_command(
            label="Reset Zoom",
            state="disabled",  # Placeholder
            accelerator="Ctrl+0"
        )
        self.view_menu.add_separator()
        self.view_menu.add_command(
            label="Reset Layout",
            command=self._on_view_reset_layout
        )
        self.menubar.add_cascade(label="View", menu=self.view_menu)
        
        # Tools Menu
        self.tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.tools_menu.add_command(
            label="Export Data...",
            state="disabled",  # Placeholder
            accelerator="Ctrl+E"
        )
        self.tools_menu.add_command(
            label="Export Plot...",
            state="disabled",  # Placeholder
            accelerator="Ctrl+Shift+E"
        )
        self.tools_menu.add_separator()
        self.tools_menu.add_command(
            label="Preferences...",
            state="disabled",  # Placeholder
            accelerator="Ctrl+,"
        )
        self.menubar.add_cascade(label="Tools", menu=self.tools_menu)
        
        # Help Menu
        self.help_menu = tk.Menu(self.menubar, tearoff=0)
        self.help_menu.add_command(
            label="User Guide",
            state="disabled",  # Placeholder
            accelerator="F1"
        )
        self.help_menu.add_command(
            label="Keyboard Shortcuts",
            state="disabled",  # Placeholder
            accelerator="Ctrl+?"
        )
        self.help_menu.add_separator()
        self.help_menu.add_command(
            label="About",
            command=self._on_help_about
        )
        self.menubar.add_cascade(label="Help", menu=self.help_menu)
    
    def _create_frame_menu(self):
        """Create a frame-based menu as fallback."""
        # This is a fallback for cases where we can't set the menu bar directly
        menu_frame = ttk.Frame(self.frame)
        menu_frame.pack(fill="x", padx=2, pady=2)
        
        # Create menu buttons
        file_btn = ttk.Menubutton(menu_frame, text="File")
        file_btn.pack(side="left")
        file_btn.configure(menu=self.file_menu)
        
        view_btn = ttk.Menubutton(menu_frame, text="View")
        view_btn.pack(side="left")
        view_btn.configure(menu=self.view_menu)
        
        tools_btn = ttk.Menubutton(menu_frame, text="Tools")
        tools_btn.pack(side="left")
        tools_btn.configure(menu=self.tools_menu)
        
        help_btn = ttk.Menubutton(menu_frame, text="Help")
        help_btn.pack(side="right")
        help_btn.configure(menu=self.help_menu)
    
    # Menu Event Handlers
    def _on_file_open(self):
        """Handle File -> Open menu action."""
        if self.controller:
            self.controller.on_menu_file_open()
        else:
            self.logger.warning("No controller set for file open action")
    
    def _on_file_exit(self):
        """Handle File -> Exit menu action."""
        if self.controller:
            self.controller.on_menu_file_exit()
        else:
            self.logger.warning("No controller set for file exit action")
    
    def _on_view_toggle_left_panel(self):
        """Handle View -> Toggle Left Panel menu action."""
        if self.controller:
            self.controller.on_menu_view_toggle_left_panel()
        else:
            self.logger.warning("No controller set for toggle left panel action")
    
    def _on_view_toggle_right_panel(self):
        """Handle View -> Toggle Right Panel menu action."""
        if self.controller:
            self.controller.on_menu_view_toggle_right_panel()
        else:
            self.logger.warning("No controller set for toggle right panel action")
    
    def _on_view_reset_layout(self):
        """Handle View -> Reset Layout menu action."""
        if self.controller:
            self.controller.on_menu_view_reset_layout()
        else:
            self.logger.warning("No controller set for reset layout action")
    
    def _on_help_about(self):
        """Handle Help -> About menu action."""
        if self.controller:
            self.controller.on_menu_help_about()
        else:
            self.logger.warning("No controller set for help about action")
    
    # State Management
    def on_state_changed(self, event: str):
        """
        Handle state changes from the application.
        
        Args:
            event: The type of state change event
        """
        # Menu bar doesn't need to react to most state changes
        # but this method is here for consistency
        pass
    
    # Utility Methods
    def enable_menu_item(self, menu_path: str, enabled: bool = True):
        """
        Enable or disable a menu item.
        
        Args:
            menu_path: Path to the menu item (e.g., "file.open")
            enabled: Whether to enable or disable the item
        """
        try:
            state = "normal" if enabled else "disabled"
            # This would require more complex menu management
            # For now, it's a placeholder for future enhancement
            self.logger.debug(f"Menu item '{menu_path}' set to: {state}")
        except Exception as e:
            self.logger.error(f"Error setting menu item state: {e}")
    
    def update_recent_files(self, file_paths: list):
        """
        Update the recent files menu.
        
        Args:
            file_paths: List of recent file paths
        """
        # Placeholder for future implementation
        self.logger.debug(f"Recent files updated: {len(file_paths)} items")
