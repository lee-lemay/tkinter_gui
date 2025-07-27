"""
Right Panel Component

This module contains the right panel component that displays
analysis views and visualizations using matplotlib integration.
Phase 4: Basic Visualization using Matplotlib
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Optional, Any, Dict, List

from ..visualization.matplotlib_canvas import MatplotlibCanvas
from ..visualization.plot_manager import PlotManager
from ..plotting.backends import MatplotlibBackend
from ..plotting.widgets import StatisticsTabWidget


class RightPanel:
    """
    Right panel component that provides analysis views and visualizations.
    
    Phase 4 implementation with matplotlib integration and extensible design.
    """
    
    def __init__(self, parent: tk.Widget):
        """
        Initialize the right panel.
        
        Args:
            parent: The parent widget
        """
        self.parent = parent
        self.logger = logging.getLogger(__name__)
        self.controller: Optional[Any] = None
        self.plot_manager: Optional[PlotManager] = None
        
        # Store matplotlib canvases for each tab
        self.canvas_widgets: Dict[str, MatplotlibCanvas] = {}
        
        # Create the main frame
        self.frame = ttk.Frame(parent)
        
        # Create panel content
        self._create_content()
        
        self.logger.debug("Right panel initialized with matplotlib integration")
    
    def set_controller(self, controller: Any):
        """
        Set the controller for this component.
        
        Args:
            controller: The application controller
        """
        self.controller = controller
        
        # Initialize plot manager with business logic interface
        if hasattr(controller, 'data_interface'):
            self.plot_manager = PlotManager(controller.data_interface)
        
        # Pass controller and plot manager to modular widgets
        if hasattr(self, 'statistics_tab'):
            self.statistics_tab.set_controller(controller)
            if hasattr(self, 'plot_manager'):
                self.statistics_tab.set_plot_manager(self.plot_manager)
        
        self.logger.debug("Controller set for right panel")
    
    def _create_content(self):
        """Create the right panel content."""
        # Title
        title_label = ttk.Label(
            self.frame,
            text="Visualization & Analysis",
            font=("TkDefaultFont", 10, "bold")
        )
        title_label.pack(fill="x", padx=10, pady=(10, 5))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Bind tab selection events
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        
        # Create tabs with matplotlib integration
        self._create_tabs()
        
        # Create demo plot for overview tab
        self._create_demo_plot()
    
    def _create_tabs(self):
        """Create the analysis view tabs with matplotlib integration for Phase 5."""
        # Overview Tab (with basic plot)
        self._create_overview_tab()
        
        # Visualization Tab (main plotting area)
        self._create_visualization_tab()
        
        # Statistics Tab (with statistical plots) 
        self._create_statistics_tab()
        
        # Geospatial Tab (for lat/lon plots)
        self._create_geospatial_tab()
        
        # Phase 5 tabs - New matplotlib plots
        self._create_error_analysis_tab()
        self._create_rms_error_tab()
        self._create_lifetime_tab()
        self._create_animation_tab()
    
    def _create_overview_tab(self):
        """Create the overview tab with demo plot."""
        overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(overview_frame, text="Overview")
        
        # Create header frame
        header_frame = ttk.Frame(overview_frame)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        # Welcome message
        welcome_label = ttk.Label(
            header_frame,
            text="Data Analysis Application - Phase 5",
            font=("TkDefaultFont", 12, "bold")
        )
        welcome_label.pack(anchor="w")
        
        # Feature description
        feature_label = ttk.Label(
            header_frame,
            text="Extended matplotlib visualization capabilities - All Phase 5 plots enabled",
            font=("TkDefaultFont", 10, "italic")
        )
        feature_label.pack(anchor="w", pady=(5, 0))
        
        # Create matplotlib canvas for demo plot
        canvas_frame = ttk.Frame(overview_frame)
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.canvas_widgets['overview'] = MatplotlibCanvas(canvas_frame)
        self.canvas_widgets['overview'].frame.pack(fill="both", expand=True)
        
        # Instructions frame
        instructions_frame = ttk.Frame(overview_frame)
        instructions_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        instructions_label = ttk.Label(
            instructions_frame,
            text="Load datasets using the File menu to enable additional visualization options.",
            font=("TkDefaultFont", 9, "italic")
        )
        instructions_label.pack(anchor="w")
    
    def _create_visualization_tab(self):
        """Create the main visualization tab with track counts and dataset selection."""
        viz_frame = ttk.Frame(self.notebook)
        self.notebook.add(viz_frame, text="Visualization")
        
        # Create control panel with horizontal layout
        control_frame = ttk.LabelFrame(viz_frame, text="Track Counts Plot Controls")
        control_frame.pack(fill="x", padx=10, pady=10)
        
        # Main horizontal container
        controls_container = ttk.Frame(control_frame)
        controls_container.pack(fill="x", padx=5, pady=5)
        
        # Dataset selection frame (left section)
        dataset_frame = ttk.LabelFrame(controls_container, text="Dataset Selection (default: all)")
        dataset_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        # Dataset selection variables and controls
        self.dataset_selection_vars = {}
        self.dataset_selection_frame = ttk.Frame(dataset_frame)
        self.dataset_selection_frame.pack(fill="x", padx=5, pady=5)
        
        # Dataset selection buttons
        buttons_frame = ttk.Frame(dataset_frame)
        buttons_frame.pack(fill="x", padx=5, pady=2)
        
        ttk.Button(buttons_frame, text="Select All", 
                  command=self._select_all_datasets).pack(side="left", padx=2)
        ttk.Button(buttons_frame, text="Select None", 
                  command=self._select_no_datasets).pack(side="left", padx=2)
        
        # Actions frame (right section)
        actions_frame = ttk.LabelFrame(controls_container, text="Actions")
        actions_frame.pack(side="left", fill="y", padx=5)
        
        # Refresh datasets button
        self.refresh_datasets_btn = ttk.Button(
            actions_frame,
            text="Refresh Datasets",
            command=self._refresh_dataset_selection
        )
        self.refresh_datasets_btn.pack(padx=5, pady=5)
        
        # Create matplotlib canvas
        canvas_frame = ttk.Frame(viz_frame)
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.canvas_widgets['visualization'] = MatplotlibCanvas(canvas_frame)
        self.canvas_widgets['visualization'].frame.pack(fill="both", expand=True)
        
        # Initialize dataset selection
        self._refresh_dataset_selection()
    
    def _create_statistics_tab(self):
        """Create the statistics tab using modular widget architecture."""
        # Create backend for this tab
        stats_backend = MatplotlibBackend()
        
        # Create the statistics tab widget
        self.statistics_tab = StatisticsTabWidget(self.notebook, stats_backend)
        self.notebook.add(self.statistics_tab, text="Statistics")
        
        # Set dependencies
        if hasattr(self, 'controller'):
            self.statistics_tab.set_controller(self.controller)
        if hasattr(self, 'plot_manager'):
            self.statistics_tab.set_plot_manager(self.plot_manager)
        
        # Store reference in a separate dict for the new modular widgets
        if not hasattr(self, 'tab_widgets'):
            self.tab_widgets = {}
        self.tab_widgets['statistics'] = self.statistics_tab
    
    def _create_geospatial_tab(self):
        """Create the geospatial analysis tab with enhanced controls."""
        geo_frame = ttk.Frame(self.notebook)
        self.notebook.add(geo_frame, text="Geospatial")
        
        # Control panel with horizontal layout
        control_frame = ttk.LabelFrame(geo_frame, text="Geospatial Plot Controls")
        control_frame.pack(fill="x", padx=10, pady=10)
        
        # Main horizontal container for all control sections
        controls_container = ttk.Frame(control_frame)
        controls_container.pack(fill="x", padx=5, pady=5)
        
        # Data selection frame (left section)
        data_frame = ttk.LabelFrame(controls_container, text="Data Selection")
        data_frame.pack(side="left", fill="y", padx=5)
        
        # Track selection
        tracks_frame = ttk.Frame(data_frame)
        tracks_frame.pack(fill="x", padx=5, pady=2)
        
        ttk.Label(tracks_frame, text="Tracks:").pack(side="left")
        self.geo_tracks_var = tk.StringVar(value="all")
        self.geo_tracks_combo = ttk.Combobox(tracks_frame, textvariable=self.geo_tracks_var,
                                           values=["all", "some", "none"], state="readonly", width=10)
        self.geo_tracks_combo.pack(side="left", padx=5)
        
        # Truth selection
        truth_frame = ttk.Frame(data_frame)
        truth_frame.pack(fill="x", padx=5, pady=2)
        
        ttk.Label(truth_frame, text="Truth:").pack(side="left")
        self.geo_truth_var = tk.StringVar(value="all")
        self.geo_truth_combo = ttk.Combobox(truth_frame, textvariable=self.geo_truth_var,
                                          values=["all", "some", "none"], state="readonly", width=10)
        self.geo_truth_combo.pack(side="left", padx=5)
        
        # Coordinate range frame (center section)
        range_frame = ttk.LabelFrame(controls_container, text="Coordinate Range")
        range_frame.pack(side="left", fill="y", padx=5)
        
        # Latitude range
        lat_frame = ttk.Frame(range_frame)
        lat_frame.pack(fill="x", padx=5, pady=2)
        
        ttk.Label(lat_frame, text="Latitude:").pack(side="left")
        ttk.Label(lat_frame, text="Min:").pack(side="left", padx=(10, 2))
        self.geo_lat_min_var = tk.DoubleVar(value=-1.0)  # Will be updated based on data
        self.geo_lat_min_spin = ttk.Spinbox(lat_frame, from_=-90.0, to=90.0, increment=0.01,
                                          textvariable=self.geo_lat_min_var, width=8, format="%.4f")
        self.geo_lat_min_spin.pack(side="left", padx=2)
        
        ttk.Label(lat_frame, text="Max:").pack(side="left", padx=(10, 2))
        self.geo_lat_max_var = tk.DoubleVar(value=1.0)  # Will be updated based on data
        self.geo_lat_max_spin = ttk.Spinbox(lat_frame, from_=-90.0, to=90.0, increment=0.01,
                                          textvariable=self.geo_lat_max_var, width=8, format="%.4f")
        self.geo_lat_max_spin.pack(side="left", padx=2)
        
        # Longitude range
        lon_frame = ttk.Frame(range_frame)
        lon_frame.pack(fill="x", padx=5, pady=2)
        
        ttk.Label(lon_frame, text="Longitude:").pack(side="left")
        ttk.Label(lon_frame, text="Min:").pack(side="left", padx=(10, 2))
        self.geo_lon_min_var = tk.DoubleVar(value=-1.0)  # Will be updated based on data
        self.geo_lon_min_spin = ttk.Spinbox(lon_frame, from_=-180.0, to=180.0, increment=0.01,
                                          textvariable=self.geo_lon_min_var, width=8, format="%.4f")
        self.geo_lon_min_spin.pack(side="left", padx=2)
        
        ttk.Label(lon_frame, text="Max:").pack(side="left", padx=(10, 2))
        self.geo_lon_max_var = tk.DoubleVar(value=1.0)  # Will be updated based on data
        self.geo_lon_max_spin = ttk.Spinbox(lon_frame, from_=-180.0, to=180.0, increment=0.01,
                                          textvariable=self.geo_lon_max_var, width=8, format="%.4f")
        self.geo_lon_max_spin.pack(side="left", padx=2)
        
        # Add Reset Range button to the right of longitude controls
        ttk.Button(lon_frame, text="Reset Range", 
                  command=self._reset_geo_range).pack(side="left", padx=(10, 2))
        
        # Add change handlers for auto-update
        self.geo_lat_min_var.trace('w', self._on_geo_range_changed)
        self.geo_lat_max_var.trace('w', self._on_geo_range_changed)
        self.geo_lon_min_var.trace('w', self._on_geo_range_changed)
        self.geo_lon_max_var.trace('w', self._on_geo_range_changed)
        
        # Initialize ranges based on data
        self._initialize_coordinate_ranges()
        
        # Buttons frame (right section)
        buttons_frame = ttk.LabelFrame(controls_container, text="Actions")
        buttons_frame.pack(side="left", fill="y", padx=5)
        
        # Create matplotlib canvas
        canvas_frame = ttk.Frame(geo_frame)
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.canvas_widgets['geospatial'] = MatplotlibCanvas(canvas_frame)
        self.canvas_widgets['geospatial'].frame.pack(fill="both", expand=True)
        
        # Set zoom callback for coordinate range updates
        self.canvas_widgets['geospatial'].set_zoom_callback(self._on_geospatial_zoom)
    
    def _create_error_analysis_tab(self):
        """Create the North/East error analysis tab with track selection."""
        error_frame = ttk.Frame(self.notebook)
        self.notebook.add(error_frame, text="Error Analysis")
        
        # Control panel with horizontal layout
        control_frame = ttk.LabelFrame(error_frame, text="Error Analysis Controls")
        control_frame.pack(fill="x", padx=10, pady=10)
        
        # Main horizontal container
        controls_container = ttk.Frame(control_frame)
        controls_container.pack(fill="x", padx=5, pady=5)
        
        # Track selection frame
        track_frame = ttk.LabelFrame(controls_container, text="Track Selection")
        track_frame.pack(side="left", fill="y", padx=5)
        
        # Track selection options
        selection_frame = ttk.Frame(track_frame)
        selection_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(selection_frame, text="Tracks:").pack(side="left")
        self.error_tracks_var = tk.StringVar(value="all")
        self.error_tracks_combo = ttk.Combobox(selection_frame, textvariable=self.error_tracks_var,
                                             values=["all", "some"], state="readonly", width=10)
        self.error_tracks_combo.pack(side="left", padx=5)
        
        # Track list frame (shown when "some" is selected)
        self.error_track_list_frame = ttk.Frame(track_frame)
        
        # Bind selection change
        self.error_tracks_combo.bind('<<ComboboxSelected>>', self._on_error_track_selection_changed)
        
        # Create matplotlib canvas
        canvas_frame = ttk.Frame(error_frame)
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.canvas_widgets['error_analysis'] = MatplotlibCanvas(canvas_frame)
        self.canvas_widgets['error_analysis'].frame.pack(fill="both", expand=True)
    
    def _create_rms_error_tab(self):
        """Create the 3D RMS error tab with track selection."""
        rms_frame = ttk.Frame(self.notebook)
        self.notebook.add(rms_frame, text="RMS Error")
        
        # Control panel with horizontal layout
        control_frame = ttk.LabelFrame(rms_frame, text="RMS Error Controls")
        control_frame.pack(fill="x", padx=10, pady=10)
        
        # Main horizontal container
        controls_container = ttk.Frame(control_frame)
        controls_container.pack(fill="x", padx=5, pady=5)
        
        # Track selection frame
        track_frame = ttk.LabelFrame(controls_container, text="Track Selection")
        track_frame.pack(side="left", fill="y", padx=5)
        
        # Track selection options
        selection_frame = ttk.Frame(track_frame)
        selection_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(selection_frame, text="Tracks:").pack(side="left")
        self.rms_tracks_var = tk.StringVar(value="all")
        self.rms_tracks_combo = ttk.Combobox(selection_frame, textvariable=self.rms_tracks_var,
                                           values=["all", "some"], state="readonly", width=10)
        self.rms_tracks_combo.pack(side="left", padx=5)
        
        # Track list frame (shown when "some" is selected)
        self.rms_track_list_frame = ttk.Frame(track_frame)
        
        # Bind selection change
        self.rms_tracks_combo.bind('<<ComboboxSelected>>', self._on_rms_track_selection_changed)
        
        # Create matplotlib canvas
        canvas_frame = ttk.Frame(rms_frame)
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.canvas_widgets['rms_error'] = MatplotlibCanvas(canvas_frame)
        self.canvas_widgets['rms_error'].frame.pack(fill="both", expand=True)
    
    def _create_lifetime_tab(self):
        """Create the track/truth lifetime tab."""
        lifetime_frame = ttk.Frame(self.notebook)
        self.notebook.add(lifetime_frame, text="Lifetime")
        
        # Control panel
        control_frame = ttk.LabelFrame(lifetime_frame, text="Lifetime Controls")
        control_frame.pack(fill="x", padx=10, pady=10)
        
        # Show lifetime plot button
        # Options frame
        options_frame = ttk.Frame(control_frame)
        options_frame.pack(fill="x", padx=5, pady=5)
        
        self.lifetime_tracks_var = tk.BooleanVar(value=True)
        self.lifetime_truth_var = tk.BooleanVar(value=False)
        
        tracks_cb = ttk.Checkbutton(
            options_frame,
            text="Include Tracks",
            variable=self.lifetime_tracks_var
        )
        tracks_cb.pack(side="left", padx=5)
        
        truth_cb = ttk.Checkbutton(
            options_frame,
            text="Include Truth",
            variable=self.lifetime_truth_var
        )
        truth_cb.pack(side="left", padx=5)
        
        # Create matplotlib canvas
        canvas_frame = ttk.Frame(lifetime_frame)
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.canvas_widgets['lifetime'] = MatplotlibCanvas(canvas_frame)
        self.canvas_widgets['lifetime'].frame.pack(fill="both", expand=True)
    
    def _create_animation_tab(self):
        """Create the animation tab with enhanced controls."""
        animation_frame = ttk.Frame(self.notebook)
        self.notebook.add(animation_frame, text="Animation")
        
        # Control panel with horizontal layout
        control_frame = ttk.LabelFrame(animation_frame, text="Animation Controls")
        control_frame.pack(fill="x", padx=10, pady=10)
        
        # Main horizontal container for all control sections
        controls_container = ttk.Frame(control_frame)
        controls_container.pack(fill="x", padx=5, pady=5)
        
        # Data selection frame (left section)
        data_frame = ttk.LabelFrame(controls_container, text="Data Selection")
        data_frame.pack(side="left", fill="y", padx=5)
        
        # Track selection
        tracks_frame = ttk.Frame(data_frame)
        tracks_frame.pack(fill="x", padx=5, pady=2)
        
        ttk.Label(tracks_frame, text="Tracks:").pack(side="left")
        self.anim_tracks_var = tk.StringVar(value="all")
        self.anim_tracks_combo = ttk.Combobox(tracks_frame, textvariable=self.anim_tracks_var,
                                            values=["all", "some", "none"], state="readonly", width=10)
        self.anim_tracks_combo.pack(side="left", padx=5)
        
        # Truth selection
        truth_frame = ttk.Frame(data_frame)
        truth_frame.pack(fill="x", padx=5, pady=2)
        
        ttk.Label(truth_frame, text="Truth:").pack(side="left")
        self.anim_truth_var = tk.StringVar(value="all")
        self.anim_truth_combo = ttk.Combobox(truth_frame, textvariable=self.anim_truth_var,
                                           values=["all", "some", "none"], state="readonly", width=10)
        self.anim_truth_combo.pack(side="left", padx=5)
        
        # Coordinate range frame (center section)
        anim_range_frame = ttk.LabelFrame(controls_container, text="Coordinate Range")
        anim_range_frame.pack(side="left", fill="y", padx=5)
        
        # Latitude range
        anim_lat_frame = ttk.Frame(anim_range_frame)
        anim_lat_frame.pack(fill="x", padx=5, pady=2)
        
        ttk.Label(anim_lat_frame, text="Latitude:").pack(side="left")
        ttk.Label(anim_lat_frame, text="Min:").pack(side="left", padx=(10, 2))
        self.anim_lat_min_var = tk.DoubleVar(value=-1.0)  # Will be updated based on data
        self.anim_lat_min_spin = ttk.Spinbox(anim_lat_frame, from_=-90.0, to=90.0, increment=0.01,
                                           textvariable=self.anim_lat_min_var, width=8, format="%.4f")
        self.anim_lat_min_spin.pack(side="left", padx=2)
        
        ttk.Label(anim_lat_frame, text="Max:").pack(side="left", padx=(10, 2))
        self.anim_lat_max_var = tk.DoubleVar(value=1.0)  # Will be updated based on data
        self.anim_lat_max_spin = ttk.Spinbox(anim_lat_frame, from_=-90.0, to=90.0, increment=0.01,
                                           textvariable=self.anim_lat_max_var, width=8, format="%.4f")
        self.anim_lat_max_spin.pack(side="left", padx=2)
        
        # Longitude range
        anim_lon_frame = ttk.Frame(anim_range_frame)
        anim_lon_frame.pack(fill="x", padx=5, pady=2)
        
        ttk.Label(anim_lon_frame, text="Longitude:").pack(side="left")
        ttk.Label(anim_lon_frame, text="Min:").pack(side="left", padx=(10, 2))
        self.anim_lon_min_var = tk.DoubleVar(value=-1.0)  # Will be updated based on data
        self.anim_lon_min_spin = ttk.Spinbox(anim_lon_frame, from_=-180.0, to=180.0, increment=0.01,
                                           textvariable=self.anim_lon_min_var, width=8, format="%.4f")
        self.anim_lon_min_spin.pack(side="left", padx=2)
        
        ttk.Label(anim_lon_frame, text="Max:").pack(side="left", padx=(10, 2))
        self.anim_lon_max_var = tk.DoubleVar(value=1.0)  # Will be updated based on data
        self.anim_lon_max_spin = ttk.Spinbox(anim_lon_frame, from_=-180.0, to=180.0, increment=0.01,
                                           textvariable=self.anim_lon_max_var, width=8, format="%.4f")
        self.anim_lon_max_spin.pack(side="left", padx=2)
        
        # Add Reset Range button to the right of longitude controls
        ttk.Button(anim_lon_frame, text="Reset Range", 
                  command=self._reset_animation_range).pack(side="left", padx=(10, 2))
        
        # Add change handlers for auto-update
        self.anim_lat_min_var.trace('w', self._on_anim_range_changed)
        self.anim_lat_max_var.trace('w', self._on_anim_range_changed)
        self.anim_lon_min_var.trace('w', self._on_anim_range_changed)
        self.anim_lon_max_var.trace('w', self._on_anim_range_changed)
        
        # Initialize ranges if this is called after geospatial tab (geospatial tab handles initial setup)
        # This ensures both tabs have consistent initial values
        
        # Playback controls frame (right section)
        playback_frame = ttk.LabelFrame(controls_container, text="Playback Controls")
        playback_frame.pack(side="left", fill="y", padx=5)
        
        # Animation state variables
        self.anim_playing = tk.BooleanVar(value=False)
        self.anim_current_frame = tk.IntVar(value=0)
        self.anim_speed = tk.DoubleVar(value=1.0)
        
        # Animation data and timing
        self.anim_data = None
        self.anim_timestamps = []
        self.anim_max_frames = 0
        self.anim_timer_id = None
        self.base_interval = 100  # Base interval in milliseconds (0.1 seconds to match data)
        
        # First row - main playback controls
        playback_row1 = ttk.Frame(playback_frame)
        playback_row1.pack(fill="x", padx=5, pady=2)
        
        self.play_btn = ttk.Button(playback_row1, text="▶", width=3,
                                  command=self._animation_play, state="disabled")
        self.play_btn.pack(side="left", padx=2)
        
        self.pause_btn = ttk.Button(playback_row1, text="⏸", width=3,
                                   command=self._animation_pause, state="disabled")
        self.pause_btn.pack(side="left", padx=2)
        
        self.stop_btn = ttk.Button(playback_row1, text="⏹", width=3,
                                  command=self._animation_stop, state="disabled")
        self.stop_btn.pack(side="left", padx=2)
        
        self.step_back_btn = ttk.Button(playback_row1, text="⏮", width=3,
                                       command=self._animation_step_back, state="disabled")
        self.step_back_btn.pack(side="left", padx=2)
        
        self.step_forward_btn = ttk.Button(playback_row1, text="⏭", width=3,
                                          command=self._animation_step_forward, state="disabled")
        self.step_forward_btn.pack(side="left", padx=2)
        
        # Frame indicator
        self.frame_label = ttk.Label(playback_row1, text="Frame: 0/0")
        self.frame_label.pack(side="left", padx=(10, 2))

        # Second row - speed control
        playback_row2 = ttk.Frame(playback_frame)
        playback_row2.pack(fill="x", padx=5, pady=2)
        
        ttk.Label(playback_row2, text="Speed:").pack(side="left")
        self.speed_scale = ttk.Scale(playback_row2, from_=0.1, to=5.0, 
                                    variable=self.anim_speed, orient="horizontal", length=80)
        self.speed_scale.pack(side="left", padx=2)
        
        self.speed_label = ttk.Label(playback_row2, text="1.0x")
        self.speed_label.pack(side="left", padx=2)
        
        # Bind speed change
        self.anim_speed.trace('w', self._on_speed_changed)
        
        # Create matplotlib canvas
        canvas_frame = ttk.Frame(animation_frame)
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.canvas_widgets['animation'] = MatplotlibCanvas(canvas_frame)
        self.canvas_widgets['animation'].frame.pack(fill="both", expand=True)
        
        # Set zoom callback for coordinate range updates
        self.canvas_widgets['animation'].set_zoom_callback(self._on_animation_zoom)
    
    
    def _create_demo_plot(self):
        """Create a demo plot for the overview tab."""
        if 'overview' in self.canvas_widgets:
            # Create demo plot data
            demo_data = {
                'plot_type': 'demo'
            }
            self.canvas_widgets['overview'].create_simple_plot(demo_data)
    
    def _show_track_counts(self):
        """Show track counts in the statistics tab."""
        if not self.plot_manager or not self.controller:
            return
        
        try:
            # Use the new modular statistics tab if available
            if hasattr(self, 'statistics_tab'):
                self.statistics_tab.auto_update()
            else:
                # Fallback to old method for backward compatibility
                app_state = self.controller.get_state()
                plot_data = self.plot_manager.prepare_plot_data('track_counts', app_state)
                
                if 'error' not in plot_data and 'statistics' in self.canvas_widgets:
                    canvas = self.canvas_widgets['statistics']
                    canvas.create_simple_plot({'track_counts': plot_data['track_counts']})
            
        except Exception as e:
            self.logger.error(f"Error showing track counts: {e}")
    
    def _auto_update_geospatial_plot(self):
        """Automatically update the geospatial plot when focus dataset changes."""
        try:
            if not self.plot_manager or not self.controller:
                return
            
            app_state = self.controller.get_state()
            focus_info = app_state.get_focus_dataset_info()
            
            # Only auto-update if we have a loaded focus dataset with data
            if (focus_info and 
                focus_info.status.value == "loaded" and 
                ((focus_info.tracks_df is not None and not focus_info.tracks_df.empty) or
                 (focus_info.truth_df is not None and not focus_info.truth_df.empty))):
                
                # Get plot configuration from UI enhanced controls
                config = {
                    'tracks_selection': getattr(self, 'geo_tracks_var', tk.StringVar(value="all")).get(),
                    'truth_selection': getattr(self, 'geo_truth_var', tk.StringVar(value="all")).get(),
                    'lat_range': (getattr(self, 'geo_lat_min_var', tk.DoubleVar(value=-90.0)).get(),
                                 getattr(self, 'geo_lat_max_var', tk.DoubleVar(value=90.0)).get()),
                    'lon_range': (getattr(self, 'geo_lon_min_var', tk.DoubleVar(value=-180.0)).get(),
                                 getattr(self, 'geo_lon_max_var', tk.DoubleVar(value=180.0)).get())
                }
                
                plot_data = self.plot_manager.prepare_plot_data('lat_lon_scatter', app_state, config)
                
                if 'error' not in plot_data and 'geospatial' in self.canvas_widgets:
                    canvas = self.canvas_widgets['geospatial']
                    canvas.create_simple_plot(plot_data)
                    self.logger.debug(f"Auto-updated geospatial plot for dataset: {focus_info.name}")
            
        except Exception as e:
            self.logger.error(f"Error auto-updating geospatial plot: {e}")
    
    def _auto_update_error_plot(self):
        """Auto-update error analysis plot when focus dataset changes."""
        try:
            if not self.plot_manager or not self.controller:
                return
            
            app_state = self.controller.get_state()
            focus_info = app_state.get_focus_dataset_info()
            
            # Only auto-update if we have a loaded focus dataset with data
            if (focus_info and 
                focus_info.status.value == "loaded" and 
                focus_info.tracks_df is not None and not focus_info.tracks_df.empty and
                focus_info.truth_df is not None and not focus_info.truth_df.empty):
                
                # Get plot configuration from UI
                config = {
                    'tracks_selection': getattr(self, 'error_tracks_var', tk.StringVar(value="all")).get()
                }
                
                plot_data = self.plot_manager.prepare_plot_data('north_east_error', app_state, config)
                
                if 'error' not in plot_data and 'error_analysis' in self.canvas_widgets:
                    self.canvas_widgets['error_analysis'].create_simple_plot(plot_data)
                    self.logger.debug(f"Auto-updated error plot for dataset: {focus_info.name}")
            
        except Exception as e:
            self.logger.error(f"Error auto-updating error plot: {e}")
    
    def _auto_update_rms_plot(self):
        """Auto-update RMS error plot when focus dataset changes."""
        try:
            if not self.plot_manager or not self.controller:
                return
            
            app_state = self.controller.get_state()
            focus_info = app_state.get_focus_dataset_info()
            
            # Only auto-update if we have a loaded focus dataset with data
            if (focus_info and 
                focus_info.status.value == "loaded" and 
                focus_info.tracks_df is not None and not focus_info.tracks_df.empty and
                focus_info.truth_df is not None and not focus_info.truth_df.empty):
                
                # Get plot configuration from UI
                config = {
                    'tracks_selection': getattr(self, 'rms_tracks_var', tk.StringVar(value="all")).get()
                }
                
                plot_data = self.plot_manager.prepare_plot_data('rms_error_3d', app_state, config)
                
                if 'error' not in plot_data and 'rms_error' in self.canvas_widgets:
                    self.canvas_widgets['rms_error'].create_simple_plot(plot_data)
                    self.logger.debug(f"Auto-updated RMS plot for dataset: {focus_info.name}")
            
        except Exception as e:
            self.logger.error(f"Error auto-updating RMS plot: {e}")
    
    def _auto_update_lifetime_plot(self):
        """Auto-update lifetime plot when focus dataset changes."""
        try:
            if not self.plot_manager or not self.controller:
                return
            
            app_state = self.controller.get_state()
            focus_info = app_state.get_focus_dataset_info()
            
            # Only auto-update if we have a loaded focus dataset with data
            if (focus_info and 
                focus_info.status.value == "loaded" and 
                focus_info.tracks_df is not None and not focus_info.tracks_df.empty):
                
                plot_data = self.plot_manager.prepare_plot_data('track_truth_lifetime', app_state, {})
                
                if 'error' not in plot_data and 'lifetime' in self.canvas_widgets:
                    self.canvas_widgets['lifetime'].create_simple_plot(plot_data)
                    self.logger.debug(f"Auto-updated lifetime plot for dataset: {focus_info.name}")
            
        except Exception as e:
            self.logger.error(f"Error auto-updating lifetime plot: {e}")
    
    def _auto_update_animation_plot(self):
        """Auto-update animation plot when focus dataset changes."""
        try:
            if not self.plot_manager or not self.controller:
                return
            
            app_state = self.controller.get_state()
            focus_info = app_state.get_focus_dataset_info()
            
            # Only auto-update if we have a loaded focus dataset with data
            if (focus_info and 
                focus_info.status.value == "loaded" and 
                ((focus_info.tracks_df is not None and not focus_info.tracks_df.empty) or
                 (focus_info.truth_df is not None and not focus_info.truth_df.empty))):
                
                # Get plot configuration from UI
                config = {
                    'tracks_selection': getattr(self, 'anim_tracks_var', tk.StringVar(value="all")).get(),
                    'truth_selection': getattr(self, 'anim_truth_var', tk.StringVar(value="all")).get(),
                    'lat_range': (getattr(self, 'anim_lat_min_var', tk.DoubleVar(value=-90.0)).get(),
                                 getattr(self, 'anim_lat_max_var', tk.DoubleVar(value=90.0)).get()),
                    'lon_range': (getattr(self, 'anim_lon_min_var', tk.DoubleVar(value=-180.0)).get(),
                                 getattr(self, 'anim_lon_max_var', tk.DoubleVar(value=180.0)).get())
                }
                
                plot_data = self.plot_manager.prepare_plot_data('lat_lon_animation', app_state, config)
                
                if 'error' not in plot_data and 'animation' in self.canvas_widgets:
                    self.canvas_widgets['animation'].create_simple_plot(plot_data)
                    # Enable playback controls if available
                    if hasattr(self, 'play_btn'):
                        self.play_btn.config(state="normal")
                    if hasattr(self, 'stop_btn'):
                        self.stop_btn.config(state="normal")
                    self.logger.debug(f"Auto-updated animation plot for dataset: {focus_info.name}")
            
        except Exception as e:
            self.logger.error(f"Error auto-updating animation plot: {e}")
    
    def _auto_update_statistics_plot(self):
        """Auto-update statistics plot when focus dataset changes."""
        try:
            if not self.controller:
                self.logger.debug("No controller available for statistics auto-update")
                return
            
            app_state = self.controller.get_state()
            focus_info = app_state.get_focus_dataset_info()
            
            # Check if we have a loaded focus dataset with any data
            if (focus_info and focus_info.status.value == "loaded"):
                # Check if any data is available (tracks, truth, or detections)
                has_data = (
                    (focus_info.tracks_df is not None and not focus_info.tracks_df.empty) or
                    (focus_info.truth_df is not None and not focus_info.truth_df.empty) or
                    (focus_info.detections_df is not None and not focus_info.detections_df.empty)
                )
                
                if has_data:
                    # Use the new modular statistics tab if available
                    if hasattr(self, 'statistics_tab') and hasattr(self.statistics_tab, 'auto_update'):
                        self.statistics_tab.auto_update()
                        self.logger.debug(f"Auto-updated modular statistics plot for dataset: {focus_info.name}")
                    elif self.plot_manager:
                        # Fallback to old method
                        plot_data = self.plot_manager.prepare_plot_data('track_counts', app_state, {})
                        
                        if 'error' not in plot_data and 'visualization' in self.canvas_widgets:
                            self.canvas_widgets['visualization'].create_simple_plot(plot_data)
                            self.logger.debug(f"Auto-updated legacy statistics plot for dataset: {focus_info.name}")
                else:
                    self.logger.debug(f"No data available in focus dataset: {focus_info.name}")
            else:
                self.logger.debug("No loaded focus dataset available for statistics update")
            
        except Exception as e:
            self.logger.error(f"Error auto-updating statistics plot: {e}")
    
    def _show_north_east_error_plot(self):
        """Show North/East error plot in the error analysis tab."""
        if not self.plot_manager or not self.controller:
            return
        
        try:
            app_state = self.controller.get_state()
            plot_data = self.plot_manager.prepare_plot_data('north_east_error', app_state)
            
            if 'error' not in plot_data:
                canvas = self.canvas_widgets['error_analysis']
                canvas.create_simple_plot({'error_data': plot_data['error_data']})
            
        except Exception as e:
            self.logger.error(f"Error showing North/East error plot: {e}")
    
    def _show_rms_error_plot(self):
        """Show 3D RMS error plot in the RMS error tab."""
        if not self.plot_manager or not self.controller:
            return
        
        try:
            app_state = self.controller.get_state()
            plot_data = self.plot_manager.prepare_plot_data('rms_error_3d', app_state)
            
            if 'error' not in plot_data:
                canvas = self.canvas_widgets['rms_error']
                canvas.create_simple_plot({'rms_data': plot_data['rms_data']})
            
        except Exception as e:
            self.logger.error(f"Error showing RMS error plot: {e}")
    
    def _show_lifetime_plot(self):
        """Show lifetime plot in the lifetime tab."""
        if not self.plot_manager or not self.controller:
            return
        
        try:
            app_state = self.controller.get_state()
            
            # Get plot configuration from UI
            config = {
                'include_tracks': self.lifetime_tracks_var.get(),
                'include_truth': self.lifetime_truth_var.get()
            }
            
            plot_data = self.plot_manager.prepare_plot_data('track_truth_lifetime', app_state, config)
            
            if 'error' not in plot_data:
                canvas = self.canvas_widgets['lifetime']
                canvas.create_simple_plot({'lifetime_data': plot_data['lifetime_data']})
            
        except Exception as e:
            self.logger.error(f"Error showing lifetime plot: {e}")
    
    def _on_tab_changed(self, event):
        """Handle tab change events."""
        try:
            current_tab = self.get_current_tab()
            self.logger.debug(f"Tab changed to: {current_tab}")
            
            # Refresh data when switching to certain tabs
            if current_tab == "Visualization":
                self._refresh_dataset_selection()
        
        except Exception as e:
            self.logger.error(f"Error handling tab change: {e}")
    
    # State Management
    def on_state_changed(self, event: str):
        """
        Handle state changes from the application.
        
        Args:
            event: The type of state change event
        """
        try:
            if not self.controller:
                return
            
            state = self.controller.get_state()
            
            if event == "datasets_changed":
                # Refresh dataset selection when datasets change
                self._refresh_dataset_selection()
                
                # Update coordinate ranges based on new data
                self._initialize_coordinate_ranges()
                
                # Update track counts display
                self._show_track_counts()
                
                # Check if focus dataset is loaded and auto-update all plots
                focus_info = state.get_focus_dataset_info()
                if focus_info and focus_info.status.value == "loaded":
                    # Initialize coordinate ranges based on the newly loaded data
                    self._initialize_coordinate_ranges()
                    
                    self._auto_update_geospatial_plot()
                    self._auto_update_error_plot()
                    self._auto_update_rms_plot()
                    self._auto_update_lifetime_plot()
                    self._auto_update_animation_plot()
                    self._auto_update_statistics_plot()
                
                self.logger.debug(f"Datasets changed, all plots refreshed")
            
            elif event == "focus_changed":
                # Refresh dataset selection when focus dataset changes
                self._refresh_dataset_selection()
                
                # Update coordinate ranges when focus changes
                self._initialize_coordinate_ranges()
                
                # Auto-update all plots if focus dataset is loaded
                focus_info = state.get_focus_dataset_info()
                if focus_info and focus_info.status.value == "loaded":
                    self._auto_update_geospatial_plot()
                    self._auto_update_error_plot()
                    self._auto_update_rms_plot()
                    self._auto_update_lifetime_plot()
                    self._auto_update_animation_plot()
                    self._auto_update_statistics_plot()
                
                self.logger.debug(f"Focus changed, all plots refreshed")
            
        except Exception as e:
            self.logger.error(f"Error handling state change '{event}': {e}")
    
    # Utility Methods
    def get_current_tab(self) -> str:
        """
        Get the name of the currently selected tab.
        
        Returns:
            Name of the current tab, or empty string if none selected
        """
        try:
            current_index = self.notebook.index(self.notebook.select())
            return self.notebook.tab(current_index, "text")
        except Exception as e:
            self.logger.error(f"Error getting current tab: {e}")
            return ""
    
    def select_tab(self, tab_name: str):
        """
        Select a specific tab.
        
        Args:
            tab_name: Name of the tab to select
        """
        try:
            tab_count = self.notebook.index("end")
            for i in range(tab_count):
                if self.notebook.tab(i, "text") == tab_name:
                    self.notebook.select(i)
                    self.logger.debug(f"Selected tab: {tab_name}")
                    break
        except Exception as e:
            self.logger.error(f"Error selecting tab: {e}")
    
    def export_current_plot(self):
        """
        Export the current tab's plot to a file (opens file dialog).
        """
        try:
            current_tab = self.get_current_tab().lower()
            if current_tab in self.canvas_widgets:
                # Call export_plot without parameters (it opens a file dialog)
                self.canvas_widgets[current_tab].export_plot()
                self.logger.info(f"Exported plot from {current_tab} tab")
        except Exception as e:
            self.logger.error(f"Error exporting plot: {e}")
    
    def clear_current_plot(self):
        """Clear the current tab's plot."""
        try:
            current_tab = self.get_current_tab().lower()
            if current_tab in self.canvas_widgets:
                self.canvas_widgets[current_tab].clear_plot()
                self.logger.info(f"Cleared plot in {current_tab} tab")
        except Exception as e:
            self.logger.error(f"Error clearing plot: {e}")
    
    # Dataset Selection Methods
    def _refresh_dataset_selection(self):
        """Refresh the dataset selection controls."""
        if not self.controller:
            return
        
        try:
            # Clear existing selection controls
            for widget in self.dataset_selection_frame.winfo_children():
                widget.destroy()
            
            # Get current datasets
            state = self.controller.get_state()
            datasets = state.datasets
            
            # Create checkboxes for each dataset
            self.dataset_selection_vars.clear()
            for dataset_name in datasets.keys():
                var = tk.BooleanVar(value=True)  # Default to all selected
                self.dataset_selection_vars[dataset_name] = var
                
                cb = ttk.Checkbutton(
                    self.dataset_selection_frame,
                    text=dataset_name,
                    variable=var
                )
                cb.pack(anchor="w", padx=5, pady=1)
            
        except Exception as e:
            self.logger.error(f"Error refreshing dataset selection: {e}")
    
    def _select_all_datasets(self):
        """Select all datasets for track counts plot."""
        for var in self.dataset_selection_vars.values():
            var.set(True)
    
    def _select_no_datasets(self):
        """Deselect all datasets for track counts plot."""
        for var in self.dataset_selection_vars.values():
            var.set(False)
    
    def _show_track_counts_plot(self):
        """Show the track counts plot with selected datasets."""
        if not self.plot_manager or not self.controller:
            return
        
        try:
            # Get selected datasets
            selected_datasets = [
                name for name, var in self.dataset_selection_vars.items() 
                if var.get()
            ]
            
            if not selected_datasets:
                self.logger.warning("No datasets selected for track counts plot")
                return
            
            # Prepare plot configuration
            plot_config = {'selected_datasets': selected_datasets}
            
            # Get application state and prepare data
            app_state = self.controller.get_state()
            plot_data = self.plot_manager.prepare_plot_data('track_counts', app_state, plot_config)
            
            if 'error' in plot_data:
                self.logger.error(f"Error preparing track counts data: {plot_data['error']}")
                return
            
            # Create the plot
            self.canvas_widgets['visualization'].create_simple_plot(plot_data)
            
        except Exception as e:
            self.logger.error(f"Error showing track counts plot: {e}")
    
    # Range Reset Methods
    def _reset_geo_range(self):
        """Reset geospatial coordinate ranges to data-based defaults."""
        # Re-initialize ranges based on current data
        self._initialize_coordinate_ranges()
        # Trigger plot update after reset
        self._auto_update_geospatial_plot()
    
    def _reset_animation_range(self):
        """Reset animation coordinate ranges to data-based defaults."""
        # Re-initialize ranges based on current data
        self._initialize_coordinate_ranges()
        # Trigger plot update after reset
        self._show_animation_plot()
    
    # Range Change Handlers
    def _on_geo_range_changed(self, *args):
        """Handle changes in geospatial coordinate ranges."""
        try:
            # Skip if we're updating ranges from zoom event
            if hasattr(self, '_updating_geo_ranges') and self._updating_geo_ranges:
                return
                
            # Validate ranges
            lat_min = self.geo_lat_min_var.get()
            lat_max = self.geo_lat_max_var.get()
            lon_min = self.geo_lon_min_var.get()
            lon_max = self.geo_lon_max_var.get()
            
            # Ensure min < max
            if lat_min >= lat_max:
                return  # Skip update if invalid range
            if lon_min >= lon_max:
                return  # Skip update if invalid range
            
            # Update the geospatial plot
            self._auto_update_geospatial_plot()
            
        except Exception as e:
            self.logger.error(f"Error updating geospatial plot after range change: {e}")
    
    def _on_anim_range_changed(self, *args):
        """Handle changes in animation coordinate ranges."""
        try:
            # Skip if we're updating ranges from zoom event
            if hasattr(self, '_updating_anim_ranges') and self._updating_anim_ranges:
                return
                
            # Validate ranges
            lat_min = self.anim_lat_min_var.get()
            lat_max = self.anim_lat_max_var.get()
            lon_min = self.anim_lon_min_var.get()
            lon_max = self.anim_lon_max_var.get()
            
            # Ensure min < max
            if lat_min >= lat_max:
                return  # Skip update if invalid range
            if lon_max <= lon_min:
                return  # Skip update if invalid range
            
            # Update the stored animation data ranges
            if hasattr(self, 'anim_data') and self.anim_data:
                self.anim_data['lat_range'] = (lat_min, lat_max)
                self.anim_data['lon_range'] = (lon_min, lon_max)
                
                # If we have animation data, just update the current frame with new ranges
                self._update_animation_frame()
            else:
                # If no animation data yet, regenerate the entire plot
                self._show_animation_plot()
            
        except Exception as e:
            self.logger.error(f"Error updating animation plot after range change: {e}")
    
    def _on_geospatial_zoom(self, xlim, ylim):
        """Handle zoom/pan events on geospatial plot."""
        try:
            # Update the coordinate range controls to match the new zoom level
            lon_min, lon_max = xlim
            lat_min, lat_max = ylim
            
            # Check if we're already updating to prevent recursion
            if getattr(self, '_updating_geo_ranges', False):
                return
                
            # Set a flag to prevent recursive updates
            self._updating_geo_ranges = True
            
            try:
                # Update the variables
                self.geo_lat_min_var.set(lat_min)
                self.geo_lat_max_var.set(lat_max)
                self.geo_lon_min_var.set(lon_min)
                self.geo_lon_max_var.set(lon_max)
                
                self.logger.debug(f"Geospatial zoom updated ranges: lat {lat_min:.4f}-{lat_max:.4f}, lon {lon_min:.4f}-{lon_max:.4f}")
            finally:
                self._updating_geo_ranges = False
            
        except Exception as e:
            self.logger.error(f"Error handling geospatial zoom: {e}")
            # Ensure flag is cleared even on error
            self._updating_geo_ranges = False
    
    def _on_animation_zoom(self, xlim, ylim):
        """Handle zoom/pan events on animation plot."""
        try:
            # Update the coordinate range controls to match the new zoom level
            lon_min, lon_max = xlim
            lat_min, lat_max = ylim
            
            # Check if we're already updating to prevent recursion
            if getattr(self, '_updating_anim_ranges', False):
                return
                
            # Set a flag to prevent recursive updates
            self._updating_anim_ranges = True
            
            try:
                # Update the variables
                self.anim_lat_min_var.set(lat_min)
                self.anim_lat_max_var.set(lat_max)
                self.anim_lon_min_var.set(lon_min)
                self.anim_lon_max_var.set(lon_max)
                
                # Update the stored animation data ranges so they persist
                if hasattr(self, 'anim_data') and self.anim_data:
                    self.anim_data['lat_range'] = (lat_min, lat_max)
                    self.anim_data['lon_range'] = (lon_min, lon_max)
                
                # If animation is currently playing, update the current frame
                if hasattr(self, 'anim_data') and self.anim_data and not self.anim_playing.get():
                    self._update_animation_frame()
                
                self.logger.debug(f"Animation zoom updated ranges: lat {lat_min:.4f}-{lat_max:.4f}, lon {lon_min:.4f}-{lon_max:.4f}")
            finally:
                self._updating_anim_ranges = False
            
        except Exception as e:
            self.logger.error(f"Error handling animation zoom: {e}")
            # Ensure flag is cleared even on error
            self._updating_anim_ranges = False
    
    # Coordinate Range Initialization Methods
    def _initialize_coordinate_ranges(self):
        """Initialize coordinate ranges based on actual data."""
        try:
            if not self.controller:
                return
                
            app_state = self.controller.get_state()
            focus_dataset = app_state.get_focus_dataset_info() if app_state else None
            
            # Use focus dataset if available, otherwise try current_data
            if focus_dataset and focus_dataset.status.value == "loaded":
                # Get bounds from tracks and truth data
                all_lats = []
                all_lons = []
                
                if focus_dataset.tracks_df is not None and not focus_dataset.tracks_df.empty:
                    if 'lat' in focus_dataset.tracks_df.columns:
                        all_lats.extend(focus_dataset.tracks_df['lat'].dropna().tolist())
                    if 'lon' in focus_dataset.tracks_df.columns:
                        all_lons.extend(focus_dataset.tracks_df['lon'].dropna().tolist())
                
                if focus_dataset.truth_df is not None and not focus_dataset.truth_df.empty:
                    if 'lat' in focus_dataset.truth_df.columns:
                        all_lats.extend(focus_dataset.truth_df['lat'].dropna().tolist())
                    if 'lon' in focus_dataset.truth_df.columns:
                        all_lons.extend(focus_dataset.truth_df['lon'].dropna().tolist())
                
                if focus_dataset.detections_df is not None and not focus_dataset.detections_df.empty:
                    if 'lat' in focus_dataset.detections_df.columns:
                        all_lats.extend(focus_dataset.detections_df['lat'].dropna().tolist())
                    if 'lon' in focus_dataset.detections_df.columns:
                        all_lons.extend(focus_dataset.detections_df['lon'].dropna().tolist())
                
                if len(all_lats) > 0 and len(all_lons) > 0:
                    # Calculate data bounds with small padding
                    lat_min, lat_max = min(all_lats), max(all_lats)
                    lon_min, lon_max = min(all_lons), max(all_lons)
                    
                    # Add 10% padding
                    lat_range = lat_max - lat_min if lat_max != lat_min else 0.1
                    lon_range = lon_max - lon_min if lon_max != lon_min else 0.1
                    padding_lat = 0.01
                    padding_lon = 0.01
                    
                    lat_min -= padding_lat
                    lat_max += padding_lat
                    lon_min -= padding_lon
                    lon_max += padding_lon
                    
                    # Make the range square by taking the larger range and centering
                    lat_center = (lat_max + lat_min) / 2.0
                    lon_center = (lon_max + lon_min) / 2.0
                    max_range = max(lat_max - lat_min, lon_max - lon_min)
                    half_range = max_range / 2.0
                    
                    # Set square ranges for geospatial controls
                    if hasattr(self, 'geo_lat_min_var'):
                        self.geo_lat_min_var.set(lat_center - half_range)
                        self.geo_lat_max_var.set(lat_center + half_range)
                        self.geo_lon_min_var.set(lon_center - half_range)
                        self.geo_lon_max_var.set(lon_center + half_range)
                    
                    # Set matching ranges for animation controls
                    if hasattr(self, 'anim_lat_min_var'):
                        self.anim_lat_min_var.set(lat_center - half_range)
                        self.anim_lat_max_var.set(lat_center + half_range)
                        self.anim_lon_min_var.set(lon_center - half_range)
                        self.anim_lon_max_var.set(lon_center + half_range)
                    
                    self.logger.debug(f"Initialized coordinate ranges: lat [{lat_center - half_range:.1f}, {lat_center + half_range:.1f}], "
                                    f"lon [{lon_center - half_range:.1f}, {lon_center + half_range:.1f}]")
                    return
            
            # If no focus dataset with data is available, use default ranges
            self.logger.debug("No loaded focus dataset available, using default coordinate ranges")
                    
        except Exception as e:
            self.logger.error(f"Error initializing coordinate ranges: {e}")

    def update_coordinate_ranges(self):
        """Update coordinate ranges when new data is loaded."""
        self._initialize_coordinate_ranges()

    # Track Selection Change Handlers
    def _on_error_track_selection_changed(self, event=None):
        """Handle changes in error analysis track selection."""
        selection = self.error_tracks_var.get()
        if selection == "some":
            # Show track list for individual selection
            self._show_track_list(self.error_track_list_frame, 'error')
        else:
            # Hide track list
            self._hide_track_list(self.error_track_list_frame)
    
    def _on_rms_track_selection_changed(self, event=None):
        """Handle changes in RMS error track selection."""
        selection = self.rms_tracks_var.get()
        if selection == "some":
            # Show track list for individual selection
            self._show_track_list(self.rms_track_list_frame, 'rms')
        else:
            # Hide track list
            self._hide_track_list(self.rms_track_list_frame)
    
    def _show_track_list(self, parent_frame, plot_type):
        """Show track list for individual selection."""
        # Clear existing widgets
        for widget in parent_frame.winfo_children():
            widget.destroy()
        
        # Pack the frame
        parent_frame.pack(fill="x", padx=5, pady=5)
        
        # Get available tracks
        if not self.controller:
            return
        
        try:
            state = self.controller.get_state()
            focus_info = state.get_focus_dataset_info()
            
            if not focus_info or focus_info.status.value != "loaded":
                ttk.Label(parent_frame, text="No dataset loaded").pack()
                return
            
            tracks_data = focus_info.data.get('tracks')
            if tracks_data is None or tracks_data.empty:
                ttk.Label(parent_frame, text="No tracks available").pack()
                return
            
            # Get unique track IDs
            track_ids = sorted(tracks_data['track_id'].unique())
            
            # Create scrollable frame for track checkboxes
            canvas = tk.Canvas(parent_frame, height=100)
            scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Create track selection variables
            track_vars = {}
            for track_id in track_ids[:20]:  # Limit to first 20 for UI performance
                var = tk.BooleanVar(value=True)
                track_vars[track_id] = var
                
                cb = ttk.Checkbutton(
                    scrollable_frame,
                    text=f"Track {track_id}",
                    variable=var
                )
                cb.pack(anchor="w", padx=5, pady=1)
            
            # Store track variables
            if plot_type == 'error':
                self.error_track_vars = track_vars
            elif plot_type == 'rms':
                self.rms_track_vars = track_vars
            
            # Pack canvas and scrollbar
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            if len(track_ids) > 20:
                ttk.Label(parent_frame, 
                         text=f"Showing first 20 of {len(track_ids)} tracks").pack()
        
        except Exception as e:
            self.logger.error(f"Error showing track list: {e}")
            ttk.Label(parent_frame, text="Error loading tracks").pack()
    
    def _hide_track_list(self, parent_frame):
        """Hide track list frame."""
        parent_frame.pack_forget()
        for widget in parent_frame.winfo_children():
            widget.destroy()
    
    # Animation Control Methods
    def _animation_play(self):
        """Start animation playback."""
        if self.anim_data is None or self.anim_max_frames == 0:
            self.logger.warning("No animation data available for playback")
            return
            
        self.anim_playing.set(True)
        self.play_btn.config(state="disabled")
        self.pause_btn.config(state="normal")
        self.stop_btn.config(state="normal")
        self.step_back_btn.config(state="disabled")
        self.step_forward_btn.config(state="disabled")
        
        # Start animation timer
        self._animation_timer()
        self.logger.info("Animation play started")
    
    def _animation_pause(self):
        """Pause animation playback."""
        self.anim_playing.set(False)
        self.play_btn.config(state="normal")
        self.pause_btn.config(state="disabled")
        self.step_back_btn.config(state="normal")
        self.step_forward_btn.config(state="normal")
        
        # Cancel timer
        if self.anim_timer_id:
            self.canvas_widgets['animation'].frame.after_cancel(self.anim_timer_id)
            self.anim_timer_id = None
            
        self.logger.info("Animation paused")
    
    def _animation_stop(self):
        """Stop animation playback."""
        self.anim_playing.set(False)
        self.anim_current_frame.set(0)
        self.play_btn.config(state="normal")
        self.pause_btn.config(state="disabled")
        self.step_back_btn.config(state="normal")
        self.step_forward_btn.config(state="normal")
        
        # Cancel timer
        if self.anim_timer_id:
            self.canvas_widgets['animation'].frame.after_cancel(self.anim_timer_id)
            self.anim_timer_id = None
            
        # Update plot to show initial frame
        self._update_animation_frame()
        self.logger.info("Animation stopped")
    
    def _animation_step_back(self):
        """Step animation back one frame."""
        current = self.anim_current_frame.get()
        if current > 0:
            self.anim_current_frame.set(current - 1)
            self._update_animation_frame()
        self.logger.info(f"Animation stepped back to frame {self.anim_current_frame.get()}")
    
    def _animation_step_forward(self):
        """Step animation forward one frame."""
        current = self.anim_current_frame.get()
        if current < self.anim_max_frames - 1:
            self.anim_current_frame.set(current + 1)
            self._update_animation_frame()
        self.logger.info(f"Animation stepped forward to frame {self.anim_current_frame.get()}")
        
    def _animation_timer(self):
        """Timer function for animation playback."""
        if not self.anim_playing.get():
            return
            
        current_frame = self.anim_current_frame.get()
        
        # Check if we've reached the end
        if current_frame >= self.anim_max_frames - 1:
            self._animation_stop()
            return
            
        # Advance to next frame
        self.anim_current_frame.set(current_frame + 1)
        self._update_animation_frame()
        
        # Calculate interval based on speed (speed 1.0 = base_interval)
        interval = int(self.base_interval / self.anim_speed.get())
        interval = max(10, interval)  # Minimum 10ms interval
        
        # Schedule next update
        self.anim_timer_id = self.canvas_widgets['animation'].frame.after(interval, self._animation_timer)
    
    def _update_animation_frame(self):
        """Update the animation plot to show current frame."""
        if self.anim_data is None:
            return
            
        current_frame = self.anim_current_frame.get()
        
        # Update frame label
        self.frame_label.config(text=f"Frame: {current_frame + 1}/{self.anim_max_frames}")
        
        # Get data up to current timestamp
        if current_frame < len(self.anim_timestamps):
            current_time = self.anim_timestamps[current_frame]
            
            # Filter data to current time
            filtered_data = self._filter_animation_data_to_time(current_time)
            
            # Use current coordinate ranges from controls instead of stored ones
            filtered_data['lat_range'] = (self.anim_lat_min_var.get(), self.anim_lat_max_var.get())
            filtered_data['lon_range'] = (self.anim_lon_min_var.get(), self.anim_lon_max_var.get())
            
            # Update plot
            self.canvas_widgets['animation'].create_animation_frame(filtered_data, current_frame, self.anim_max_frames)
    
    def _filter_animation_data_to_time(self, current_time):
        """Filter animation data to show only data up to current time."""
        filtered_data = {
            'tracks': None,
            'truth': None,
            'current_time': current_time,
            'lat_range': self.anim_data.get('lat_range') if self.anim_data else None,
            'lon_range': self.anim_data.get('lon_range') if self.anim_data else None
        }
        
        # Filter tracks data
        if self.anim_data and 'tracks' in self.anim_data and self.anim_data['tracks'] is not None:
            tracks_df = self.anim_data['tracks']
            if 'timestamp' in tracks_df.columns:
                filtered_data['tracks'] = tracks_df[tracks_df['timestamp'] <= current_time]
        
        # Filter truth data
        if self.anim_data and 'truth' in self.anim_data and self.anim_data['truth'] is not None:
            truth_df = self.anim_data['truth']
            if 'timestamp' in truth_df.columns:
                filtered_data['truth'] = truth_df[truth_df['timestamp'] <= current_time]
                
        return filtered_data
    
    def _on_speed_changed(self, *args):
        """Handle speed scale changes."""
        speed = self.anim_speed.get()
        self.speed_label.config(text=f"{speed:.1f}x")
        self.logger.debug(f"Animation speed changed to {speed:.1f}x")
    
    # Enhanced Plot Methods with New Controls
    def _show_lat_lon_plot(self):
        """Show lat/lon plot with enhanced controls."""
        if not self.plot_manager or not self.controller:
            return
        
        try:
            # Get selection parameters
            tracks_selection = self.geo_tracks_var.get()
            truth_selection = self.geo_truth_var.get()
            
            # Get coordinate ranges
            lat_min = self.geo_lat_min_var.get()
            lat_max = self.geo_lat_max_var.get()
            lon_min = self.geo_lon_min_var.get()
            lon_max = self.geo_lon_max_var.get()
            
            # Validate ranges
            if lat_min >= lat_max or lon_min >= lon_max:
                self.logger.error("Invalid coordinate ranges")
                return
            
            # Prepare plot configuration
            plot_config = {
                'tracks_selection': tracks_selection,
                'truth_selection': truth_selection,
                'lat_range': (lat_min, lat_max),
                'lon_range': (lon_min, lon_max)
            }
            
            # Get application state and prepare data
            app_state = self.controller.get_state()
            plot_data = self.plot_manager.prepare_plot_data('lat_lon_scatter', app_state, plot_config)
            
            if 'error' in plot_data:
                self.logger.error(f"Error preparing lat/lon data: {plot_data['error']}")
                return
            
            # Create the plot
            self.canvas_widgets['geospatial'].create_simple_plot(plot_data)
            
        except Exception as e:
            self.logger.error(f"Error showing lat/lon plot: {e}")
    
    def _show_animation_plot(self):
        """Show animation plot with enhanced controls."""
        if not self.plot_manager or not self.controller:
            return
        
        try:
            # Get selection parameters
            tracks_selection = self.anim_tracks_var.get()
            truth_selection = self.anim_truth_var.get()
            
            # Get coordinate ranges
            lat_min = self.anim_lat_min_var.get()
            lat_max = self.anim_lat_max_var.get()
            lon_min = self.anim_lon_min_var.get()
            lon_max = self.anim_lon_max_var.get()
            
            # Validate ranges
            if lat_min >= lat_max or lon_min >= lon_max:
                self.logger.error("Invalid coordinate ranges")
                return
            
            # Prepare plot configuration
            plot_config = {
                'tracks_selection': tracks_selection,
                'truth_selection': truth_selection,
                'lat_range': (lat_min, lat_max),
                'lon_range': (lon_min, lon_max)
            }
            
            # Get application state and prepare data
            app_state = self.controller.get_state()
            plot_data = self.plot_manager.prepare_plot_data('lat_lon_animation', app_state, plot_config)
            
            if 'error' in plot_data:
                self.logger.error(f"Error preparing animation data: {plot_data['error']}")
                return
            
            # Store animation data and prepare timestamps
            self.anim_data = plot_data.get('animation_data', {})
            if self.anim_data:
                self.anim_data['lat_range'] = (lat_min, lat_max)
                self.anim_data['lon_range'] = (lon_min, lon_max)
                
                # Extract all timestamps and sort them
                timestamps = set()
                
                if 'tracks' in self.anim_data and self.anim_data['tracks'] is not None:
                    tracks_df = self.anim_data['tracks']
                    if 'timestamp' in tracks_df.columns:
                        timestamps.update(tracks_df['timestamp'])
                        
                if 'truth' in self.anim_data and self.anim_data['truth'] is not None:
                    truth_df = self.anim_data['truth']
                    if 'timestamp' in truth_df.columns:
                        timestamps.update(truth_df['timestamp'])
                
                self.anim_timestamps = sorted(list(timestamps))
                self.anim_max_frames = len(self.anim_timestamps)
                
                # Reset to first frame
                self.anim_current_frame.set(0)
                
                # Show initial frame
                self._update_animation_frame()
                
                # Enable playback controls
                self.play_btn.config(state="normal")
                self.stop_btn.config(state="normal")
                self.step_back_btn.config(state="normal")
                self.step_forward_btn.config(state="normal")
                
                self.logger.info(f"Animation prepared with {self.anim_max_frames} frames")
            else:
                self.logger.error("No animation data available")
            
        except Exception as e:
            self.logger.error(f"Error showing animation plot: {e}")
