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
from .geospatial_tab import GeospatialTabWidget
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
    'GeospatialTabWidget',
    'AnimationTabWidget'
]
