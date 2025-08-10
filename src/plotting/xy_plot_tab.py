"""Generic / Base XY Plot Tab

This module provides a minimal, extensible base class for all X-Y plotting tabs.

Design goals:
    - Provide a generic plotting pipeline (formatter -> plot_manager -> backend)
    - Eliminate baked-in UI controls (title / axis labels / style / refresh button)
    - Allow subclasses to contribute custom controls via hook methods
    - Keep optional dataset selection (tracks / truth) since it's broadly useful
    - Keep a simple update mechanism that subclasses can trigger (request_update)

Extension points for subclasses:
    - override get_config_formatter() to supply a callable (app_state, widgets) -> config dict
    - override get_formatter_widgets() to append widgets passed to the formatter
    - override build_custom_controls(parent_frame) to add UI elements; call request_update() when they change
    - override modify_config(config) to post-process the formatter output before plotting

Formatter output contract:
    Required: 'x' (sequence), 'y' (sequence or dict name->sequence)
    Optional: 'title', 'xlabel', 'ylabel', 'style' (line|scatter)
    Any additional keys are passed through untouched to PlotManager.
"""

import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, List, Optional, Callable
import logging

from .widgets import PlotTabWidget
from .backends import PlotBackend
from .control_widgets import DataSelectionWidget, TrackSelectionWidget


class XYPlotTabWidget(PlotTabWidget):
    """Base class for generic XY plotting tabs.

    Subclasses should typically only override hook methods rather than rewriting
    the plotting pipeline.
    """

    def __init__(
            self,
            parent: tk.Widget,
            backend: PlotBackend,
            include_data_selection: bool = False,
            include_track_selection: bool = False,
            formatter_name: Optional[str] = None,
            title: str = "XY Plot",
        ):
            # Flags controlling which selector widgets to include
            self.include_data_selection = include_data_selection
            self.include_track_selection = include_track_selection

            # Formatter plumbing
            self._formatter_name = formatter_name

            # Widget references (created later if flags enabled)
            self.data_selection_widget = None
            self.track_selection_widget = None

            super().__init__(parent, backend, title)

            # Initial plot attempt
            self._update_xy_plot()

    def _create_controls(self):
        # Only create selection widget + subclass custom controls.
        if self.include_data_selection:
            self.data_selection_widget = DataSelectionWidget(self.control_frame, collapsed=True)
            self.data_selection_widget.pack(fill="x", padx=5, pady=5)
            # Auto-update on selection changes
            self.data_selection_widget.set_tracks_callback(lambda _: self.request_update())
            self.data_selection_widget.set_truth_callback(lambda _: self.request_update())

        if self.include_track_selection:
            self.track_selection_widget = TrackSelectionWidget(self.control_frame, collapsed=True)
            self.track_selection_widget.pack(fill="x", padx=5, pady=5)
            self.track_selection_widget.set_selection_callback(lambda _sel: self.request_update())

        # Subclass hook for adding custom controls
        try:
            self.build_custom_controls(self.control_frame)
        except Exception as e:
            logging.getLogger(__name__).debug(f"No custom controls or error building them: {e}")

    def _propagate_controller_to_widgets(self):
        if self.controller and self.include_data_selection and self.data_selection_widget:
            self.data_selection_widget.set_controller(self.controller)
        if self.controller and self.include_track_selection and self.track_selection_widget:
            self.track_selection_widget.set_controller(self.controller)

    # ---- Extension hooks -------------------------------------------------
    def get_config_formatter(self) -> Optional[Callable[[Any, List[Any]], Dict[str, Any]]]:
        """Return a config formatter. Subclasses override to supply one when not passed explicitly."""
        return None

    def get_formatter_widgets(self) -> List[Any]:
        """Return extra widgets to pass to the formatter. Subclasses may override."""
        return []

    def build_custom_controls(self, parent: tk.Widget):  # pragma: no cover - default no-op
        """Hook for subclasses to add custom UI controls (call request_update() on changes)."""
        return None

    def modify_config(self, config: Dict[str, Any]) -> Dict[str, Any]:  # pragma: no cover - default no-op
        """Final hook allowing subclasses to tweak config before plotting."""
        return config

    # ---- Public helper ---------------------------------------------------
    def request_update(self):
        """Trigger a plot refresh (safe to call from UI callbacks)."""
        self._update_xy_plot()

    def _build_plot_config(self) -> Dict[str, Any]:
        """Build config via the provided formatter; supply defaults; allow subclass post-processing."""
        if not self.controller:
            return {'x': [], 'y': []}

        # The formatters are registered in the xy_config_formatters.py file
        # The formatter name is passed in to this class's constructor
        formatter = None
        if formatter is None and getattr(self, '_formatter_name', None):
            try:
                from .xy_config_formatters import get_formatter
                formatter = get_formatter(self._formatter_name)  # type: ignore[arg-type]
            except Exception:
                formatter = None
        if formatter is None:
            formatter = self.get_config_formatter()
        if not formatter:
            return {'x': [], 'y': []}

        # This instance's widgets are passed in to the formatter. 
        # Their values are queried to build the configuration.
        widgets: List[Any] = []
        if self.include_data_selection and self.data_selection_widget:
            widgets.append(self.data_selection_widget)
        if self.include_track_selection and self.track_selection_widget:
            widgets.append(self.track_selection_widget)
        widgets.extend(self.get_formatter_widgets())

        # The formatter also takes the current application state (which contains all the data)
        app_state = self.controller.get_state()
        try:
            built_cfg: Dict[str, Any] = formatter(app_state, widgets) or {}
        except Exception as e:
            logging.getLogger(__name__).error(f"Formatter error: {e}")
            built_cfg = {'x': [], 'y': []}

        # Provide default style while avoiding some static analysis confusion
        if 'style' not in built_cfg or not isinstance(built_cfg.get('style'), (str,)):
            built_cfg['style'] = 'line'

        built_cfg = self.modify_config(built_cfg)
        return built_cfg

    def _update_xy_plot(self):
        try:
            if not (self.plot_manager and self.controller):
                self.clear_plot()
                return

            app_state = self.controller.get_state()
            config = self._build_plot_config()
            plot_data = self.plot_manager.prepare_plot_data('generic_xy', app_state, config)

            if plot_data and 'error' not in plot_data:
                # Pass through labels and title to backend
                viz_cfg = {
                    'title': config.get('title', 'XY Plot'),
                    'xlabel': config.get('xlabel', 'X'),
                    'ylabel': config.get('ylabel', 'Y'),
                    'style': config.get('style', 'line'),
                    'series_styles': config.get('series_styles'),
                    'y_ticks': config.get('y_ticks'),
                }
                self.update_plot('generic_xy', plot_data, viz_cfg)
            else:
                self.clear_plot()
        except Exception as e:
            logging.getLogger(__name__).error(f"Error updating XY plot: {e}")
            self.clear_plot()

    def auto_update(self):
        self.on_focus_dataset_changed()
        self._update_xy_plot()

    def on_focus_dataset_changed(self):
        try:
            super().on_focus_dataset_changed()
        except Exception as e:
            logging.getLogger(__name__).error(f"Error handling focus change in XY tab: {e}")
