"""
Data Interface - Business Logic Interface

This module defines the abstract interface for data operations and provides
a mock implementation for development purposes.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from pathlib import Path
import pandas as pd
from datetime import datetime
import os

from ..models.application_state import DatasetInfo, DatasetStatus


class ValidationResults:
    """Results of dataset validation."""
    
    def __init__(self):
        self.is_valid = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.jobs_available: List[str] = []
    
    def add_error(self, message: str):
        """Add an error message."""
        self.errors.append(message)
        self.is_valid = False
    
    def add_warning(self, message: str):
        """Add a warning message."""
        self.warnings.append(message)
    
    def add_job(self, job_name: str):
        """Add an available job."""
        self.jobs_available.append(job_name)


class SummaryStats:
    """Summary statistics for a dataset."""
    
    def __init__(self):
        self.num_tracks = 0
        self.num_detections = 0  
        self.num_truth_measurements = 0
        self.duration_seconds = 0.0
        self.date_range: Optional[str] = None
        self.has_pkl_files = False


class ErrorMetrics:
    """Error metrics computed from tracks and truth."""
    
    def __init__(self):
        self.rms_position_error = 0.0
        self.mean_position_error = 0.0
        self.max_position_error = 0.0


class DataInterface(ABC):
    """
    Abstract interface for data operations.
    
    This defines the contract that the business logic must implement
    for dataset operations, validation, and analysis.
    """
    
    @abstractmethod
    def load_dataset(self, dataset_path: Path) -> Dict[str, pd.DataFrame]:
        """
        Load a dataset from the specified path.
        
        Args:
            dataset_path: Path to the dataset directory
            
        Returns:
            Dictionary with keys 'truth', 'detections', 'tracks' and DataFrame values
        """
        pass
    
    @abstractmethod  
    def validate_dataset(self, dataframes: Dict[str, pd.DataFrame]) -> ValidationResults:
        """
        Validate the dataset DataFrames.
        
        Args:
            dataframes: Dictionary of DataFrames to validate
            
        Returns:
            ValidationResults object with validation status and details
        """
        pass
    
    @abstractmethod
    def get_dataset_summary(self, dataframes: Dict[str, pd.DataFrame]) -> SummaryStats:
        """
        Get summary statistics for a dataset.
        
        Args:
            dataframes: Dictionary of DataFrames to analyze
            
        Returns:
            SummaryStats object with dataset statistics
        """
        pass
    
    @abstractmethod
    def compute_errors(self, tracks_df: pd.DataFrame, truth_df: pd.DataFrame) -> ErrorMetrics:
        """
        Compute error metrics between tracks and truth.
        
        Args:
            tracks_df: Tracks DataFrame
            truth_df: Truth DataFrame
            
        Returns:
            ErrorMetrics object with computed error statistics
        """
        pass


class MockDataInterface(DataInterface):
    """
    Mock implementation of the DataInterface for development.
    
    This provides placeholder functionality until the real business logic
    is integrated.
    """
    
    def __init__(self):
        """Initialize the mock data interface."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Mock data interface initialized")
    
    def load_dataset(self, dataset_path: Path) -> Dict[str, pd.DataFrame]:
        """
        Load a dataset from the specified path.
        
        This mock implementation loads CSV files from the expected subdirectories.
        """
        self.logger.info(f"Loading dataset from: {dataset_path}")
        
        dataframes = {}
        
        # Expected subdirectories and their data types
        subdirs = {
            'truth': 'truth',
            'detections': 'detections', 
            'tracks': 'tracks'
        }
        
        for subdir_name, data_type in subdirs.items():
            subdir_path = dataset_path / subdir_name
            
            if subdir_path.exists():
                # Find CSV files in the subdirectory
                csv_files = list(subdir_path.glob("*.csv"))
                
                if csv_files:
                    # Load the first CSV file found
                    csv_file = csv_files[0]
                    try:
                        df = pd.read_csv(csv_file)
                        dataframes[data_type] = df
                        self.logger.debug(f"Loaded {data_type}: {len(df)} records from {csv_file.name}")
                    except Exception as e:
                        self.logger.error(f"Error loading {csv_file}: {e}")
                        # Create empty DataFrame with expected columns
                        dataframes[data_type] = self._create_empty_dataframe(data_type)
                else:
                    self.logger.warning(f"No CSV files found in {subdir_path}")
                    dataframes[data_type] = self._create_empty_dataframe(data_type)
            else:
                self.logger.warning(f"Subdirectory not found: {subdir_path}")
                dataframes[data_type] = self._create_empty_dataframe(data_type)
        
        return dataframes
    
    def _create_empty_dataframe(self, data_type: str) -> pd.DataFrame:
        """Create an empty DataFrame with the expected columns for the data type."""
        if data_type == 'truth':
            return pd.DataFrame(columns=['timestamp', 'lat', 'lon', 'alt', 'id'])
        elif data_type == 'tracks':
            return pd.DataFrame(columns=['timestamp', 'lat', 'lon', 'alt', 'track_id'])
        elif data_type == 'detections':
            return pd.DataFrame(columns=['timestamp', 'lat', 'lon', 'alt', 'detection_id'])
        else:
            return pd.DataFrame()
    
    def validate_dataset(self, dataframes: Dict[str, pd.DataFrame]) -> ValidationResults:
        """
        Validate the dataset DataFrames.
        
        This mock implementation performs basic validation checks.
        """
        results = ValidationResults()
        
        # Check if all required data types are present
        required_types = ['truth', 'detections', 'tracks']
        
        for data_type in required_types:
            if data_type not in dataframes:
                results.add_error(f"Missing {data_type} data")
            elif dataframes[data_type].empty:
                results.add_warning(f"Empty {data_type} data")
            else:
                # Check column structure
                df = dataframes[data_type]
                expected_cols = self._get_expected_columns(data_type)
                
                if list(df.columns) != expected_cols:
                    results.add_error(f"Invalid columns in {data_type} data")
                else:
                    # Data is valid, add available jobs
                    results.add_job(f"Analyze {data_type}")
        
        # Add some mock analysis jobs if validation passes
        if results.is_valid:
            results.add_job("Track-Truth Association")
            results.add_job("Error Analysis")
            results.add_job("Statistical Summary")
            results.add_job("Geospatial Visualization")
        
        return results
    
    def _get_expected_columns(self, data_type: str) -> List[str]:
        """Get expected columns for each data type."""
        if data_type == 'truth':
            return ['timestamp', 'lat', 'lon', 'alt', 'id']
        elif data_type == 'tracks':
            return ['timestamp', 'lat', 'lon', 'alt', 'track_id']
        elif data_type == 'detections':
            return ['timestamp', 'lat', 'lon', 'alt', 'detection_id']
        else:
            return []
    
    def get_dataset_summary(self, dataframes: Dict[str, pd.DataFrame]) -> SummaryStats:
        """
        Get summary statistics for a dataset.
        """
        stats = SummaryStats()
        
        # Count records
        if 'tracks' in dataframes:
            stats.num_tracks = len(dataframes['tracks']['track_id'].unique()) if 'track_id' in dataframes['tracks'].columns else 0
        
        if 'detections' in dataframes:
            stats.num_detections = len(dataframes['detections'])
        
        if 'truth' in dataframes:
            stats.num_truth_measurements = len(dataframes['truth'])
        
        # Calculate duration from timestamp data
        all_timestamps = []
        for df in dataframes.values():
            if 'timestamp' in df.columns and not df.empty:
                # Convert to numeric if needed
                timestamps = pd.to_numeric(df['timestamp'], errors='coerce').dropna()
                all_timestamps.extend(timestamps.tolist())
        
        if all_timestamps:
            min_ts = min(all_timestamps)
            max_ts = max(all_timestamps)
            stats.duration_seconds = max_ts - min_ts
            
            # Mock date range
            try:
                start_time = datetime.fromtimestamp(min_ts)
                end_time = datetime.fromtimestamp(max_ts)
                stats.date_range = f"{start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')}"
            except (ValueError, OSError):
                # If timestamp conversion fails, use a mock date range
                stats.date_range = "2024-01-01 10:00 to 2024-01-01 10:10"
        
        return stats
    
    def compute_errors(self, tracks_df: pd.DataFrame, truth_df: pd.DataFrame) -> ErrorMetrics:
        """
        Compute error metrics between tracks and truth.
        
        This is a mock implementation that returns placeholder values.
        """
        metrics = ErrorMetrics()
        
        # Mock error calculations
        if not tracks_df.empty and not truth_df.empty:
            metrics.rms_position_error = 12.5  # meters
            metrics.mean_position_error = 8.3   # meters
            metrics.max_position_error = 45.2   # meters
        
        return metrics
