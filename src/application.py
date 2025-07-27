"""
Data Analysis Application - Main Application Class

This module contains the main application class that coordinates all components
and manages the application lifecycle.
"""

import tkinter as tk
import logging
from typing import Optional

from .gui.main_window import MainWindow
from .models.application_state import ApplicationState
from .controllers.application_controller import ApplicationController


class DataAnalysisApp:
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
        self.logger.info("Initializing Data Analysis Application")
        
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
            
            # Initialize the view (main window)
            self.view = MainWindow(self.root)
            
            # Initialize the controller
            self.controller = ApplicationController(self.model, self.view)
            
            # Setup the view with the controller
            self.view.set_controller(self.controller)
            
            self.logger.info("Application components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize application components: {e}")
            raise
    
    def run(self, demo_mode=False, demo_duration=None):
        """
        Start the application main loop.
        
        Args:
            demo_mode: If True, run in demo mode with automatic shutdown
            demo_duration: Duration in seconds for demo mode (default 10)
        """
        if not self.root:
            raise RuntimeError("Application not properly initialized")
        
        try:
            self.logger.info("Starting application main loop")
            
            # Configure the main window
            self.root.title("Data Analysis Application")
            self.root.geometry("1200x800")
            self.root.minsize(800, 600)
            
            # If demo mode, schedule automatic shutdown
            if demo_mode:
                duration = demo_duration or 10
                self.logger.info(f"Running in demo mode for {duration} seconds")
                self.root.after(duration * 1000, self.shutdown)
            
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
