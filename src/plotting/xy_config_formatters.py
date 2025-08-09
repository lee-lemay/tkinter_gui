"""
Formatter utilities for XYPlotTabWidget.

Each formatter must be a callable: (app_state, widgets) -> Dict[str, Any]
It returns a config dict with keys:
  - x: list of x values (required)
  - y: list or dict of y series (required). If dict, keys are series labels.
  - title/xlabel/ylabel/style: optional
"""
from __future__ import annotations
from typing import Any, Dict, List


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
    """Compute 3D RMS positional error vs time matching RMSErrorTabWidget functionality.

    Returns pass-through x (relative seconds) and y (single series dict) for generic_xy plotting.
    Honors track selection from TrackSelectionWidget or DataSelectionWidget (get_selected_tracks method).
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

    rms_errors = []
    times = []

    try:
        for _, track_row in tracks_df.iterrows():
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
            rms = np.sqrt(lat_error**2 + lon_error**2 + alt_error**2)
            rms_errors.append(rms)
            times.append(track_row['timestamp'])
    except Exception:
        return {'x': [], 'y': [], 'title': 'RMS 3D Error'}

    if not times:
        return {'x': [], 'y': [], 'title': 'RMS 3D Error'}

    ts = pd.to_datetime(times)
    start = ts.min()
    x_seconds = [(t - start).total_seconds() for t in ts]

    return {
        'x': x_seconds,
        'y': {'RMS 3D Error': rms_errors},
        'title': '3D RMS Error Over Time',
        'xlabel': 'Time (s)',
        'ylabel': 'RMS Error (m)',
        'style': 'line',
        'series_styles': {
            'RMS 3D Error': {'type': 'line', 'color': 'tab:green', 'marker': '^', 'linestyle': '-', 'label': 'RMS 3D Error'}
        }
    }
