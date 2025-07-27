# Data Analysis Application - Requirements Specification

## 1. Overview

### 1.1 Purpose
The application is a tkinter-based GUI for reviewing and analyzing datasets containing truth, detection, and tracking data. The tool provides multiple interactive views and visualizations to help users understand and analyze their data.

### 1.2 Scope
The application will handle multiple datasets organized in a structured directory format, and provide a UI to the application's business logic. The business logic will not be a part of this initial GUI. This application will allow datasets to be selected, and the business logic will load data into pandas DataFrames, validate against schemas, and provide analysis. The analysis will be visualized using this application.

For now, the inital dataset will be a stand-in for real datasets, just to get the application working. Later, when the application is integrated with the business logic, the stand in datasets will be dropped.

## 2. System Architecture

### 2.1 Technology Stack
- **Frontend**: Python tkinter
- **Data Processing**: Pandas, performed by business logic
- **Visualization**: matplotlib, plotly (for interactive plots)
- **Schema Validation**: python dictionary based schemas
- **File I/O**: Standard Python libraries

### 2.2 Application Structure
```
Main Application
├── GUI Framework (tkinter)
├── Data Management Layer
├── Visualization Engine
├── Schema Validation
└── File System Interface
```

### 2.3 Business Logic Interface
- **Data Loading Interface**: Abstract class defining methods for dataset operations
- **Schema Validation Interface**: Methods for validating loaded data
- **Analysis Interface**: Methods for computing statistics and derived data
- **Mock Implementation**: Placeholder implementation for development phase

# Example interface methods:
# - load_dataset(dataset_path) -> Dict[str, DataFrame]
# - validate_dataset(dataframes) -> ValidationResults
# - get_dataset_summary(dataframes) -> SummaryStats
# - compute_errors(tracks, truth) -> ErrorMetrics

## 3. Data Organization Requirements

### 3.1 Directory Structure
```
dataset_directory/
├── dataset_one_name/
│   ├── truth/
│   ├── detections/
│   └── tracks/
├── dataset_two_name/
│   ├── truth/
│   ├── detections/
│   └── tracks/
└── dataset_n_name/
    ├── truth/
    ├── detections/
    └── tracks/
```

### 3.2 File Types
- **Truth files**: Ground truth data
- **Detection files**: Detection/observation data
- **Track files**: Track/trajectory data

### 3.3 Data Loading Requirements
- Support for CSV files containing placeholder data
- Configurable dataset selection (none, some, or all)
- Dataset directory selection interface
- Automatic loading into pandas DataFrames (for now loading placeholder data)
- Schema validation post-loading (not necessary for the initial implementation)

## 4. User Interface Requirements

### 4.1 Main Window Layout
```
┌─────────────────────────────────────────────┐
│              Menu Bar                        │
├──────────────┬──────────────────────────────┤
│              │                              │
│              │                              │
│  Left Panel  │        Right Panel           │
│              │                              │
│              │                              │
├──────────────┴──────────────────────────────┤
│              Status Bar                      │
└─────────────────────────────────────────────┘
```

### 4.2 Left Panel Requirements
- **Dataset Overview Section**:
  - scrollable list of all available datasets
  - Basic info for each dataset (if its already loaded, its date, size, and whether or not .pkl files of processed data exists)
  - Indicators for presence of: truth/detections/tracks
  - A button to use .pkl files for already processed datasets if the .pkl file is available
  - A button to process all selected datasets.
  
- **Current Dataset Focus Section**:
  - Detailed information about selected dataset
  - Name, date, duration, # tracks, detections, and truth measurements
  - Jobs that can be done using this dataset (determined during validation).
  - As datasets are loaded, this section displays what dataset is currently being loaded, how long it will take, and how many are left
  - A field to set the association range
  - A drop down to select the method
  - A button to reprocess
  
- **Dataset Selection Controls**:
  - Dropdown for selecting current focus dataset
  - Checkboxes for enabling/disabling datasets in analysis
  - Refresh/reload controls

### 4.3 Right Panel Requirements
- **View Selection**: Tab-based selection for different analysis views. Some are unavailable depending on Jobs that can be done using this dataset (determined during validation).
- **Interactive Plot Area**: Main display area for visualizations
- **Control Panel**: Parameters and options for current view

### 4.4 Menu Bar Requirements
- **File Menu**: Open dataset directory, recent directories, exit
- **View Menu**: Toggle panels, zoom controls, reset layout
- **Tools Menu**: Export data, plot export, preferences
- **Help Menu**: About, user guide, keyboard shortcuts

## 5. Analysis Views and Visualizations

### 5.1 Statistical Views
- **5.1.1 Several sample Matplotlib interactive graphs, each with their own tabs**:
  - Used as a basis for other matplotlib interactive graphs 
  - Export functionality
  - Create different tabs for following:
  -- Number of tracks for all selected datasets
  --- Control Panel allows selection of all or some of datasets (default all)
  -- Latitude, longitude plots for tracks and truth for current focus dataset
  --- Control Panel allows selection of all or some of tracks, all or some of truths, allows max/min lat/lon to be selected
  -- North/East error for current for the focus dataset
  --- Control Panel allows selection of all or some of tracks
  -- 3D RMS error for current for the focus dataset
  --- Control Panel allows selection of all or some of tracks
  -- Track/truth lifetime for the focus dataset
  --- Control Panel allows selection of all/some/none of tracks (default all) and all/some/none of truth (default none)
  -- Latitude, longitude animation plots for tracks and truth for current focus dataset
  --- Control Panel allows selection of all or some of tracks, all or some of truths, allows max/min lat/lon to be selected
  --- Playback controls (play, pause, step, speed)

- **5.1.2 Several sample plotly interactive graphs, each with their own tabs**:
  - Used as a basis for other plotly interactive graphs 
  - Mouseover tooltips for all data
  - Export functionality
  - Create different tabs for following:
  -- Number of tracks for all selected datasets
  --- Control Panel allows selection of all or some of datasets (default all)
  -- Latitude, longitude plots for tracks and truth for current focus dataset
  --- Control Panel allows selection of all or some of tracks, all or some of truths, allows max/min lat/lon to be selected
  -- North/East error for current for the focus dataset
  --- Control Panel allows selection of all or some of tracks
  -- 3D RMS error for current for the focus dataset
  --- Control Panel allows selection of all or some of tracks
  -- Track/truth lifetime for the focus dataset
  --- Control Panel allows selection of all/some/none of tracks (default all) and all/some/none of truth (default none)
  -- Latitude, longitude animation plots for tracks and truth for current focus dataset
  --- Control Panel allows selection of all or some of tracks, all or some of truths, allows max/min lat/lon to be selected
  --- Playback controls (play, pause, step, speed)
  -- User defined plots:
  --- Field selection for X/Y axes
  --- Multiple plot types (scatter, line, bar, etc.)

## 6. Data Management Requirements

### 6.1 Data Loading
- **Directory Selection**: Browse and select dataset_directory
- **Dataset Discovery**: Automatically scan for valid datasets
- **Pickle file detection**: Automatically scan for presence of .pkl files indicating dataset has already been processed
- **Selective Loading**: User choice of which datasets to load
- **Progress Indication**: Loading progress for datasets
- **Error Handling**: Graceful handling of corrupt or invalid files

### 6.2 Schema Validation
- **Configurable Schemas**: Handled by business logic

### 6.3 Data Processing
- **Configurable Schemas**: Handled by business logic

## 7. User Interaction Requirements

### 7.1 Navigation
- **Responsive Interface**: Smooth interaction even with large datasets
- **Keyboard Shortcuts**: Common operations accessible via keyboard
- **Context Menus**: Right-click menus for common actions

### 7.2 Customization
- **Color Schemes**: Customizable color palettes
- **Layout Options**: Adjustable panel sizes
- **Export Options**: Save plots and data extracts

## 8. Performance Requirements

### 8.1 Data Handling
- **Memory Management**: Efficient memory usage for multiple datasets
- **Lazy Loading**: Load data on-demand where possible
- **Caching**: Cache processed results for performance

### 8.2 Visualization Performance
- **Responsive Plotting**: Smooth interaction with plots
- **Efficient Rendering**: Optimize rendering for large datasets
- **Progressive Loading**: Show partial results while processing

## 9. Technical Requirements

### 9.1 File Format Support
- **CSV files**: Standard comma-separated values
  - Expected columns for truth: [timestamp, lat, lon, alt, id]
  - Expected columns for tracks: [timestamp, lat, lon, alt, track_id]
  - Expected columns for detections: [timestamp, lat, lon, alt, detection_id]
- .pkl files

### 9.2 Dependencies
- Python 3.8+
- tkinter (standard library)
- pandas
- matplotlib
- numpy
- plotly (for advanced interactive plots)

## 10. Development Phases

### 10.1 Phase 1: Core Infrastructure
- Basic tkinter application window
- Menu bar and status bar
- Left/right panel layout with placeholder content
- Basic navigation between panels

### 10.2 Phase 2: Placeholder Data Generation
- Create two placeholder datasets
- Each contains placeholder tracks, truths, and detections in CSV format

### 10.3 Phase 3: Data Management
- Directory selection dialog
- Dataset discovery and listing
- Mock business logic interface implementation
- Left panel dataset overview implementation
- Dataset selection and focus controls

### 10.4 Phase 4: Basic Visualization using Matplotlib
- Extensible, modular software design practice for reusable components
- Matplotlib canvas integration
- NavigationToolbar2Tk setup
- First simple plot 
- Plot export functionality
- Tab-based view selection framework

### 10.5 Phase 5: Other Matplotlib plots
- As defined in section 5.1.1

### 10.6 Phase 6: Basic Visualization using plotly
- Extensible, modular software design practice for reusable components
- Matplotlib canvas integration
- NavigationToolbar2Tk setup
- First simple plot 
- Plot export functionality
- Tab-based view selection framework

### 10.7 Phase 7: Other plotly plots
- As defined in section 5.1.2

---
