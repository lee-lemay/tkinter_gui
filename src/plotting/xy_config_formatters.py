"""
Formatter utilities for XYPlotTabWidget.

Each formatter must be a callable: (app_state, widgets) -> Dict[str, Any]
It returns a config dict with keys:
  - x: list of x values (required)
  - y: list or dict of y series (required). If dict, keys are series labels.
  - title/xlabel/ylabel/style: optional
"""
from __future__ import annotations
from typing import Any, Dict, List, Tuple
import itertools


def error_north_east_over_time(app_state, widgets: List[Any]) -> Dict[str, Any]:
    """Build north/east error time series, replicating ErrorAnalysisTab logic via PlotManager.

    This formatter directly computes errors similar to PlotManager._prepare_north_east_error_data
    but returns pass-through x/y arrays for the generic_xy pipeline.
    """
    focus = app_state.get_focus_dataset_info()
    if not focus or focus.status.value != "loaded":
        return {'x': [], 'y': [], 'title': 'Error Analysis'}

    tracks_df = getattr(focus, 'tracks_df', None)
    truth_df = getattr(focus, 'truth_df', None)
    if tracks_df is None or truth_df is None or tracks_df.empty or truth_df.empty:
        return {'x': [], 'y': [], 'title': 'Error Analysis'}

    # Get track selection from any DataSelectionWidget or TrackSelectionWidget in widgets
    selected_tracks = None
    for w in widgets:
        try:
            if hasattr(w, 'get_selected_tracks'):
                sel = w.get_selected_tracks()
                if sel:
                    selected_tracks = sel
                    break
        except Exception:
            pass

    import numpy as np
    import pandas as pd
    # Filter tracks if selection present
    if selected_tracks is not None:
        if len(selected_tracks) > 0:
          if 'track_id' in tracks_df.columns:
              tracks_df = tracks_df[tracks_df['track_id'].isin(selected_tracks)]
        else:
            return {'x': [], 'y': [], 'title': 'Error Analysis'}
    else:
        return {'x': [], 'y': [], 'title': 'Error Analysis'}

    if tracks_df.empty:
        return {'x': [], 'y': [], 'title': 'Error Analysis'}

    north_errors = []
    east_errors = []
    times = []

    try:
        for _, track_row in tracks_df.iterrows():
            time_diffs = abs(truth_df['timestamp'] - track_row['timestamp'])
            closest_idx = time_diffs.idxmin()
            truth_row = truth_df.loc[closest_idx]
            lat_error = (track_row['lat'] - truth_row['lat']) * 111000
            lon_error = (track_row['lon'] - truth_row['lon']) * 111000 * np.cos(np.radians(truth_row['lat']))
            north_errors.append(lat_error)
            east_errors.append(lon_error)
            times.append(track_row['timestamp'])
    except Exception:
        return {'x': [], 'y': [], 'title': 'Error Analysis'}

    if not times:
        return {'x': [], 'y': [], 'title': 'Error Analysis'}

    # Convert timestamps to relative seconds from start
    ts = pd.to_datetime(times)
    start = ts.min()
    x_seconds = [(t - start).total_seconds() for t in ts]

    return {
        'x': x_seconds,
        'y': {'North Error': north_errors, 'East Error': east_errors},
        'title': 'North/East Position Errors',
        'xlabel': 'Time (s)',
        'ylabel': 'Error (m)',
        'style': 'line',
        'series_styles': {
            'North Error': {'type': 'line', 'color': 'tab:blue', 'marker': 'o', 'linestyle': '-', 'label': 'North Error'},
            'East Error': {'type': 'line', 'color': 'tab:orange', 'marker': 's', 'linestyle': '--', 'label': 'East Error'}
        }
    }


# --- Split North / East individual error formatter helpers ---
def _compute_north_east_errors(app_state, widgets: List[Any]) -> Tuple[List[float], List[float], List[float]]:
    """Internal helper returning (x_seconds, north_errors, east_errors) or empty lists if unavailable."""
    focus = app_state.get_focus_dataset_info()
    if not focus or focus.status.value != "loaded":
        return [], [], []

    tracks_df = getattr(focus, 'tracks_df', None)
    truth_df = getattr(focus, 'truth_df', None)
    if tracks_df is None or truth_df is None or tracks_df.empty or truth_df.empty:
        return [], [], []

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

    if selected_tracks is None:
        return [], [], []
    if len(selected_tracks) == 0:
        return [], [], []

    if 'track_id' in tracks_df.columns:
        tracks_df = tracks_df[tracks_df['track_id'].isin(selected_tracks)]
    if tracks_df.empty:
        return [], [], []

    import numpy as np
    import pandas as pd

    north_errors: List[float] = []
    east_errors: List[float] = []
    times = []
    try:
        for _, track_row in tracks_df.iterrows():
            time_diffs = abs(truth_df['timestamp'] - track_row['timestamp'])
            closest_idx = time_diffs.idxmin()
            truth_row = truth_df.loc[closest_idx]
            lat_error = (track_row['lat'] - truth_row['lat']) * 111000
            lon_error = (track_row['lon'] - truth_row['lon']) * 111000 * np.cos(np.radians(truth_row['lat']))
            north_errors.append(lat_error)
            east_errors.append(lon_error)
            times.append(track_row['timestamp'])
    except Exception:
        return [], [], []

    if not times:
        return [], [], []

    ts = pd.to_datetime(times)
    start = ts.min()
    x_seconds = [(t - start).total_seconds() for t in ts]
    return x_seconds, north_errors, east_errors


def north_error_over_time(app_state, widgets: List[Any]) -> Dict[str, Any]:
    """Formatter for north (latitudinal) positional error vs time, per track (multi-series).

    Assumes each selected track has timestamps on a uniform cadence. If lengths differ,
    series are truncated to the shortest length so that a shared X axis can be used.
    """
    focus = app_state.get_focus_dataset_info()
    if not focus or focus.status.value != "loaded":
        return {'x': [], 'y': [], 'title': 'North Error'}
    tracks_df = getattr(focus, 'tracks_df', None)
    truth_df = getattr(focus, 'truth_df', None)
    if tracks_df is None or truth_df is None or tracks_df.empty or truth_df.empty:
        return {'x': [], 'y': [], 'title': 'North Error'}

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
    if selected_tracks is None or len(selected_tracks) == 0:
        return {'x': [], 'y': [], 'title': 'North Error'}
    if 'track_id' in tracks_df.columns:
        tracks_df = tracks_df[tracks_df['track_id'].isin(selected_tracks)]
    if tracks_df.empty:
        return {'x': [], 'y': [], 'title': 'North Error'}

    import numpy as np
    import pandas as pd

    series_dict: Dict[str, List[float]] = {}
    time_arrays: List[List[Any]] = []

    for track_id, df_track in tracks_df.groupby('track_id'):
        df_track = df_track.sort_values('timestamp')
        north_errors: List[float] = []
        times: List[Any] = []
        for _, track_row in df_track.iterrows():
            try:
                time_diffs = abs(truth_df['timestamp'] - track_row['timestamp'])
                closest_idx = time_diffs.idxmin()
                truth_row = truth_df.loc[closest_idx]
                lat_error = (track_row['lat'] - truth_row['lat']) * 111000
            except Exception:
                continue
            north_errors.append(lat_error)
            times.append(track_row['timestamp'])
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
    color_cycle = ['tab:blue','tab:orange','tab:green','tab:red','tab:purple','tab:brown','tab:pink','tab:gray','tab:olive','tab:cyan']
    markers = itertools.cycle(['o','s','^','D','v','>','<','P','X','*'])
    series_styles: Dict[str, Dict[str, Any]] = {}
    for idx, key in enumerate(series_dict.keys()):
        series_styles[key] = {
            'type': 'line',
            'color': color_cycle[idx % len(color_cycle)],
            'marker': next(markers),
            'linestyle': '-',
            'label': key,
        }

    return {
        'x': x_seconds,
        'y': series_dict,
        'title': 'North Position Error (per Track)',
        'xlabel': 'Time (s)',
        'ylabel': 'Error (m)',
        'style': 'line',
        'series_styles': series_styles,
    }


def east_error_over_time(app_state, widgets: List[Any]) -> Dict[str, Any]:
    """Formatter for east (longitudinal) positional error vs time, per track (multi-series)."""
    focus = app_state.get_focus_dataset_info()
    if not focus or focus.status.value != "loaded":
        return {'x': [], 'y': [], 'title': 'East Error'}
    tracks_df = getattr(focus, 'tracks_df', None)
    truth_df = getattr(focus, 'truth_df', None)
    if tracks_df is None or truth_df is None or tracks_df.empty or truth_df.empty:
        return {'x': [], 'y': [], 'title': 'East Error'}

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
    if selected_tracks is None or len(selected_tracks) == 0:
        return {'x': [], 'y': [], 'title': 'East Error'}
    if 'track_id' in tracks_df.columns:
        tracks_df = tracks_df[tracks_df['track_id'].isin(selected_tracks)]
    if tracks_df.empty:
        return {'x': [], 'y': [], 'title': 'East Error'}

    import numpy as np
    import pandas as pd

    series_dict: Dict[str, List[float]] = {}
    time_arrays: List[List[Any]] = []
    for track_id, df_track in tracks_df.groupby('track_id'):
        df_track = df_track.sort_values('timestamp')
        east_errors: List[float] = []
        times: List[Any] = []
        for _, track_row in df_track.iterrows():
            try:
                time_diffs = abs(truth_df['timestamp'] - track_row['timestamp'])
                closest_idx = time_diffs.idxmin()
                truth_row = truth_df.loc[closest_idx]
                east_error = (track_row['lon'] - truth_row['lon']) * 111000 * np.cos(np.radians(truth_row['lat']))
            except Exception:
                continue
            east_errors.append(east_error)
            times.append(track_row['timestamp'])
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

    color_cycle = ['tab:blue','tab:orange','tab:green','tab:red','tab:purple','tab:brown','tab:pink','tab:gray','tab:olive','tab:cyan']
    markers = itertools.cycle(['o','s','^','D','v','>','<','P','X','*'])
    series_styles: Dict[str, Dict[str, Any]] = {}
    for idx, key in enumerate(series_dict.keys()):
        series_styles[key] = {
            'type': 'line',
            'color': color_cycle[idx % len(color_cycle)],
            'marker': next(markers),
            'linestyle': '--',
            'label': key,
        }

    return {
        'x': x_seconds,
        'y': series_dict,
        'title': 'East Position Error (per Track)',
        'xlabel': 'Time (s)',
        'ylabel': 'Error (m)',
        'style': 'line',
        'series_styles': series_styles,
    }


def example_tracks_lat_lon_over_time(app_state, widgets: List[Any]) -> Dict[str, Any]:
    """Example: build x/y from focus dataset tracks: time vs lat and lon.
    If a DataSelectionWidget is present in widgets, honor selected tracks.
    """
    focus = app_state.get_focus_dataset_info()
    if not focus or focus.status.value != "loaded" or focus.tracks_df is None or focus.tracks_df.empty:
        return {'x': [], 'y': []}

    df = focus.tracks_df

    # Try to get selections from DataSelectionWidget if provided
    selected_tracks = None
    for w in widgets:
        try:
            if hasattr(w, 'get_selected_tracks'):
                selected_tracks = w.get_selected_tracks()
                break
        except Exception:
            pass

    if selected_tracks and isinstance(selected_tracks, list) and 'All' not in selected_tracks:
        df = df[df['track_id'].isin(selected_tracks)]

    if df.empty:
        return {'x': [], 'y': []}

    # Sort by timestamp if present
    if 'timestamp' in df.columns:
        df = df.sort_values('timestamp')
        x_vals = df['timestamp'].tolist()
    else:
        x_vals = list(range(len(df)))

    series: Dict[str, Any] = {}
    if 'lat' in df.columns:
        series['lat'] = df['lat'].tolist()
    if 'lon' in df.columns:
        series['lon'] = df['lon'].tolist()

    return {
        'x': x_vals,
        'y': series if series else [],
        'title': 'Tracks lat/lon over time',
        'xlabel': 'Time',
        'ylabel': 'Value',
        'style': 'line',
    }


def rms_error_3d_over_time(app_state, widgets: List[Any]) -> Dict[str, Any]:
    """Compute 3D positional error magnitude vs time per track (multi-series RMS-style plot).

    For each trackId we provide a separate error magnitude time series (sqrt(dx^2+dy^2+dz^2)).
    All series share a common X axis truncated to the minimum length across tracks for alignment.
    Honors selected tracks; if multiple, each becomes its own line.
    """
    focus = app_state.get_focus_dataset_info()
    if not focus or focus.status.value != "loaded":
        return {'x': [], 'y': [], 'title': 'RMS 3D Error'}

    tracks_df = getattr(focus, 'tracks_df', None)
    truth_df = getattr(focus, 'truth_df', None)
    if tracks_df is None or truth_df is None or tracks_df.empty or truth_df.empty:
        return {'x': [], 'y': [], 'title': 'RMS 3D Error'}

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

    if selected_tracks is not None:
        # If empty selection explicitly, return empty plot
        if len(selected_tracks) == 0:
            return {'x': [], 'y': [], 'title': 'RMS 3D Error'}
        if 'track_id' in tracks_df.columns:
            tracks_df = tracks_df[tracks_df['track_id'].isin(selected_tracks)]
    if tracks_df.empty:
        return {'x': [], 'y': [], 'title': 'RMS 3D Error'}
    

    import numpy as np
    import pandas as pd

    series_dict: Dict[str, List[float]] = {}
    time_arrays: List[List[Any]] = []
    try:
        for track_id, df_track in tracks_df.groupby('track_id'):
            df_track = df_track.sort_values('timestamp')
            errs: List[float] = []
            times: List[Any] = []
            for _, track_row in df_track.iterrows():
                try:
                    time_diffs = abs(truth_df['timestamp'] - track_row['timestamp'])
                    closest_idx = time_diffs.idxmin()
                    truth_row = truth_df.loc[closest_idx]
                    lat_error = (track_row['lat'] - truth_row['lat']) * 111000
                    lon_error = (track_row['lon'] - truth_row['lon']) * 111000 * np.cos(np.radians(truth_row['lat']))
                    alt_error = 0.0
                    if 'alt' in track_row and 'alt' in truth_row:
                        try:
                            alt_error = (track_row['alt'] - truth_row['alt'])
                        except Exception:
                            alt_error = 0.0
                    err_mag = np.sqrt(lat_error**2 + lon_error**2 + alt_error**2)
                except Exception:
                    continue
                errs.append(err_mag)
                times.append(track_row['timestamp'])
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
    color_cycle = ['tab:blue','tab:orange','tab:green','tab:red','tab:purple','tab:brown','tab:pink','tab:gray','tab:olive','tab:cyan']
    markers = itertools.cycle(['o','s','^','D','v','>','<','P','X','*'])
    series_styles: Dict[str, Dict[str, Any]] = {}
    for idx, key in enumerate(series_dict.keys()):
        series_styles[key] = {
            'type': 'line',
            'color': color_cycle[idx % len(color_cycle)],
            'marker': next(markers),
            'linestyle': '-',
            'label': key,
        }

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

def track_existence_over_time(app_state, widgets: List[Any]) -> Dict[str, Any]:
    focus = app_state.get_focus_dataset_info()
    if not focus or focus.status.value != "loaded":
        return {"x": [], "y": [], "title": "Track Lifetimes"}
    tracks_df = getattr(focus, 'tracks_df', None)
    if tracks_df is None or tracks_df.empty:
        return {"x": [], "y": [], "title": "Track Lifetimes"}

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
    if selected_tracks is not None and len(selected_tracks) > 0:
        df = df[df['track_id'].isin(selected_tracks)]
    if df.empty:
        return {"x": [], "y": [], "title": "Track Lifetimes"}

    # Group by track and compute start/end
    import pandas as pd
    df = df.sort_values('timestamp')
    series_dict: Dict[str, List[float]] = {}
    starts = []
    ends = []
    labels = []  # original track_id labels (could be non-numeric)
    for idx, (track_id, grp) in enumerate(df.groupby('track_id')):
        ts = pd.to_datetime(grp['timestamp'])
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
