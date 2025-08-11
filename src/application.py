"""
Data Analysis Application - Main Application Class

This module contains the main application class that coordinates all components
and manages the application lifecycle.
"""

import tkinter as tk
import logging
from typing import Optional
from pathlib import Path

from .gui.main_window import MainWindow
from .models.application_state import ApplicationState
from .controllers.application_controller import ApplicationController
from .utils.config_loader import ConfigLoader


class TrackViewApp:
    """
    Main application class that orchestrates the entire application.
    
    This class follows the Model-View-Controller (MVC) pattern:
    - Model: ApplicationState
    - View: MainWindow and its components
    - Controller: ApplicationController
    """
    
    def __init__(self):
        """Initialize the application."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing TrackView Application")
        
        # Initialize the main tkinter root
        self.root: Optional[tk.Tk] = None
        
        # MVC Components
        self.model: Optional[ApplicationState] = None
        self.view: Optional[MainWindow] = None
        self.controller: Optional[ApplicationController] = None
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all application components."""
        try:
            # Create the main tkinter root window
            self.root = tk.Tk()
            
            # Initialize the model (application state)
            self.model = ApplicationState()
            
            # Model loads configuration internally; we only need to decide on dataset auto-load
            self._load_startup_configuration()
            
            # Initialize the view (main window)
            self.view = MainWindow(self.root)
            
            # Initialize the controller
            self.controller = ApplicationController(self.model, self.view)
            
            # Setup the view with the controller
            # The view passes the controller to all child components
            self.view.set_controller(self.controller)

            # Trigger an initial state update
            self.model.send_controller_changed_message()
            
            self.logger.info("Application components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize application components: {e}")
            raise
    
    def _load_startup_configuration(self):
        """Load config.yaml and apply values into the model. Auto-populate datasets if directory set."""
        try:
            # Ensure model is available for type checkers and at runtime
            assert self.model is not None
            model = self.model

            config_path = Path(__file__).resolve().parent.parent / "config.yaml"
            loader = ConfigLoader(self.logger)
            cfg = loader.load(config_path)
            ds_dir = cfg.get("DatasetDirectory")
            if ds_dir:
                # Defer actual loading until controller exists: handled in run()
                self._pending_startup_dataset_dir = Path(ds_dir)
            else:
                self._pending_startup_dataset_dir = None
            self.logger.debug(f"Startup dataset_dir from config: {ds_dir}")
        except Exception as e:
            self.logger.error(f"Error loading startup configuration: {e}")
            self._pending_startup_dataset_dir = None

    def run(self):
        """
        Start the application main loop.
        """
        if not self.root:
            raise RuntimeError("Application not properly initialized")
        
        try:
            self.logger.info("Starting application main loop")
            
            # Configure the main window
            self.root.title("TrackView")
            self.root.geometry("1200x800")
            self.root.minsize(800, 600)

            # If a startup dataset directory was configured, kick off loading now
            try:
                if getattr(self, "_pending_startup_dataset_dir", None) and self.controller:
                    # Use controller API so scanning happens in background and UI updates
                    self.controller.load_dataset_directory(str(self._pending_startup_dataset_dir))
            finally:
                # Clear the pending flag to avoid reloading on subsequent runs
                self._pending_startup_dataset_dir = None
            
            # Start the tkinter main loop
            self.root.mainloop()
            
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
            raise
        finally:
            self.logger.info("Application shutting down")
    
    def shutdown(self):
        """Gracefully shutdown the application."""
        try:
            self.logger.info("Shutting down application")
            
            # Cleanup controller
            if self.controller:
                self.controller.cleanup()
            
            # Destroy the main window
            if self.root:
                self.root.quit()
                self.root.destroy()
                
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            raise
