"""Formatter support utilities.

Provides shared helper logic to reduce duplication across XY config formatter
functions (error metrics, lifetime plots, etc.). Extracting this logic keeps
each formatter focused on domain-specific transformation while this module
centralizes:

    - Focus dataset validation
    - Track selection extraction from provided widgets
    - Nearest-truth row matching for per-track timestamps
    - Time axis alignment + truncation of multi-series to a common length
    - Simple style generation (colors / markers / line variants)

These helpers intentionally avoid any GUI dependencies beyond the minimal
"widget has method" duck-typing already present in existing code.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import itertools

try:  # Optional heavy dependencies (guard for faster import path)
    import pandas as pd  # type: ignore
    import numpy as np  # type: ignore
except Exception:  # pragma: no cover - should exist in runtime env
    pd = None  # type: ignore
    np = None  # type: ignore

COLOR_CYCLE = [
    'tab:blue','tab:orange','tab:green','tab:red','tab:purple',
    'tab:brown','tab:pink','tab:gray','tab:olive','tab:cyan'
]
MARKER_CYCLE = ['o','s','^','D','v','>','<','P','X','*']

@dataclass
class FocusDataFrames:
    """Lightweight container for focus dataset dataframes of interest."""
    tracks_df: Any = None
    truth_df: Any = None

class FormatterSupport:
    """Namespace of static helper methods used by formatters."""

    @staticmethod
    def get_focus_or_empty(app_state) -> Optional[FocusDataFrames]:
        """Return FocusDataFrames if focus dataset loaded & non-empty else None."""
        try:
            focus = app_state.get_focus_dataset_info()
            if not focus or focus.status.value != "loaded":
                return None
            tracks_df = getattr(focus, 'tracks_df', None)
            truth_df = getattr(focus, 'truth_df', None)
            return FocusDataFrames(tracks_df=tracks_df, truth_df=truth_df)
        except Exception:
            return None

    @staticmethod
    def extract_selected_tracks(widgets: Sequence[Any]) -> Optional[List[Any]]:
        """Return selected track IDs from first widget exposing get_selected_tracks.

        None => no selection context (formatter should usually return empty plot).
        []   => explicit empty selection (formatter should return empty data).
        list => concrete selection.
        """
        for w in widgets:
            try:
                if hasattr(w, 'get_selected_tracks'):
                    sel = w.get_selected_tracks()
                    return sel  # may be list or []
            except Exception:
                continue
        return None

    @staticmethod
    def compute_nearest_truth_rows(track_rows, truth_df) -> List[Tuple[Any, Any]]:
        """Return list of (track_row, matched_truth_row) using nearest timestamp."""
        pairs: List[Tuple[Any, Any]] = []
        if truth_df is None or track_rows is None:
            return pairs
        try:
            for _, tr in track_rows.iterrows():
                try:
                    time_diffs = (truth_df['timestamp'] - tr['timestamp']).abs()
                    closest_idx = time_diffs.idxmin()
                    pairs.append((tr, truth_df.loc[closest_idx]))
                except Exception:
                    continue
        except Exception:
            return []
        return pairs

    @staticmethod
    def build_time_axis_and_truncate(
        series_dict: Dict[str, List[float]],
        list_of_time_lists: List[List[Any]]
    ) -> Tuple[List[float], Dict[str, List[float]]]:
        """Truncate all series to shortest length and build relative-seconds X axis."""
        if not series_dict or not list_of_time_lists:
            return [], {}
        try:
            min_len = min(len(v) for v in series_dict.values() if v)
        except ValueError:
            return [], {}
        if min_len <= 0:
            return [], {}
        for k in list(series_dict.keys()):
            series_dict[k] = series_dict[k][:min_len]
        try:
            if pd is not None:
                ts = pd.to_datetime(list_of_time_lists[0][:min_len])
                start = ts.min()
                x_seconds = [(t - start).total_seconds() for t in ts]
            else:  # numeric or datetime-like fallback (assumes arithmetic works)
                base_series = list_of_time_lists[0][:min_len]
                base0 = base_series[0]
                try:
                    x_seconds = [float(t - base0) for t in base_series]
                except Exception:
                    # last resort: enumerated index
                    x_seconds = list(range(len(base_series)))
        except Exception:
            return [], {}
        # Ensure float list for type consistency
        try:
            x_seconds_float = [float(v) for v in x_seconds]
        except Exception:
            x_seconds_float = []
        return x_seconds_float, series_dict

    @staticmethod
    def get_series_styles(
        labels: Iterable[str],
        line_styles_variant: str = 'solid'
    ) -> Dict[str, Dict[str, Any]]:
        """Generate style dict for labels with optional line style variant."""
        styles: Dict[str, Dict[str, Any]] = {}
        colors = itertools.cycle(COLOR_CYCLE)
        markers = itertools.cycle(MARKER_CYCLE)
        dash_cycle = itertools.cycle(['-', '--', '-.', ':'])
        for label in labels:
            if line_styles_variant == 'solid':
                linestyle = '-'
            elif line_styles_variant == 'dashed':
                linestyle = '--'
            elif line_styles_variant == 'mixed':
                linestyle = next(dash_cycle)
            else:
                linestyle = '-'
            styles[label] = {
                'type': 'line',
                'color': next(colors),
                'marker': next(markers),
                'linestyle': linestyle,
                'label': label,
            }
        return styles

__all__ = [
    'FormatterSupport',
    'FocusDataFrames',
    'COLOR_CYCLE',
    'MARKER_CYCLE',
]
