"""Histogram config formatters & registry.

Provides formatter functions that prepare histogram configurations for the
PlotManager 'histogram' pipeline. These reuse generic selection helpers from
formatter_support and adopt the same registry pattern as xy_config_formatters.

Design:
- Reuse FormatterSupport for focus dataset & selection.
- Each formatter returns dict with: values (list[float]), mean, std, title, metric.
- Binning/styling left to backend; formatter constrains distribution window (mean ± 3*std).
"""
from __future__ import annotations
from typing import Any, Dict, Sequence, Callable, Optional, List
import math

from .formatter_support import FormatterSupport as FS

Formatter = Callable[[Any, Sequence[Any]], Dict[str, Any]]
FORMATTER_REGISTRY: Dict[str, Formatter] = {}

def register_hist_formatter(name: str) -> Callable[[Formatter], Formatter]:
    def _decorator(func: Formatter) -> Formatter:
        FORMATTER_REGISTRY[name] = func
        return func
    return _decorator

def get_hist_formatter(name: str) -> Optional[Formatter]:
    return FORMATTER_REGISTRY.get(name)

# Helper to extract track selection (reuse existing logic in FS.extract_selected_tracks)

def _collect_track_errors(app_state, widgets: Sequence[Any], component: str) -> List[float]:
    focus = FS.get_focus_or_empty(app_state)
    if not focus or focus.tracks_df is None or focus.truth_df is None:
        return []
    tracks_df = focus.tracks_df
    truth_df = focus.truth_df
    if tracks_df.empty or truth_df.empty:
        return []

    selected_tracks = FS.extract_selected_tracks(widgets)
    if selected_tracks is not None and len(selected_tracks) == 0:
        return []
    if selected_tracks:
        if 'track_id' in tracks_df.columns:
            tracks_df = tracks_df[tracks_df['track_id'].isin(selected_tracks)]
        if tracks_df.empty:
            return []

    import numpy as np

    errors: List[float] = []
    for _, row in tracks_df.iterrows():
        try:
            diffs = abs(truth_df['timestamp'] - row['timestamp'])
            idx = diffs.idxmin()
            truth_row = truth_df.loc[idx]
            if component == 'north':
                err = (row['lat'] - truth_row['lat']) * 111000.0
            else:  # east
                err = (row['lon'] - truth_row['lon']) * 111000.0 * math.cos(math.radians(truth_row['lat']))
            errors.append(float(err))
        except Exception:
            continue
    return errors

@register_hist_formatter('north_error_histogram')
def north_error_histogram(app_state, widgets: Sequence[Any]) -> Dict[str, Any]:
    """Build histogram config for north (latitudinal) error.

    Returns schema:
    {
      'histograms': [ {'values': [...], 'edges': [...], 'mean': m, 'std': s, 'style': {...}, 'bands': [...] } ],
      'overlays': [],
      'title': 'North Error Histogram'
    }
    Edges are 7 points (mean ± k*std for k=0..3) giving 6 bins.
    """
    vals = _collect_track_errors(app_state, widgets, 'north')
    import numpy as np
    if not vals:
        # Still return schema with empty histogram so downstream logic can handle gracefully
        return {
            'histograms': [
                {
                    'values': [], 'edges': [], 'mean': 0.0, 'std': 1.0,
                    'style': {'outline_only': True, 'sigma_bands': True, 'mean_line': True},
                }
            ],
            'overlays': [],
            'title': 'North Error Histogram'
        }
    arr = np.array(vals, dtype=float)
    mean = float(arr.mean())
    std = float(arr.std(ddof=0)) or 1.0
    # Detect histogram control widget (first instance found)
    hist_ctrl = None
    for w in widgets:
        if w.__class__.__name__ == 'HistogramControlWidget':  # avoid import cycle
            hist_ctrl = w
            break
    extent_sigma = 4.0
    bins_requested = 7
    gaussian_overlay = False
    scatter_var = None
    scatter_enabled = False
    if hist_ctrl:
        try:
            extent_sigma = max(1.0, min(8.0, hist_ctrl.get_sigma_extent()))
            bins_requested = hist_ctrl.get_bin_count()
            gaussian_overlay = hist_ctrl.gaussian_overlay_enabled()
            scatter_enabled = hist_ctrl.scatter_overlay_enabled()
            scatter_var = hist_ctrl.get_scatter_variable()
        except Exception:
            pass
    # Ensure odd bin count
    if bins_requested % 2 == 0:
        bins_requested += 1
    half_bins_each_side = (bins_requested - 1)//2
    # Build edges centered at mean across ±extent_sigma using equal-width bins
    import numpy as np
    left = mean - extent_sigma*std
    right = mean + extent_sigma*std
    edges = np.linspace(left, right, bins_requested+1).tolist()
    hist = {
        'values': arr.tolist(),
        'edges': edges,
        'mean': mean,
        'std': std,
        'style': {'outline_only': True, 'sigma_bands': True, 'mean_line': True, 'color': 'black', 'mean_label': 'Mean'},
    }
    overlays: List[Dict[str, Any]] = []
    if gaussian_overlay:
        try:
            xs = np.linspace(left, right, 200)
            # Normal PDF scaled to approximate counts (multiply by total samples * bin width)
            bin_width = (right-left)/bins_requested if bins_requested else 1
            pdf = (1.0/(std*np.sqrt(2*np.pi))) * np.exp(-0.5*((xs-mean)/std)**2)
            scaled = pdf * len(arr) * bin_width
            overlays.append({'x': xs.tolist(), 'y': scaled.tolist(), 'style': {'type':'line','color':'black','label':'Gaussian'}})
        except Exception:
            pass
    # Optional scatter overlay placeholder (secondary axis not yet in backend; include style hint)
    if scatter_enabled and scatter_var:
        overlays.append({'x': [mean], 'y': [0], 'style': {'type':'scatter','color':'red','label':f'{scatter_var} (scatter)','secondary_y': True}})
    return {
        'histograms': [hist],
        'overlays': overlays,
        'title': 'North Error Histogram'
    }

@register_hist_formatter('east_error_histogram')
def east_error_histogram(app_state, widgets: Sequence[Any]) -> Dict[str, Any]:
    """Build histogram config for east (longitudinal) error."""
    vals = _collect_track_errors(app_state, widgets, 'east')
    import numpy as np
    if not vals:
        return {
            'histograms': [
                {
                    'values': [], 'edges': [], 'mean': 0.0, 'std': 1.0,
                    'style': {'outline_only': True, 'sigma_bands': True, 'mean_line': True},
                }
            ],
            'overlays': [],
            'title': 'East Error Histogram'
        }
    arr = np.array(vals, dtype=float)
    mean = float(arr.mean())
    std = float(arr.std(ddof=0)) or 1.0
    # Shared control extraction logic
    hist_ctrl = None
    for w in widgets:
        if w.__class__.__name__ == 'HistogramControlWidget':
            hist_ctrl = w
            break
    extent_sigma = 4.0
    bins_requested = 7
    gaussian_overlay = False
    scatter_var = None
    scatter_enabled = False
    if hist_ctrl:
        try:
            extent_sigma = max(1.0, min(8.0, hist_ctrl.get_sigma_extent()))
            bins_requested = hist_ctrl.get_bin_count()
            gaussian_overlay = hist_ctrl.gaussian_overlay_enabled()
            scatter_enabled = hist_ctrl.scatter_overlay_enabled()
            scatter_var = hist_ctrl.get_scatter_variable()
        except Exception:
            pass
    if bins_requested % 2 == 0:
        bins_requested += 1
    import numpy as np
    left = mean - extent_sigma*std
    right = mean + extent_sigma*std
    edges = np.linspace(left, right, bins_requested+1).tolist()
    hist = {
        'values': arr.tolist(),
        'edges': edges,
        'mean': mean,
        'std': std,
        'style': {'outline_only': True, 'sigma_bands': True, 'mean_line': True, 'color': 'black', 'mean_label': 'Mean'},
    }
    overlays: List[Dict[str, Any]] = []
    if gaussian_overlay:
        try:
            xs = np.linspace(left, right, 200)
            bin_width = (right-left)/bins_requested if bins_requested else 1
            pdf = (1.0/(std*np.sqrt(2*np.pi))) * np.exp(-0.5*((xs-mean)/std)**2)
            scaled = pdf * len(arr) * bin_width
            overlays.append({'x': xs.tolist(), 'y': scaled.tolist(), 'style': {'type':'line','color':'black','label':'Gaussian'}})
        except Exception:
            pass
    if scatter_enabled and scatter_var:
        overlays.append({'x': [mean], 'y': [0], 'style': {'type':'scatter','color':'red','label':f'{scatter_var} (scatter)','secondary_y': True}})
    return {
        'histograms': [hist],
        'overlays': overlays,
        'title': 'East Error Histogram'
    }

__all__ = [
    'get_hist_formatter',
    'register_hist_formatter',
    'north_error_histogram',
    'east_error_histogram'
]
