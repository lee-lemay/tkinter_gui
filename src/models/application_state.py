"""
Application State Model

This module contains the application state that represents the data model
for the entire application following the MVC pattern.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import pandas as pd
import json


class DatasetStatus(Enum):
    """Enumeration for dataset status."""
    UNKNOWN = "unknown"
    AVAILABLE = "available"
    LOADING = "loading"
    LOADED = "loaded"
    ERROR = "error"


@dataclass
class DatasetInfo:
    """Information about a single dataset."""
    name: str
    path: Path
    status: DatasetStatus = DatasetStatus.UNKNOWN
    has_truth: bool = False
    has_detections: bool = False
    has_tracks: bool = False
    has_pkl: bool = False
    size_bytes: int = 0
    last_modified: Optional[str] = None
    error_message: Optional[str] = None
    
    # Data frames (when loaded)
    truth_df: Optional[pd.DataFrame] = None
    detections_df: Optional[pd.DataFrame] = None
    tracks_df: Optional[pd.DataFrame] = None


class ApplicationState:
    """
    Central application state that manages all data and UI state.
    
    This class acts as the Model in the MVC pattern, containing all
    application data and providing methods to modify it safely.
    """
    
    def __init__(self):
        """Initialize the application state."""
        self.logger = logging.getLogger(__name__)
        
        # Dataset management
        self._dataset_directory: Optional[Path] = None
        self._datasets: Dict[str, DatasetInfo] = {}
        self._selected_datasets: List[str] = []
        self._focus_dataset: Optional[str] = None
        
        # UI state
        self._current_view: str = "overview"
        self._left_panel_visible: bool = True
        self._right_panel_visible: bool = True
        
        # Processing state
        self._processing_status: str = "idle"
        self._processing_progress: float = 0.0
        
        # Observers for state changes (for MVC communication)
        self._observers: List[Any] = []

        # Recent directories (limited to 5 most recent, persistent across sessions)
        self._recent_directories: List[str] = []
        self._max_recent_directories: int = 5
        
        # Application configuration (loaded at startup)
        # ForceUpdate: whether to re-scan/reload datasets forcefully
        # MetricMethod: error metric method name (e.g., 'Haversine')
        # DistanceThreshold: numeric threshold in meters
        self._force_update: bool = False
        self._metric_method: str = "Haversine"
        self._distance_threshold: float = 1000.0
        
        # Load recent directories from previous sessions
        self._load_recent_directories()
        
        
        self.logger.info("Application state initialized")

    def send_controller_changed_message(self):
        """
        Notify all observers that the controller has changed.
        
        This is used to trigger UI updates when the controller is set.
        """
        self.logger.debug("Sending controller changed message to observers")
        self._notify_observers("controller_changed")
    
    # Configuration Management
    @property
    def force_update(self) -> bool:
        return self._force_update

    @force_update.setter
    def force_update(self, value: bool):
        if value != self._force_update:
            self._force_update = bool(value)
            self.logger.debug(f"Config changed: force_update={self._force_update}")
            self._notify_observers("config_changed")

    @property
    def metric_method(self) -> str:
        return self._metric_method

    @metric_method.setter
    def metric_method(self, value: str):
        if value and value != self._metric_method:
            self._metric_method = str(value)
            self.logger.debug(f"Config changed: metric_method={self._metric_method}")
            self._notify_observers("config_changed")

    @property
    def distance_threshold(self) -> float:
        return self._distance_threshold

    @distance_threshold.setter
    def distance_threshold(self, value: float):
        try:
            v = float(value)
        except Exception:
            v = self._distance_threshold
        if v != self._distance_threshold:
            self._distance_threshold = v
            self.logger.debug(f"Config changed: distance_threshold={self._distance_threshold}")
            self._notify_observers("config_changed")
    
    # Dataset Directory Management
    @property
    def dataset_directory(self) -> Optional[Path]:
        """Get the current dataset directory."""
        return self._dataset_directory
    
    @dataset_directory.setter
    def dataset_directory(self, path: Optional[Path]):
        """Set the dataset directory and notify observers."""
        if path != self._dataset_directory:
            self._dataset_directory = path
            self.logger.info(f"Dataset directory set to: {path}")
            self._notify_observers("dataset_directory_changed")
    
    # Dataset Management
    @property
    def datasets(self) -> Dict[str, DatasetInfo]:
        """Get all datasets."""
        return self._datasets.copy()
    
    def add_dataset(self, dataset_info: DatasetInfo):
        """Add a dataset to the collection."""
        self._datasets[dataset_info.name] = dataset_info
        self.logger.debug(f"Added dataset: {dataset_info.name}")
        self._notify_observers("datasets_changed")
    
    def remove_dataset(self, dataset_name: str):
        """Remove a dataset from the collection."""
        if dataset_name in self._datasets:
            del self._datasets[dataset_name]
            
            # Clean up related state
            if dataset_name in self._selected_datasets:
                self._selected_datasets.remove(dataset_name)
            
            if self._focus_dataset == dataset_name:
                self._focus_dataset = None
            
            self.logger.debug(f"Removed dataset: {dataset_name}")
            self._notify_observers("datasets_changed")
    
    def clear_datasets(self):
        """Clear all datasets."""
        self._datasets.clear()
        self._selected_datasets.clear()
        self._focus_dataset = None
        self.logger.info("All datasets cleared")
        self._notify_observers("datasets_changed")
    
    # Dataset Selection Management
    @property
    def selected_datasets(self) -> List[str]:
        """Get list of selected dataset names."""
        return self._selected_datasets.copy()
    
    def add_selected_dataset(self, dataset_name: str):
        """Add a dataset to the selection."""
        if dataset_name in self._datasets and dataset_name not in self._selected_datasets:
            self._selected_datasets.append(dataset_name)
            self.logger.debug(f"Selected dataset: {dataset_name}")
            self._notify_observers("selection_changed")
    
    def remove_selected_dataset(self, dataset_name: str):
        """Remove a dataset from the selection."""
        if dataset_name in self._selected_datasets:
            self._selected_datasets.remove(dataset_name)
            self.logger.debug(f"Deselected dataset: {dataset_name}")
            self._notify_observers("selection_changed")
    
    def set_selected_datasets(self, dataset_names: List[str]):
        """Set the complete list of selected datasets."""
        # Validate that all names exist
        valid_names = [name for name in dataset_names if name in self._datasets]
        self._selected_datasets = valid_names
        self.logger.debug(f"Set selected datasets: {valid_names}")
        self._notify_observers("selection_changed")
    
    # Focus Dataset Management
    @property
    def focus_dataset(self) -> Optional[str]:
        """Get the currently focused dataset name."""
        return self._focus_dataset
    
    @focus_dataset.setter
    def focus_dataset(self, dataset_name: Optional[str]):
        """Set the focus dataset."""
        if dataset_name != self._focus_dataset:
            if dataset_name is None or dataset_name in self._datasets:
                self._focus_dataset = dataset_name
                self.logger.debug(f"Focus dataset set to: {dataset_name}")
                self._notify_observers("focus_changed")
            else:
                self.logger.warning(f"Cannot set focus to non-existent dataset: {dataset_name}")
    
    def get_focus_dataset_info(self) -> Optional[DatasetInfo]:
        """Get the DatasetInfo for the currently focused dataset."""
        if self._focus_dataset and self._focus_dataset in self._datasets:
            return self._datasets[self._focus_dataset]
        return None
    
    # UI State Management
    @property
    def current_view(self) -> str:
        """Get the current view name."""
        return self._current_view
    
    @current_view.setter
    def current_view(self, view_name: str):
        """Set the current view."""
        if view_name != self._current_view:
            self._current_view = view_name
            self.logger.debug(f"Current view set to: {view_name}")
            self._notify_observers("view_changed")
    
    @property
    def left_panel_visible(self) -> bool:
        """Get left panel visibility."""
        return self._left_panel_visible
    
    @left_panel_visible.setter
    def left_panel_visible(self, visible: bool):
        """Set left panel visibility."""
        if visible != self._left_panel_visible:
            self._left_panel_visible = visible
            self._notify_observers("panel_visibility_changed")
    
    @property
    def right_panel_visible(self) -> bool:
        """Get right panel visibility."""
        return self._right_panel_visible
    
    @right_panel_visible.setter
    def right_panel_visible(self, visible: bool):
        """Set right panel visibility."""
        if visible != self._right_panel_visible:
            self._right_panel_visible = visible
            self._notify_observers("panel_visibility_changed")
    
    # Processing Status Management
    @property
    def processing_status(self) -> str:
        """Get the current processing status."""
        return self._processing_status
    
    @processing_status.setter
    def processing_status(self, status: str):
        """Set the processing status."""
        if status != self._processing_status:
            self._processing_status = status
            self.logger.debug(f"Processing status: {status}")
            self._notify_observers("processing_status_changed")
    
    @property
    def processing_progress(self) -> float:
        """Get the current processing progress (0.0 to 1.0)."""
        return self._processing_progress
    
    @processing_progress.setter
    def processing_progress(self, progress: float):
        """Set the processing progress (0.0 to 1.0)."""
        progress = max(0.0, min(1.0, progress))  # Clamp to valid range
        if progress != self._processing_progress:
            self._processing_progress = progress
            self._notify_observers("processing_progress_changed")
    
    # Observer Pattern for MVC Communication
    def add_observer(self, observer: Any):
        """Add an observer to be notified of state changes."""
        if observer not in self._observers:
            self._observers.append(observer)
            self.logger.debug("Observer added")
    
    def remove_observer(self, observer: Any):
        """Remove an observer."""
        if observer in self._observers:
            self._observers.remove(observer)
            self.logger.debug("Observer removed")
    
    def _notify_observers(self, event: str):
        """Notify all observers of a state change."""
        for observer in self._observers:
            if hasattr(observer, 'on_state_changed'):
                try:
                    observer.on_state_changed(event)
                except Exception as e:
                    self.logger.error(f"Error notifying observer: {e}")
    
    # Utility Methods
    def get_statistics(self) -> Dict[str, Any]:
        """Get general statistics about the current state."""
        return {
            "total_datasets": len(self._datasets),
            "selected_datasets": len(self._selected_datasets),
            "loaded_datasets": len([d for d in self._datasets.values() 
                                  if d.status == DatasetStatus.LOADED]),
            "focus_dataset": self._focus_dataset,
            "current_view": self._current_view,
            "processing_status": self._processing_status
        }
        
    # Recent Directories Management
    @property
    def recent_directories(self) -> List[str]:
        """Get the list of recent directories."""
        return self._recent_directories.copy()
    
    def add_recent_directory(self, directory_path: str):
        """
        Add a directory to the recent directories list.
        
        Args:
            directory_path: Path to the directory to add
        """
        try:
            # Convert to absolute path string for consistency
            abs_path = str(Path(directory_path).resolve())
            
            # Remove if already exists (to move to front)
            if abs_path in self._recent_directories:
                self._recent_directories.remove(abs_path)
            
            # Add to front
            self._recent_directories.insert(0, abs_path)
            
            # Limit to max number
            if len(self._recent_directories) > self._max_recent_directories:
                self._recent_directories = self._recent_directories[:self._max_recent_directories]
            
            self.logger.debug(f"Added recent directory: {abs_path}")
            
            # Save to disk immediately
            self._save_recent_directories()
            
            # Notify observers
            self._notify_observers("recent_directories_changed")
            
        except Exception as e:
            self.logger.error(f"Error adding recent directory: {e}")
    
    def clear_recent_directories(self):
        """Clear all recent directories."""
        self._recent_directories.clear()
        self.logger.debug("Recent directories cleared")
        
        # Save to disk
        self._save_recent_directories()
        
        # Notify observers
        self._notify_observers("recent_directories_changed")
    
    def remove_recent_directory(self, directory_path: str):
        """
        Remove a specific directory from recent directories.
        
        Args:
            directory_path: Path to remove
        """
        try:
            abs_path = str(Path(directory_path).resolve())
            if abs_path in self._recent_directories:
                self._recent_directories.remove(abs_path)
                self.logger.debug(f"Removed recent directory: {abs_path}")
                
                # Save to disk
                self._save_recent_directories()
                
                # Notify observers
                self._notify_observers("recent_directories_changed")
        except Exception as e:
            self.logger.error(f"Error removing recent directory: {e}")
    
    def _get_config_directory(self) -> Path:
        """Get the application configuration directory."""
        config_dir = Path.home() / ".data_analysis_app"
        config_dir.mkdir(exist_ok=True)
        return config_dir
    
    def _save_recent_directories(self):
        """Save recent directories to a persistent file."""
        try:
            config_file = self._get_config_directory() / "recent_directories.json"
            
            # Only save directories that still exist
            existing_dirs = [d for d in self._recent_directories if Path(d).exists()]
            
            with open(config_file, 'w') as f:
                json.dump(existing_dirs, f, indent=2)
            
            # Update the in-memory list if some directories were removed
            if len(existing_dirs) != len(self._recent_directories):
                self._recent_directories = existing_dirs
            
            self.logger.debug(f"Recent directories saved to: {config_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving recent directories: {e}")
    
    def _load_recent_directories(self):
        """Load recent directories from persistent file."""
        try:
            config_file = self._get_config_directory() / "recent_directories.json"
            
            if config_file.exists():
                with open(config_file, 'r') as f:
                    loaded_dirs = json.load(f)
                
                # Validate that directories still exist
                self._recent_directories = [d for d in loaded_dirs if Path(d).exists()]
                
                self.logger.debug(f"Recent directories loaded: {len(self._recent_directories)} items")
                
                # If some directories were invalid, save the cleaned list
                if len(self._recent_directories) != len(loaded_dirs):
                    self._save_recent_directories()
            
                # Notify observers
                self._notify_observers("recent_directories_changed")
            else:
                self.logger.debug("No recent directories file found, starting with empty list")
                
        except Exception as e:
            self.logger.error(f"Error loading recent directories: {e}")
            self._recent_directories = []
