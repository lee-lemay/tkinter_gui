"""
Plotting module for the data analysis application.

This module provides the plotting infrastructure including backends, widgets,
and tab implementations for various types of data visualization.
"""

# Import core plotting components
from .backends import PlotBackend, MatplotlibBackend
from .widgets import PlotCanvasWidget, PlotTabWidget

# Import reusable control widgets
from .control_widgets import (
    DataSelectionWidget,
    CoordinateRangeWidget,
    TrackSelectionWidget,
    PlaybackControlWidget    
)

# Import all tab widget implementations
from .overview_tab import OverviewTabWidget
from .visualization_tab import VisualizationTabWidget
from .geospatial_tab import GeospatialTabWidget
from .error_analysis_tab import ErrorAnalysisTabWidget
from .rms_error_tab import RMSErrorTabWidget
from .lifetime_tab import LifetimeTabWidget
from .animation_tab import AnimationTabWidget
from .statistics_tab import StatisticsTabWidget

__all__ = [
    # Core plotting components
    'PlotBackend',
    'MatplotlibBackend', 
    'PlotCanvasWidget',
    'PlotTabWidget',
    'StatisticsTabWidget',
    
    # Control widgets
    'DataSelectionWidget',
    'CoordinateRangeWidget',
    'TrackSelectionWidget',
    'PlaybackControlWidget',
    
    # Tab widgets
    'OverviewTabWidget',
    'VisualizationTabWidget',
    'GeospatialTabWidget',
    'ErrorAnalysisTabWidget',
    'RMSErrorTabWidget',
    'LifetimeTabWidget',
    'AnimationTabWidget'
]
