"""
Left Panel Component

This module contains the left panel component that displays
dataset information and selection controls.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Optional, Any


class LeftPanel:
    """
    Left panel component that provides dataset overview and selection.
    """
    
    def __init__(self, parent: tk.Widget):
        """
        Initialize the left panel.
        
        Args:
            parent: The parent widget
        """
        self.parent = parent
        self.logger = logging.getLogger(__name__)
        self.controller: Optional[Any] = None
        
        # Create the main frame
        self.frame = ttk.Frame(parent, width=300)
        self.frame.pack_propagate(False)  # Maintain fixed width
        
        # Create panel sections
        self._create_sections()
        
        self.logger.debug("Left panel initialized")
    
    def set_controller(self, controller: Any):
        """
        Set the controller for this component.
        
        Args:
            controller: The application controller
        """
        self.controller = controller
        self.logger.debug("Controller set for left panel")
    
    def _create_sections(self):
        """Create all sections of the left panel."""
        # Title
        title_label = ttk.Label(
            self.frame,
            text="Dataset Management",
            font=("TkDefaultFont", 10, "bold")
        )
        title_label.pack(fill="x", padx=10, pady=(10, 5))
        
        # Dataset Overview Section
        self._create_dataset_overview_section()
        
        # Separator
        ttk.Separator(self.frame, orient="horizontal").pack(fill="x", padx=10, pady=10)
        
        # Current Dataset Focus Section
        self._create_focus_section()
    
    def _create_dataset_overview_section(self):
        """Create the dataset overview section."""
        # Section header
        overview_frame = ttk.LabelFrame(self.frame, text="Dataset Overview", padding=5)
        overview_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Dataset list with scrollbar
        list_frame = ttk.Frame(overview_frame)
        list_frame.pack(fill="both", expand=True)
        
        # Create treeview for datasets with detailed columns
        columns = ("Loaded", "Date", "Size MB", "PKL", "Truth", "Detections", "Tracks")
        self.dataset_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="tree headings",
            height=8
        )
        
        # Configure columns with appropriate widths
        self.dataset_tree.heading("#0", text="Dataset Name")
        self.dataset_tree.column("#0", width=140, anchor="w")
        
        # Column configurations with optimal widths for visibility
        column_configs = {
            "Loaded": {"width": 60, "anchor": "center"},
            "Date": {"width": 80, "anchor": "center"},
            "Size MB": {"width": 65, "anchor": "e"},
            "PKL": {"width": 40, "anchor": "center"},
            "Truth": {"width": 50, "anchor": "center"},
            "Detections": {"width": 75, "anchor": "center"},
            "Tracks": {"width": 55, "anchor": "center"}
        }
        
        for col in columns:
            self.dataset_tree.heading(col, text=col)
            config = column_configs[col]
            self.dataset_tree.column(col, width=config["width"], anchor=config["anchor"])
        
        # Scrollbar for treeview
        tree_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.dataset_tree.yview)
        self.dataset_tree.configure(yscrollcommand=tree_scroll.set)
        
        # Pack treeview and scrollbar
        self.dataset_tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")
        
        # Bind selection event
        self.dataset_tree.bind("<<TreeviewSelect>>", self._on_dataset_selection)
        
        # Bind double-click to load dataset
        self.dataset_tree.bind("<Double-1>", self._on_dataset_double_click)
        
        # Control buttons frame
        buttons_frame = ttk.Frame(overview_frame)
        buttons_frame.pack(fill="x", pady=(5, 0))
        
        # Use PKL files button
        self.use_pkl_btn = ttk.Button(
            buttons_frame,
            text="Use PKL Files",
            command=self._on_use_pkl_files,
            state="disabled"
        )
        self.use_pkl_btn.pack(side="left", padx=(0, 5))
        
        # Process datasets button
        self.process_btn = ttk.Button(
            buttons_frame,
            text="Process Selected",
            command=self._on_process_datasets,
            state="disabled"
        )
        self.process_btn.pack(side="right")
    
    def _create_focus_section(self):
        """Create the current dataset focus section."""
        # Section header
        focus_frame = ttk.LabelFrame(self.frame, text="Focus Dataset", padding=5)
        focus_frame.pack(fill="x", padx=10, pady=5)
        
        # Dataset info display
        info_frame = ttk.Frame(focus_frame)
        info_frame.pack(fill="x")
        
        # Name
        ttk.Label(info_frame, text="Name:").grid(row=0, column=0, sticky="w", pady=1)
        self.focus_name_var = tk.StringVar(value="None")
        ttk.Label(info_frame, textvariable=self.focus_name_var, font=("TkDefaultFont", 9)).grid(
            row=0, column=1, sticky="w", padx=(5, 0), pady=1
        )
        
        # Date and Duration
        ttk.Label(info_frame, text="Date:").grid(row=1, column=0, sticky="w", pady=1)
        self.focus_date_var = tk.StringVar(value="-")
        ttk.Label(info_frame, textvariable=self.focus_date_var, font=("TkDefaultFont", 9)).grid(
            row=1, column=1, sticky="w", padx=(5, 0), pady=1
        )
        
        # Counts
        ttk.Label(info_frame, text="Tracks:").grid(row=2, column=0, sticky="w", pady=1)
        self.focus_tracks_var = tk.StringVar(value="-")
        ttk.Label(info_frame, textvariable=self.focus_tracks_var, font=("TkDefaultFont", 9)).grid(
            row=2, column=1, sticky="w", padx=(5, 0), pady=1
        )
        
        ttk.Label(info_frame, text="Detections:").grid(row=3, column=0, sticky="w", pady=1)
        self.focus_detections_var = tk.StringVar(value="-")
        ttk.Label(info_frame, textvariable=self.focus_detections_var, font=("TkDefaultFont", 9)).grid(
            row=3, column=1, sticky="w", padx=(5, 0), pady=1
        )
        
        ttk.Label(info_frame, text="Truth:").grid(row=4, column=0, sticky="w", pady=1)
        self.focus_truth_var = tk.StringVar(value="-")
        ttk.Label(info_frame, textvariable=self.focus_truth_var, font=("TkDefaultFont", 9)).grid(
            row=4, column=1, sticky="w", padx=(5, 0), pady=1
        )
        
        # Configure grid weights
        info_frame.grid_columnconfigure(1, weight=1)
        
        # Processing controls (placeholder for future phases)
        controls_frame = ttk.Frame(focus_frame)
        controls_frame.pack(fill="x", pady=(10, 0))
        
        # Association range
        ttk.Label(controls_frame, text="Association Range:").pack(anchor="w")
        range_frame = ttk.Frame(controls_frame)
        range_frame.pack(fill="x", pady=(2, 5))
        
        self.range_var = tk.StringVar(value="100.0")
        range_entry = ttk.Entry(range_frame, textvariable=self.range_var, width=10)
        range_entry.pack(side="left")
        ttk.Label(range_frame, text="meters").pack(side="left", padx=(5, 0))
        
        # Reprocess button
        self.reprocess_btn = ttk.Button(
            controls_frame,
            text="Reprocess",
            command=self._on_reprocess,
            state="disabled"
        )
        self.reprocess_btn.pack(anchor="e")
    
    # Event Handlers
    def _on_dataset_selection(self, event):
        """Handle dataset selection in the treeview."""
        selection = self.dataset_tree.selection()
        if selection and self.controller:
            dataset_name = self.dataset_tree.item(selection[0])["text"]
            self.logger.debug(f"Dataset selected: {dataset_name}")
            # Set as focus dataset
            self.controller.set_focus_dataset(dataset_name)
    
    def _on_dataset_double_click(self, event):
        """Handle double-click on dataset to load it."""
        selection = self.dataset_tree.selection()
        if selection and self.controller:
            dataset_name = self.dataset_tree.item(selection[0])["text"]
            self.logger.debug(f"Dataset double-clicked for loading: {dataset_name}")
            # Load the dataset
            self.controller.load_single_dataset(dataset_name)
    
    def _on_use_pkl_files(self):
        """Handle Use PKL Files button click."""
        self.logger.info("Use PKL files requested")
        if self.controller:
            # TODO: Implement PKL file loading in future phase
            selected = self._get_selected_dataset_names()
            if selected:
                message = f"PKL file loading for:\\n\\n" + "\\n".join([f"• {name}" for name in selected])
                message += "\\n\\nThis feature will be implemented in a future phase."
                self.controller.view.show_info("PKL Loading", message)
            else:
                self.controller.view.show_info("No Selection", "Please select datasets first.")
    
    def _on_process_datasets(self):
        """Handle Process Selected button click."""
        self.logger.info("Process datasets requested")
        if self.controller:
            selected = self._get_selected_dataset_names()
            if selected:
                self.controller.process_datasets(selected)
            else:
                self.controller.view.show_info("No Selection", "Please select datasets to process.")
    
    def _on_reprocess(self):
        """Handle Reprocess button click."""
        self.logger.info("Reprocess requested")
        if self.controller:
            focus_dataset = self.controller.get_focus_dataset()
            if focus_dataset:
                self.controller.process_datasets([focus_dataset.name])
            else:
                self.controller.view.show_info("No Focus Dataset", "Please select a focus dataset first.")
    
    # Helper Methods
    def _get_selected_dataset_names(self):
        """Get the names of selected datasets."""
        selected_items = self.dataset_tree.selection()
        dataset_names = []
        
        for item in selected_items:
            dataset_name = self.dataset_tree.item(item)["text"]
            dataset_names.append(dataset_name)
        
        return dataset_names
    
    def _update_dataset_tree(self, datasets):
        """Update the dataset treeview with current datasets."""
        # Clear existing items
        for item in self.dataset_tree.get_children():
            self.dataset_tree.delete(item)
        
        # Add datasets with detailed information
        for name, dataset_info in datasets.items():
            # Loaded status based on DatasetStatus
            if dataset_info.status.value == "loaded":
                loaded_status = "✓"
            elif dataset_info.status.value == "loading":
                loaded_status = "⏳"
            elif dataset_info.status.value == "error":
                loaded_status = "❌"
            else:
                loaded_status = "✗"
            
            # Date (formatted for display)
            date_str = "-"
            if dataset_info.last_modified:
                try:
                    from datetime import datetime
                    if isinstance(dataset_info.last_modified, str):
                        # Try to parse common date formats
                        for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%m/%d/%Y"]:
                            try:
                                dt = datetime.strptime(dataset_info.last_modified, fmt)
                                date_str = dt.strftime("%m/%d/%y")
                                break
                            except ValueError:
                                continue
                        if date_str == "-":
                            # If parsing fails, use first 8 characters
                            date_str = dataset_info.last_modified[:8]
                    else:
                        date_str = str(dataset_info.last_modified)[:8]
                except:
                    date_str = "-"
            
            # Size in MB (formatted to 1 decimal place)
            size_mb_str = "-"
            if dataset_info.size_bytes and dataset_info.size_bytes > 0:
                size_mb = dataset_info.size_bytes / (1024 * 1024)
                if size_mb >= 100:
                    size_mb_str = f"{size_mb:.0f}"
                elif size_mb >= 10:
                    size_mb_str = f"{size_mb:.1f}"
                else:
                    size_mb_str = f"{size_mb:.2f}"
            
            # PKL file existence (green check or red X)
            pkl_status = "✓" if dataset_info.has_pkl else "✗"
            
            # Data indicators - show counts if loaded, otherwise availability
            if dataset_info.status.value == "loaded":
                # Show actual counts for loaded datasets
                truth_str = str(len(dataset_info.truth_df)) if dataset_info.truth_df is not None else "0"
                detections_str = str(len(dataset_info.detections_df)) if dataset_info.detections_df is not None else "0"
                
                # For tracks, count unique track IDs if available
                if dataset_info.tracks_df is not None and not dataset_info.tracks_df.empty:
                    if 'track_id' in dataset_info.tracks_df.columns:
                        tracks_str = str(len(dataset_info.tracks_df['track_id'].unique()))
                    else:
                        tracks_str = str(len(dataset_info.tracks_df))
                else:
                    tracks_str = "0"
            else:
                # Show availability indicators for unloaded datasets
                truth_str = "✓" if dataset_info.has_truth else "✗"
                detections_str = "✓" if dataset_info.has_detections else "✗"
                tracks_str = "✓" if dataset_info.has_tracks else "✗"
            
            # Insert item with all detailed information
            self.dataset_tree.insert(
                "",
                "end",
                text=name,
                values=(loaded_status, date_str, size_mb_str, pkl_status, truth_str, detections_str, tracks_str)
            )
    
    def _update_focus_info(self, dataset_info):
        """Update the focus dataset information display."""
        if dataset_info:
            self.focus_name_var.set(dataset_info.name)
            self.focus_date_var.set(dataset_info.last_modified or "-")
            
            # Show actual counts if dataset is loaded
            if dataset_info.status.value == "loaded":
                # Calculate actual counts from loaded DataFrames
                tracks_count = 0
                detections_count = 0
                truth_count = 0
                
                if dataset_info.tracks_df is not None and not dataset_info.tracks_df.empty:
                    # Count unique track IDs
                    if 'track_id' in dataset_info.tracks_df.columns:
                        tracks_count = len(dataset_info.tracks_df['track_id'].unique())
                    else:
                        tracks_count = len(dataset_info.tracks_df)
                
                if dataset_info.detections_df is not None and not dataset_info.detections_df.empty:
                    detections_count = len(dataset_info.detections_df)
                
                if dataset_info.truth_df is not None and not dataset_info.truth_df.empty:
                    truth_count = len(dataset_info.truth_df)
                
                self.focus_tracks_var.set(str(tracks_count))
                self.focus_detections_var.set(str(detections_count))
                self.focus_truth_var.set(str(truth_count))
            else:
                # Show availability indicators if not loaded
                tracks_status = "✓" if dataset_info.has_tracks else "✗"
                detections_status = "✓" if dataset_info.has_detections else "✗"
                truth_status = "✓" if dataset_info.has_truth else "✗"
                
                self.focus_tracks_var.set(tracks_status)
                self.focus_detections_var.set(detections_status)
                self.focus_truth_var.set(truth_status)
        else:
            self.focus_name_var.set("None")
            self.focus_date_var.set("-")
            self.focus_tracks_var.set("-")
            self.focus_detections_var.set("-")
            self.focus_truth_var.set("-")
    
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
                self._update_dataset_tree(state.datasets)
                
                # Update button states (enable Process when datasets exist)
                dataset_names = list(state.datasets.keys())
                has_datasets = len(dataset_names) > 0
                self.process_btn.configure(state="normal" if has_datasets else "disabled")
            
            elif event == "focus_changed":
                focus_info = state.get_focus_dataset_info()
                self._update_focus_info(focus_info)
                
                # Enable/disable reprocess based on focus availability
                if focus_info:
                    self.reprocess_btn.configure(state="normal")
                else:
                    self.reprocess_btn.configure(state="disabled")
            
        except Exception as e:
            self.logger.error(f"Error handling state change '{event}': {e}")
