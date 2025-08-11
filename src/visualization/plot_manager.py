"""
Plot Manager

This module provides plot management functionality including plot selection,
data preparation, and coordination between the business logic and visualization components.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from ..models.application_state import ApplicationState, DatasetInfo
from ..business.data_interface import DataInterface
from ..utils.schema_access import get_col


class PlotManager:
    """
    Manages plot creation and data preparation for visualization components.
    
    This class acts as a bridge between the business logic interface and 
    visualization components, providing a clean separation of concerns.
    """
    
    def __init__(self, data_interface: DataInterface):
        """
        Initialize the plot manager.
        
        Args:
            data_interface: The business logic interface for data operations
        """
        self.data_interface = data_interface
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("Plot manager initialized")
    
    def prepare_plot_data(self, plot_id: str, app_state: ApplicationState, 
                         plot_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Prepare data for a specific plot type.
        
        Args:
            plot_id: Identifier for the plot type
            app_state: Current application state
            plot_config: Optional plot configuration parameters
            
        Returns:
            Dictionary containing prepared plot data
        """
        try:
            if plot_config is None:
                plot_config = {}
            
            self.logger.debug(f"Preparing data for plot: {plot_id}")
            
            if plot_id == 'track_counts':
                return self._prepare_track_counts_data(app_state, plot_config)
            elif plot_id == 'lat_lon_scatter':
                return self._prepare_lat_lon_data(app_state, plot_config)
            elif plot_id == 'lat_lon_animation':
                return self._prepare_animation_data(app_state, plot_config)
            elif plot_id == 'generic_xy':
                return self._prepare_generic_xy_data(app_state, plot_config)
            elif plot_id == 'histogram':
                return self._prepare_histogram_data(app_state, plot_config)
            else:
                raise ValueError(f"Unknown plot type: {plot_id}")
        
        except Exception as e:
            self.logger.error(f"Error preparing plot data for {plot_id}: {e}")
            return {'error': str(e)}
    
    def _prepare_track_counts_data(self, app_state: ApplicationState, 
                                  config: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for track counts plot."""
        track_counts = {}
        
        # Get datasets to include (selected or all loaded)
        datasets_to_include = config.get('selected_datasets', [])
        if not datasets_to_include:
            datasets_to_include = [name for name, info in app_state.datasets.items() 
                                 if info.status.value == "loaded"]
        
        # Count tracks for each dataset
        for dataset_name in datasets_to_include:
            if dataset_name in app_state.datasets:
                dataset_info = app_state.datasets[dataset_name]
                if dataset_info.status.value == "loaded" and dataset_info.tracks_df is not None:
                    try:
                        schema = getattr(dataset_info, 'schema', None)
                        track_col = get_col(schema, 'tracks', 'track_id')
                        if track_col in dataset_info.tracks_df.columns:
                            count = len(dataset_info.tracks_df[track_col].unique())
                        else:
                            count = 0
                            self.logger.error(f"{track_col} not in dataset {dataset_info.name}.tracks_df.columns")
                    except Exception:
                            count = 0
                            self.logger.error(f"Error counting tracks in {dataset_info.name}")
                    track_counts[dataset_name] = count
                else:
                    track_counts[dataset_name] = 0
        
        return {
            'track_counts': track_counts,
            'title': 'Track Counts by Dataset',
            'plot_type': 'bar'
        }
    
    def _filter_tracks_and_truth_data(self, focus_dataset, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter tracks and truth data based on selection criteria.
        Returns filtered dataframes and coordinate bounds.
        """        
        
        all_lats = []
        all_lons = []

        geodetic_bounds: Optional[Tuple[float, float]] = None
        result: Dict[str, Any] = {
            'tracks_df': None,
            'truth_df': None,
            'lat_range': geodetic_bounds,
            'lon_range': geodetic_bounds
        }

        # Process tracks data for scatter plot
        tracks_selection = config.get('tracks', "All")
        if (tracks_selection != "None"  
            and focus_dataset.tracks_df is not None 
            and not focus_dataset.tracks_df.empty):
            
            tracks_df = focus_dataset.tracks_df.copy()
            
            # Filter tracks based on selection
            if "All" in tracks_selection:
                # Include all tracks
                filtered_tracks = tracks_df
            elif isinstance(tracks_selection, list) and len(tracks_selection) > 0:
                # Normalize selection types to match dataframe dtype (handles str/int mismatch)
                try:
                    schema = getattr(focus_dataset, 'schema', None)
                    track_col = get_col(schema, 'tracks', 'track_id')
                    col_dtype = tracks_df[track_col].dtype
                    if col_dtype.kind in 'iu' and any(isinstance(x, str) for x in tracks_selection):
                        norm_selection = []
                        for x in tracks_selection:
                            try:
                                norm_selection.append(int(x))
                            except Exception:
                                pass
                        tracks_selection = norm_selection if norm_selection else tracks_selection
                except Exception:
                    pass
                # Include specific track_ids
                schema = getattr(focus_dataset, 'schema', None)
                track_col = get_col(schema, 'tracks', 'track_id')
                filtered_tracks = tracks_df[tracks_df[track_col].isin(tracks_selection)]
            else:
                # Empty list or other values - include no tracks
                filtered_tracks = tracks_df.iloc[0:0]  # Empty DataFrame with same structure
            
            if not filtered_tracks.empty:
                schema = getattr(focus_dataset, 'schema', None)
                track_col = get_col(schema, 'tracks', 'track_id')
                ts_col    = get_col(schema, 'tracks', 'timestamp')
                lat_col   = get_col(schema, 'tracks', 'lat')
                lon_col   = get_col(schema, 'tracks', 'lon')
                needed = [track_col, ts_col, lat_col, lon_col]
                result['tracks_df'] = filtered_tracks[needed].copy()
                all_lats.extend(filtered_tracks[lat_col].dropna().tolist())
                all_lons.extend(filtered_tracks[lon_col].dropna().tolist())

        # Process truth data for scatter plot
        truth_selection = config.get('truth', "All")
        if (truth_selection != "None" and 
            focus_dataset.truth_df is not None and not focus_dataset.truth_df.empty):
            
            truth_df = focus_dataset.truth_df.copy()
            
            # Filter truth based on selection
            if "All" in truth_selection:
                # Include all truth
                filtered_truth = truth_df
            elif isinstance(truth_selection, list) and len(truth_selection) > 0:
                # Normalize selection types (str/int)
                try:
                    schema = getattr(focus_dataset, 'schema', None)
                    truth_id_col = get_col(schema, 'truth', 'truth_id')
                    col_dtype = truth_df[truth_id_col].dtype
                    if col_dtype.kind in 'iu' and any(isinstance(x, str) for x in truth_selection):
                        norm_truth = []
                        for x in truth_selection:
                            try:
                                norm_truth.append(int(x))
                            except Exception:
                                pass
                        truth_selection = norm_truth if norm_truth else truth_selection
                except Exception:
                    pass
                # Include specific truth ids
                schema = getattr(focus_dataset, 'schema', None)
                truth_id_col = get_col(schema, 'truth', 'truth_id')
                filtered_truth = truth_df[truth_df[truth_id_col].isin(truth_selection)]
            else:
                # Empty list or other values - include no truth
                filtered_truth = truth_df.iloc[0:0]  # Empty DataFrame with same structure
            
            if not filtered_truth.empty:
                schema = getattr(focus_dataset, 'schema', None)
                truth_id_col = get_col(schema, 'truth', 'truth_id')
                ts_col  = get_col(schema, 'truth', 'timestamp')
                lat_col = get_col(schema, 'truth', 'lat')
                lon_col = get_col(schema, 'truth', 'lon')
                needed = [truth_id_col, ts_col, lat_col, lon_col]
                result['truth_df'] = filtered_truth[needed].copy()
                all_lats.extend(filtered_truth[lat_col].dropna().tolist())
                all_lons.extend(filtered_truth[lon_col].dropna().tolist())

        if 'lat_range' in config and config['lat_range'] is not None:
            result['lat_range'] = config['lat_range']
        if 'lon_range' in config and config['lon_range'] is not None:
            result['lon_range'] = config['lon_range']
        if not result.get('lat_range') and not result.get('lon_range'):
            # Calculate coordinate ranges from actual data (similar to animation function)
            calculated_lat_range = None
            calculated_lon_range = None
            if len(all_lats) > 0 and len(all_lons) > 0:
                lat_min, lat_max = min(all_lats), max(all_lats)
                lon_min, lon_max = min(all_lons), max(all_lons)

                # Make the bounding box square (same as animation)
                lat_center = (lat_max + lat_min) / 2.0
                lon_center = (lon_max + lon_min) / 2.0
                
                # Calculate ranges and take the larger one
                lat_span = lat_max - lat_min if lat_max != lat_min else 0.02
                lon_span = lon_max - lon_min if lon_max != lon_min else 0.02
                
                # Add 5% padding to the larger span
                max_span = max(lat_span, lon_span)
                padded_span = max_span * 1.05  # 5% padding
                half_span = padded_span / 2.0
                
                # Create square ranges centered on the data
                calculated_lat_range = (lat_center - half_span, lat_center + half_span)
                calculated_lon_range = (lon_center - half_span, lon_center + half_span)
                result['lat_range'] = calculated_lat_range
                result['lon_range'] = calculated_lon_range
        
        return result
    
    def _prepare_lat_lon_data(self, app_state: ApplicationState, 
                             config: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for latitude/longitude scatter plot."""
        focus_dataset = app_state.get_focus_dataset_info()
        
        if not focus_dataset or focus_dataset.status.value != "loaded":
            return {'error': 'No loaded focus dataset available'}

        result = self._filter_tracks_and_truth_data(focus_dataset, config)

        # Pass coordinate ranges from config (user-set ranges take precedence)
        result['title'] = f'Lat/Lon Plot - {focus_dataset.name}'
        # Propagate plot mode directives (with defaults if not supplied)
        result['tracks_plot_mode'] = config.get('tracks_plot_mode', 'trajectory')
        result['truth_plot_mode'] = config.get('truth_plot_mode', 'scatter')

        return result
    
    def _prepare_animation_data(self, app_state: ApplicationState, 
                               config: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for animated lat/lon plot."""        
        focus_dataset = app_state.get_focus_dataset_info()

        if not focus_dataset or focus_dataset.status.value != "loaded":
            return {'error': 'No loaded focus dataset available'}
        
        result = self._filter_tracks_and_truth_data(focus_dataset, config)        
        result['time_range'] = {}
        # Propagate plot mode directives (with defaults if not supplied)
        result['tracks_plot_mode'] = config.get('tracks_plot_mode', 'trajectory')
        result['truth_plot_mode'] = config.get('truth_plot_mode', 'scatter')
        
        # Calculate time range for animation
        all_times = []
        ts_col    = get_col(focus_dataset.schema, 'tracks', 'timestamp')
        if result['tracks_df'] is not None and not result['tracks_df'].empty:
            all_times.extend(result['tracks_df'][ts_col].tolist())
        ts_col    = get_col(focus_dataset.schema, 'truth', 'timestamp')
        if result['truth_df'] is not None and not result['truth_df'].empty:
            all_times.extend(result['truth_df'][ts_col].tolist())
        
        if all_times:
            result['time_range'] = {
                'start': min(all_times),
                'end': max(all_times),
                'duration': (max(all_times) - min(all_times)).total_seconds()
            }
        
        return result

    def _prepare_generic_xy_data(self, app_state: ApplicationState, config: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for a generic, configurable XY plot.

        Config keys (examples):
          - x: column name for x values (schema mode) OR list-like of x values (pass-through mode)
          - y: list[str] column names (schema mode) OR list-like/dict of series -> list-like (pass-through mode)
          - source: 'tracks' | 'truth' | 'detections' (default 'tracks')
          - tracks: list of track_ids or 'All'/'None' (optional; only used if present)
          - truth: list of truth ids or 'All'/'None' (optional; only used if present)
          - xlabel/ylabel/title/style: passed through to backend
        Only filter/sort on ids if corresponding config keys are present.
        """
        focus = app_state.get_focus_dataset_info()
        if not focus or focus.status.value != "loaded":
            return {'error': 'No loaded focus dataset available'}

        # Helper to coerce sequences (including pandas/np series) to list
        def _to_list(obj):
            try:
                if obj is None:
                    return []
                if hasattr(obj, 'tolist'):
                    return obj.tolist()
                if isinstance(obj, (list, tuple)):
                    return list(obj)
                return list(obj)  # fallback iterator coercion
            except Exception:
                return []

        x_val = config.get('x')
        y_val = config.get('y')
        source = (config.get('source') or 'tracks').lower()

        # ---- Pass-through mode (x provided as concrete sequence) ----
        if x_val is not None and not isinstance(x_val, str):
            x_series = _to_list(x_val)
            if y_val is None:
                return {'error': 'y values are required'}

            series: Dict[str, Any] = {'x': x_series}
            if isinstance(y_val, dict):
                for name, arr in y_val.items():
                    y_list = _to_list(arr)
                    if len(y_list) != len(x_series):
                        return {'error': f'Length mismatch for series "{name}": x({len(x_series)}) vs y({len(y_list)})'}
                    series[name] = y_list
            else:
                y_list = _to_list(y_val)
                if len(y_list) != len(x_series):
                    return {'error': f'Length mismatch: x({len(x_series)}) vs y({len(y_list)})'}
                series['y'] = y_list

            out: Dict[str, Any] = {
                'series': series,
                'title': config.get('title', 'XY Plot'),
                'xlabel': config.get('xlabel', 'X'),
                'ylabel': config.get('ylabel', 'Y'),
                'style': config.get('style', 'line'),
            }
            # Pass through selected metadata keys
            meta_keys = ['series_styles', 'y_ticks', 'x_ticks', 'xlim', 'ylim', 'legend', 'grid']
            for k in meta_keys:
                if k in config:
                    out[k] = config[k]
            return out

        # ---- Schema mode (x/y reference dataframe columns) ----
        x_col = x_val
        y_cols = y_val or []
        if not x_col or not y_cols:
            return {'error': 'Both x and y must be provided'}

        # Select source DataFrame
        df = None
        id_col = None
        if source == 'truth':
            df = focus.truth_df
            id_col = get_col(focus.schema, 'truth', 'truth_id')
        elif source == 'detections':
            df = focus.detections_df
            id_col = get_col(focus.schema, 'tracks', 'track_id')
        else:
            df = focus.tracks_df
            id_col = get_col(focus.schema, 'tracks', 'track_id')

        if df is None or df.empty:
            return {'error': f'No data available in source: {source}'}

        filtered = df
        # Track filtering
        if 'tracks' in config and id_col == get_col(focus.schema, 'tracks', 'track_id') and id_col in filtered.columns:
            sel = config['tracks']
            if sel == "None":
                filtered = filtered.iloc[0:0]
            elif isinstance(sel, list) and len(sel) > 0 and "All" not in sel:
                filtered = filtered[filtered[id_col].isin(sel)]
        # Truth filtering
        if 'truth' in config and id_col == get_col(focus.schema, 'truth', 'truth_id') and id_col in filtered.columns:
            sel = config['truth']
            if sel == "None":
                filtered = filtered.iloc[0:0]
            elif isinstance(sel, list) and len(sel) > 0 and "All" not in sel:
                filtered = filtered[filtered[id_col].isin(sel)]

        if filtered.empty:
            return {'error': 'No rows after filtering'}

        required_cols = [x_col] + y_cols
        missing = [c for c in required_cols if c not in filtered.columns]
        if missing:
            return {'error': f'Missing columns in source: {missing}'}

        filtered = filtered.dropna(subset=required_cols)
        try:
            if filtered[x_col].dtype.kind == 'M':
                filtered = filtered.sort_values(by=x_col)
        except Exception:
            pass

        series: Dict[str, Any] = {'x': filtered[x_col].tolist()}
        for y in y_cols:
            series[y] = filtered[y].tolist()

        out = {
            'series': series,
            'title': config.get('title', 'XY Plot'),
            'xlabel': config.get('xlabel', 'X'),
            'ylabel': config.get('ylabel', 'Y'),
            'style': config.get('style', 'line'),
        }
        meta_keys = ['series_styles', 'y_ticks', 'x_ticks', 'xlim', 'ylim', 'legend', 'grid']
        for k in meta_keys:
            if k in config:
                out[k] = config[k]
        return out

    def _prepare_histogram_data(self, app_state: ApplicationState, config: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for histogram plotting (pass-through & light validation).

        Expectation per new schema: histogram formatters supply fully-populated
        statistics (mean/std) and explicit bin edges. Here we only:
          - Ensure required top-level keys exist
          - Filter out malformed histogram entries lacking required fields
          - Do NOT compute mean/std or edges (responsibility of formatter)
        """
        raw_hists = config.get('histograms', [])
        validated: List[Dict[str, Any]] = []
        for h in raw_hists:
            try:
                vals = h.get('values')
                edges = h.get('edges')
                if vals is None or edges is None:
                    continue  # skip invalid
                # Coerce to list (lightly)
                if not isinstance(vals, list):
                    if hasattr(vals, 'tolist'):
                        vals = vals.tolist()
                    else:
                        try:
                            vals = list(vals)
                        except Exception:
                            vals = []
                if not isinstance(edges, list):
                    if hasattr(edges, 'tolist'):
                        edges = edges.tolist()
                    else:
                        try:
                            edges = list(edges)
                        except Exception:
                            edges = []
                # Minimal structural checks
                if len(edges) < 2:
                    continue
                mean = h.get('mean')
                std = h.get('std')
                # Leave mean/std as-is (formatter responsibility); if absent, backend will display defaults
                validated.append({
                    'values': vals,
                    'edges': edges,
                    'mean': mean,
                    'std': std,
                    'style': h.get('style', {}),
                    'bands': h.get('bands'),
                })
            except Exception:
                continue
        return {
            'histograms': validated,
            'overlays': config.get('overlays', []),
            'title': config.get('title', 'Histogram'),
        }