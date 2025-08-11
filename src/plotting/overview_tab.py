"""Overview tab showing focus dataset metadata.

Displays information about the
currently focused dataset (path, size, time ranges, counts, presence of
dataframes) in a simple read-only layout. 
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Any, Dict
import logging

from ..models.application_state import DatasetInfo
from datetime import datetime
import math


class OverviewTabWidget(ttk.Frame):
    """Lightweight overview tab displaying dataset metadata"""

    def __init__(self, parent: tk.Widget):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__ + '.overview')
        self.controller: Optional[Any] = None
        self.fields: Dict[str, tk.StringVar] = {}
        self._create_focus_dataset_panel()
    
    def _create_focus_dataset_panel(self):
        """Create panel that shows focus dataset metadata."""
        panel = ttk.Frame(self)
        panel.pack(fill="both", expand=True, padx=10, pady=10)

        title = ttk.Label(panel, text="Focus Dataset Overview", font=("TkDefaultFont", 12, "bold"))
        title.pack(anchor="w", pady=(0, 10))

        self.info_frame = ttk.Frame(panel)
        self.info_frame.pack(fill="x")

        # Mapping of label -> tk.StringVar for dynamic update
        self.fields: Dict[str, tk.StringVar] = {}
        ordered_fields = [
            ("Path", "-"),
            ("Date (by earliest track)", "-"),
            ("Size (MB)", "-"),
            ("Track Count", "-"),
            ("Track Time Range", "-"),
            ("Truth Count", "-"),
            ("Truth Time Range", "-"),
            ("DataFrames Present", "-"),
        ]
        for r, (label, default) in enumerate(ordered_fields):
            ttk.Label(self.info_frame, text=f"{label}:").grid(row=r, column=0, sticky="w", pady=2)
            var = tk.StringVar(value=default)
            self.fields[label] = var
            ttk.Label(self.info_frame, textvariable=var).grid(row=r, column=1, sticky="w", padx=(5,0), pady=2)
        self.info_frame.grid_columnconfigure(1, weight=1)

        # List of dataframe attribute names to check presence; extendable later
        self._dataframe_names = [
            'truth_df',
            'tracks_df',
            'metrics_df',
            'resampled_truth_df',
            'resampled_tracks_df',
        ]

        self._update_focus_info()
    
    # Public API expected by right_panel
    def set_controller(self, controller: Any):
        self.controller = controller
        self._update_focus_info()

    def auto_update(self):  # invoked on state changes
        self._update_focus_info()

    # New internal helpers
    def _update_focus_info(self):
        if not self.controller:
            return
        try:
            state = self.controller.get_state()
            focus = state.get_focus_dataset_info()
            if not focus or focus.status.value != "loaded":
                for v in self.fields.values():
                    v.set("-")
                return
            self._populate_fields_from_dataset(focus)
        except Exception as e:
            self.logger.debug(f"Focus info update skipped: {e}")

    def _populate_fields_from_dataset(self, ds: DatasetInfo):
        # Path
        self.fields["Path"].set(str(ds.path))
        # Size MB
        if ds.size_bytes:
            size_mb = ds.size_bytes / (1024 * 1024)
            if size_mb >= 100:
                size_str = f"{size_mb:.0f}"
            elif size_mb >= 10:
                size_str = f"{size_mb:.1f}"
            else:
                size_str = f"{size_mb:.2f}"
        else:
            size_str = "-"
        self.fields["Size (MB)"].set(size_str)

        # Tracks stats
        track_range_str = "-"
        track_count_str = "-"
        earliest_track_dt = None
        if ds.tracks_df is not None and not ds.tracks_df.empty:
            try:
                if 'track_id' in ds.tracks_df.columns:
                    track_count_str = str(len(ds.tracks_df['track_id'].dropna().unique()))
                else:
                    track_count_str = str(len(ds.tracks_df))
                if 'timestamp' in ds.tracks_df.columns:
                    tseries = ds.tracks_df['timestamp'].dropna()
                    if not tseries.empty:
                        earliest_track_dt = tseries.min()
                        latest_track_dt = tseries.max()
                        track_range_str = f"{self._fmt_ts(earliest_track_dt)} -> {self._fmt_ts(latest_track_dt)}"
            except Exception:
                pass
        self.fields["Track Count"].set(track_count_str)
        self.fields["Track Time Range"].set(track_range_str)

        # Truth stats
        truth_range_str = "-"
        truth_count_str = "-"
        earliest_truth_dt = None
        if ds.truth_df is not None and not ds.truth_df.empty:
            try:
                id_col = 'id' if 'id' in ds.truth_df.columns else None
                if id_col:
                    truth_count_str = str(len(ds.truth_df[id_col].dropna().unique()))
                else:
                    truth_count_str = str(len(ds.truth_df))
                if 'timestamp' in ds.truth_df.columns:
                    tseries = ds.truth_df['timestamp'].dropna()
                    if not tseries.empty:
                        earliest_truth_dt = tseries.min()
                        latest_truth_dt = tseries.max()
                        truth_range_str = f"{self._fmt_ts(earliest_truth_dt)} -> {self._fmt_ts(latest_truth_dt)}"
            except Exception:
                pass
        self.fields["Truth Count"].set(truth_count_str)
        self.fields["Truth Time Range"].set(truth_range_str)

        # Date (earliest track timestamp if available else earliest truth)
        chosen_dt = earliest_track_dt or earliest_truth_dt
        self.fields["Date (by earliest track)"].set(self._fmt_ts(chosen_dt) if chosen_dt else "-")

        # DataFrame presence list
        present = []
        for name in self._dataframe_names:
            if hasattr(ds, name) and getattr(ds, name) is not None:
                df_obj = getattr(ds, name)
                try:
                    if df_obj is not None and not getattr(df_obj, 'empty', False):
                        present.append(name)
                except Exception:
                    present.append(name)
        self.fields["DataFrames Present"].set(", ".join(present) if present else "None")

    def _fmt_ts(self, ts):
        if ts is None:
            return "-"
        try:
            if isinstance(ts, (int, float)):
                # Heuristic: treat large numbers as epoch seconds
                if ts > 1e12:  # likely ns
                    ts = ts / 1e9
                if ts > 1e10:  # ms
                    ts = ts / 1e3
                return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            # If pandas Timestamp or datetime
            if hasattr(ts, 'to_pydatetime'):
                ts = ts.to_pydatetime()
            if isinstance(ts, datetime):
                return ts.strftime('%Y-%m-%d %H:%M:%S')
            return str(ts)[:19]
        except Exception:
            return str(ts)
