"""
Dataset Scanner Utility

This module provides utilities for scanning directories and discovering
valid datasets according to the expected directory structure.
"""

import logging
from typing import List, Dict, Optional
from pathlib import Path
import os
from datetime import datetime

from ..models.application_state import DatasetInfo, DatasetStatus


class DatasetScanner:
    """
    Utility class for scanning directories and discovering datasets.
    
    This scanner looks for datasets following the expected structure:
    dataset_directory/
    ├── dataset_name/
    │   ├── truth/
    │   ├── detections/
    │   └── tracks/
    """
    
    def __init__(self):
        """Initialize the dataset scanner."""
        self.logger = logging.getLogger(__name__)
    
    def scan_directory(self, directory_path: Path) -> List[DatasetInfo]:
        """
        Scan a directory for valid datasets.
        
        Args:
            directory_path: Path to the directory containing datasets
            
        Returns:
            List of DatasetInfo objects for discovered datasets
        """
        self.logger.info(f"Scanning directory for datasets: {directory_path}")
        
        datasets = []
        
        if not directory_path.exists():
            self.logger.warning(f"Directory does not exist: {directory_path}")
            return datasets
        
        if not directory_path.is_dir():
            self.logger.warning(f"Path is not a directory: {directory_path}")
            return datasets
        
        # Scan each subdirectory
        for item in directory_path.iterdir():
            if item.is_dir():
                dataset_info = self._analyze_dataset_directory(item)
                if dataset_info:
                    datasets.append(dataset_info)
        
        self.logger.info(f"Found {len(datasets)} valid datasets")
        return datasets
    
    def _analyze_dataset_directory(self, dataset_path: Path) -> Optional[DatasetInfo]:
        """
        Analyze a potential dataset directory.
        
        Args:
            dataset_path: Path to the dataset directory
            
        Returns:
            DatasetInfo object if valid dataset, None otherwise
        """
        dataset_name = dataset_path.name
        self.logger.debug(f"Analyzing potential dataset: {dataset_name}")
        
        # Check for required subdirectories
        required_subdirs = ['truth', 'detections', 'tracks']
        subdirs_status = {}
        
        for subdir_name in required_subdirs:
            subdir_path = dataset_path / subdir_name
            has_csv_files = False
            
            if subdir_path.exists() and subdir_path.is_dir():
                # Check for CSV files in the subdirectory
                csv_files = list(subdir_path.glob("*.csv"))
                has_csv_files = len(csv_files) > 0
            
            subdirs_status[subdir_name] = has_csv_files
        
        # Only consider it a valid dataset if at least one subdirectory has CSV files
        if not any(subdirs_status.values()):
            self.logger.debug(f"No CSV files found in {dataset_name}, skipping")
            return None
        
        # Check for pickle files
        pkl_files = list(dataset_path.glob("*.pkl"))
        has_pkl = len(pkl_files) > 0
        
        # Get directory size and modification time
        size_bytes = self._get_directory_size(dataset_path)
        last_modified = self._get_last_modified_time(dataset_path)
        
        # Create DatasetInfo object
        dataset_info = DatasetInfo(
            name=dataset_name,
            path=dataset_path,
            status=DatasetStatus.AVAILABLE,
            has_truth=subdirs_status['truth'],
            has_detections=subdirs_status['detections'],
            has_tracks=subdirs_status['tracks'],
            has_pkl=has_pkl,
            size_bytes=size_bytes,
            last_modified=last_modified
        )
        
        self.logger.debug(f"Valid dataset found: {dataset_name}")
        return dataset_info
    
    def _get_directory_size(self, directory_path: Path) -> int:
        """
        Calculate the total size of a directory in bytes.
        
        Args:
            directory_path: Path to the directory
            
        Returns:
            Total size in bytes
        """
        total_size = 0
        
        try:
            for dirpath, dirnames, filenames in os.walk(directory_path):
                for filename in filenames:
                    file_path = Path(dirpath) / filename
                    try:
                        total_size += file_path.stat().st_size
                    except (OSError, FileNotFoundError):
                        # Skip files that can't be accessed
                        continue
        except Exception as e:
            self.logger.warning(f"Error calculating directory size for {directory_path}: {e}")
        
        return total_size
    
    def _get_last_modified_time(self, directory_path: Path) -> Optional[str]:
        """
        Get the last modified time of the directory.
        
        Args:
            directory_path: Path to the directory
            
        Returns:
            Formatted last modified time string
        """
        try:
            mtime = directory_path.stat().st_mtime
            modified_time = datetime.fromtimestamp(mtime)
            return modified_time.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            self.logger.warning(f"Error getting modification time for {directory_path}: {e}")
            return None
    
    def validate_dataset_structure(self, dataset_path: Path) -> Dict[str, bool]:
        """
        Validate the structure of a specific dataset.
        
        Args:
            dataset_path: Path to the dataset directory
            
        Returns:
            Dictionary with validation results for each component
        """
        validation_results = {
            'has_truth_dir': False,
            'has_detections_dir': False,
            'has_tracks_dir': False,
            'has_truth_csv': False,
            'has_detections_csv': False,
            'has_tracks_csv': False,
            'has_pkl_files': False
        }
        
        if not dataset_path.exists():
            return validation_results
        
        # Check subdirectories
        subdirs = ['truth', 'detections', 'tracks']
        for subdir in subdirs:
            subdir_path = dataset_path / subdir
            
            # Check if directory exists
            dir_key = f"has_{subdir}_dir"
            validation_results[dir_key] = subdir_path.exists() and subdir_path.is_dir()
            
            # Check if directory has CSV files
            csv_key = f"has_{subdir}_csv"
            if validation_results[dir_key]:
                csv_files = list(subdir_path.glob("*.csv"))
                validation_results[csv_key] = len(csv_files) > 0
        
        # Check for pickle files
        pkl_files = list(dataset_path.glob("*.pkl"))
        validation_results['has_pkl_files'] = len(pkl_files) > 0
        
        return validation_results
    
    def get_dataset_file_info(self, dataset_path: Path) -> Dict[str, List[str]]:
        """
        Get detailed file information for a dataset.
        
        Args:
            dataset_path: Path to the dataset directory
            
        Returns:
            Dictionary with file lists for each data type
        """
        file_info = {
            'truth_files': [],
            'detections_files': [],
            'tracks_files': [],
            'pkl_files': []
        }
        
        if not dataset_path.exists():
            return file_info
        
        # Get CSV files in each subdirectory
        subdirs = ['truth', 'detections', 'tracks']
        for subdir in subdirs:
            subdir_path = dataset_path / subdir
            if subdir_path.exists():
                csv_files = [f.name for f in subdir_path.glob("*.csv")]
                file_info[f"{subdir}_files"] = csv_files
        
        # Get pickle files
        pkl_files = [f.name for f in dataset_path.glob("*.pkl")]
        file_info['pkl_files'] = pkl_files
        
        return file_info
