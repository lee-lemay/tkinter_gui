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
from ..utils.schema_access import get_col

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
    """Return per-track errors using precomputed errors if available or compute ad-hoc.

    component: 'north' or 'east'
    """
    focus = FS.get_focus_or_empty(app_state)
    if not focus:
        return []

    # Prefer precomputed errors dataframe if capability present
    if 'precomputed_errors' in getattr(focus, 'capabilities', []):
        errors_df = getattr(focus, 'errors_df', None)
        if errors_df is not None and not errors_df.empty:
            schema = getattr(focus, 'schema', None)
            track_col = get_col(schema, 'errors', 'track_id')
            val_col = get_col(schema, 'errors', f'{component}_error')
            if val_col in errors_df.columns:
                selected_tracks = FS.extract_selected_tracks(widgets)
                df = errors_df
                if selected_tracks:
                    if track_col in df.columns:
                        df = df[df[track_col].isin(selected_tracks)]
                if track_col in df.columns and val_col in df.columns and not df.empty:
                    try:
                        return [float(v) for v in df[val_col].dropna().tolist()]
                    except Exception:
                        return []
        # Fall through to compute if no usable precomputed values

    # Fallback manual computation
    tracks_df = getattr(focus, 'tracks_df', None)
    truth_df  = getattr(focus, 'truth_df', None)
    if tracks_df is None or truth_df is None or tracks_df.empty or truth_df.empty:
        return []

    # Resolve columns via schema mapping
    schema = getattr(focus, 'schema', None)
    t_ts_col   = get_col(schema, 'tracks', 'timestamp')
    t_lat_col  = get_col(schema, 'tracks', 'lat')
    t_lon_col  = get_col(schema, 'tracks', 'lon')
    t_id_col   = get_col(schema, 'tracks', 'track_id')
    tr_ts_col  = get_col(schema, 'truth', 'timestamp')
    tr_lat_col = get_col(schema, 'truth', 'lat')
    tr_lon_col = get_col(schema, 'truth', 'lon')

    if any(c not in tracks_df.columns for c in [t_ts_col, t_lat_col, t_lon_col]) or any(c not in truth_df.columns for c in [tr_ts_col, tr_lat_col, tr_lon_col]):
        return []

    selected_tracks = FS.extract_selected_tracks(widgets)
    if selected_tracks is not None and len(selected_tracks) == 0:
        return []
    if selected_tracks and t_id_col in tracks_df.columns:
        tracks_df = tracks_df[tracks_df[t_id_col].isin(selected_tracks)]
        if tracks_df.empty:
            return []

    errors: List[float] = []
    try:
        for _, row in tracks_df.iterrows():
            try:
                diffs = (truth_df[tr_ts_col] - row[t_ts_col]).abs()
                idx = diffs.idxmin()
                truth_row = truth_df.loc[idx]
                if component == 'north':
                    err = (row[t_lat_col] - truth_row[tr_lat_col]) * 111000.0
                else:
                    err = (row[t_lon_col] - truth_row[tr_lon_col]) * 111000.0 * math.cos(math.radians(truth_row[tr_lat_col]))
                errors.append(float(err))
            except Exception:
                continue
    except Exception:
        return []
    return errors

def _build_error_histogram(app_state, widgets: Sequence[Any], component: str, title: str) -> Dict[str, Any]:
    """Generic builder for error histograms (north/east) including optional secondary scatter.

    If a HistogramControlWidget is present and a scatter variable selected, aggregates the
    scatter variable values per error bin and produces a secondary-axis scatter overlay.
    """
    # Base errors
    vals = _collect_track_errors(app_state, widgets, component)
    import numpy as np
    if not vals:
        return {
            'histograms': [
                {'values': [], 'edges': [], 'mean': 0.0, 'std': 1.0,
                 'style': {'outline_only': True, 'sigma_bands': True, 'mean_line': True}}
            ],
            'overlays': [],
            'title': title
        }
    arr = np.array(vals, dtype=float)
    mean = float(arr.mean())
    std = float(arr.std(ddof=0)) or 1.0

    # Control widget detection
    hist_ctrl = None
    for w in widgets:
        if w.__class__.__name__ == 'HistogramControlWidget':
            hist_ctrl = w
            break
    extent_sigma              = 4.0
    bins_requested            = 7
    gaussian_overlay          = False
    unit_gaussian_overlay     = False
    best_fit_gaussian_overlay = False
    scatter_var               = None
    scatter_enabled           = False
    y_mode                    = 'sigma'
    sigma_bands_enabled       = True
    if hist_ctrl:
        try:
            extent_sigma              = max(1.0, min(8.0, hist_ctrl.get_sigma_extent()))
            bins_requested            = hist_ctrl.get_bin_count()
            gaussian_overlay          = hist_ctrl.gaussian_overlay_enabled()
            unit_gaussian_overlay     = hist_ctrl.unit_gaussian_enabled()
            best_fit_gaussian_overlay = hist_ctrl.best_fit_gaussian_enabled()
            scatter_enabled           = hist_ctrl.scatter_overlay_enabled()
            scatter_var               = hist_ctrl.get_scatter_variable()
            y_mode                    = getattr(hist_ctrl, 'y_range_mode', lambda: 'sigma')()
            sigma_bands_enabled       = getattr(hist_ctrl, 'sigma_bands_enabled', lambda: True)()
        except Exception:
            pass
    if bins_requested < 1:
        bins_requested = 41
    if bins_requested % 2 == 0:  # ensure odd
        bins_requested += 1
    if y_mode == 'sigma':
        left  = mean - extent_sigma*std
        right = mean + extent_sigma*std
    else:
        # AutoFit: use min/max with 5% padding each side
        vmin = float(arr.min())
        vmax = float(arr.max())
        if vmin == vmax:
            vmin -= std
            vmax += std
        span = vmax - vmin
        pad = span * 0.05
        left = vmin - pad
        right = vmax + pad
    edges_arr = np.linspace(left, right, bins_requested + 1)
    edges     = edges_arr.tolist()

    hist = {
        'values': arr.tolist(),
        'edges': edges,
        'mean': mean,
        'std': std,
        'style': {'outline_only': True, 'sigma_bands': bool(sigma_bands_enabled), 'mean_line': True, 'color': 'black', 'mean_label': 'Mean'},
    }

    overlays: List[Dict[str, Any]] = []
    # Gaussian overlays
    if gaussian_overlay:
        try:
            xs = np.linspace(left, right, 200)
            bin_width = (right - left) / bins_requested if bins_requested else 1
            pdf = (1.0 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((xs - mean) / std) ** 2)
            scale_factor = len(arr) * bin_width
            scaled = pdf * scale_factor
            overlays.append({'x': xs.tolist(), 'y': scaled.tolist(), 'style': {'type': 'line', 'color': 'black', 'label': f'Unit Gaussian scaled by {scale_factor:.0f}'}})
        except Exception:
            pass
        
    if unit_gaussian_overlay:
        try:
            xs = np.linspace(left, right, 200)
            bin_width = (right - left) / bins_requested if bins_requested else 1
            pdf = (1.0 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((xs - mean) / std) ** 2)
            scaled = pdf
            overlays.append({'x': xs.tolist(), 'y': scaled.tolist(), 'style': {'type': 'line', 'color': 'black', 'label': 'Unit Gaussian'}})
        except Exception:
            pass
        
    if best_fit_gaussian_overlay:
        try:
            xs = np.linspace(left, right, 200)
            bin_width = (right - left) / bins_requested if bins_requested else 1
            pdf = (1.0 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((xs - mean) / std) ** 2)
            scaled = pdf
            overlays.append({'x': xs.tolist(), 'y': scaled.tolist(), 'style': {'type': 'line', 'color': 'black', 'label': 'Best Fit Gaussian'}})
        except Exception:
            pass
      

    # Secondary scatter overlay (bin-averaged scatter variable)
    if scatter_enabled and scatter_var:
        try:
            focus = FS.get_focus_or_empty(app_state)
            tracks_df = focus.tracks_df if focus else None
            truth_df = focus.truth_df if focus else None
            if tracks_df is not None and truth_df is not None and not tracks_df.empty and scatter_var in tracks_df.columns:
                # Re-run per-row loop to align scatter values with error values
                scatter_vals: List[float] = []
                error_vals: List[float] = []
                for _, row in tracks_df.iterrows():
                    try:
                        schema = focus.schema if focus else None
                        track_time_col = get_col(schema, 'tracks', 'timestamp')
                        truth_time_col = get_col(schema, 'truth', 'timestamp')
                        diffs = abs(truth_df[truth_time_col] - row[track_time_col])
                        idx = diffs.idxmin()
                        truth_row = truth_df.loc[idx]
                        if component == 'north':
                            err = (row['lat'] - truth_row['lat']) * 111000.0
                        else:
                            err = (row['lon'] - truth_row['lon']) * 111000.0 * math.cos(math.radians(truth_row['lat']))
                        sv = row[scatter_var]
                        if sv is not None and not (isinstance(sv, float) and math.isnan(sv)):
                            error_vals.append(float(err))
                            scatter_vals.append(float(sv))
                    except Exception:
                        continue
                if error_vals:
                    error_arr = np.array(error_vals, dtype=float)
                    scatter_arr = np.array(scatter_vals, dtype=float)
                    bin_indices = np.searchsorted(edges_arr, error_arr, side='right') - 1
                    nbins = len(edges_arr) - 1
                    bin_sums = np.zeros(nbins, dtype=float)
                    bin_counts = np.zeros(nbins, dtype=int)
                    for e_idx, sval in zip(bin_indices, scatter_arr):
                        if 0 <= e_idx < nbins:
                            bin_sums[e_idx] += sval
                            bin_counts[e_idx] += 1
                    with np.errstate(invalid='ignore'):
                        bin_means = np.divide(bin_sums, bin_counts, out=np.full_like(bin_sums, np.nan), where=bin_counts>0)
                    centers = (edges_arr[:-1] + edges_arr[1:]) / 2.0
                    overlays.append({
                        'x': centers.tolist(),
                        'y': bin_means.tolist(),
                        'style': {'type': 'scatter', 'color': 'red', 'label': f'{scatter_var} avg', 'marker': 'o', 'secondary_y': True, 'secondary_ylabel': scatter_var}
                    })
        except Exception:
            pass

    return {
        'histograms': [hist],
        'overlays': overlays,
        'title': title
    }


@register_hist_formatter('north_error_histogram')
def north_error_histogram(app_state, widgets: Sequence[Any]) -> Dict[str, Any]:
    return _build_error_histogram(app_state, widgets, 'north', 'North Error Histogram')

@register_hist_formatter('east_error_histogram')
def east_error_histogram(app_state, widgets: Sequence[Any]) -> Dict[str, Any]:
    return _build_error_histogram(app_state, widgets, 'east', 'East Error Histogram')

__all__ = [
    'get_hist_formatter',
    'register_hist_formatter',
    'north_error_histogram',
    'east_error_histogram'
]
