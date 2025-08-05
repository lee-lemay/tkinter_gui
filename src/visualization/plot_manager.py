"""
Plot Manager

This module provides plot management functionality including plot selection,
data preparation, and coordination between the business logic and visualization components.
"""

import logging
from logging import config
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from ..models.application_state import ApplicationState, DatasetInfo
from ..business.data_interface import DataInterface


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
        
        # Available plot types for Phase 5 (all matplotlib plots)
        self.available_plots = {
            'track_counts': {
                'name': 'Track Counts by Dataset',
                'description': 'Bar chart showing number of tracks per dataset',
                'requires_focus': False,
                'requires_multiple': True
            },
            'lat_lon_scatter': {
                'name': 'Latitude vs Longitude',
                'description': 'Scatter plot of track and truth positions',
                'requires_focus': True,
                'requires_multiple': False
            },
            'north_east_error': {
                'name': 'North/East Error',
                'description': 'North and East position errors for tracks',
                'requires_focus': True,
                'requires_multiple': False
            },
            'rms_error_3d': {
                'name': '3D RMS Error',
                'description': '3D visualization of RMS position errors',
                'requires_focus': True,
                'requires_multiple': False
            },
            'track_truth_lifetime': {
                'name': 'Track/Truth Lifetime',
                'description': 'Lifetime duration plots for tracks and truth',
                'requires_focus': True,
                'requires_multiple': False
            },
            'lat_lon_animation': {
                'name': 'Lat/Lon Animation',
                'description': 'Animated latitude/longitude plot with time progression',
                'requires_focus': True,
                'requires_multiple': False
            },
            'demo_plot': {
                'name': 'Demo Plot',
                'description': 'Sample mathematical functions demonstration',
                'requires_focus': False,
                'requires_multiple': False
            }
        }
        
        self.logger.info("Plot manager initialized")
    
    def get_available_plots(self, app_state: ApplicationState) -> List[Dict[str, Any]]:
        """
        Get list of available plots based on current application state.
        
        Args:
            app_state: Current application state
            
        Returns:
            List of dictionaries describing available plots
        """
        available = []
        
        has_datasets = len(app_state.datasets) > 0
        has_focus = app_state.focus_dataset is not None
        has_loaded_focus = (has_focus and 
                           app_state.focus_dataset in app_state.datasets and
                           app_state.datasets[app_state.focus_dataset].status.value == "loaded")
        
        for plot_id, plot_info in self.available_plots.items():
            # Check requirements
            can_create = True
            
            if plot_info['requires_multiple'] and not has_datasets:
                can_create = False
            
            if plot_info['requires_focus'] and not has_loaded_focus:
                can_create = False
            
            available.append({
                'id': plot_id,
                'name': plot_info['name'],
                'description': plot_info['description'],
                'enabled': can_create,
                'reason': self._get_disabled_reason(plot_info, has_datasets, has_focus, has_loaded_focus)
            })
        
        return available
    
    def _get_disabled_reason(self, plot_info: Dict[str, Any], has_datasets: bool, 
                            has_focus: bool, has_loaded_focus: bool) -> Optional[str]:
        """Get reason why a plot is disabled."""
        if plot_info['requires_multiple'] and not has_datasets:
            return "No datasets available"
        
        if plot_info['requires_focus'] and not has_focus:
            return "No focus dataset selected"
        
        if plot_info['requires_focus'] and has_focus and not has_loaded_focus:
            return "Focus dataset not loaded"
        
        return None
    
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
            elif plot_id == 'north_east_error':
                return self._prepare_north_east_error_data(app_state, plot_config)
            elif plot_id == 'rms_error_3d':
                return self._prepare_rms_error_3d_data(app_state, plot_config)
            elif plot_id == 'track_truth_lifetime':
                return self._prepare_lifetime_data(app_state, plot_config)
            elif plot_id == 'lat_lon_animation':
                return self._prepare_animation_data(app_state, plot_config)
            elif plot_id == 'demo_plot':
                return self._prepare_demo_data(app_state, plot_config)
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
                    if 'track_id' in dataset_info.tracks_df.columns:
                        count = len(dataset_info.tracks_df['track_id'].unique())
                    else:
                        count = len(dataset_info.tracks_df)
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
            if tracks_selection == "All":
                # Include all tracks
                filtered_tracks = tracks_df
            elif isinstance(tracks_selection, list) and len(tracks_selection) > 0:
                # Include specific track_ids
                filtered_tracks = tracks_df[tracks_df['track_id'].isin(tracks_selection)]
            else:
                # Empty list or other values - include no tracks
                filtered_tracks = tracks_df.iloc[0:0]  # Empty DataFrame with same structure
            
            if not filtered_tracks.empty and 'lat' in filtered_tracks.columns and 'lon' in filtered_tracks.columns:
                result['tracks_df'] = filtered_tracks[['track_id', 'timestamp', 'lat', 'lon']].copy()
                # Collect lat/lon for range calculation
                all_lats.extend(filtered_tracks['lat'].dropna().tolist())
                all_lons.extend(filtered_tracks['lon'].dropna().tolist())

        # Process truth data for scatter plot
        truth_selection = config.get('truth', "All")
        if (truth_selection != "None" and 
            focus_dataset.truth_df is not None and not focus_dataset.truth_df.empty):
            
            truth_df = focus_dataset.truth_df.copy()
            
            # Filter truth based on selection
            if truth_selection == "All":
                # Include all truth
                filtered_truth = truth_df
            elif isinstance(truth_selection, list) and len(truth_selection) > 0:
                # Include specific truth ids
                filtered_truth = truth_df[truth_df['id'].isin(truth_selection)]
            else:
                # Empty list or other values - include no truth
                filtered_truth = truth_df.iloc[0:0]  # Empty DataFrame with same structure
            
            if not filtered_truth.empty:
                result['truth_df'] = filtered_truth[['id', 'timestamp', 'lat', 'lon']].copy()
                # Collect lat/lon for range calculation
                all_lats.extend(filtered_truth['lat'].dropna().tolist())
                all_lons.extend(filtered_truth['lon'].dropna().tolist())

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
        
        return result
    
    def _prepare_animation_data(self, app_state: ApplicationState, 
                               config: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for animated lat/lon plot."""        
        focus_dataset = app_state.get_focus_dataset_info()

        if not focus_dataset or focus_dataset.status.value != "loaded":
            return {'error': 'No loaded focus dataset available'}
        
        result = self._filter_tracks_and_truth_data(focus_dataset, config)        
        result['time_range'] = {}
        
        # Calculate time range for animation
        all_times = []
        if result['tracks_df'] is not None and not result['tracks_df'].empty:
            all_times.extend(result['tracks_df']['timestamp'].tolist())
        if result['truth_df'] is not None and not result['truth_df'].empty:
            all_times.extend(result['truth_df']['timestamp'].tolist())
        
        if all_times:
            result['time_range'] = {
                'start': min(all_times),
                'end': max(all_times),
                'duration': (max(all_times) - min(all_times)).total_seconds()
            }
        
        return result
    
    def _prepare_demo_data(self, app_state: ApplicationState, 
                          config: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare demo plot data."""
        return {
            'demo_data': True,
            'title': 'Demo Plot - Mathematical Functions',
            'plot_type': 'line'
        }
    
    def validate_plot_requirements(self, plot_id: str, app_state: ApplicationState) -> Dict[str, Any]:
        """
        Validate that requirements are met for creating a specific plot.
        
        Args:
            plot_id: Plot type identifier
            app_state: Current application state
            
        Returns:
            Dictionary with validation results
        """
        if plot_id not in self.available_plots:
            return {
                'valid': False,
                'reason': f'Unknown plot type: {plot_id}'
            }
        
        plot_info = self.available_plots[plot_id]
        
        # Check dataset requirements
        if plot_info['requires_multiple']:
            loaded_datasets = [name for name, info in app_state.datasets.items() 
                             if info.status.value == "loaded"]
            if not loaded_datasets:
                return {
                    'valid': False,
                    'reason': 'No loaded datasets available for multi-dataset plot'
                }
        
        # Check focus requirements
        if plot_info['requires_focus']:
            focus_info = app_state.get_focus_dataset_info()
            if not focus_info:
                return {
                    'valid': False,
                    'reason': 'No focus dataset selected'
                }
            if focus_info.status.value != "loaded":
                return {
                    'valid': False,
                    'reason': 'Focus dataset is not loaded'
                }
        
        return {'valid': True}
    
    def _prepare_north_east_error_data(self, app_state: ApplicationState, 
                                      config: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for North/East error plot."""
        import numpy as np
        
        focus_dataset = app_state.get_focus_dataset_info()
        if not focus_dataset or focus_dataset.status.value != "loaded":
            return {'error': 'No loaded focus dataset available'}
        
        if (focus_dataset.tracks_df is None or focus_dataset.tracks_df.empty or
            focus_dataset.truth_df is None or focus_dataset.truth_df.empty):
            return {'error': 'Missing tracks or truth data for error calculation'}
        
        tracks_df = focus_dataset.tracks_df
        truth_df = focus_dataset.truth_df
        
        # Simple error calculation - match by timestamp (simplified)
        error_data = {'north_errors': [], 'east_errors': [], 'timestamps': []}
        
        for _, track_row in tracks_df.iterrows():
            # Find closest truth point by timestamp
            time_diffs = abs(truth_df['timestamp'] - track_row['timestamp'])
            closest_idx = time_diffs.idxmin()
            truth_row = truth_df.loc[closest_idx]
            
            # Calculate approximate North/East errors (simplified lat/lon diff)
            lat_error = (track_row['lat'] - truth_row['lat']) * 111000  # approx meters per degree
            lon_error = (track_row['lon'] - truth_row['lon']) * 111000 * np.cos(np.radians(truth_row['lat']))
            
            error_data['north_errors'].append(lat_error)
            error_data['east_errors'].append(lon_error)
            error_data['timestamps'].append(track_row['timestamp'])
        
        return {
            'error_data': error_data,
            'title': f'North/East Error - {focus_dataset.name}',
            'plot_type': 'error'
        }
    
    def _prepare_rms_error_3d_data(self, app_state: ApplicationState, 
                                  config: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for 3D RMS error plot."""
        import numpy as np
        
        focus_dataset = app_state.get_focus_dataset_info()
        if not focus_dataset or focus_dataset.status.value != "loaded":
            return {'error': 'No loaded focus dataset available'}
        
        if (focus_dataset.tracks_df is None or focus_dataset.tracks_df.empty or
            focus_dataset.truth_df is None or focus_dataset.truth_df.empty):
            return {'error': 'Missing tracks or truth data for error calculation'}
        
        tracks_df = focus_dataset.tracks_df
        truth_df = focus_dataset.truth_df
        
        # Calculate 3D RMS errors
        rms_data = {'x_pos': [], 'y_pos': [], 'rms_error_3d': [], 'timestamps': []}
        
        for _, track_row in tracks_df.iterrows():
            # Find closest truth point
            time_diffs = abs(truth_df['timestamp'] - track_row['timestamp'])
            closest_idx = time_diffs.idxmin()
            truth_row = truth_df.loc[closest_idx]
            
            # Calculate 3D position error
            lat_error = (track_row['lat'] - truth_row['lat']) * 111000
            lon_error = (track_row['lon'] - truth_row['lon']) * 111000 * np.cos(np.radians(truth_row['lat']))
            alt_error = track_row['alt'] - truth_row['alt']
            
            rms_error_3d = np.sqrt(lat_error**2 + lon_error**2 + alt_error**2)
            
            rms_data['x_pos'].append(track_row['lat'])
            rms_data['y_pos'].append(track_row['lon'])
            rms_data['rms_error_3d'].append(rms_error_3d)
            rms_data['timestamps'].append(track_row['timestamp'])
        
        return {
            'rms_data': rms_data,
            'title': f'3D RMS Error - {focus_dataset.name}',
            'plot_type': 'rms_3d'
        }
    
    def _prepare_lifetime_data(self, app_state: ApplicationState, 
                              config: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for track/truth lifetime plot."""
        focus_dataset = app_state.get_focus_dataset_info()
        if not focus_dataset or focus_dataset.status.value != "loaded":
            return {'error': 'No loaded focus dataset available'}
        
        lifetime_data = {'track_lifetimes': [], 'truth_lifetimes': []}
        
        # Calculate track lifetimes
        if (config.get('include_tracks', True) and 
            focus_dataset.tracks_df is not None and not focus_dataset.tracks_df.empty):
            tracks_df = focus_dataset.tracks_df
            
            for track_id in tracks_df['track_id'].unique():
                track_data = tracks_df[tracks_df['track_id'] == track_id]
                if len(track_data) > 1:
                    start_time = track_data['timestamp'].min()
                    end_time = track_data['timestamp'].max()
                    lifetime = (end_time - start_time).total_seconds()
                    lifetime_data['track_lifetimes'].append(lifetime)
        
        # Calculate truth lifetimes
        if (config.get('include_truth', False) and 
            focus_dataset.truth_df is not None and not focus_dataset.truth_df.empty):
            truth_df = focus_dataset.truth_df
            
            for truth_id in truth_df['id'].unique():
                truth_data = truth_df[truth_df['id'] == truth_id]
                if len(truth_data) > 1:
                    start_time = truth_data['timestamp'].min()
                    end_time = truth_data['timestamp'].max()
                    lifetime = (end_time - start_time).total_seconds()
                    lifetime_data['truth_lifetimes'].append(lifetime)
        
        return {
            'lifetime_data': lifetime_data,
            'title': f'Track/Truth Lifetime - {focus_dataset.name}',
            'plot_type': 'lifetime'
        }
    
    def get_plot_info(self, plot_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific plot type."""
        return self.available_plots.get(plot_id)
    
    def get_plot_list(self) -> List[str]:
        """Get list of all available plot IDs."""
        return list(self.available_plots.keys())
