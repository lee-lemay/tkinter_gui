"""
Menu Bar Component

This module contains the menu bar component that provides
the main application menu system.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Optional, Any
from pathlib import Path


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

        # Initialize recent directories start index
        self._recent_dirs_start_index = 2  # Default position after "Open..." and first separator
        
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
        
        if hasattr(self.controller, 'model'):
            self.controller.model.add_observer(self)
    
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
        
        # Placeholder for recent directories (will be populated dynamically)
        # We'll track the separator index to insert recent directories after it
        self._recent_dirs_start_index = self.file_menu.index('end') + 1
        
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
        if event == "recent_directories_changed" or event == "controller_changed":
            self._update_recent_directories_menu()
    
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
    def _update_recent_directories_menu(self):
        """Update the recent directories in the File menu."""
        try:
            # Remove existing recent directory menu items
            self._remove_recent_directory_items()
            
            if not self.controller:
                # Add "No Recent Directories" placeholder
                insert_index = self._recent_dirs_start_index
                self.file_menu.insert_command(
                    insert_index,
                    label="Recent Directories:",
                    state="disabled"
                )
                self.file_menu.insert_command(
                    insert_index + 1,
                    label="No Recent Directories",
                    state="disabled"
                )
                return
            
            # Get recent directories from controller
            state = self.controller.get_state()
            recent_dirs = state.recent_directories
            
            # Add "Recent Directories:" header
            insert_index = self._recent_dirs_start_index
            self.file_menu.insert_command(
                insert_index,
                label="Recent Directories:",
                state="disabled"
            )
            insert_index += 1
            
            if not recent_dirs:
                # No recent directories
                self.file_menu.insert_command(
                    insert_index,
                    label="No Recent Directories",
                    state="disabled"
                )
            else:
                # Add each recent directory
                for i, directory in enumerate(recent_dirs):
                    # Show just the directory name, not full path
                    display_name = Path(directory).name
                    if not display_name:
                        display_name = str(Path(directory))
                    
                    # Limit display name length
                    if len(display_name) > 35:
                        display_name = display_name[:32] + "..."
                    
                    self.file_menu.insert_command(
                        insert_index,
                        label=f"{i+1}: {display_name}",
                        command=lambda path=directory: self._on_recent_directory_selected(path)
                    )
                    insert_index += 1
        
        except Exception as e:
            self.logger.error(f"Error updating recent directories menu: {e}")
    
    def _remove_recent_directory_items(self):
        """Remove existing recent directory items from the File menu."""
        try:
            # Find the range of items to remove (between the two separators)
            try:
                menu_length = self.file_menu.index('end')
            except tk.TclError:
                # Menu is empty or has no items
                return
            
            if menu_length is None:
                return
                
            # Remove items from the end backwards to avoid index shifting
            items_to_remove = []
            
            # Look for items after our start index and before the Exit command
            for i in range(self._recent_dirs_start_index, menu_length + 1):
                try:
                    menu_type = self.file_menu.type(i)
                    label = self.file_menu.entrycget(i, 'label')
                    
                    # Stop when we hit the Exit command
                    if label == "Exit":
                        break
                    
                    # Mark items for removal (recent dirs header, directories, and "No Recent Directories")
                    if (menu_type == 'command' and 
                        (label == "Recent Directories:" or
                         label == "No Recent Directories" or
                         (len(label) > 2 and label[1] == ':' and label[0].isdigit()))):
                        items_to_remove.append(i)
                        
                except tk.TclError:
                    # Index doesn't exist, we've gone too far
                    break
            
            # Remove items (backwards to maintain indices)
            for index in reversed(items_to_remove):
                self.file_menu.delete(index)
                
        except Exception as e:
            self.logger.error(f"Error removing recent directory items: {e}")
    
    def _on_recent_directory_selected(self, directory_path: str):
        """Handle selection of a recent directory."""
        try:
            self.logger.info(f"Recent directory selected: {directory_path}")
            if self.controller:
                # Check if directory still exists
                if Path(directory_path).exists():
                    self.controller.load_dataset_directory(directory_path)
                else:
                    from tkinter import messagebox
                    messagebox.showerror(
                        "Directory Not Found",
                        f"The directory no longer exists:\n{directory_path}"
                    )
                    # Remove from recent directories
                    self.controller.remove_recent_directory(directory_path)
            else:
                self.logger.warning("No controller set for recent directory selection")
        except Exception as e:
            self.logger.error(f"Error opening recent directory: {e}")
    
    def _on_clear_recent_directories(self):
        """Handle clearing of recent directories."""
        try:
            from tkinter import messagebox
            if messagebox.askyesno(
                "Clear Recent Directories",
                "Are you sure you want to clear all recent directories?"
            ):
                if self.controller:
                    self.controller.clear_recent_directories()
                else:
                    self.logger.warning("No controller set for clearing recent directories")
        except Exception as e:
            self.logger.error(f"Error clearing recent directories: {e}")