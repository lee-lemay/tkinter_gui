"""
Reusable control widgets for plot tabs.

This module provides standardized control widgets that can be reused
across different plot tabs, promoting consistency and reducing code duplication.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, List, Dict, Callable, Any
import logging
from ..utils.schema_access import get_col


class CollapsibleWidget(ttk.Frame):
    """
    Base class for collapsible widgets with expand/collapse functionality.
    """
    
    def __init__(self, parent: tk.Widget, title: str = "Widget", collapsed: bool = False):
        """
        Initialize the collapsible widget.
        
        Args:
            parent: Parent widget
            title: Title for the widget
            collapsed: Initial collapsed state
        """
        super().__init__(parent)
        self.title = title
        self.collapsed = collapsed
        self.logger = logging.getLogger(__name__)
        
        # Create header frame with expand/collapse button
        self.header_frame = ttk.Frame(self)
        self.header_frame.pack(fill="x", padx=2, pady=2)
        
        # Toggle button
        self.toggle_button = ttk.Button(
            self.header_frame,
            text="▼" if not collapsed else "►",
            width=3,
            command=self._toggle_collapsed
        )
        self.toggle_button.pack(side="left", padx=(0, 5))
        
        # Title label
        self.title_label = ttk.Label(
            self.header_frame,
            text=title,
            font=("TkDefaultFont", 9, "bold")
        )
        self.title_label.pack(side="left")
        
        # Content frame (will be shown/hidden)
        self.content_frame = ttk.LabelFrame(self, text="", padding=5)
        if not collapsed:
            self.content_frame.pack(fill="both", expand=True, padx=2, pady=(0, 2))
    
    def _toggle_collapsed(self):
        """Toggle the collapsed state of the widget."""
        self.collapsed = not self.collapsed
        
        if self.collapsed:
            # Hide content
            self.content_frame.pack_forget()
            self.toggle_button.config(text="►")
            self.logger.debug(f"Collapsed widget: {self.title}")
        else:
            # Show content
            self.content_frame.pack(fill="both", expand=True, padx=2, pady=(0, 2))
            self.toggle_button.config(text="▼")
            self.logger.debug(f"Expanded widget: {self.title}")
    
    def set_collapsed(self, collapsed: bool):
        """
        Set the collapsed state programmatically.
        
        Args:
            collapsed: True to collapse, False to expand
        """
        if self.collapsed != collapsed:
            self._toggle_collapsed()
    
    def is_collapsed(self) -> bool:
        """
        Check if the widget is currently collapsed.
        
        Returns:
            True if collapsed, False if expanded
        """
        return self.collapsed


class DataSelectionWidget(CollapsibleWidget):
    """
    Widget for selecting tracks and truth data with compact listboxes.
    Used by Geospatial and Animation tabs.
    """
    
    def __init__(self, parent: tk.Widget, title: str = "Data Selection", collapsed: bool = False):
        """
        Initialize the data selection widget.
        
        Args:
            parent: Parent widget
            title: Title for the label frame
            collapsed: Initial collapsed state
        """
        super().__init__(parent, title, collapsed)
        
        # Controller for accessing data
        self.controller: Optional[Any] = None
        
        # Callbacks
        self.tracks_callback: Optional[Callable[[List[str]], None]] = None
        self.truth_callback: Optional[Callable[[List[str]], None]] = None
        
        # UI elements
        self.tracks_listbox: Optional[tk.Listbox] = None
        self.truth_listbox: Optional[tk.Listbox] = None
        
        # Store original data for selection handling
        self.track_ids: List[str] = []
        self.truth_ids: List[str] = []
        
        self._create_controls()
    
    def _create_controls(self):
        """Create the selection controls."""
        # Create horizontal layout for side-by-side listboxes
        container = ttk.Frame(self.content_frame)
        container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Tracks section (left side)
        tracks_frame = ttk.LabelFrame(container, text="Tracks", padding=3)
        tracks_frame.pack(side="left", fill="both", expand=True, padx=(0, 3))
        
        # Create tracks listbox with scrollbar
        tracks_list_frame = ttk.Frame(tracks_frame)
        tracks_list_frame.pack(fill="both", expand=True)
        
        self.tracks_listbox = tk.Listbox(
            tracks_list_frame,
            selectmode=tk.EXTENDED,  # Enables Ctrl+Click and Shift+Click
            height=5,  # Compact height
            exportselection=False,  # Prevents losing selection when switching widgets
            font=("TkDefaultFont", 8)
        )
        
        tracks_scrollbar = ttk.Scrollbar(tracks_list_frame, orient="vertical", command=self.tracks_listbox.yview)
        self.tracks_listbox.configure(yscrollcommand=tracks_scrollbar.set)
        
        self.tracks_listbox.pack(side="left", fill="both", expand=True)
        tracks_scrollbar.pack(side="right", fill="y")
        
        # Bind tracks selection change
        self.tracks_listbox.bind("<<ListboxSelect>>", self._on_tracks_listbox_select)
        
        # Truth section (right side)
        truth_frame = ttk.LabelFrame(container, text="Truth", padding=3)
        truth_frame.pack(side="right", fill="both", expand=True, padx=(3, 0))
        
        # Create truth listbox with scrollbar
        truth_list_frame = ttk.Frame(truth_frame)
        truth_list_frame.pack(fill="both", expand=True)
        
        self.truth_listbox = tk.Listbox(
            truth_list_frame,
            selectmode=tk.EXTENDED,  # Enables Ctrl+Click and Shift+Click
            height=5,  # Compact height
            exportselection=False,  # Prevents losing selection when switching widgets
            font=("TkDefaultFont", 8)
        )
        
        truth_scrollbar = ttk.Scrollbar(truth_list_frame, orient="vertical", command=self.truth_listbox.yview)
        self.truth_listbox.configure(yscrollcommand=truth_scrollbar.set)
        
        self.truth_listbox.pack(side="left", fill="both", expand=True)
        truth_scrollbar.pack(side="right", fill="y")
        
        # Bind truth selection change
        self.truth_listbox.bind("<<ListboxSelect>>", self._on_truth_listbox_select)
        
        # Initially show empty state
        self._show_empty_state()
    
    def _show_empty_state(self):
        """Show empty state when no data is loaded."""
        if self.tracks_listbox:
            self.tracks_listbox.delete(0, tk.END)
            self.tracks_listbox.config(state="disabled")
        
        if self.truth_listbox:
            self.truth_listbox.delete(0, tk.END)
            self.truth_listbox.config(state="disabled")
    
    def _populate_tracks(self, track_ids: List[str]):
        """Populate the tracks listbox."""
        if not self.tracks_listbox:
            return
        
        self.tracks_listbox.delete(0, tk.END)
        self.tracks_listbox.config(state="normal")
        
        if not track_ids:
            self.tracks_listbox.config(state="disabled")
            return
        
        self.track_ids = track_ids
        
        # Add special options
        self.tracks_listbox.insert(0, "All")
        self.tracks_listbox.insert(1, "None")
        
        # Add track items
        for track_id in sorted(track_ids):
            self.tracks_listbox.insert(tk.END, f"Track {track_id}")
        
        # Select all tracks by default (skip "None" and separator)
        self.tracks_listbox.selection_set(0)  # Select "All Tracks"
    
    def _populate_truth(self, truth_ids: List[str]):
        """Populate the truth listbox."""
        if not self.truth_listbox:
            return
        
        self.truth_listbox.delete(0, tk.END)
        self.truth_listbox.config(state="normal")
        
        if not truth_ids:
            self.truth_listbox.insert(0, "No truth data available")
            self.truth_listbox.config(state="disabled")
            return
        
        self.truth_ids = truth_ids
        
        # Add special options
        self.truth_listbox.insert(0, "All")
        self.truth_listbox.insert(1, "None")
        
        # Add truth items
        for truth_id in sorted(truth_ids):
            self.truth_listbox.insert(tk.END, f"Truth {truth_id}")
        
        # Select all truth by default (skip "None" and separator)
        self.truth_listbox.selection_set(0)  # Select "All Truth"
    
    def _on_tracks_listbox_select(self, event=None):
        """Handle tracks listbox selection changes."""
        if not self.tracks_listbox or not self.track_ids:
            return
        
        selected_indices = self.tracks_listbox.curselection()
        if not selected_indices:
            return
        
        selected_items = [self.tracks_listbox.get(i) for i in selected_indices]
        
        # Handle special selections
        if "All" in selected_items:
            # Select all tracks (clear current selection and select all individual tracks)
            self.tracks_listbox.selection_clear(0, tk.END)
            self.tracks_listbox.selection_set(0)  # "All Tracks"
            for i in range(3, self.tracks_listbox.size()):  # Skip "All", "None", separator
                self.tracks_listbox.selection_set(i)
            selected_tracks = self.track_ids
        elif "None" in selected_items:
            # Clear all selections
            self.tracks_listbox.selection_clear(0, tk.END)
            self.tracks_listbox.selection_set(1)  # "None"
            selected_tracks = []
        else:
            # Normal selection - extract IDs from "Track X" format
            selected_tracks = []
            for item in selected_items:
                if item.startswith("Track ") and not item.startswith("─"):
                    track_id = item.replace("Track ", "")
                    selected_tracks.append(track_id)
        
        # Coerce selected track IDs back to original dtype (avoid str/int mismatch)
        if selected_tracks and self.track_ids:
            ref_type = type(self.track_ids[0])
            try:
                if ref_type is not str:
                    selected_tracks = [ref_type(t) if isinstance(t, str) else t for t in selected_tracks]
            except Exception:
                pass

        if self.tracks_callback:
            self.tracks_callback(selected_tracks)
    
    def _on_truth_listbox_select(self, event=None):
        """Handle truth listbox selection changes."""
        if not self.truth_listbox or not self.truth_ids:
            return
        
        selected_indices = self.truth_listbox.curselection()
        if not selected_indices:
            return
        
        selected_items = [self.truth_listbox.get(i) for i in selected_indices]
        
        # Handle special selections
        if "All" in selected_items:
            # Select all truth (clear current selection and select all individual items)
            self.truth_listbox.selection_clear(0, tk.END)
            self.truth_listbox.selection_set(0)  # "All Truth"
            for i in range(3, self.truth_listbox.size()):  # Skip "All", "None", separator
                self.truth_listbox.selection_set(i)
            selected_truth = self.truth_ids
        elif "None" in selected_items:
            # Clear all selections
            self.truth_listbox.selection_clear(0, tk.END)
            self.truth_listbox.selection_set(1)  # "None"
            selected_truth = []
        else:
            # Normal selection - extract IDs from "Truth X" format
            selected_truth = []
            for item in selected_items:
                if item.startswith("Truth ") and not item.startswith("─"):
                    truth_id = item.replace("Truth ", "")
                    selected_truth.append(truth_id)
        
        # Coerce selected truth IDs back to original dtype
        if selected_truth and self.truth_ids:
            ref_type = type(self.truth_ids[0])
            try:
                if ref_type is not str:
                    selected_truth = [ref_type(t) if isinstance(t, str) else t for t in selected_truth]
            except Exception:
                pass

        if self.truth_callback:
            self.truth_callback(selected_truth)
    
    def set_controller(self, controller: Any):
        """Set the controller for accessing track data."""
        self.controller = controller
        if controller:
            # Register as observer for focus changes
            controller.model.add_observer(self)
            # Load initial data if available
            self._update_data_from_focus()
    
    def on_state_changed(self, event: str):
        """Handle state changes from the application."""
        if event == "focus_changed":
            self._update_data_from_focus()
    
    def _update_data_from_focus(self):
        """Update track and truth lists from the focus dataset."""
        if not self.controller:
            return
        
        try:
            state = self.controller.get_state()
            focus_info = state.get_focus_dataset_info()
            
            if not focus_info or focus_info.status.value != "loaded":
                self._show_empty_state()
                return
            
            # Extract track IDs
            track_ids = []
            schema = getattr(focus_info, 'schema', None)
            if focus_info.tracks_df is not None and not focus_info.tracks_df.empty:
                try:
                    track_col = get_col(schema, 'tracks', 'track_id')
                    if track_col in focus_info.tracks_df.columns:
                        track_ids = focus_info.tracks_df[track_col].unique().tolist()
                    else:
                        self.logger.error(f"{track_col} not in dataset {focus_info.name}.tracks_df.columns")
                except Exception as e:
                    self.logger.error(f"Error loading track ids from {focus_info.name}: {e}")
            
            # Extract truth IDs
            truth_ids = []
            if focus_info.truth_df is not None and not focus_info.truth_df.empty:
                truth_col = get_col(schema, 'truth', 'truth_id')
                if truth_col in focus_info.truth_df.columns:
                    truth_ids = focus_info.truth_df[truth_col].unique().tolist()
            
            # Update the UI
            self._populate_tracks(track_ids)
            self._populate_truth(truth_ids)

            if self.tracks_callback:
                self.tracks_callback(self.get_selected_tracks())

            if self.truth_callback:
                self.truth_callback(self.get_selected_truth())
            
        except Exception as e:
            self.logger.error(f"Error updating data from focus: {e}")
            self._show_empty_state()
    
    def set_tracks_callback(self, callback: Callable[[List[str]], None]):
        """Set callback for tracks selection changes."""
        self.tracks_callback = callback
    
    def set_truth_callback(self, callback: Callable[[List[str]], None]):
        """Set callback for truth selection changes."""
        self.truth_callback = callback
    
    def get_selected_tracks(self) -> List[str]:
        """Get current tracks selection."""
        if not self.tracks_listbox or not self.track_ids:
            return []
        
        selected_indices = self.tracks_listbox.curselection()
        if not selected_indices:
            return []
        
        selected_items = [self.tracks_listbox.get(i) for i in selected_indices]
        
        # Handle special selections
        if "All" in selected_items:
            return self.track_ids
        elif "None" in selected_items:
            return []
        else:
            # Extract IDs from "Track X" format
            selected_tracks = []
            for item in selected_items:
                if item.startswith("Track ") and not item.startswith("─"):
                    track_id = item.replace("Track ", "")
                    selected_tracks.append(track_id)
            # Coerce to original dtype
            if selected_tracks and self.track_ids:
                ref_type = type(self.track_ids[0])
                try:
                    if ref_type is not str:
                        selected_tracks = [ref_type(t) if isinstance(t, str) else t for t in selected_tracks]
                except Exception:
                    pass
            return selected_tracks
    
    def get_selected_truth(self) -> List[str]:
        """Get current truth selection."""
        if not self.truth_listbox or not self.truth_ids:
            return []
        
        selected_indices = self.truth_listbox.curselection()
        if not selected_indices:
            return []
        
        selected_items = [self.truth_listbox.get(i) for i in selected_indices]
        
        # Handle special selections
        if "All" in selected_items:
            return self.truth_ids
        elif "None" in selected_items:
            return []
        else:
            # Extract IDs from "Truth X" format
            selected_truth = []
            for item in selected_items:
                if item.startswith("Truth ") and not item.startswith("─"):
                    truth_id = item.replace("Truth ", "")
                    selected_truth.append(truth_id)
            # Coerce to original dtype
            if selected_truth and self.truth_ids:
                ref_type = type(self.truth_ids[0])
                try:
                    if ref_type is not str:
                        selected_truth = [ref_type(t) if isinstance(t, str) else t for t in selected_truth]
                except Exception:
                    pass
            return selected_truth
    
    def get_tracks_selection(self) -> List[str]:
        """Get current tracks selection (alias for compatibility)."""
        return self.get_selected_tracks()
    
    def get_truth_selection(self) -> List[str]:
        """Get current truth selection (alias for compatibility)."""
        return self.get_selected_truth()
    
    def set_tracks_selection(self, track_ids: List[str]):
        """Set tracks selection."""
        if not self.tracks_listbox or not self.track_ids:
            return
        
        self.tracks_listbox.selection_clear(0, tk.END)
        
        if not track_ids:
            # Select "None"
            self.tracks_listbox.selection_set(1)
        elif set(track_ids) == set(self.track_ids):
            # Select "All Tracks"
            self.tracks_listbox.selection_set(0)
        else:
            # Select individual tracks
            for i in range(3, self.tracks_listbox.size()):  # Skip "All", "None", separator
                item = self.tracks_listbox.get(i)
                if item.startswith("Track "):
                    track_id = item.replace("Track ", "")
                    if track_id in track_ids:
                        self.tracks_listbox.selection_set(i)
    
    def set_truth_selection(self, truth_ids: List[str]):
        """Set truth selection."""
        if not self.truth_listbox or not self.truth_ids:
            return
        
        self.truth_listbox.selection_clear(0, tk.END)
        
        if not truth_ids:
            # Select "None"
            self.truth_listbox.selection_set(1)
        elif set(truth_ids) == set(self.truth_ids):
            # Select "All Truth"
            self.truth_listbox.selection_set(0)
        else:
            # Select individual truth items
            for i in range(3, self.truth_listbox.size()):  # Skip "All", "None", separator
                item = self.truth_listbox.get(i)
                if item.startswith("Truth "):
                    truth_id = item.replace("Truth ", "")
                    if truth_id in truth_ids:
                        self.truth_listbox.selection_set(i)


class CoordinateRangeWidget(CollapsibleWidget):
    """
    Widget for setting latitude and longitude ranges.
    Used by Geospatial and Animation tabs.
    """
    
    def __init__(self, parent: tk.Widget, title: str = "Coordinate Range", collapsed: bool = False):
        """
        Initialize the coordinate range widget.
        
        Args:
            parent: Parent widget
            title: Title for the label frame
            collapsed: Initial collapsed state
        """
        super().__init__(parent, title, collapsed)
        
        # Variables for coordinate ranges
        self.lat_min_var = tk.DoubleVar(value=-1.0)
        self.lat_max_var = tk.DoubleVar(value=1.0)
        self.lon_min_var = tk.DoubleVar(value=-1.0)
        self.lon_max_var = tk.DoubleVar(value=1.0)
        
        # Callback for range changes
        self.range_callback: Optional[Callable] = None
        self.reset_callback: Optional[Callable] = None
        
        self._create_controls()
    
    def _create_controls(self):
        """Create the coordinate range controls."""
        # Latitude range
        lat_frame = ttk.Frame(self.content_frame)
        lat_frame.pack(fill="x", padx=5, pady=2)
        
        ttk.Label(lat_frame, text="Latitude:").pack(side="left")
        ttk.Label(lat_frame, text="Min:").pack(side="left", padx=(10, 2))
        self.lat_min_spin = ttk.Spinbox(
            lat_frame, 
            from_=-90.0, 
            to=90.0, 
            increment=0.01,
            textvariable=self.lat_min_var, 
            width=8, 
            format="%.4f"
        )
        self.lat_min_spin.pack(side="left", padx=2)
        
        ttk.Label(lat_frame, text="Max:").pack(side="left", padx=(10, 2))
        self.lat_max_spin = ttk.Spinbox(
            lat_frame,
            from_=-90.0,
            to=90.0,
            increment=0.01,
            textvariable=self.lat_max_var,
            width=8,
            format="%.4f"
        )
        self.lat_max_spin.pack(side="left", padx=2)
        
        # Longitude range
        lon_frame = ttk.Frame(self.content_frame)
        lon_frame.pack(fill="x", padx=5, pady=2)
        
        ttk.Label(lon_frame, text="Longitude:").pack(side="left")
        ttk.Label(lon_frame, text="Min:").pack(side="left", padx=(10, 2))
        self.lon_min_spin = ttk.Spinbox(
            lon_frame,
            from_=-180.0,
            to=180.0,
            increment=0.01,
            textvariable=self.lon_min_var,
            width=8,
            format="%.4f"
        )
        self.lon_min_spin.pack(side="left", padx=2)
        
        ttk.Label(lon_frame, text="Max:").pack(side="left", padx=(10, 2))
        self.lon_max_spin = ttk.Spinbox(
            lon_frame,
            from_=-180.0,
            to=180.0,
            increment=0.01,
            textvariable=self.lon_max_var,
            width=8,
            format="%.4f"
        )
        self.lon_max_spin.pack(side="left", padx=2)
        
        # Reset button
        self.reset_btn = ttk.Button(
            lon_frame,
            text="Reset Range",
            command=self._on_reset
        )
        self.reset_btn.pack(side="left", padx=(10, 2))
        
        # Set up change handlers
        self.lat_min_var.trace('w', self._on_range_changed)
        self.lat_max_var.trace('w', self._on_range_changed)
        self.lon_min_var.trace('w', self._on_range_changed)
        self.lon_max_var.trace('w', self._on_range_changed)
    
    def _on_range_changed(self, *args):
        """Handle coordinate range changes."""
        if self.range_callback:
            self.range_callback(self.get_ranges())
    
    def _on_reset(self):
        """Handle reset button click."""
        if self.reset_callback:
            self.reset_callback()
    
    def set_range_callback(self, callback: Callable[[Dict[str, tuple]], None]):
        """Set callback for range changes."""
        self.range_callback = callback
    
    def set_reset_callback(self, callback: Callable[[], None]):
        """Set callback for reset button."""
        self.reset_callback = callback
    
    def get_ranges(self) -> Dict[str, tuple]:
        """Get current coordinate ranges."""
        return {
            'lat_range': (self.lat_min_var.get(), self.lat_max_var.get()),
            'lon_range': (self.lon_min_var.get(), self.lon_max_var.get())
        }
    
    def set_ranges(self, lat_range: tuple, lon_range: tuple):
        """Set coordinate ranges."""
        self.lat_min_var.set(lat_range[0])
        self.lat_max_var.set(lat_range[1])
        self.lon_min_var.set(lon_range[0])
        self.lon_max_var.set(lon_range[1])

        self.lat_min_spin.set(f"{lat_range[0]:.4f}")
        self.lat_max_spin.set(f"{lat_range[1]:.4f}")
        self.lon_min_spin.set(f"{lon_range[0]:.4f}")
        self.lon_max_spin.set(f"{lon_range[1]:.4f}")


class TrackSelectionWidget(CollapsibleWidget):
    """
    Widget for selecting individual tracks with compact listbox.
    Used by Error Analysis and RMS Error tabs.
    """
    
    def __init__(self, parent: tk.Widget, title: str = "Track Selection", collapsed: bool = False):
        """
        Initialize the track selection widget.
        
        Args:
            parent: Parent widget
            title: Title for the label frame
            collapsed: Initial collapsed state
        """
        super().__init__(parent, title, collapsed)
        
        # Controller for accessing data
        self.controller: Optional[Any] = None
        
        # Callbacks
        self.selection_callback: Optional[Callable[[List[str]], None]] = None
        
        # UI elements
        self.tracks_listbox: Optional[tk.Listbox] = None
        
        # Store original data for selection handling
        self.track_ids: List[str] = []
        self._id_lookup: Dict[str, Any] = {}
        
        self._create_controls()
    
    def _create_controls(self):
        """Create the track selection controls."""
        # Create tracks listbox with scrollbar
        list_frame = ttk.Frame(self.content_frame)
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.tracks_listbox = tk.Listbox(
            list_frame,
            selectmode=tk.EXTENDED,  # Enables Ctrl+Click and Shift+Click
            height=5,  # More room for tracks in single widget
            exportselection=False,  # Prevents losing selection when switching widgets
            font=("TkDefaultFont", 8)
        )
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tracks_listbox.yview)
        self.tracks_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.tracks_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind selection change
        self.tracks_listbox.bind("<<ListboxSelect>>", self._on_tracks_listbox_select)
        
        # Initially show empty state
        self._show_empty_state()
    
    def _show_empty_state(self):
        """Show empty state when no tracks are loaded."""
        if self.tracks_listbox:
            self.tracks_listbox.delete(0, tk.END)
            self.tracks_listbox.config(state="disabled")
    
    def _clear_track_list(self):
        """Clear the track listbox."""
        if self.tracks_listbox:
            self.tracks_listbox.delete(0, tk.END)
    
    def _populate_tracks(self, track_ids: List[str]):
        """Populate the track selection list."""
        if not self.tracks_listbox:
            return
        
        self.tracks_listbox.delete(0, tk.END)
        self.tracks_listbox.config(state="normal")
        
        if not track_ids:
            self._show_empty_state()
            return
        
        self.track_ids = track_ids
        self._id_lookup = {str(t): t for t in track_ids}
        
        # Add special options
        self.tracks_listbox.insert(0, "All Tracks")
        self.tracks_listbox.insert(1, "None")
        
        # Add track items
        for track_id in sorted(track_ids):
            self.tracks_listbox.insert(tk.END, f"Track {track_id}")
        
        # Select all tracks by default
        self.tracks_listbox.selection_set(0)  # Select "All Tracks"
    
    def _select_all_tracks(self):
        """Select all tracks."""
        if self.tracks_listbox and self.track_ids:
            self.tracks_listbox.selection_clear(0, tk.END)
            self.tracks_listbox.selection_set(0)  # Select "All Tracks"
            for i in range(2, self.tracks_listbox.size()):  # Select all individual tracks
                self.tracks_listbox.selection_set(i)
            self._on_tracks_listbox_select()
    
    def _select_no_tracks(self):
        """Deselect all tracks."""
        if self.tracks_listbox:
            self.tracks_listbox.selection_clear(0, tk.END)
            self.tracks_listbox.selection_set(1)  # Select "None"
            self._on_tracks_listbox_select()
    
    def _on_track_selection_changed(self):
        """Handle track selection changes."""
        self._on_tracks_listbox_select()
    
    def _on_tracks_listbox_select(self, event=None):
        """Handle tracks listbox selection changes."""
        if not self.tracks_listbox or not self.track_ids:
            return
        
        selected_indices = self.tracks_listbox.curselection()
        if not selected_indices:
            return
        
        selected_items = [self.tracks_listbox.get(i) for i in selected_indices]
        
        # Handle special selections
        if "All Tracks" in selected_items:
            # Select all tracks
            self.tracks_listbox.selection_clear(0, tk.END)
            self.tracks_listbox.selection_set(0)  # "All Tracks"
            for i in range(2, self.tracks_listbox.size()):  # Skip "All", "None" 
                self.tracks_listbox.selection_set(i)
            selected_tracks = self.track_ids
        elif "None" in selected_items:
            # Clear all selections
            self.tracks_listbox.selection_clear(0, tk.END)
            self.tracks_listbox.selection_set(1)  # "None"
            selected_tracks = []
        else:
            # Normal selection - extract IDs from "Track X" format
            selected_tracks = []
            for item in selected_items:
                if item.startswith("Track ") and not item.startswith("─"):
                    track_id = item.replace("Track ", "")
                    selected_tracks.append(track_id)
        
        if self.selection_callback:
            self.selection_callback(selected_tracks)
    
    def set_controller(self, controller: Any):
        """Set the controller for accessing track data."""
        self.controller = controller
        if controller:
            # Register as observer for focus changes
            controller.model.add_observer(self)
            # Load initial data if available
            self._update_tracks_from_focus()
    
    def on_state_changed(self, event: str):
        """Handle state changes from the application."""
        if event == "focus_changed":
            self._update_tracks_from_focus()
    
    def _update_tracks_from_focus(self):
        """Update track list from the focus dataset."""
        if not self.controller:
            return
        
        try:
            state = self.controller.get_state()
            focus_info = state.get_focus_dataset_info()
            
            if not focus_info or focus_info.status.value != "loaded":
                self._show_empty_state()
                return
            
            # Extract track IDs
            track_ids = []
            if focus_info.tracks_df is not None and not focus_info.tracks_df.empty:
                from ..utils.schema_access import get_col
                schema = getattr(focus_info, 'schema', None)
                track_col = get_col(schema, 'tracks', 'track_id')
                if track_col in focus_info.tracks_df.columns:
                    track_ids = focus_info.tracks_df[track_col].unique().tolist()
                else:
                    self.logger.error(f"{track_col} not in dataset {focus_info.name}.tracks_df.columns")
            
            # Update the UI
            self._populate_tracks(track_ids)

            if self.selection_callback:
                self.selection_callback(self.get_selected_tracks())
            
        except Exception as e:
            self.logger.error(f"Error updating tracks from focus: {e}")
            self._show_empty_state()
    
    def set_selection_callback(self, callback: Callable[[List[str]], None]):
        """Set callback for selection changes."""
        self.selection_callback = callback
    
    def get_selected_tracks(self) -> List[str]:
        """Get list of selected track IDs."""
        if not self.tracks_listbox or not self.track_ids:
            return []
        
        selected_indices = self.tracks_listbox.curselection()
        if not selected_indices:
            return []
        
        selected_items = [self.tracks_listbox.get(i) for i in selected_indices]
        
        # Handle special selections
        if "All Tracks" in selected_items:
            return self.track_ids
        elif "None" in selected_items:
            return []
        else:
            selected_tracks = []
            for item in selected_items:
                if item.startswith("Track ") and not item.startswith("─"):
                    raw = item.replace("Track ", "")
                    if raw in getattr(self, '_id_lookup', {}):
                        selected_tracks.append(self._id_lookup[raw])
                    else:
                        try:
                            selected_tracks.append(int(raw))
                        except ValueError:
                            selected_tracks.append(raw)
            return selected_tracks
    
    def get_selection(self) -> List[str]:
        """Get current selection (alias for compatibility)."""
        return self.get_selected_tracks()
    
    def set_selection(self, track_ids: List[str]):
        """Set track selection."""
        if not self.tracks_listbox or not self.track_ids:
            return
        
        self.tracks_listbox.selection_clear(0, tk.END)
        
        if not track_ids:
            # Select "None"
            self.tracks_listbox.selection_set(1)
        elif set(track_ids) == set(self.track_ids):
            # Select "All Tracks"
            self.tracks_listbox.selection_set(0)
        else:
            # Select individual tracks
            for i in range(3, self.tracks_listbox.size()):  # Skip "All", "None", separator
                item = self.tracks_listbox.get(i)
                if item.startswith("Track "):
                    track_id = item.replace("Track ", "")
                    if track_id in track_ids:
                        self.tracks_listbox.selection_set(i)


class PlaybackControlWidget(CollapsibleWidget):
    """
    Widget for animation playback controls.
    Used by Animation tab.
    """
    
    def __init__(self, parent: tk.Widget, title: str = "Playback Controls", collapsed: bool = False):
        """
        Initialize the playback control widget.
        
        Args:
            parent: Parent widget
            title: Title for the label frame
            collapsed: Initial collapsed state
        """
        super().__init__(parent, title, collapsed)
        
        # Animation state variables
        self.playing = tk.BooleanVar(value=False)
        self.current_frame = tk.IntVar(value=0)
        self.speed = tk.DoubleVar(value=1.0)
        
        # Animation data and timing
        self.max_frames = 0
        self.timer_id: Optional[str] = None
        self.base_interval = 100  # Base interval in milliseconds
        
        # Callbacks
        self.play_callback: Optional[Callable] = None
        self.pause_callback: Optional[Callable] = None
        self.stop_callback: Optional[Callable] = None
        self.step_callback: Optional[Callable] = None
        self.speed_callback: Optional[Callable] = None
        
        self._create_controls()
    
    def _create_controls(self):
        """Create the playback controls."""
        # First row - main playback controls
        playback_row1 = ttk.Frame(self.content_frame)
        playback_row1.pack(fill="x", padx=5, pady=2)
        
        self.play_btn = ttk.Button(
            playback_row1,
            text="▶",
            width=3,
            command=self._on_play,
            state="disabled"
        )
        self.play_btn.pack(side="left", padx=2)
        
        self.pause_btn = ttk.Button(
            playback_row1,
            text="⏸",
            width=3,
            command=self._on_pause,
            state="disabled"
        )
        self.pause_btn.pack(side="left", padx=2)
        
        self.stop_btn = ttk.Button(
            playback_row1,
            text="⏹",
            width=3,
            command=self._on_stop,
            state="disabled"
        )
        self.stop_btn.pack(side="left", padx=2)
        
        self.step_back_btn = ttk.Button(
            playback_row1,
            text="⏮",
            width=3,
            command=self._on_step_back,
            state="disabled"
        )
        self.step_back_btn.pack(side="left", padx=2)
        
        self.step_forward_btn = ttk.Button(
            playback_row1,
            text="⏭",
            width=3,
            command=self._on_step_forward,
            state="disabled"
        )
        self.step_forward_btn.pack(side="left", padx=2)
        
        # Frame indicator
        self.frame_label = ttk.Label(playback_row1, text="Frame: 0/0")
        self.frame_label.pack(side="left", padx=(10, 2))
        
        # Second row - speed control
        playback_row2 = ttk.Frame(self.content_frame)
        playback_row2.pack(fill="x", padx=5, pady=2)
        
        ttk.Label(playback_row2, text="Speed:").pack(side="left")
        self.speed_scale = ttk.Scale(
            playback_row2,
            from_=0.1,
            to=5.0,
            variable=self.speed,
            orient="horizontal",
            length=80
        )
        self.speed_scale.pack(side="left", padx=2)
        
        self.speed_label = ttk.Label(playback_row2, text="1.0x")
        self.speed_label.pack(side="left", padx=2)
        
        # Bind speed change
        self.speed.trace('w', self._on_speed_changed)
    
    def _on_play(self):
        """Handle play button."""
        if self.play_callback:
            self.play_callback()
    
    def _on_pause(self):
        """Handle pause button."""
        if self.pause_callback:
            self.pause_callback()
    
    def _on_stop(self):
        """Handle stop button."""
        if self.stop_callback:
            self.stop_callback()
    
    def _on_step_back(self):
        """Handle step back button."""
        if self.step_callback:
            self.step_callback(-1)
    
    def _on_step_forward(self):
        """Handle step forward button."""
        if self.step_callback:
            self.step_callback(1)
    
    def _on_speed_changed(self, *args):
        """Handle speed change."""
        speed_val = self.speed.get()
        self.speed_label.config(text=f"{speed_val:.1f}x")
        if self.speed_callback:
            self.speed_callback(speed_val)
    
    def set_play_callback(self, callback: Callable[[], None]):
        """Set callback for play button."""
        self.play_callback = callback
    
    def set_pause_callback(self, callback: Callable[[], None]):
        """Set callback for pause button."""
        self.pause_callback = callback
    
    def set_stop_callback(self, callback: Callable[[], None]):
        """Set callback for stop button."""
        self.stop_callback = callback
    
    def set_step_callback(self, callback: Callable[[int], None]):
        """Set callback for step buttons (direction: -1 or 1)."""
        self.step_callback = callback
    
    def set_speed_callback(self, callback: Callable[[float], None]):
        """Set callback for speed changes."""
        self.speed_callback = callback
    
    def set_total_frames(self, total_frames: int):
        """Set the total number of frames."""
        self.max_frames = total_frames
        self.update_frame_display()
        
        # Enable/disable controls based on frame availability
        state = "normal" if total_frames > 0 else "disabled"
        self.play_btn.config(state=state)
        self.pause_btn.config(state="disabled")
        self.stop_btn.config(state="disabled")
        self.step_back_btn.config(state="disabled")
        self.step_forward_btn.config(state="disabled")
    
    def set_current_frame(self, frame: int):
        """Set the current frame."""
        self.current_frame.set(frame)
        self.update_frame_display()
    
    def update_frame_display(self):
        """Update the frame indicator."""
        current = self.current_frame.get()
        total = self.max_frames
        self.frame_label.config(text=f"Frame: {current + 1}/{total}")
    
    def get_current_frame(self) -> int:
        """Get current frame."""
        return self.current_frame.get()
    
    def get_speed(self) -> float:
        """Get current speed."""
        return self.speed.get()
    
    def is_playing(self) -> bool:
        """Check if animation is playing."""
        return self.playing.get()
    
    def set_playing(self, playing: bool):
        """Set playing state."""
        self.playing.set(playing)


class HistogramControlWidget(CollapsibleWidget):
    """Controls for histogram formatting.

    Exposes:
      - Gaussian overlay toggle
      - Bin count (odd number) selector
      - Extent in standard deviations (±Nσ)
      - Optional secondary scatter overlay variable selection

    The histogram formatter can query this widget (if present in its widgets list)
    via its public getters to decide how to build the histogram config.
    """

    def __init__(self,
                 parent: tk.Widget,
                 title: str = "Histogram Controls",
                 collapsed: bool = False,
                 scatter_variables: Optional[List[str]] = None):
        super().__init__(parent, title, collapsed)
        self._scatter_variables = scatter_variables or []
        # Tk variables
        self.gaussian_var = tk.BooleanVar(value=False)
        self.unit_gaussian_var = tk.BooleanVar(value=False)
        self.best_fit_gaussian_var = tk.BooleanVar(value=False)
        self.bin_count_var = tk.IntVar(value=41)
        self.sigma_extent_var = tk.DoubleVar(value=4.0)  # default ±4σ
        self.scatter_enabled_var = tk.BooleanVar(value=False)
        self.scatter_var_choice = tk.StringVar(value=self._scatter_variables[0] if self._scatter_variables else "")

        # Callback when any control changes
        self._change_callback: Optional[Callable[[], None]] = None
        self._create_controls()

    # UI construction
    def _create_controls(self):  # type: ignore[override]
        frame = self.content_frame

        # Row 1: Bins (odd) | Extent (±σ)
        row1 = ttk.Frame(frame)
        row1.pack(fill='x', padx=5, pady=2)
        # vertical separator helper
        def _vsep(parent):
            sep = ttk.Separator(parent, orient='vertical')
            sep.pack(side='left', fill='y', padx=6, pady=2)
            return sep

        ttk.Label(row1, text="# Bins (odd):").pack(side='left')
        self.bins_spin = ttk.Spinbox(row1, from_=3, to=101, increment=2, textvariable=self.bin_count_var, width=6, command=self._on_bins_changed)
        self.bins_spin.pack(side='left', padx=(4, 2))

        _vsep(row1)
        ttk.Label(row1, text="Plot Extent (±σ):").pack(side='left')
        self.extent_spin = ttk.Spinbox(row1, from_=1.0, to=8.0, increment=0.5, textvariable=self.sigma_extent_var, width=6, command=self._notify_change)
        self.extent_spin.pack(side='left', padx=(4, 2))

        # Row 2: Overlays: Gaussian variants + Scatter (if provided)
        overlays_row = ttk.Frame(frame)
        overlays_row.pack(fill='x', padx=5, pady=(4, 2))
        ttk.Label(overlays_row, text="Overlays:").pack(side='left')

        # Gaussian (scaled to counts) original
        gauss_chk = ttk.Checkbutton(overlays_row, text="Gaussian", variable=self.gaussian_var, command=self._notify_change)
        gauss_chk.pack(side='left', padx=(6,0))
        _vsep(overlays_row)
        # Unit Gaussian (unscaled PDF)
        unit_gauss_chk = ttk.Checkbutton(overlays_row, text="Unit Gaussian", variable=self.unit_gaussian_var, command=self._notify_change)
        unit_gauss_chk.pack(side='left')
        _vsep(overlays_row)
        # Best Fit Gaussian (unscaled PDF duplicate semantics per spec)
        best_gauss_chk = ttk.Checkbutton(overlays_row, text="Best Fit Gaussian", variable=self.best_fit_gaussian_var, command=self._notify_change)
        best_gauss_chk.pack(side='left')

        if self._scatter_variables:
            _vsep(overlays_row)
            scatter_chk = ttk.Checkbutton(overlays_row, text="Scatter", variable=self.scatter_enabled_var, command=self._notify_change)
            scatter_chk.pack(side='left')
            ttk.Label(overlays_row, text="Variable:").pack(side='left', padx=(8, 2))
            self.scatter_combo = ttk.Combobox(overlays_row, state='readonly', values=self._scatter_variables, textvariable=self.scatter_var_choice, width=16)
            self.scatter_combo.pack(side='left', padx=4)
            self.scatter_combo.bind('<<ComboboxSelected>>', lambda _e: self._notify_change())

        # Traces & event bindings so manual typing triggers updates
        self.sigma_extent_var.trace_add('write', lambda *_: self._on_extent_commit())
        # Commit events (Return key or leaving focus)
        self.bins_spin.bind('<Return>', lambda e: self._on_bins_commit())
        self.bins_spin.bind('<FocusOut>', lambda e: self._on_bins_commit())
        self.extent_spin.bind('<Return>', lambda e: self._on_extent_commit())
        self.extent_spin.bind('<FocusOut>', lambda e: self._on_extent_commit())

    # Internal helpers
    def _ensure_odd_bins(self):
        try:
            v = self.bin_count_var.get()
            if v % 2 == 0:  # make it odd
                self.bin_count_var.set(v + 1)
        except Exception:
            pass

    # Trace callbacks
    def _on_extent_var_typed(self):
        # Just propagate change; value already in self.sigma_extent_var
        self._notify_change()

    # Commit handlers (redundant safety for platforms where trace timing differs)
    def _on_bins_commit(self):
        self._ensure_odd_bins()
        self._notify_change()

    def _on_extent_commit(self):
        self._notify_change()

    def _on_bins_changed(self):
        self._ensure_odd_bins()
        self._notify_change()

    def _notify_change(self):
        if self._change_callback:
            try:
                self._change_callback()
            except Exception:
                pass

    # Public API for formatter
    def get_bin_count(self) -> int:
        return int(self.bin_count_var.get())

    def get_sigma_extent(self) -> float:
        return float(self.sigma_extent_var.get())

    def gaussian_overlay_enabled(self) -> bool:
        return bool(self.gaussian_var.get())

    def unit_gaussian_enabled(self) -> bool:
        return bool(self.unit_gaussian_var.get())

    def best_fit_gaussian_enabled(self) -> bool:
        return bool(self.best_fit_gaussian_var.get())

    def scatter_overlay_enabled(self) -> bool:
        return bool(self.scatter_enabled_var.get()) and bool(self._scatter_variables)

    def get_scatter_variable(self) -> Optional[str]:
        if not self.scatter_overlay_enabled():
            return None
        return self.scatter_var_choice.get() or None

    def set_change_callback(self, cb: Callable[[], None]):
        self._change_callback = cb

__all__ = [
    # existing exports (implicitly via wildcard import usage) -- ensure new widget accessible
    'HistogramControlWidget'
]
