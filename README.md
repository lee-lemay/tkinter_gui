# Data Analysis Application - Phase 1

A modular, extensible tkinter-based GUI application for analyzing datasets containing truth, detection, and tracking data.

## Phase 1: Core Infrastructure ✅

Phase 1 implements the foundational architecture and basic GUI structure following best practices for modularity, extensibility, and maintainability.

### Features Implemented

- **MVC Architecture**: Clean separation of Model, View, and Controller components
- **Modular Design**: Extensible component-based architecture
- **Professional GUI Layout**: Menu bar, status bar, left panel, right panel
- **State Management**: Centralized application state with observer pattern
- **Logging System**: Comprehensive logging with file and console output
- **Error Handling**: Robust error handling throughout the application
- **Responsive Design**: Proper grid layout with resizable panels

### Architecture Overview

```
Main Application
├── MVC Pattern
│   ├── Model: ApplicationState (src/models/)
│   ├── View: MainWindow + Components (src/gui/, src/components/)
│   └── Controller: ApplicationController (src/controllers/)
├── Utilities (src/utils/)
└── Main Entry Point (main.py)
```

### Directory Structure

```
tkinter_gui/
├── main.py                          # Application entry point
├── requirements.txt                  # Dependencies
├── test_phase1.py                   # Test script
├── requirements_specification.md    # Project requirements
└── src/
    ├── __init__.py
    ├── application.py               # Main application orchestrator
    ├── models/
    │   ├── __init__.py
    │   └── application_state.py     # Application state management
    ├── controllers/
    │   ├── __init__.py
    │   └── application_controller.py # MVC controller
    ├── gui/
    │   ├── __init__.py
    │   └── main_window.py           # Main window layout
    ├── components/
    │   ├── __init__.py
    │   ├── menu_bar.py              # Menu bar component
    │   ├── status_bar.py            # Status bar component
    │   ├── left_panel.py            # Dataset management panel
    │   └── right_panel.py           # Analysis views panel
    └── utils/
        ├── __init__.py
        └── logger.py                # Logging utilities
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- tkinter (usually included with Python)

### Installation
1. Clone or download the project
2. Navigate to the project directory
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application
```bash
python main.py
```

### Testing
Run the test script to verify the implementation:
```bash
python test_phase1.py
```

## Key Components

### 1. Application State (Model)
- **File**: `src/models/application_state.py`
- **Purpose**: Centralized state management
- **Features**:
  - Dataset collection management
  - UI state tracking
  - Observer pattern for state changes
  - Processing status and progress tracking

### 2. Main Window (View)
- **File**: `src/gui/main_window.py`
- **Purpose**: Main application window coordination
- **Features**:
  - Responsive grid layout
  - Panel visibility management
  - Component coordination
  - Dialog utilities

### 3. Application Controller
- **File**: `src/controllers/application_controller.py`
- **Purpose**: Coordinates Model-View interactions
- **Features**:
  - Menu action handling
  - State change propagation
  - Error handling
  - Business logic coordination

### 4. GUI Components

#### Menu Bar (`src/components/menu_bar.py`)
- File operations menu
- View controls menu
- Tools menu (placeholder)
- Help menu

#### Status Bar (`src/components/status_bar.py`)
- Processing status display
- Progress indication
- Dataset count display
- Current view indicator

#### Left Panel (`src/components/left_panel.py`)
- Dataset overview list
- Focus dataset information
- Selection controls
- Processing options (placeholders)

#### Right Panel (`src/components/right_panel.py`)
- Tabbed analysis views
- Overview tab with welcome message
- Placeholder tabs for future phases

## Design Principles

### 1. Modularity
- Each component is self-contained
- Clear interfaces between components
- Easy to extend and modify

### 2. Extensibility
- Observer pattern for loose coupling
- Abstract interfaces for future business logic
- Pluggable component architecture

### 3. Maintainability
- Comprehensive logging
- Clear error messages
- Consistent code structure
- Type hints and documentation

### 4. Best Practices
- MVC architectural pattern
- Separation of concerns
- DRY (Don't Repeat Yourself)
- SOLID principles

## Future Phases

### Phase 2: Data Management
- Dataset loading and validation
- File system integration
- Mock business logic implementation

### Phase 3: Basic Visualization
- Matplotlib integration
- NavigationToolbar2Tk setup
- First interactive plots

### Phase 4: Analysis Views
- Statistical analysis views
- Geospatial plotting
- Error analysis tools

### Phase 5: Advanced Features
- Animation capabilities
- Custom plot builder
- Export functionality

## Configuration

### Logging
- Logs are written to `logs/` directory
- Console and file output
- Configurable log levels
- Automatic log rotation

### UI Layout
- Resizable panels
- Persistent layout state
- Keyboard shortcuts
- Context menus (future)

## Dependencies

- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **matplotlib**: Plotting and visualization
- **tkinter**: GUI framework (standard library)

## Contributing

When extending the application:

1. Follow the established MVC pattern
2. Add appropriate logging
3. Include error handling
4. Update this README for new features
5. Add tests for new functionality

## License

This project is part of a data analysis application development effort.

---

**Phase 1 Status**: ✅ Complete
**Next Phase**: Data Management (Phase 2)
