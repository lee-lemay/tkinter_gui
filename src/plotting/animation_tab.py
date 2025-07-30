"""
Animation tab widget for the data analysis application.

This module provides the Animation tab widget that extends the base PlotTabWidget
with animation-specific functionality and controls.
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Any, Dict
import logging

from .widgets import PlotTabWidget
from .backends import PlotBackend
from .control_widgets import CoordinateRangeWidget, DataSelectionWidget, PlaybackControlWidget


class AnimationTabWidget(PlotTabWidget):
    """
    Animation tab widget for creating animated visualizations of track data.
    
    This widget provides controls for animation playback, coordinate range selection,
    and various animation visualization options.
    """
    
    def __init__(self, parent: tk.Widget, backend: PlotBackend):
        """
        Initialize the animation tab widget.
        
        Args:
            parent: Parent widget
            backend: Plot backend to use
        """        
        # Animation state
        self.is_playing = False
        self.current_frame = 0
        self.total_frames = 0
        self.animation_speed_var = tk.DoubleVar(value=1.0)
        self.track_selection_var = ["All"]
        self.truth_selection_var = ["All"]
        
        # Initialize control widgets
        self.coord_range_widget = None
        self.playback_widget = None
        
        super().__init__(parent, backend, "Animation")
        
        # Show initial plot following template pattern
        self._show_initial_plot()
    
    def _create_controls(self):
        """Create animation-specific control widgets."""
        # Add track and truth selection widget
        self.data_selection_widget = DataSelectionWidget(self.control_frame)
        self.data_selection_widget.pack(fill="x", padx=5, pady=5)
        self.data_selection_widget.set_tracks_callback(self._on_track_data_selection_changed)
        self.data_selection_widget.set_truth_callback(self._on_truth_data_selection_changed)
        
        controls_frame = ttk.Frame(self.control_frame)
        controls_frame.pack(fill="x", padx=5, pady=5)

        # Add coordinate range widget
        self.coord_range_widget = CoordinateRangeWidget(
            controls_frame,
            title="Animation Bounds"
        )
        self.coord_range_widget.pack(side="left", fill="both", expand=True, padx=(0, 5), pady=5)
        self.coord_range_widget.set_range_callback(self._on_coord_range_changed)
        self.coord_range_widget.set_reset_callback(self._on_reset_bounds)
        
        # Add playback control widget
        self.playback_widget = PlaybackControlWidget(controls_frame)
        self.playback_widget.pack(side="right", fill="y", padx=(5,0), pady=5)
        self.playback_widget.set_play_callback(self._on_play)
        self.playback_widget.set_pause_callback(self._on_pause)
        self.playback_widget.set_stop_callback(self._on_stop)
        self.playback_widget.set_step_callback(self._on_step)
        self.playback_widget.set_speed_callback(self._on_speed_callback_changed)   

    def _propagate_controller_to_widgets(self):
        """Propagate controller to child widgets."""
        if hasattr(self, 'data_selection_widget') and self.controller:
            if self.data_selection_widget:
                self.data_selection_widget.set_controller(self.controller)
    
    def _on_track_data_selection_changed(self, selection: List[str]):
        """Handle data selection changes."""
        self.logger.debug(f"Data selection changed: {selection}")
        self.track_selection_var = selection
        self._on_setup_animation()
    
    def _on_truth_data_selection_changed(self, selection: List[str]):
        """Handle data selection changes."""
        self.logger.debug(f"Data selection changed: {selection}")
        self.truth_selection_var = selection
        self._on_setup_animation()
    
    def _on_coord_range_changed(self, ranges: Dict[str, tuple]):
        """Handle coordinate range changes."""
        self.logger.debug(f"Coordinate ranges changed: {ranges}")
        self.lon_range = ranges.get('lon_range', (-1.0, 1.0))
        self.lat_range = ranges.get('lat_range', (-1.0, 1.0))
    
    def _on_reset_bounds(self):
        """Handle reset bounds button click."""
        self.logger.debug("Resetting animation bounds")
        # Reset to default bounds and update animation
        if self.coord_range_widget:
            
            if self.original_animation_data:
                self.lat_range = self.original_animation_data.get('lat_range', (-1.0, 1.0))
                self.lon_range = self.original_animation_data.get('lon_range', (-1.0, 1.0))
            else:
                self.lat_range = (-1.0, 1.0)
                self.lon_range = (-1.0, 1.0)
                    
            self.coord_range_widget.set_ranges(self.lat_range, self.lon_range)
            if self.is_playing:
                self._update_current_frame()
    
    def _on_play(self):
        """Handle play button click."""
        self.logger.debug("Animation play button clicked")
        self.is_playing = True
        self._start_animation()
    
    def _start_animation(self):
        """Start the animation playback."""
        if self.total_frames == 0:
            self.logger.warning("No animation frames available")
            return
        
        try:
            if self.playback_widget:        
              self.playback_widget.play_btn.config(state="disabled")
              self.playback_widget.pause_btn.config(state="normal")
              self.playback_widget.stop_btn.config(state="normal")
              self.playback_widget.step_back_btn.config(state="disabled")
              self.playback_widget.step_forward_btn.config(state="disabled")
        except Exception as e:
            self.logger.error(f"Error updating playback controls: {e}")
        
        # Start animation loop
        self._animation_loop()
    
    def _on_pause(self):
        """Handle pause button click."""
        self.logger.debug("Animation pause button clicked")
        self._pause_animation()
    
    def _pause_animation(self):
        """Pause the animation playback."""
        # Animation loop will check is_playing flag
        self.is_playing = False
        
        try:
          if self.playback_widget:        
            self.playback_widget.play_btn.config(state="normal")
            self.playback_widget.pause_btn.config(state="disabled")
            self.playback_widget.stop_btn.config(state="normal")
            self.playback_widget.step_back_btn.config(state="normal")
            self.playback_widget.step_forward_btn.config(state="normal")
        except Exception as e:
            self.logger.error(f"Error updating playback controls: {e}")
    
    def _on_stop(self):
        """Handle stop button click."""
        self.logger.debug("Animation stopped")
        self.is_playing = False
        self.current_frame = 0
        try:
          if self.playback_widget:        
            self.playback_widget.play_btn.config(state="normal")
            self.playback_widget.pause_btn.config(state="disabled")
            self.playback_widget.stop_btn.config(state="disabled")
            self.playback_widget.step_back_btn.config(state="normal")
            self.playback_widget.step_forward_btn.config(state="normal")
        except Exception as e:
            self.logger.error(f"Error updating playback controls: {e}")
        self._update_current_frame()
    
    def _on_step(self, direction: int):
        """Handle step forward/backward button clicks."""
        direction_str = "forward" if direction > 0 else "backward"
        self.logger.debug(f"Animation step {direction_str}")
        
        if direction > 0 and self.current_frame < self.total_frames - 1:
            self.current_frame += 1
        elif direction < 0 and self.current_frame > 0:
            self.current_frame -= 1
        
        self._update_current_frame()
        
        if self.playback_widget:
            self.playback_widget.set_current_frame(self.current_frame)
    
    def _on_speed_callback_changed(self, speed: float):
        """Handle animation speed changes from playback widget."""
        self.logger.debug(f"Animation speed changed to: {speed}")
        self.animation_speed_var.set(speed)
    
    def _on_animation_settings(self):
        """Handle animation settings button click."""
        try:
            # Create a simple settings dialog
            settings_window = tk.Toplevel(self.winfo_toplevel())
            settings_window.title("Animation Settings")
            settings_window.geometry("300x200")
            
            # Add some basic settings
            ttk.Label(settings_window, text="Frame Rate (FPS):").pack(pady=5)
            fps_var = tk.IntVar(value=30)
            fps_spin = ttk.Spinbox(settings_window, from_=1, to=60, textvariable=fps_var)
            fps_spin.pack(pady=5)
            
            ttk.Label(settings_window, text="Resolution:").pack(pady=5)
            res_var = tk.StringVar(value="1920x1080")
            res_combo = ttk.Combobox(settings_window, textvariable=res_var,
                                   values=["1920x1080", "1280x720", "800x600"])
            res_combo.pack(pady=5)
            
            # OK button
            ok_btn = ttk.Button(settings_window, text="OK", 
                              command=settings_window.destroy)
            ok_btn.pack(pady=20)
            
        except Exception as e:
            self.logger.error(f"Error opening settings: {e}")
    
    def _on_setup_animation(self):
        """Setup the animation with current settings."""
        try:

            if hasattr(self, 'data_selection_widget') and self.data_selection_widget:
                # Get selected tracks and truth from the widget
                # You'll need to implement methods in DataSelectionWidget to return these
                self.track_selection_var = self.data_selection_widget.get_selected_tracks()
                self.truth_selection_var = self.data_selection_widget.get_selected_truth()

            config = {
                'tracks': self.track_selection_var,  # Can be "All", "None", or list of track_ids
                'truth': self.truth_selection_var     # Can be "All", "None", or list of truth ids
            }

            plot_data = None
            if self.plot_manager and self.controller:
                app_state = self.controller.get_state()
                plot_data = self.plot_manager.prepare_plot_data('lat_lon_animation', app_state, config)
            
            # Setup the animation if we have data
            if plot_data and 'error' not in plot_data:
                # Store original animation data for frame filtering
                self.original_animation_data = plot_data.get('animation_data', {})

                # Set coordinate ranges from calculated data
                self.lat_range = plot_data.get('lat_range')
                self.lon_range = plot_data.get('lon_range')
                
                if self.lat_range and self.lon_range and hasattr(self, 'coord_range_widget'):
                    if self.coord_range_widget:
                        self.coord_range_widget.set_ranges(self.lat_range, self.lon_range)

                animation_data = plot_data.get('animation_data', {})
    
                # Extract all unique timestamps for frame calculation
                all_timestamps = set()
                
                if animation_data.get('tracks') is not None:
                    tracks_df = animation_data['tracks']
                    if 'timestamp' in tracks_df.columns:
                        all_timestamps.update(tracks_df['timestamp'])
                
                if animation_data.get('truth') is not None:
                    truth_df = animation_data['truth']
                    if 'timestamp' in truth_df.columns:
                        all_timestamps.update(truth_df['timestamp'])
                
                # Sort timestamps for frame sequence
                sorted_timestamps = sorted(list(all_timestamps))
                self.total_frames = len(sorted_timestamps)
                self.animation_timestamps = sorted_timestamps  # Store for frame filtering
                self.current_frame = 0
                
                # Update playback widget
                if self.playback_widget:
                    self.playback_widget.set_total_frames(self.total_frames)
                    self.playback_widget.set_current_frame(0)
                
                # Create initial frame
                config = {
                    'title': plot_data.get('title', 'Animation')
                }
                
                self.update_plot('lat_lon_animation', plot_data, config)
                self.logger.debug("Animation setup completed successfully")
            else:
                self.logger.debug("No valid data for animation setup")
                self.clear_plot()
                
        except Exception as e:
            self.logger.error(f"Error setting up animation: {e}")
            self.clear_plot()
    
    def _animation_loop(self):
        """Main animation loop."""
        if not self.is_playing:
            return
        
        # Update to next frame
        self.current_frame = (self.current_frame + 1) % self.total_frames
        self._update_current_frame()
        
        # Update playback widget
        if self.playback_widget:
            self.playback_widget.set_current_frame(self.current_frame)
        
        # Schedule next frame
        delay = int(1000 / (30 * self.animation_speed_var.get())) 
        self.after(delay, self._animation_loop)
    
    def _update_current_frame(self):
        """Update the display for the current frame."""
        try:
            if not hasattr(self, 'animation_timestamps') or self.current_frame >= len(self.animation_timestamps):
                return
            
            current_timestamp = self.animation_timestamps[self.current_frame]
        
            # Get the original animation data
            # You'll need to store this from _on_setup_animation()
            if hasattr(self, 'original_animation_data'):
                filtered_data = self._filter_data_to_timestamp(current_timestamp)
                
                config = {
                    'title': f'Animation Frame {self.current_frame + 1}/{self.total_frames}',
                    'frame': self.current_frame,
                    'current_frame': self.current_frame,
                    'total_frames': self.total_frames 
                }
                
                self.update_plot('animation_frame', filtered_data, config)
            
        except Exception as e:
            self.logger.error(f"Error updating frame: {e}")

    def _filter_data_to_timestamp(self, current_timestamp):
        """Filter animation data to show only data up to current timestamp."""
        filtered_data = {
            'animation_data': {
                'tracks': None,
                'truth': None,
                'time_range': self.original_animation_data.get('time_range', {}),
                'lat_range': self.lat_range,
                'lon_range': self.lon_range
            },
            'current_time': current_timestamp
        }
        
        # Filter tracks
        if self.original_animation_data.get('tracks') is not None:
            tracks_df = self.original_animation_data['tracks']
            filtered_tracks = tracks_df[tracks_df['timestamp'] <= current_timestamp]
            filtered_data['animation_data']['tracks'] = filtered_tracks
        
        # Filter truth
        if self.original_animation_data.get('truth') is not None:
            truth_df = self.original_animation_data['truth']
            filtered_truth = truth_df[truth_df['timestamp'] <= current_timestamp]
            filtered_data['animation_data']['truth'] = filtered_truth
        
        # Include coordinate ranges
        if hasattr(self, 'coord_range_widget'):
            if self.coord_range_widget:
              ranges = self.coord_range_widget.get_ranges()
              filtered_data['lat_range'] = ranges.get('lat_range')
              filtered_data['lon_range'] = ranges.get('lon_range')
        
        return filtered_data
    
    def auto_update(self):
        """Auto-update the animation when data changes."""
        self.logger.debug("Auto-updating animation")
        # Stop current animation and setup new one
        self.is_playing = False
        self._on_setup_animation()
    
    def should_auto_update(self, focus_info: Any) -> bool:
        """
        Check if this tab should auto-update.
        
        Animation tab should auto-update when datasets change,
        but only if not currently playing.
        """
        return not self.is_playing
    
    def _show_initial_plot(self):
        """Show initial plot when tab is first displayed."""
        self._on_setup_animation()
