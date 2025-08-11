"""Histogram plot tab widget.

Analogous to XYPlotTabWidget but specialized for histogram render requests.
Formatter returns values + stats; PlotManager prepares; backend renders.
"""
from __future__ import annotations
import tkinter as tk
from typing import Any, Dict, List, Optional, Callable, Sequence
import logging

from .widgets import PlotTabWidget
from .backends import PlotBackend
from .control_widgets import DataSelectionWidget, TrackSelectionWidget, HistogramControlWidget
from .histogram_config_formatters import get_hist_formatter

class HistogramPlotTabWidget(PlotTabWidget):
    def __init__(
        self,
        parent: tk.Widget,
        backend: PlotBackend,
        include_data_selection: bool = False,
        include_track_selection: bool = True,
        config_formatter: Optional[Callable[[Any, Sequence[Any]], Dict[str, Any]]] = None,
        formatter_widgets: Optional[List[Any]] = None,
        formatter_name: Optional[str] = None,
        title: str = 'Histogram'
    ):
        self.include_data_selection = include_data_selection
        self.include_track_selection = include_track_selection
        self._explicit_formatter = config_formatter
        self._explicit_formatter_widgets = list(formatter_widgets) if formatter_widgets else []
        self._formatter_name = formatter_name
        self.data_selection_widget = None
        self.track_selection_widget = None
        self.hist_control_widget: Optional[HistogramControlWidget] = None
        super().__init__(parent, backend, title)
        self._update_histogram()

    def _create_controls(self):
        if self.include_data_selection:
            self.data_selection_widget = DataSelectionWidget(self.control_frame, collapsed=True)
            self.data_selection_widget.pack(fill='x', padx=5, pady=5)
            self.data_selection_widget.set_tracks_callback(lambda _: self.request_update())
            self.data_selection_widget.set_truth_callback(lambda _: self.request_update())
        # Create a horizontal row for track selection + histogram controls side by side
        row_frame = tk.Frame(self.control_frame)
        row_frame.pack(fill='x', padx=5, pady=5)
        if self.include_track_selection:
            self.track_selection_widget = TrackSelectionWidget(row_frame, collapsed=True)
            self.track_selection_widget.pack(side='left', fill='both', expand=True, padx=(0,5))
            self.track_selection_widget.set_selection_callback(lambda _: self.request_update())
        self.hist_control_widget = HistogramControlWidget(row_frame, collapsed=True, scatter_variables=['lat','lon','speed'])
        self.hist_control_widget.pack(side='left', fill='both', expand=True)
        self.hist_control_widget.set_change_callback(lambda: self.request_update())
        # Placeholder for custom controls hook
        try:
            self.build_custom_controls(self.control_frame)  # type: ignore[attr-defined]
        except Exception as e:
            logging.getLogger(__name__).debug(f'No custom histogram controls: {e}')

    def _propagate_controller_to_widgets(self):
        if self.controller and self.include_data_selection and self.data_selection_widget:
            self.data_selection_widget.set_controller(self.controller)
        if self.controller and self.include_track_selection and self.track_selection_widget:
            self.track_selection_widget.set_controller(self.controller)

    # Hooks similar to XY
    def get_config_formatter(self):
        return None

    def get_formatter_widgets(self) -> List[Any]:
        return []

    def request_update(self):
        self._update_histogram()

    def _build_hist_config(self) -> Dict[str, Any]:
        if not self.controller:
            return {'histograms': []}
        formatter = self._explicit_formatter
        if formatter is None and self._formatter_name:
            try:
                formatter = get_hist_formatter(self._formatter_name)  # type: ignore[assignment]
            except Exception:
                formatter = None
        if formatter is None:
            formatter = self.get_config_formatter()
        if not formatter:
            return {'histograms': []}
        widgets: List[Any] = []
        if self.include_data_selection and self.data_selection_widget:
            widgets.append(self.data_selection_widget)
        if self.include_track_selection and self.track_selection_widget:
            widgets.append(self.track_selection_widget)
        # Insert histogram control widget before explicit extras so formatters can find it early
        if self.hist_control_widget:
            widgets.append(self.hist_control_widget)
        widgets.extend(self._explicit_formatter_widgets)
        widgets.extend(self.get_formatter_widgets())
        app_state = self.controller.get_state()
        try:
            cfg = formatter(app_state, widgets) or {}
        except Exception as e:
            logging.getLogger(__name__).error(f'Histogram formatter error: {e}')
            cfg = {'histograms': []}
        # Upgrade legacy single-hist format (if any older formatter still returns it)
        if 'values' in cfg and 'histograms' not in cfg:
            # Wrap into new schema with placeholder edges if absent (will be rejected later if edges missing)
            single = cfg
            cfg = {'histograms': [single], 'title': single.get('title','Histogram')}
        return cfg

    def _update_histogram(self):
        try:
            if not (self.plot_manager and self.controller):
                self.clear_plot()
                return
            cfg = self._build_hist_config()
            app_state = self.controller.get_state()
            plot_data = self.plot_manager.prepare_plot_data('histogram', app_state, cfg)
            if plot_data and plot_data.get('histograms'):
                self.update_plot('histogram', plot_data, {'title': plot_data.get('title','Histogram')})
            else:
                self.clear_plot()
        except Exception as e:
            logging.getLogger(__name__).error(f'Error updating histogram: {e}')
            self.clear_plot()

    def auto_update(self):
        self.on_focus_dataset_changed()
        self._update_histogram()

    def on_focus_dataset_changed(self):  # override with safety
        try:
            super().on_focus_dataset_changed()
        except Exception:
            pass
