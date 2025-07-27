"""
Plot Manager

This module provides plot management functionality including plot selection,
data preparation, and coordination between the business logic and visualization components.
"""

import logging
from typing import Dict, List, Optional, Any
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
        
        # Available plot types for Phase 4 (only the first simple plot)
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
                         plot_config: Dict[str, Any] = None) -> Dict[str, Any]:
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
    
    def _prepare_lat_lon_data(self, app_state: ApplicationState, 
                             config: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for latitude/longitude scatter plot."""
        focus_dataset = app_state.get_focus_dataset_info()
        
        if not focus_dataset or focus_dataset.status.value != "loaded":
            return {'error': 'No loaded focus dataset available'}
        
        lat_lon_data = {}
        
        # Include tracks if requested (default True)
        if config.get('include_tracks', True) and focus_dataset.tracks_df is not None:
            tracks_df = focus_dataset.tracks_df
            if not tracks_df.empty and 'lat' in tracks_df.columns and 'lon' in tracks_df.columns:
                lat_lon_data['tracks'] = tracks_df[['lat', 'lon']].copy()
        
        # Include truth if requested (default True)  
        if config.get('include_truth', True) and focus_dataset.truth_df is not None:
            truth_df = focus_dataset.truth_df
            if not truth_df.empty and 'lat' in truth_df.columns and 'lon' in truth_df.columns:
                lat_lon_data['truth'] = truth_df[['lat', 'lon']].copy()
        
        return {
            'lat_lon_data': lat_lon_data,
            'title': f'Lat/Lon Plot - {focus_dataset.name}',
            'plot_type': 'scatter'
        }
    
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
    
    def get_plot_info(self, plot_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific plot type."""
        return self.available_plots.get(plot_id)
    
    def get_plot_list(self) -> List[str]:
        """Get list of all available plot IDs."""
        return list(self.available_plots.keys())
