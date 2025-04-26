"""
Visualization Module for GUIPySOFI.

This module handles visualization of original data and SOFI results.
"""

import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import threading
import time
import gc


class DataVisualizer:
    """Handles visualization of TIFF stacks and SOFI results."""
    
    def __init__(self, parent_frame, is_sofi=False):
        """
        Initialize the visualizer.
        
        Args:
            parent_frame: The tkinter frame to use for display
            is_sofi: Boolean indicating if this visualizer is for SOFI results
        """
        self.parent_frame = parent_frame
        self.is_sofi = is_sofi
        self.data = None
        self.current_frame = 0
        self.total_frames = 0
        self.is_playing = False
        self.play_thread = None
        self.play_thread_id = None
        self.colorbar = None
        
        # Create figure with fixed size
        if is_sofi:
            self.fig = plt.figure(figsize=(6, 6), dpi=100)
            self.fig.subplots_adjust(right=0.85)  # Make room for colorbar
        else:
            self.fig = plt.figure(figsize=(6, 6), dpi=100)
        
        self.ax = self.fig.add_subplot(111)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        
        # Frame counter and playback controls (for stack visualizer only)
        if not is_sofi:
            # Add playback frame and controls
            self.playback_frame = tk.Frame(parent_frame)
            self.playback_frame.pack(fill=tk.X, pady=10)
            
            # Will be populated by UI initializer
            self.prev_button = None
            self.play_button = None
            self.next_button = None
            self.frame_slider = None
            self.frame_counter = None
            self.slider_update_id = None
            
        # Initialize empty image for SOFI result
        if is_sofi:
            zeros = np.zeros((10, 10))
            self.im = self.ax.imshow(zeros, cmap='viridis')
            self.ax.set_title("No SOFI result yet")
            self.colorbar = self.fig.colorbar(self.im, ax=self.ax, shrink=0.8)
            self.colorbar.set_label('Intensity', rotation=270, labelpad=15)
        else:
            self.im = None
        
        self.ax.axis('off')
        
        # Add toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, parent_frame)
        self.toolbar.update()
        
        # Pack canvas
        if not is_sofi:
            self.canvas_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        else:
            self.canvas_widget.pack(fill=tk.BOTH, expand=True)
    
    def display_frame(self, idx):
        """
        Display a specific frame from the data.
        
        Args:
            idx: Frame index to display
        """
        if self.data is None or not hasattr(self, 'total_frames') or self.total_frames == 0:
            return
        
        if not (0 <= idx < self.total_frames):
            return
        
        self.current_frame = idx
        
        self.ax.clear()
        
        if self.is_sofi:
            # Display SOFI result (single frame)
            if self.im is None or self.im.axes is None:
                self.im = self.ax.imshow(self.data, cmap='viridis')
                if self.colorbar is not None:
                    try:
                        self.colorbar.remove()
                    except:
                        pass
                self.colorbar = self.fig.colorbar(self.im, ax=self.ax, shrink=0.8)
                self.colorbar.set_label('Intensity', rotation=270, labelpad=15)
            else:
                self.im.set_data(self.data)
                self.im.set_clim(vmin=np.min(self.data), vmax=np.max(self.data))
            
            self.ax.set_title("SOFI Result")
        else:
            # Display frame from original data
            self.ax.imshow(self.data[idx], cmap='gray')
            self.ax.set_title(f"Frame {idx+1}/{self.total_frames}")
            
            # Update frame counter if it exists
            if hasattr(self, 'frame_counter') and self.frame_counter:
                self.frame_counter.configure(text=f"{idx+1}/{self.total_frames}")
        
        self.ax.axis('off')
        self.canvas.draw_idle()
    
    def set_data(self, data, order=None, method=None, frames=None):
        """
        Set the data to visualize.
        
        Args:
            data: Numpy array containing the data
            order: SOFI order (for SOFI results only)
            method: SOFI method (for SOFI results only)
            frames: Number of frames used (for SOFI results only)
        """
        self.data = data
        
        if self.is_sofi:
            # Normalize result for display
            result = self.data.copy()
            if np.any(~np.isfinite(result)):
                result[~np.isfinite(result)] = 0
            
            # Scale to 0-1 range for display
            if np.max(result) > np.min(result):
                result = (result - np.min(result)) / (np.max(result) - np.min(result))
            
            self.data = result
            
            # Update title with metadata if provided
            title = "SOFI Result"
            if order is not None and method is not None and frames is not None:
                title = f"{order}-Order SOFI ({method}, {frames} frames)"
            
            # Update display
            self.ax.clear()
            self.im = self.ax.imshow(self.data, cmap='viridis')
            
            # Update colorbar
            if self.colorbar is not None:
                try:
                    self.colorbar.remove()
                except:
                    pass
            self.colorbar = self.fig.colorbar(self.im, ax=self.ax, shrink=0.8)
            self.colorbar.set_label('Intensity', rotation=270, labelpad=15)
            
            self.ax.set_title(title)
            self.ax.axis('off')
            self.canvas.draw()
        else:
            # For original data stack
            self.total_frames = data.shape[0]
            self.current_frame = 0
            
            # Enable controls
            if hasattr(self, 'prev_button') and self.prev_button:
                self.prev_button.configure(state=tk.NORMAL)
                self.play_button.configure(state=tk.NORMAL)
                self.next_button.configure(state=tk.NORMAL)
                self.frame_slider.configure(from_=0, to=self.total_frames-1, state=tk.NORMAL)
                self.frame_slider.set(0)
            
            # Display first frame
            self.display_frame(0)
    
    def play_pause(self):
        """Toggle playback of the stack."""
        if not hasattr(self, 'play_button') or not self.play_button:
            return
            
        if self.is_playing:
            self.is_playing = False
            self.play_button.configure(text="▶")
            self.play_thread = None
        else:
            self.is_playing = True
            self.play_button.configure(text="⏸")
            self.play_thread = threading.Thread(target=self.play_animation)
            self.play_thread.daemon = True
            self.play_thread.start()
    
    def play_animation(self):
        """Animation playback thread."""
        parent_widget = self.parent_frame.winfo_toplevel()
        current = self.current_frame
        thread_id = time.time()
        self.play_thread_id = thread_id
        
        try:
            while self.is_playing and current < self.total_frames - 1 and parent_widget.winfo_exists():
                if self.play_thread_id != thread_id:
                    break
                    
                current += 1
                self.current_frame = current
                
                # Update UI in the main thread
                parent_widget.after(0, lambda f=current: self.update_ui_for_frame(f))
                
                # Control playback speed
                time.sleep(0.1)
                
                # Periodically force garbage collection
                if current % 20 == 0:
                    gc.collect()
                
            # If we reached the end of the stack, reset the play button
            if current >= self.total_frames - 1 and parent_widget.winfo_exists():
                parent_widget.after(0, lambda: self.play_button.configure(text="▶"))
                self.is_playing = False
        except Exception as e:
            print(f"Play animation error: {str(e)}")
            self.is_playing = False
    
    def update_ui_for_frame(self, frame_idx):
        """Update UI elements for the given frame index."""
        if hasattr(self, 'frame_slider') and self.frame_slider:
            self.frame_slider.set(frame_idx)
        self.display_frame(frame_idx)
    
    def prev_frame(self):
        """Display the previous frame."""
        self.current_frame = max(0, self.current_frame - 1)
        if hasattr(self, 'frame_slider') and self.frame_slider:
            self.frame_slider.set(self.current_frame)
        self.display_frame(self.current_frame)
    
    def next_frame(self):
        """Display the next frame."""
        self.current_frame = min(self.total_frames - 1, self.current_frame + 1)
        if hasattr(self, 'frame_slider') and self.frame_slider:
            self.frame_slider.set(self.current_frame)
        self.display_frame(self.current_frame)
    
    def on_slider_press(self, event=None):
        """Handle slider press event."""
        if not hasattr(self, 'frame_slider') or not self.frame_slider:
            return
            
        idx = int(self.frame_slider.get())
        if 0 <= idx < self.total_frames and hasattr(self, 'frame_counter') and self.frame_counter:
            self.frame_counter.configure(text=f"{idx+1}/{self.total_frames}")
    
    def on_slider_motion(self, event=None):
        """Handle slider motion event."""
        if not hasattr(self, 'frame_slider') or not self.frame_slider:
            return
            
        if self.slider_update_id:
            parent_widget = self.parent_frame.winfo_toplevel()
            parent_widget.after_cancel(self.slider_update_id)
            
        parent_widget = self.parent_frame.winfo_toplevel()
        self.slider_update_id = parent_widget.after(10, self._update_frame_from_slider)
        
        idx = int(self.frame_slider.get())
        if 0 <= idx < self.total_frames and hasattr(self, 'frame_counter') and self.frame_counter:
            self.frame_counter.configure(text=f"{idx+1}/{self.total_frames}")
    
    def on_slider_release(self, event=None):
        """Handle slider release event."""
        if not hasattr(self, 'frame_slider') or not self.frame_slider:
            return
            
        parent_widget = self.parent_frame.winfo_toplevel()
            
        if self.slider_update_id:
            parent_widget.after_cancel(self.slider_update_id)
            self.slider_update_id = None
            
        idx = int(self.frame_slider.get())
        if 0 <= idx < self.total_frames:
            self.current_frame = idx
            self.display_frame(idx)
    
    def _update_frame_from_slider(self):
        """Update the displayed frame based on the slider position."""
        self.slider_update_id = None
        if not hasattr(self, 'frame_slider') or not self.frame_slider:
            return
            
        idx = int(self.frame_slider.get())
        if 0 <= idx < self.total_frames:
            self.current_frame = idx
            self.display_frame(idx) 