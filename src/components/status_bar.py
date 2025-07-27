"""
Status Bar Component

This module contains the status bar component that displays
application status information and progress indicators.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Optional, Any


class StatusBar:
    """
    Status bar component that displays application status and progress.
    """
    
    def __init__(self, parent: tk.Widget):
        """
        Initialize the status bar.
        
        Args:
            parent: The parent widget
        """
        self.parent = parent
        self.logger = logging.getLogger(__name__)
        self.controller: Optional[Any] = None
        
        # Create the status bar frame
        self.frame = ttk.Frame(parent, relief="sunken", borderwidth=1)
        
        # Create status elements
        self._create_elements()
        
        # Initialize status
        self.set_status("Ready")
        
        self.logger.debug("Status bar initialized")
    
    def set_controller(self, controller: Any):
        """
        Set the controller for this component.
        
        Args:
            controller: The application controller
        """
        self.controller = controller
        self.logger.debug("Controller set for status bar")
    
    def _create_elements(self):
        """Create all status bar elements."""
        # Main status label
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(
            self.frame,
            textvariable=self.status_var,
            anchor="w"
        )
        self.status_label.pack(side="left", padx=(5, 10), pady=2, fill="x", expand=True)
        
        # Progress bar (initially hidden)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.frame,
            variable=self.progress_var,
            mode="determinate",
            length=200
        )
        # Don't pack initially - will be shown when needed
        
        # Dataset count label
        self.dataset_count_var = tk.StringVar()
        self.dataset_count_label = ttk.Label(
            self.frame,
            textvariable=self.dataset_count_var,
            anchor="center"
        )
        self.dataset_count_label.pack(side="right", padx=(10, 5), pady=2)
        
        # Separator
        separator = ttk.Separator(self.frame, orient="vertical")
        separator.pack(side="right", fill="y", padx=5)
        
        # Current view label
        self.view_var = tk.StringVar()
        self.view_label = ttk.Label(
            self.frame,
            textvariable=self.view_var,
            anchor="center"
        )
        self.view_label.pack(side="right", padx=(10, 5), pady=2)
        
        # Update initial values
        self.dataset_count_var.set("Datasets: 0")
        self.view_var.set("View: Overview")
    
    def set_status(self, message: str):
        """
        Set the main status message.
        
        Args:
            message: The status message to display
        """
        self.status_var.set(message)
        self.logger.debug(f"Status updated: {message}")
    
    def set_progress(self, value: float, visible: bool = True):
        """
        Set the progress bar value and visibility.
        
        Args:
            value: Progress value (0.0 to 1.0)
            visible: Whether the progress bar should be visible
        """
        self.progress_var.set(value * 100)  # Convert to percentage
        
        if visible and not self.progress_bar.winfo_ismapped():
            # Show progress bar
            self.progress_bar.pack(side="right", padx=(5, 10), pady=2)
        elif not visible and self.progress_bar.winfo_ismapped():
            # Hide progress bar
            self.progress_bar.pack_forget()
        
        self.logger.debug(f"Progress updated: {value:.1%}, visible: {visible}")
    
    def set_dataset_count(self, total: int, selected: int = 0, loaded: int = 0):
        """
        Set the dataset count information.
        
        Args:
            total: Total number of datasets
            selected: Number of selected datasets
            loaded: Number of loaded datasets
        """
        if selected > 0 or loaded > 0:
            count_text = f"Datasets: {total} ({selected} selected, {loaded} loaded)"
        else:
            count_text = f"Datasets: {total}"
        
        self.dataset_count_var.set(count_text)
        self.logger.debug(f"Dataset count updated: {count_text}")
    
    def set_current_view(self, view_name: str):
        """
        Set the current view name.
        
        Args:
            view_name: Name of the current view
        """
        self.view_var.set(f"View: {view_name.title()}")
        self.logger.debug(f"Current view updated: {view_name}")
    
    def show_temporary_message(self, message: str, duration: int = 3000):
        """
        Show a temporary message that will revert after a delay.
        
        Args:
            message: The temporary message to show
            duration: Duration in milliseconds to show the message
        """
        # Store the current message
        current_message = self.status_var.get()
        
        # Set the temporary message
        self.set_status(message)
        
        # Schedule revert to original message
        self.frame.after(duration, lambda: self.set_status(current_message))
        
        self.logger.debug(f"Temporary message shown: {message} (duration: {duration}ms)")
    
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
            
            if event == "processing_status_changed":
                self.set_status(state.processing_status)
            
            elif event == "processing_progress_changed":
                # Show progress bar if processing
                is_processing = state.processing_status not in ["Ready", "idle"]
                self.set_progress(state.processing_progress, is_processing)
            
            elif event == "datasets_changed":
                datasets = state.datasets
                selected = state.selected_datasets
                loaded_count = len([d for d in datasets.values() 
                                  if hasattr(d, 'status') and d.status.value == 'loaded'])
                self.set_dataset_count(len(datasets), len(selected), loaded_count)
            
            elif event == "selection_changed":
                datasets = state.datasets
                selected = state.selected_datasets
                loaded_count = len([d for d in datasets.values() 
                                  if hasattr(d, 'status') and d.status.value == 'loaded'])
                self.set_dataset_count(len(datasets), len(selected), loaded_count)
            
            elif event == "view_changed":
                self.set_current_view(state.current_view)
            
        except Exception as e:
            self.logger.error(f"Error handling state change '{event}': {e}")
    
    # Utility Methods
    def clear_progress(self):
        """Clear and hide the progress bar."""
        self.set_progress(0.0, False)
    
    def pulse_progress(self):
        """Start an indeterminate progress animation."""
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start(10)  # 10ms interval
        
        # Show the progress bar
        if not self.progress_bar.winfo_ismapped():
            self.progress_bar.pack(side="right", padx=(5, 10), pady=2)
    
    def stop_pulse_progress(self):
        """Stop the indeterminate progress animation."""
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.clear_progress()
    
    def flash_message(self, message: str, flash_count: int = 3):
        """
        Flash a message by alternating with the current status.
        
        Args:
            message: The message to flash
            flash_count: Number of times to flash
        """
        current_message = self.status_var.get()
        
        def flash_toggle(count_remaining: int, showing_flash: bool):
            if count_remaining <= 0:
                self.set_status(current_message)
                return
            
            if showing_flash:
                self.set_status(current_message)
            else:
                self.set_status(message)
            
            # Schedule next toggle
            self.frame.after(500, lambda: flash_toggle(
                count_remaining - (1 if showing_flash else 0),
                not showing_flash
            ))
        
        # Start flashing
        flash_toggle(flash_count, False)
