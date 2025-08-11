"""XY config formatter functions & registry.

Uses FormatterSupport helpers to reduce duplication across
formatters. Each formatter returns a pass-through config for the generic_xy
pipeline in PlotManager.
"""
from __future__ import annotations
from typing import Any, Dict, List, Tuple, Sequence, Protocol, Callable, Optional
import itertools
from .formatter_support import FormatterSupport as FS
from ..utils.schema_access import get_col

class Formatter(Protocol):  # structural type for static checking
    def __call__(self, app_state, widgets: Sequence[Any]) -> Dict[str, Any]: ...  # pragma: no cover

FORMATTER_REGISTRY: Dict[str, Formatter] = {}

def register_formatter(name: str) -> Callable[[Formatter], Formatter]:
    def _decorator(func: Formatter) -> Formatter:
        FORMATTER_REGISTRY[name] = func
        return func
    return _decorator

def get_formatter(name: str) -> Optional[Formatter]:
    return FORMATTER_REGISTRY.get(name)

@register_formatter('north_error_over_time')
def north_error_over_time(app_state, widgets: Sequence[Any]) -> Dict[str, Any]:
    """Formatter for north (latitudinal) positional error vs time, per track (multi-series).

    Assumes each selected track has timestamps on a uniform cadence. If lengths differ,
    series are truncated to the shortest length so that a shared X axis can be used.
    """
    focus_dfs = FS.get_focus_or_empty(app_state)
    if not focus_dfs:
        return {'x': [], 'y': [], 'title': 'North Error'}
    schema = getattr(focus_dfs, 'schema', None)
    capabilities = getattr(focus_dfs, 'capabilities', []) or []

    # Track selection
    selected_tracks = FS.extract_selected_tracks(widgets)
    if selected_tracks is None or len(selected_tracks) == 0:
        return {'x': [], 'y': [], 'title': 'North Error'}

    import numpy as np, pandas as pd
    series_dict: Dict[str, List[float]] = {}
    time_arrays: List[List[Any]] = []

    # Precomputed errors fast-path
    if 'precomputed_errors' in capabilities and getattr(focus_dfs, 'errors_df', None) is not None:
        errors_df = getattr(focus_dfs, 'errors_df')
        if errors_df is not None and not errors_df.empty:
            track_col = get_col(schema, 'errors', 'track_id')
            ts_col    = get_col(schema, 'errors', 'timestamp')
            north_col = get_col(schema, 'errors', 'north_error')
            if all(c in errors_df.columns for c in [track_col, ts_col, north_col]):
                df = errors_df[errors_df[track_col].isin(selected_tracks)] if selected_tracks else errors_df
                if not df.empty:
                    try:
                        for track_id, grp in df.groupby(track_col):
                            grp_sorted = grp.sort_values(ts_col)
                            errs = grp_sorted[north_col].dropna().astype(float).tolist()
                            ts = pd.to_datetime(grp_sorted[ts_col])
                            if errs and not ts.empty:
                                series_dict[f"North Error {track_id}"] = errs
                                time_arrays.append(ts.tolist())
                    except Exception:
                        series_dict = {}
                        time_arrays = []
        # If we populated series_dict, proceed to axis build; else fall back
    if not series_dict:
        tracks_df = getattr(focus_dfs, 'tracks_df', None)
        truth_df  = getattr(focus_dfs, 'truth_df', None)
        if tracks_df is None or truth_df is None or tracks_df.empty or truth_df.empty:
            return {'x': [], 'y': [], 'title': 'North Error'}
        t_id_col  = get_col(schema, 'tracks', 'track_id')
        t_ts_col  = get_col(schema, 'tracks', 'timestamp')
        t_lat_col = get_col(schema, 'tracks', 'lat')
        tr_ts_col = get_col(schema, 'truth',  'timestamp')
        tr_lat_col= get_col(schema, 'truth',  'lat')
        if not all(c in tracks_df.columns for c in [t_id_col, t_ts_col, t_lat_col]) or not all(c in truth_df.columns for c in [tr_ts_col, tr_lat_col]):
            return {'x': [], 'y': [], 'title': 'North Error'}
        if selected_tracks and t_id_col in tracks_df.columns:
            tracks_df = tracks_df[tracks_df[t_id_col].isin(selected_tracks)]
            if tracks_df.empty:
                return {'x': [], 'y': [], 'title': 'North Error'}
        for track_id, df_track in tracks_df.groupby(t_id_col):
            df_track = df_track.sort_values(t_ts_col)
            north_errors: List[float] = []
            times: List[Any] = []
            for _, track_row in df_track.iterrows():
                try:
                    diffs = (truth_df[tr_ts_col] - track_row[t_ts_col]).abs()
                    idx = diffs.idxmin()
                    truth_row = truth_df.loc[idx]
                    lat_error = (track_row[t_lat_col] - truth_row[tr_lat_col]) * 111000.0
                except Exception:
                    continue
                north_errors.append(float(lat_error))
                times.append(track_row[t_ts_col])
            if north_errors and times:
                series_dict[f"North Error {track_id}"] = north_errors
                time_arrays.append(times)

    if not series_dict:
        return {'x': [], 'y': [], 'title': 'North Error'}

    # Align lengths (truncate to shortest) and build shared relative time axis
    min_len = min(len(v) for v in series_dict.values())
    for k in list(series_dict.keys()):
        series_dict[k] = series_dict[k][:min_len]
    # Use first time array truncated
    import pandas as pd  # re-import safe
    base_times = pd.to_datetime(time_arrays[0][:min_len])
    start = base_times.min()
    x_seconds = [(t - start).total_seconds() for t in base_times]

    # Dynamic styles
    series_styles = FS.get_series_styles(series_dict.keys(), 'solid')

    return {
        'x': x_seconds,
        'y': series_dict,
        'title': 'North Position Error (per Track)',
        'xlabel': 'Time (s)',
        'ylabel': 'Error (m)',
        'style': 'line',
        'series_styles': series_styles,
    }


@register_formatter('east_error_over_time')
def east_error_over_time(app_state, widgets: Sequence[Any]) -> Dict[str, Any]:
    """Formatter for east (longitudinal) positional error vs time, per track (multi-series)."""
    focus_dfs = FS.get_focus_or_empty(app_state)
    if not focus_dfs:
        return {'x': [], 'y': [], 'title': 'East Error'}
    schema = getattr(focus_dfs, 'schema', None)
    capabilities = getattr(focus_dfs, 'capabilities', []) or []
    selected_tracks = FS.extract_selected_tracks(widgets)
    if selected_tracks is None or len(selected_tracks) == 0:
        return {'x': [], 'y': [], 'title': 'East Error'}
    import numpy as np, pandas as pd
    series_dict: Dict[str, List[float]] = {}
    time_arrays: List[List[Any]] = []
    if 'precomputed_errors' in capabilities and getattr(focus_dfs, 'errors_df', None) is not None:
        errors_df = getattr(focus_dfs, 'errors_df')
        track_col = get_col(schema, 'errors', 'track_id')
        ts_col    = get_col(schema, 'errors', 'timestamp')
        east_col  = get_col(schema, 'errors', 'east_error')
        lat_col_truth = get_col(schema, 'truth', 'lat')  # needed for cosine if computing manually; not needed here
        if errors_df is not None and not errors_df.empty and all(c in errors_df.columns for c in [track_col, ts_col, east_col]):
            df = errors_df[errors_df[track_col].isin(selected_tracks)] if selected_tracks else errors_df
            if not df.empty:
                try:
                    for track_id, grp in df.groupby(track_col):
                        grp_sorted = grp.sort_values(ts_col)
                        errs = grp_sorted[east_col].dropna().astype(float).tolist()
                        ts = pd.to_datetime(grp_sorted[ts_col])
                        if errs and not ts.empty:
                            series_dict[f"East Error {track_id}"] = errs
                            time_arrays.append(ts.tolist())
                except Exception:
                    series_dict = {}
                    time_arrays = []
    if not series_dict:
        tracks_df = getattr(focus_dfs, 'tracks_df', None)
        truth_df  = getattr(focus_dfs, 'truth_df', None)
        if tracks_df is None or truth_df is None or tracks_df.empty or truth_df.empty:
            return {'x': [], 'y': [], 'title': 'East Error'}
        t_id_col  = get_col(schema, 'tracks', 'track_id')
        t_ts_col  = get_col(schema, 'tracks', 'timestamp')
        t_lon_col = get_col(schema, 'tracks', 'lon')
        tr_ts_col = get_col(schema, 'truth',  'timestamp')
        tr_lon_col= get_col(schema, 'truth',  'lon')
        tr_lat_col= get_col(schema, 'truth',  'lat')
        if not all(c in tracks_df.columns for c in [t_id_col, t_ts_col, t_lon_col]) or not all(c in truth_df.columns for c in [tr_ts_col, tr_lon_col, tr_lat_col]):
            return {'x': [], 'y': [], 'title': 'East Error'}
        if selected_tracks and t_id_col in tracks_df.columns:
            tracks_df = tracks_df[tracks_df[t_id_col].isin(selected_tracks)]
            if tracks_df.empty:
                return {'x': [], 'y': [], 'title': 'East Error'}
        for track_id, df_track in tracks_df.groupby(t_id_col):
            df_track = df_track.sort_values(t_ts_col)
            east_errors: List[float] = []
            times: List[Any] = []
            for _, track_row in df_track.iterrows():
                try:
                    diffs = (truth_df[tr_ts_col] - track_row[t_ts_col]).abs()
                    idx = diffs.idxmin()
                    truth_row = truth_df.loc[idx]
                    east_error = (track_row[t_lon_col] - truth_row[tr_lon_col]) * 111000.0 * np.cos(np.radians(truth_row[tr_lat_col]))
                except Exception:
                    continue
                east_errors.append(float(east_error))
                times.append(track_row[t_ts_col])
            if east_errors and times:
                series_dict[f"East Error {track_id}"] = east_errors
                time_arrays.append(times)

    if not series_dict:
        return {'x': [], 'y': [], 'title': 'East Error'}

    min_len = min(len(v) for v in series_dict.values())
    for k in list(series_dict.keys()):
        series_dict[k] = series_dict[k][:min_len]
    base_times = pd.to_datetime(time_arrays[0][:min_len])
    start = base_times.min()
    x_seconds = [(t - start).total_seconds() for t in base_times]

    series_styles = FS.get_series_styles(series_dict.keys(), 'dashed')

    return {
        'x': x_seconds,
        'y': series_dict,
        'title': 'East Position Error (per Track)',
        'xlabel': 'Time (s)',
        'ylabel': 'Error (m)',
        'style': 'line',
        'series_styles': series_styles,
    }

@register_formatter('rms_error_3d_over_time')
def rms_error_3d_over_time(app_state, widgets: Sequence[Any]) -> Dict[str, Any]:
    """Compute 3D positional error magnitude vs time per track (multi-series RMS-style plot).

    For each trackId we provide a separate error magnitude time series (sqrt(dx^2+dy^2+dz^2)).
    All series share a common X axis truncated to the minimum length across tracks for alignment.
    Honors selected tracks; if multiple, each becomes its own line.
    """
    focus_dfs = FS.get_focus_or_empty(app_state)
    if not focus_dfs:
        return {'x': [], 'y': [], 'title': 'RMS 3D Error'}
    schema = getattr(focus_dfs, 'schema', None)
    capabilities = getattr(focus_dfs, 'capabilities', []) or []

    # Track selection
    selected_tracks = None
    for w in widgets:
        try:
            if hasattr(w, 'get_selected_tracks'):
                sel = w.get_selected_tracks()
                if sel is not None:
                    selected_tracks = sel
                    break
        except Exception:
            pass

    import numpy as np, pandas as pd
    series_dict: Dict[str, List[float]] = {}
    time_arrays: List[List[Any]] = []
    # Simplest path: compute from track + truth (even if precomputed errors exist) for altitude consistency
    tracks_df = getattr(focus_dfs, 'tracks_df', None)
    truth_df  = getattr(focus_dfs, 'truth_df', None)
    if tracks_df is None or truth_df is None or tracks_df.empty or truth_df.empty:
        return {'x': [], 'y': [], 'title': 'RMS 3D Error'}
    t_id_col  = get_col(schema, 'tracks', 'track_id')
    t_ts_col  = get_col(schema, 'tracks', 'timestamp')
    t_lat_col = get_col(schema, 'tracks', 'lat')
    t_lon_col = get_col(schema, 'tracks', 'lon')
    t_alt_col = get_col(schema, 'tracks', 'alt')
    tr_ts_col = get_col(schema, 'truth',  'timestamp')
    tr_lat_col= get_col(schema, 'truth',  'lat')
    tr_lon_col= get_col(schema, 'truth',  'lon')
    tr_alt_col= get_col(schema, 'truth',  'alt')
    if selected_tracks is not None:
        if len(selected_tracks) == 0:
            return {'x': [], 'y': [], 'title': 'RMS 3D Error'}
        if t_id_col in tracks_df.columns:
            tracks_df = tracks_df[tracks_df[t_id_col].isin(selected_tracks)]
    if tracks_df.empty:
        return {'x': [], 'y': [], 'title': 'RMS 3D Error'}
    try:
        for track_id, df_track in tracks_df.groupby(t_id_col):
            df_track = df_track.sort_values(t_ts_col)
            errs: List[float] = []
            times: List[Any] = []
            for _, track_row in df_track.iterrows():
                try:
                    diffs = (truth_df[tr_ts_col] - track_row[t_ts_col]).abs()
                    idx = diffs.idxmin()
                    truth_row = truth_df.loc[idx]
                    lat_error = (track_row[t_lat_col] - truth_row[tr_lat_col]) * 111000.0
                    lon_error = (track_row[t_lon_col] - truth_row[tr_lon_col]) * 111000.0 * np.cos(np.radians(truth_row[tr_lat_col]))
                    alt_error = 0.0
                    if t_alt_col in track_row and tr_alt_col in truth_row:
                        try:
                            alt_error = (track_row[t_alt_col] - truth_row[tr_alt_col])
                        except Exception:
                            alt_error = 0.0
                    err_mag = float(np.sqrt(lat_error**2 + lon_error**2 + alt_error**2))
                except Exception:
                    continue
                errs.append(err_mag)
                times.append(track_row[t_ts_col])
            if errs and times:
                series_dict[f"RMS 3D Error {track_id}"] = errs
                time_arrays.append(times)
    except Exception:
        return {'x': [], 'y': [], 'title': 'RMS 3D Error'}

    if not series_dict:
        return {'x': [], 'y': [], 'title': 'RMS 3D Error'}

    # Truncate to shortest length for a shared X axis
    min_len = min(len(v) for v in series_dict.values())
    for k in list(series_dict.keys()):
        series_dict[k] = series_dict[k][:min_len]
    ts = pd.to_datetime(time_arrays[0][:min_len])
    start = ts.min()
    x_seconds = [(t - start).total_seconds() for t in ts]

    import itertools
    series_styles = FS.get_series_styles(series_dict.keys(), 'solid')

    return {
        'x': x_seconds,
        'y': series_dict,
        'title': '3D Error Magnitude (per Track)',
        'xlabel': 'Time (s)',
        'ylabel': 'Error (m)',
        'style': 'line',
        'series_styles': series_styles,
    }

"""Formatter for track existence (lifetime) lines.

Produces an XY config where each selected (or all) track IDs becomes a horizontal line
at Y = track_index (or track_id label) spanning from first to last timestamp.
"""

@register_formatter('track_existence_over_time')
def track_existence_over_time(app_state, widgets: Sequence[Any]) -> Dict[str, Any]:
    focus_dfs = FS.get_focus_or_empty(app_state)
    if not focus_dfs or getattr(focus_dfs, 'tracks_df', None) is None:
        return {"x": [], "y": [], "title": "Track Lifetimes"}
    tracks_df = focus_dfs.tracks_df
    if tracks_df is None or tracks_df.empty:
        return {"x": [], "y": [], "title": "Track Lifetimes"}
    schema = getattr(focus_dfs, 'schema', None)
    t_id_col = get_col(schema, 'tracks', 'track_id')
    t_ts_col = get_col(schema, 'tracks', 'timestamp')

    # Track selection
    selected_tracks = None
    for w in widgets:
        try:
            if hasattr(w, 'get_selected_tracks'):
                sel = w.get_selected_tracks()
                if sel is not None:
                    selected_tracks = sel
                    break
        except Exception:
            pass

    df = tracks_df
    if selected_tracks is not None and len(selected_tracks) > 0 and t_id_col in df.columns:
        df = df[df[t_id_col].isin(selected_tracks)]
    if df.empty:
        return {"x": [], "y": [], "title": "Track Lifetimes"}

    # Group by track and compute start/end
    import pandas as pd
    if t_ts_col in df.columns:
        df = df.sort_values(t_ts_col)
    series_dict: Dict[str, List[float]] = {}
    starts = []
    ends = []
    labels = []  # original track_id labels (could be non-numeric)
    if t_id_col not in df.columns:
        return {"x": [], "y": [], "title": "Track Lifetimes"}
    for idx, (track_id, grp) in enumerate(df.groupby(t_id_col)):
        if t_ts_col not in grp.columns:
            continue
        ts = pd.to_datetime(grp[t_ts_col])
        start = ts.min()
        end = ts.max()
        # Represent as two-point line; XYPlot expects full x list for each series
        series_dict[f"Track {track_id}"] = [idx, idx]  # y values constant
        starts.append(start)
        ends.append(end)
        labels.append(track_id)

    if not series_dict:
        return {"x": [], "y": [], "title": "Track Lifetimes"}

    # Build unified x axis: we'll just use relative seconds; each series will map to same x list length 2
    global_start = min(starts)
    import pandas as pd  # safe reimport
    x_seconds = [(s - global_start).total_seconds() for s in starts]
    x_seconds_end = [(e - global_start).total_seconds() for e in ends]

    # Need per-series x; generic_xy currently takes one shared 'x'. To encode variable spans,
    # we expand to piecewise: we will create a combined x with two entries (start,end) per series length 2
    # and store per-series y of same length. This assumes all series share identical x array which isn't true.
    # Workaround: choose a dense x across all endpoints and for each series use NaN outside span.
    all_points = sorted(set(x_seconds + x_seconds_end))
    import numpy as np
    series_dense: Dict[str, List[float]] = {}
    series_styles: Dict[str, Dict[str, Any]] = {}
    colors = ['tab:blue','tab:orange','tab:green','tab:red','tab:purple','tab:brown','tab:pink','tab:gray','tab:olive','tab:cyan']
    for idx, track_id in enumerate(labels):
        start_sec = x_seconds[idx]
        end_sec = x_seconds_end[idx]
        y_vals = []
        for t in all_points:
            if start_sec <= t <= end_sec:
                y_vals.append(idx)
            else:
                y_vals.append(float('nan'))
        key = f"Track {track_id}"
        series_dense[key] = y_vals
        series_styles[key] = {
            'type': 'line', 'color': colors[idx % len(colors)], 'linestyle': '-', 'marker': None, 'label': key
        }
    # Provide y-axis tick metadata so backend or consumer can set ticks/labels and padding
    y_tick_positions = list(range(len(labels)))
    y_tick_labels = [str(l) for l in labels]
    padding = 0.5  # visual padding above/below
    return {
        'x': all_points,
        'y': series_dense,
        'title': 'Track Lifetimes (Existence)',
        'xlabel': 'Time (s)',
        'ylabel': 'Track ID',
        'style': 'line',
        'series_styles': series_styles,
        'y_ticks': {'positions': y_tick_positions, 'labels': y_tick_labels, 'padding': padding},
    }
