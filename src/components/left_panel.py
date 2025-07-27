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
        
        # Separator
        ttk.Separator(self.frame, orient="horizontal").pack(fill="x", padx=10, pady=10)
        
        # Dataset Selection Controls
        self._create_selection_controls()
    
    def _create_dataset_overview_section(self):
        """Create the dataset overview section."""
        # Section header
        overview_frame = ttk.LabelFrame(self.frame, text="Dataset Overview", padding=5)
        overview_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Dataset list with scrollbar
        list_frame = ttk.Frame(overview_frame)
        list_frame.pack(fill="both", expand=True)
        
        # Create treeview for datasets
        columns = ("Status", "Type", "Size")
        self.dataset_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="tree headings",
            height=8
        )
        
        # Configure columns
        self.dataset_tree.heading("#0", text="Dataset Name")
        self.dataset_tree.column("#0", width=120, anchor="w")
        
        for col in columns:
            self.dataset_tree.heading(col, text=col)
            if col == "Status":
                self.dataset_tree.column(col, width=60, anchor="center")
            elif col == "Type":
                self.dataset_tree.column(col, width=80, anchor="center")
            else:  # Size
                self.dataset_tree.column(col, width=60, anchor="e")
        
        # Scrollbar for treeview
        tree_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.dataset_tree.yview)
        self.dataset_tree.configure(yscrollcommand=tree_scroll.set)
        
        # Pack treeview and scrollbar
        self.dataset_tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")
        
        # Bind selection event
        self.dataset_tree.bind("<<TreeviewSelect>>", self._on_dataset_selection)
        
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
        
        # Method selection
        ttk.Label(controls_frame, text="Method:").pack(anchor="w")
        self.method_var = tk.StringVar(value="Nearest Neighbor")
        method_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.method_var,
            values=["Nearest Neighbor", "Hungarian", "Global Nearest"],
            state="readonly",
            width=18
        )
        method_combo.pack(fill="x", pady=(2, 5))
        
        # Reprocess button
        self.reprocess_btn = ttk.Button(
            controls_frame,
            text="Reprocess",
            command=self._on_reprocess,
            state="disabled"
        )
        self.reprocess_btn.pack(anchor="e")
    
    def _create_selection_controls(self):
        """Create the dataset selection controls section."""
        # Section header
        selection_frame = ttk.LabelFrame(self.frame, text="Selection Controls", padding=5)
        selection_frame.pack(fill="x", padx=10, pady=5)
        
        # Focus dataset selection
        ttk.Label(selection_frame, text="Focus Dataset:").pack(anchor="w")
        self.focus_combo_var = tk.StringVar()
        self.focus_combo = ttk.Combobox(
            selection_frame,
            textvariable=self.focus_combo_var,
            state="readonly",
            width=25
        )
        self.focus_combo.pack(fill="x", pady=(2, 5))
        self.focus_combo.bind("<<ComboboxSelected>>", self._on_focus_changed)
        
        # Selection buttons
        buttons_frame = ttk.Frame(selection_frame)
        buttons_frame.pack(fill="x")
        
        # Select All button
        select_all_btn = ttk.Button(
            buttons_frame,
            text="Select All",
            command=self._on_select_all
        )
        select_all_btn.pack(side="left")
        
        # Select None button
        select_none_btn = ttk.Button(
            buttons_frame,
            text="Select None",
            command=self._on_select_none
        )
        select_none_btn.pack(side="left", padx=(5, 0))
        
        # Refresh button
        refresh_btn = ttk.Button(
            buttons_frame,
            text="Refresh",
            command=self._on_refresh
        )
        refresh_btn.pack(side="right")
    
    # Event Handlers
    def _on_dataset_selection(self, event):
        """Handle dataset selection in the treeview."""
        selection = self.dataset_tree.selection()
        if selection:
            dataset_name = self.dataset_tree.item(selection[0])["text"]
            self.logger.debug(f"Dataset selected: {dataset_name}")
            # TODO: Update focus dataset
    
    def _on_use_pkl_files(self):
        """Handle Use PKL Files button click."""
        self.logger.info("Use PKL files requested")
        if self.controller:
            # TODO: Implement PKL file loading
            pass
    
    def _on_process_datasets(self):
        """Handle Process Selected button click."""
        self.logger.info("Process datasets requested")
        if self.controller:
            selected = self._get_selected_dataset_names()
            self.controller.process_datasets(selected)
    
    def _on_reprocess(self):
        """Handle Reprocess button click."""
        self.logger.info("Reprocess requested")
        if self.controller:
            # TODO: Implement reprocessing
            pass
    
    def _on_focus_changed(self, event):
        """Handle focus dataset selection change."""
        selected = self.focus_combo_var.get()
        self.logger.debug(f"Focus dataset changed to: {selected}")
        if self.controller:
            # TODO: Update focus dataset in controller
            pass
    
    def _on_select_all(self):
        """Handle Select All button click."""
        # TODO: Select all datasets in the tree
        self.logger.debug("Select all datasets")
    
    def _on_select_none(self):
        """Handle Select None button click."""
        # TODO: Deselect all datasets in the tree
        self.logger.debug("Select no datasets")
    
    def _on_refresh(self):
        """Handle Refresh button click."""
        self.logger.info("Refresh requested")
        if self.controller:
            # TODO: Refresh dataset list
            pass
    
    # Helper Methods
    def _get_selected_dataset_names(self):
        """Get the names of selected datasets."""
        # TODO: Implement based on tree selection
        return []
    
    def _update_dataset_tree(self, datasets):
        """Update the dataset treeview with current datasets."""
        # Clear existing items
        for item in self.dataset_tree.get_children():
            self.dataset_tree.delete(item)
        
        # Add datasets
        for name, dataset_info in datasets.items():
            # Determine status display
            status = "●" if hasattr(dataset_info, 'status') else "○"
            
            # Determine type
            types = []
            if hasattr(dataset_info, 'has_truth') and dataset_info.has_truth:
                types.append("T")
            if hasattr(dataset_info, 'has_detections') and dataset_info.has_detections:
                types.append("D")
            if hasattr(dataset_info, 'has_tracks') and dataset_info.has_tracks:
                types.append("Tr")
            type_str = "/".join(types) if types else "-"
            
            # Format size
            size_str = "-"
            if hasattr(dataset_info, 'size_bytes') and dataset_info.size_bytes > 0:
                if dataset_info.size_bytes > 1024 * 1024:
                    size_str = f"{dataset_info.size_bytes / (1024 * 1024):.1f}MB"
                elif dataset_info.size_bytes > 1024:
                    size_str = f"{dataset_info.size_bytes / 1024:.1f}KB"
                else:
                    size_str = f"{dataset_info.size_bytes}B"
            
            # Insert item
            self.dataset_tree.insert(
                "",
                "end",
                text=name,
                values=(status, type_str, size_str)
            )
    
    def _update_focus_info(self, dataset_info):
        """Update the focus dataset information display."""
        if dataset_info:
            self.focus_name_var.set(dataset_info.name)
            self.focus_date_var.set(dataset_info.last_modified or "-")
            # TODO: Set actual counts when available
            self.focus_tracks_var.set("0")
            self.focus_detections_var.set("0")
            self.focus_truth_var.set("0")
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
                
                # Update focus combo
                dataset_names = list(state.datasets.keys())
                self.focus_combo.configure(values=dataset_names)
                
                # Update button states
                has_datasets = len(dataset_names) > 0
                self.process_btn.configure(state="normal" if has_datasets else "disabled")
            
            elif event == "focus_changed":
                focus_info = state.get_focus_dataset_info()
                self._update_focus_info(focus_info)
                
                if focus_info:
                    self.focus_combo_var.set(focus_info.name)
                    self.reprocess_btn.configure(state="normal")
                else:
                    self.focus_combo_var.set("")
                    self.reprocess_btn.configure(state="disabled")
            
        except Exception as e:
            self.logger.error(f"Error handling state change '{event}': {e}")
