"""
Application Controller

This module contains the main application controller that coordinates
between the model (ApplicationState) and view (MainWindow) components.
"""

import logging
from typing import Any, Optional

from ..models.application_state import ApplicationState


class ApplicationController:
    """
    Main application controller that manages the interaction between
    the model and view components following the MVC pattern.
    """
    
    def __init__(self, model: ApplicationState, view: Any):
        """
        Initialize the application controller.
        
        Args:
            model: The application state model
            view: The main window view
        """
        self.model = model
        self.view = view
        self.logger = logging.getLogger(__name__)
        
        # Register as an observer of the model
        self.model.add_observer(self)
        
        # Initialize controller state
        self._initialize_controller()
        
        self.logger.info("Application controller initialized")
    
    def _initialize_controller(self):
        """Initialize the controller and set up initial state."""
        try:
            # Set initial status
            self.model.processing_status = "Ready"
            
            # Any other initialization logic can go here
            
            self.logger.debug("Controller initialization complete")
            
        except Exception as e:
            self.logger.error(f"Error during controller initialization: {e}")
            raise
    
    # Model Observer Interface
    def on_state_changed(self, event: str):
        """
        Handle state changes from the model.
        
        Args:
            event: The type of state change event
        """
        try:
            self.logger.debug(f"Handling state change: {event}")
            
            # Forward the event to the view
            if hasattr(self.view, 'on_state_changed'):
                self.view.on_state_changed(event)
            
        except Exception as e:
            self.logger.error(f"Error handling state change '{event}': {e}")
    
    # View Event Handlers
    def on_window_close(self):
        """Handle main window close event."""
        try:
            self.logger.info("Application shutdown requested")
            
            # Perform any cleanup operations
            self.cleanup()
            
            # Close the application
            self.view.get_root().quit()
            
        except Exception as e:
            self.logger.error(f"Error during application shutdown: {e}")
            # Force quit even if there's an error
            self.view.get_root().quit()
    
    # Menu Actions
    def on_menu_file_open(self):
        """Handle File -> Open menu action."""
        try:
            self.logger.info("File open requested")
            # TODO: Implement file open dialog
            self.model.processing_status = "Opening file..."
            
            # For now, just show a placeholder message
            self.view.show_info("Not Implemented", "File open functionality will be implemented in Phase 2")
            
            self.model.processing_status = "Ready"
            
        except Exception as e:
            self.logger.error(f"Error opening file: {e}")
            self.view.show_error("Error", f"Failed to open file: {e}")
            self.model.processing_status = "Ready"
    
    def on_menu_file_exit(self):
        """Handle File -> Exit menu action."""
        self.on_window_close()
    
    def on_menu_view_toggle_left_panel(self):
        """Handle View -> Toggle Left Panel menu action."""
        try:
            current_state = self.model.left_panel_visible
            self.model.left_panel_visible = not current_state
            self.logger.debug(f"Left panel toggled to: {not current_state}")
        except Exception as e:
            self.logger.error(f"Error toggling left panel: {e}")
    
    def on_menu_view_toggle_right_panel(self):
        """Handle View -> Toggle Right Panel menu action."""
        try:
            current_state = self.model.right_panel_visible
            self.model.right_panel_visible = not current_state
            self.logger.debug(f"Right panel toggled to: {not current_state}")
        except Exception as e:
            self.logger.error(f"Error toggling right panel: {e}")
    
    def on_menu_view_reset_layout(self):
        """Handle View -> Reset Layout menu action."""
        try:
            self.model.left_panel_visible = True
            self.model.right_panel_visible = True
            self.logger.info("Layout reset to default")
        except Exception as e:
            self.logger.error(f"Error resetting layout: {e}")
    
    def on_menu_help_about(self):
        """Handle Help -> About menu action."""
        about_text = (
            "Data Analysis Application\\n"
            "Version 1.0\\n\\n"
            "A tkinter-based GUI for reviewing and analyzing\\n"
            "datasets containing truth, detection, and tracking data.\\n\\n"
            "Phase 1: Core Infrastructure"
        )
        self.view.show_info("About", about_text)
    
    # Status Updates
    def update_status(self, message: str):
        """
        Update the status bar with a message.
        
        Args:
            message: The status message to display
        """
        self.model.processing_status = message
    
    # Data Access Methods for Views
    def get_state(self) -> ApplicationState:
        """Get the current application state."""
        return self.model
    
    def get_datasets(self):
        """Get the current datasets."""
        return self.model.datasets
    
    def get_selected_datasets(self):
        """Get the currently selected datasets."""
        return self.model.selected_datasets
    
    def get_focus_dataset(self):
        """Get the currently focused dataset."""
        return self.model.get_focus_dataset_info()
    
    # Dataset Management (placeholder for future phases)
    def load_dataset_directory(self, directory_path: str):
        """
        Load datasets from a directory.
        
        Args:
            directory_path: Path to the dataset directory
        """
        try:
            self.logger.info(f"Loading dataset directory: {directory_path}")
            # TODO: Implement in Phase 2
            self.view.show_info("Not Implemented", 
                              f"Dataset loading will be implemented in Phase 2\\n"
                              f"Directory: {directory_path}")
        except Exception as e:
            self.logger.error(f"Error loading dataset directory: {e}")
            self.view.show_error("Error", f"Failed to load directory: {e}")
    
    def process_datasets(self, dataset_names: list):
        """
        Process the specified datasets.
        
        Args:
            dataset_names: List of dataset names to process
        """
        try:
            self.logger.info(f"Processing datasets: {dataset_names}")
            # TODO: Implement in Phase 3
            self.view.show_info("Not Implemented", 
                              f"Dataset processing will be implemented in Phase 3\\n"
                              f"Datasets: {', '.join(dataset_names)}")
        except Exception as e:
            self.logger.error(f"Error processing datasets: {e}")
            self.view.show_error("Error", f"Failed to process datasets: {e}")
    
    # Cleanup
    def cleanup(self):
        """Perform cleanup operations."""
        try:
            self.logger.info("Performing cleanup operations")
            
            # Remove observer from model
            self.model.remove_observer(self)
            
            # Any other cleanup operations
            
            self.logger.debug("Cleanup complete")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    # Utility Methods
    def handle_error(self, error: Exception, context: str = ""):
        """
        Handle errors in a consistent way.
        
        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred
        """
        error_msg = f"An error occurred: {error}"
        if context:
            error_msg = f"{context}: {error}"
        
        self.logger.error(error_msg)
        self.view.show_error("Error", error_msg)
        
        # Reset status to ready
        self.model.processing_status = "Ready"
