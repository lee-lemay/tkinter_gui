"""
Plotting package for abstract backend interfaces and widgets.
"""

from .backends import PlotBackend, MatplotlibBackend
from .widgets import PlotTabWidget, PlotCanvasWidget, StatisticsTabWidget

__all__ = ['PlotBackend', 'MatplotlibBackend', 'PlotTabWidget', 'PlotCanvasWidget', 'StatisticsTabWidget']
