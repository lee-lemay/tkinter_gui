"""
Application Controller

This module contains the main application controller that coordinates
between the model (ApplicationState) and view (MainWindow) components.
"""

import logging
from typing import Any, Optional
from pathlib import Path
from tkinter import filedialog, messagebox
import threading

from ..models.application_state import ApplicationState, DatasetInfo, DatasetStatus
from ..utils.dataset_scanner import DatasetScanner
from ..business.data_interface import MockDataInterface


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
        
        # Initialize business logic components
        self.dataset_scanner = DatasetScanner()
        self.data_interface = MockDataInterface()
        
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
        """Handle File -> Open Dataset Directory menu action."""
        try:
            self.logger.info("Dataset directory selection requested")
            
            # Show directory selection dialog
            directory_path = filedialog.askdirectory(
                title="Select Dataset Directory",
                mustexist=True
            )
            
            if directory_path:
                self.load_dataset_directory(directory_path)
            else:
                self.logger.debug("Directory selection cancelled")
            
        except Exception as e:
            self.logger.error(f"Error opening directory dialog: {e}")
            self.view.show_error("Error", f"Failed to open directory selection: {e}")
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
            "Phase 3: Data Management - ACTIVE"
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
    
    # Dataset Management - Phase 3 Implementation
    def load_dataset_directory(self, directory_path: str):
        """
        Load datasets from a directory.
        
        Args:
            directory_path: Path to the dataset directory
        """
        try:
            self.logger.info(f"Loading dataset directory: {directory_path}")
            self.model.processing_status = "Scanning for datasets..."
            
            # Set the dataset directory in the model
            self.model.dataset_directory = Path(directory_path)
            
            # Clear existing datasets
            self.model.clear_datasets()
            
            # Scan for datasets in a separate thread to avoid blocking UI
            threading.Thread(
                target=self._scan_datasets_thread,
                args=(Path(directory_path),),
                daemon=True
            ).start()
            
        except Exception as e:
            self.logger.error(f"Error loading dataset directory: {e}")
            self.view.show_error("Error", f"Failed to load directory: {e}")
            self.model.processing_status = "Ready"
    
    def _scan_datasets_thread(self, directory_path: Path):
        """
        Scan for datasets in a background thread.
        
        Args:
            directory_path: Path to scan for datasets
        """
        try:
            # Discover datasets
            datasets = self.dataset_scanner.scan_directory(directory_path)
            
            # Add discovered datasets to the model
            for dataset_info in datasets:
                self.model.add_dataset(dataset_info)
            
            # Update status
            if datasets:
                self.model.processing_status = f"Found {len(datasets)} datasets"
                self.logger.info(f"Successfully loaded {len(datasets)} datasets")
            else:
                self.model.processing_status = "No datasets found"
                self.logger.warning("No valid datasets found in directory")
            
        except Exception as e:
            self.logger.error(f"Error scanning for datasets: {e}")
            self.model.processing_status = f"Error: {str(e)}"
    
    def load_single_dataset(self, dataset_name: str):
        """
        Load data for a single dataset.
        
        Args:
            dataset_name: Name of the dataset to load
        """
        try:
            dataset_info = self.model.datasets.get(dataset_name)
            if not dataset_info:
                raise ValueError(f"Dataset not found: {dataset_name}")
            
            self.logger.info(f"Loading dataset: {dataset_name}")
            self.model.processing_status = f"Loading {dataset_name}..."
            
            # Update dataset status
            dataset_info.status = DatasetStatus.LOADING
            self.model.add_dataset(dataset_info)  # Trigger update
            
            # Load dataset in background thread
            threading.Thread(
                target=self._load_dataset_thread,
                args=(dataset_info,),
                daemon=True
            ).start()
            
        except Exception as e:
            self.logger.error(f"Error starting dataset load: {e}")
            self.view.show_error("Error", f"Failed to load dataset: {e}")
            self.model.processing_status = "Ready"
    
    def _load_dataset_thread(self, dataset_info: DatasetInfo):
        """
        Load a dataset in a background thread.
        
        Args:
            dataset_info: Dataset information object
        """
        try:
            # Load the dataset using the data interface
            dataframes = self.data_interface.load_dataset(dataset_info.path)
            
            # Store the loaded data
            dataset_info.truth_df = dataframes.get('truth')
            dataset_info.detections_df = dataframes.get('detections')
            dataset_info.tracks_df = dataframes.get('tracks')
            
            # Update status to loaded
            dataset_info.status = DatasetStatus.LOADED
            self.model.add_dataset(dataset_info)  # Trigger update
            
            self.model.processing_status = f"Loaded {dataset_info.name}"
            self.logger.info(f"Successfully loaded dataset: {dataset_info.name}")
            
        except Exception as e:
            self.logger.error(f"Error loading dataset {dataset_info.name}: {e}")
            dataset_info.status = DatasetStatus.ERROR
            dataset_info.error_message = str(e)
            self.model.add_dataset(dataset_info)  # Trigger update
            self.model.processing_status = f"Error loading {dataset_info.name}"
    
    def process_datasets(self, dataset_names: list):
        """
        Process the specified datasets.
        
        Args:
            dataset_names: List of dataset names to process
        """
        try:
            self.logger.info(f"Processing datasets: {dataset_names}")
            self.model.processing_status = f"Processing {len(dataset_names)} datasets..."
            
            # For now, just show a confirmation that processing would begin
            dataset_list = "\\n".join([f"• {name}" for name in dataset_names])
            message = (f"Dataset processing initiated for:\\n\\n{dataset_list}\\n\\n"
                      f"This would normally trigger business logic analysis.")
            
            self.view.show_info("Processing Started", message)
            self.model.processing_status = "Ready"
            
        except Exception as e:
            self.logger.error(f"Error processing datasets: {e}")
            self.view.show_error("Error", f"Failed to process datasets: {e}")
            self.model.processing_status = "Ready"
    
    # Dataset Selection Management
    def set_focus_dataset(self, dataset_name: Optional[str]):
        """
        Set the focus dataset.
        
        Args:
            dataset_name: Name of dataset to focus on, or None to clear focus
        """
        try:
            self.model.focus_dataset = dataset_name
            if dataset_name:
                self.logger.debug(f"Focus set to dataset: {dataset_name}")
            else:
                self.logger.debug("Focus cleared")
        except Exception as e:
            self.logger.error(f"Error setting focus dataset: {e}")
    
    def toggle_dataset_selection(self, dataset_name: str):
        """
        Toggle the selection state of a dataset.
        
        Args:
            dataset_name: Name of dataset to toggle
        """
        try:
            if dataset_name in self.model.selected_datasets:
                self.model.remove_selected_dataset(dataset_name)
            else:
                self.model.add_selected_dataset(dataset_name)
        except Exception as e:
            self.logger.error(f"Error toggling dataset selection: {e}")
    
    def refresh_datasets(self):
        """Refresh the dataset list by rescanning the current directory."""
        try:
            if self.model.dataset_directory:
                self.load_dataset_directory(str(self.model.dataset_directory))
            else:
                self.logger.warning("No dataset directory set for refresh")
                self.view.show_info("No Directory", "Please select a dataset directory first")
        except Exception as e:
            self.logger.error(f"Error refreshing datasets: {e}")
            self.view.show_error("Error", f"Failed to refresh datasets: {e}")
    
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
