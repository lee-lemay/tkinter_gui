#!/usr/bin/env python3
"""
Phase 2 Test Script

Tests the placeholder dataset generation functionality.
Verifies that generated datasets follow the requirements specification.
"""

import sys
import pandas as pd
from pathlib import Path
import logging

# Add the application directory to the Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

from src.data.dataset_generator import PlaceholderDatasetGenerator


def test_dataset_generation():
    """Test the dataset generation process."""
    print("Phase 2 Test: Placeholder Dataset Generation")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    try:
        # Create generator with test output directory
        test_output_dir = Path("test_data")
        generator = PlaceholderDatasetGenerator(test_output_dir)
        
        print("1. Generating placeholder datasets...")
        generator.generate_all_datasets()
        
        print("\n2. Validating generated datasets...")
        validation_results = validate_generated_datasets(test_output_dir)
        
        if validation_results:
            print("\n✅ All Phase 2 tests passed!")
            print("📋 Datasets are ready for Phase 3 integration")
            return True
        else:
            print("\n❌ Phase 2 tests failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False


def validate_generated_datasets(data_dir: Path) -> bool:
    """
    Validate that generated datasets meet requirements.
    
    Args:
        data_dir: Directory containing generated datasets
        
    Returns:
        True if all validations pass
    """
    print("   Checking dataset structure and content...")
    
    expected_datasets = ["sample_dataset_alpha", "sample_dataset_beta"]
    expected_subdirs = ["truth", "detections", "tracks"]
    expected_columns = {
        "truth": ["timestamp", "lat", "lon", "alt", "id"],
        "detections": ["timestamp", "lat", "lon", "alt", "detection_id"],
        "tracks": ["timestamp", "lat", "lon", "alt", "track_id"]
    }
    
    all_valid = True
    
    for dataset_name in expected_datasets:
        dataset_dir = data_dir / dataset_name
        
        if not dataset_dir.exists():
            print(f"   ❌ Missing dataset directory: {dataset_name}")
            all_valid = False
            continue
        
        print(f"   📁 Validating {dataset_name}...")
        
        for subdir_name in expected_subdirs:
            subdir_path = dataset_dir / subdir_name
            
            if not subdir_path.exists():
                print(f"      ❌ Missing subdirectory: {subdir_name}")
                all_valid = False
                continue
            
            # Find CSV files in subdirectory
            csv_files = list(subdir_path.glob("*.csv"))
            
            if not csv_files:
                print(f"      ❌ No CSV files in {subdir_name}/")
                all_valid = False
                continue
            
            # Validate first CSV file
            csv_file = csv_files[0]
            
            try:
                df = pd.read_csv(csv_file)
                
                # Check column schema
                expected_cols = expected_columns[subdir_name]
                if list(df.columns) != expected_cols:
                    print(f"      ❌ Wrong columns in {csv_file.name}")
                    print(f"         Expected: {expected_cols}")
                    print(f"         Found: {list(df.columns)}")
                    all_valid = False
                    continue
                
                # Check data content
                if len(df) == 0:
                    print(f"      ❌ Empty dataset: {csv_file.name}")
                    all_valid = False
                    continue
                
                # Check for 10 seconds of data (100 samples at 10 Hz)
                expected_samples = 100
                if len(df) != expected_samples:
                    print(f"      ⚠️  Unexpected sample count in {csv_file.name}: {len(df)} (expected {expected_samples})")
                
                # Check for reasonable coordinate values
                lat_range = df['lat'].max() - df['lat'].min()
                lon_range = df['lon'].max() - df['lon'].min()
                
                if lat_range > 1.0 or lon_range > 1.0:  # Shouldn't move more than 1 degree in 10 seconds
                    print(f"      ⚠️  Large coordinate range in {csv_file.name}")
                    print(f"         Lat range: {lat_range:.6f}, Lon range: {lon_range:.6f}")
                
                print(f"      ✅ {csv_file.name}: {len(df)} records, columns OK")
                
            except Exception as e:
                print(f"      ❌ Error reading {csv_file.name}: {e}")
                all_valid = False
    
    if all_valid:
        print("   ✅ All dataset validation checks passed")
    
    return all_valid


def display_sample_data(data_dir: Path):
    """Display sample data from generated datasets."""
    print("\n3. Sample data preview:")
    
    for dataset_name in ["sample_dataset_alpha", "sample_dataset_beta"]:
        dataset_dir = data_dir / dataset_name
        
        if not dataset_dir.exists():
            continue
        
        print(f"\n   📊 {dataset_name}:")
        
        for data_type in ["truth", "detections", "tracks"]:
            csv_files = list((dataset_dir / data_type).glob("*.csv"))
            
            if csv_files:
                df = pd.read_csv(csv_files[0])
                print(f"      {data_type}: {len(df)} records")
                
                if len(df) > 0:
                    # Show first few rows
                    print(f"         First record: lat={df.iloc[0]['lat']:.6f}, lon={df.iloc[0]['lon']:.6f}, alt={df.iloc[0]['alt']:.1f}")
                    print(f"         Last record:  lat={df.iloc[-1]['lat']:.6f}, lon={df.iloc[-1]['lon']:.6f}, alt={df.iloc[-1]['alt']:.1f}")


def main():
    """Main test function."""
    success = test_dataset_generation()
    
    if success:
        # Display sample data
        test_output_dir = Path("test_data")
        display_sample_data(test_output_dir)
        
        print("\n" + "="*60)
        print("Phase 2: Placeholder Dataset Generation - TEST RESULTS")
        print("="*60)
        print("✅ Dataset generation: PASSED")
        print("✅ Schema validation: PASSED") 
        print("✅ Data content validation: PASSED")
        print("📁 Test datasets created in: test_data/")
        print("\n🎯 Phase 2 is COMPLETE and ready for Phase 3!")
    
    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
