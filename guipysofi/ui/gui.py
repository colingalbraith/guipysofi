"""
GUI Module for GUIPySOFI.

This module contains the main SOFIGUI class that orchestrates the application.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
import threading

# Local imports
from guipysofi.core.data_manager import DataManager
from guipysofi.ui.visualizer import DataVisualizer
from guipysofi.utils.help import show_help, inspect_pysofi
from guipysofi.utils.compatibility import get_compatibility_report, check_pysofi_compatibility
from guipysofi.version import __version__ as VERSION


class SOFIGUI:
    """Main GUI class for the GUIPySOFI application."""
    
    def __init__(self, root):
        """
        Initialize the GUI.
        
        Args:
            root: The root tkinter window
        """
        self.root = root
        self.root.title("GUIPySOFI: An Open Source Graphical Extension to the PySOFI Analysis Tool")
        self.root.geometry("1200x900")
        self.root.configure(bg='#f0f0f0')
        
        # Check PySOFI compatibility
        self.pysofi_available, self.pysofi_authentic, self.pysofi_version, self.pysofi_details = check_pysofi_compatibility()
        
        # Initialize data manager
        self.data_manager = DataManager(
            status_callback=self.update_status,
            progress_callback=self.update_progress
        )
        
        # Set up styles
        self._setup_styles()
        
        # Create main UI structure
        self._create_ui_structure()
        
        # Set up event bindings
        self._setup_event_bindings()
        
        # Show PySOFI compatibility warning if necessary
        self._check_pysofi_on_startup()
    
    def _setup_styles(self):
        """Set up ttk styles for the application."""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Helvetica', 11))
        style.configure('TButton', font=('Helvetica', 11, 'bold'), padding=6)
        style.configure('TCheckbutton', background='#f0f0f0', font=('Helvetica', 11))
        style.configure('TLabelframe', background='#f0f0f0', font=('Helvetica', 11, 'bold'))
        style.configure('TLabelframe.Label', background='#f0f0f0', font=('Helvetica', 11, 'bold'))
        style.configure('TNotebook', background='#f0f0f0')
        style.configure('TNotebook.Tab', font=('Helvetica', 11), padding=[10, 5])
        style.configure('Accent.TButton', background="#4a86e8", foreground="#ffffff", font=('Helvetica', 11, 'bold'))
    
    def _create_ui_structure(self):
        """Create the UI structure."""
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="15")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self._create_header()
        
        # Main content
        paned = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Control panel
        self.control_frame = ttk.LabelFrame(paned, text="Analysis Controls", padding="10")
        paned.add(self.control_frame, weight=30)
        
        # Visualization panel
        viz_frame = ttk.Frame(paned)
        paned.add(viz_frame, weight=70)
        
        # Create controls
        self._create_file_input_controls()
        self._create_sofi_parameter_controls()
        self._create_advanced_options_controls()
        self._create_correction_controls()
        self._create_reconstruction_controls()
        self._create_action_buttons()
        
        # Create visualization tabs
        self._create_visualization_tabs(viz_frame)
        
        # Create status bar
        self._create_status_bar()
    
    def _create_header(self):
        """Create header section."""
        header_frame = ttk.Frame(self.main_frame, padding=10)
        header_frame.pack(fill=tk.X, pady=5)
        
        app_title = ttk.Label(
            header_frame, 
            text="GUIPySOFI", 
            font=('Helvetica', 18, 'bold')
        )
        app_title.pack(side=tk.LEFT)
        
        app_version = ttk.Label(
            header_frame, 
            text=f"v{VERSION}", 
            font=('Helvetica', 10)
        )
        app_version.pack(side=tk.LEFT, padx=5, pady=8)
        
        help_button = ttk.Button(
            header_frame, 
            text="Help", 
            command=self._show_help,
            style="Accent.TButton"
        )
        help_button.pack(side=tk.RIGHT)
        
        # Check for internal implementations
        internal_implementations = []
        for detail in self.pysofi_details:
            if "supported: No" in detail:
                feature = detail.split("supported")[0].strip()
                internal_implementations.append(feature)
        
        if internal_implementations:
            warning_frame = ttk.Frame(self.main_frame, padding=5)
            warning_frame.pack(fill=tk.X)
            
            warning_text = f"Note: Using internal implementations for: {', '.join(internal_implementations)}. Consider upgrading PySOFI package."
            warning_label = ttk.Label(
                warning_frame,
                text=warning_text,
                foreground='orange',
                font=('Helvetica', 9, 'italic')
            )
            warning_label.pack(fill=tk.X)
    
    def _create_file_input_controls(self):
        """Create file input controls."""
        file_frame = ttk.LabelFrame(self.control_frame, text="Data Input", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=30)
        file_entry.grid(row=0, column=0, sticky=tk.EW, padx=5, pady=5)
        
        browse_button = ttk.Button(file_frame, text="Browse...", command=self._load_file)
        browse_button.grid(row=0, column=1, padx=5, pady=5)
        
        drop_label = ttk.Label(file_frame, text="Drop TIFF stack here")
        drop_label.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Make drop targets
        self._make_drop_target(file_entry)
        self._make_drop_target(file_frame)
        self._make_drop_target(drop_label)
    
    def _create_sofi_parameter_controls(self):
        """Create SOFI parameter controls."""
        params_frame = ttk.LabelFrame(self.control_frame, text="SOFI Parameters", padding="10")
        params_frame.pack(fill=tk.X, pady=(0, 15))
        
        # SOFI Order
        order_frame = ttk.Frame(params_frame)
        order_frame.pack(fill=tk.X, pady=5)
        ttk.Label(order_frame, text="SOFI Order:").pack(side=tk.LEFT, padx=5)
        
        self.order_var = tk.IntVar(value=2)
        order_slider = ttk.Scale(
            order_frame, 
            from_=2, 
            to=8, 
            orient=tk.HORIZONTAL, 
            variable=self.order_var, 
            length=150
        )
        order_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.order_value_label = ttk.Label(order_frame, text="2")
        self.order_value_label.pack(side=tk.LEFT, padx=5)
        
        # Update label when order changes
        self.order_var.trace_add(
            "write", 
            lambda *args: self.order_value_label.config(text=str(int(self.order_var.get())))
        )
        
        # Frames to use
        frames_frame = ttk.Frame(params_frame)
        frames_frame.pack(fill=tk.X, pady=5)
        ttk.Label(frames_frame, text="Frames to use:").pack(side=tk.LEFT, padx=5)
        
        self.frames_var = tk.IntVar(value=200)
        ttk.Entry(frames_frame, textvariable=self.frames_var, width=10).pack(side=tk.LEFT, padx=5)
    
    def _create_advanced_options_controls(self):
        """Create advanced options controls."""
        adv_frame = ttk.LabelFrame(self.control_frame, text="Advanced Options", padding="10")
        adv_frame.pack(fill=tk.X, pady=(0, 15))
        
        method_frame = ttk.Frame(adv_frame)
        method_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(method_frame, text="Method:").pack(side=tk.LEFT, padx=5)
        self.method_var = tk.StringVar(value="xc")
        method_combo = ttk.Combobox(
            method_frame, 
            textvariable=self.method_var, 
            width=8, 
            values=("xc", "ac", "cc")
        )
        method_combo.pack(side=tk.LEFT, padx=5)
        
        # Check if PySOFI has weighting attribute
        has_weighting = False
        for detail in self.pysofi_details:
            if "Weighting attribute" in detail:
                has_weighting = "Present" in detail
        
        ttk.Label(method_frame, text="Weighting:").pack(side=tk.LEFT, padx=5)
        self.weight_var = tk.StringVar(value="none")
        weight_combo = ttk.Combobox(
            method_frame, 
            textvariable=self.weight_var, 
            width=10, 
            values=("none", "balanced", "tapered")
        )
        weight_combo.pack(side=tk.LEFT, padx=5)
        
        # Add note about weighting if not supported
        if not has_weighting:
            ttk.Label(
                adv_frame,
                text="Note: Weighting may not be supported in this PySOFI version",
                font=('Helvetica', 9),
                foreground='orange'
            ).pack(anchor=tk.W, padx=5, pady=(0, 5))
    
    def _create_correction_controls(self):
        """Create correction controls."""
        corr_frame = ttk.LabelFrame(self.control_frame, text="Corrections", padding="10")
        corr_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.bleach_var = tk.BooleanVar(value=False)
        bleach_button = ttk.Checkbutton(
            corr_frame, 
            text="Bleaching Correction", 
            variable=self.bleach_var
        )
        bleach_button.pack(anchor=tk.W, pady=5)
        
        # Add note about implementation
        use_package_bleach = any("Bleaching correction supported: Yes" in detail for detail in self.pysofi_details)
        if not use_package_bleach:
            ttk.Label(
                corr_frame,
                text="Note: Using internal implementation for bleaching correction",
                font=('Helvetica', 9),
                foreground='orange'
            ).pack(anchor=tk.W, padx=20)
        else:
            ttk.Label(
                corr_frame,
                text="Using PySOFI package implementation",
                font=('Helvetica', 9),
                foreground='green'
            ).pack(anchor=tk.W, padx=20)
        
        self.drift_var = tk.BooleanVar(value=False)
        drift_button = ttk.Checkbutton(
            corr_frame, 
            text="Drift Correction", 
            variable=self.drift_var
        )
        drift_button.pack(anchor=tk.W, pady=5)
        
        # Add note about implementation
        use_package_drift = any("Drift correction supported: Yes" in detail for detail in self.pysofi_details)
        if not use_package_drift:
            ttk.Label(
                corr_frame,
                text="Note: Using internal implementation for drift correction",
                font=('Helvetica', 9),
                foreground='orange'
            ).pack(anchor=tk.W, padx=20)
        else:
            ttk.Label(
                corr_frame,
                text="Using PySOFI package implementation",
                font=('Helvetica', 9),
                foreground='green'
            ).pack(anchor=tk.W, padx=20)
    
    def _create_reconstruction_controls(self):
        """Create reconstruction controls."""
        recon_frame = ttk.LabelFrame(self.control_frame, text="Reconstruction", padding="10")
        recon_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.deconv_var = tk.BooleanVar(value=False)
        deconv_button = ttk.Checkbutton(
            recon_frame, 
            text="Apply Deconvolution", 
            variable=self.deconv_var
        )
        deconv_button.pack(anchor=tk.W, pady=5)
        
        # Add note about implementation
        if not any("Deconvolution supported: Yes" in detail for detail in self.pysofi_details):
            ttk.Label(
                recon_frame,
                text="Note: Using internal implementation for deconvolution",
                font=('Helvetica', 9),
                foreground='blue'
            ).pack(anchor=tk.W, padx=20)
        
        # Add note about deconvolution requirements
        ttk.Label(
            recon_frame,
            text="Note: Requires 3rd-order or higher SOFI",
            font=('Helvetica', 9)
        ).pack(anchor=tk.W, padx=20)
    
    def _create_action_buttons(self):
        """Create action buttons."""
        action_frame = ttk.Frame(self.control_frame, padding="10")
        action_frame.pack(fill=tk.X, pady=10)
        
        self.run_button = ttk.Button(action_frame, text="Run SOFI Analysis", command=self._run_sofi)
        self.run_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        self.save_button = ttk.Button(action_frame, text="Save Results", command=self._save_result)
        self.save_button.pack(side=tk.RIGHT, padx=5, expand=True, fill=tk.X)
    
    def _create_visualization_tabs(self, viz_frame):
        """Create visualization tabs."""
        self.notebook = ttk.Notebook(viz_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Original Data Tab
        self.orig_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.orig_frame, text="Original Data")
        
        # SOFI Result Tab
        self.sofi_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.sofi_frame, text="SOFI Result")
        
        # Create visualizers
        self.orig_visualizer = DataVisualizer(self.orig_frame, is_sofi=False)
        self.sofi_visualizer = DataVisualizer(self.sofi_frame, is_sofi=True)
        
        # Add playback controls to original data visualizer
        self._add_playback_controls()
    
    def _add_playback_controls(self):
        """Add playback controls to the original data visualizer."""
        # Connect playback controls
        self.orig_visualizer.prev_button = ttk.Button(
            self.orig_visualizer.playback_frame, 
            text="◀", 
            command=self.orig_visualizer.prev_frame, 
            state=tk.DISABLED
        )
        self.orig_visualizer.prev_button.pack(side=tk.LEFT, padx=5)
        
        self.orig_visualizer.play_button = ttk.Button(
            self.orig_visualizer.playback_frame, 
            text="▶", 
            command=self.orig_visualizer.play_pause, 
            state=tk.DISABLED
        )
        self.orig_visualizer.play_button.pack(side=tk.LEFT, padx=5)
        
        self.orig_visualizer.next_button = ttk.Button(
            self.orig_visualizer.playback_frame, 
            text="▶▶", 
            command=self.orig_visualizer.next_frame, 
            state=tk.DISABLED
        )
        self.orig_visualizer.next_button.pack(side=tk.LEFT, padx=5)
        
        # Add slider
        self.orig_visualizer.frame_slider_var = tk.IntVar(value=0)
        self.orig_visualizer.frame_slider = ttk.Scale(
            self.orig_visualizer.playback_frame, 
            from_=0, 
            to=100, 
            orient=tk.HORIZONTAL,
            variable=self.orig_visualizer.frame_slider_var, 
            length=300, 
            state=tk.DISABLED
        )
        self.orig_visualizer.frame_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Connect slider events
        self.orig_visualizer.frame_slider.bind("<ButtonRelease-1>", self.orig_visualizer.on_slider_release)
        self.orig_visualizer.frame_slider.bind("<B1-Motion>", self.orig_visualizer.on_slider_motion)
        self.orig_visualizer.frame_slider.bind("<Button-1>", self.orig_visualizer.on_slider_press)
        
        # Add frame counter
        self.orig_visualizer.frame_counter = ttk.Label(self.orig_visualizer.playback_frame, text="0/0")
        self.orig_visualizer.frame_counter.pack(side=tk.LEFT, padx=5)
    
    def _create_status_bar(self):
        """Create status bar."""
        status_frame = ttk.Frame(self.main_frame, padding=5)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(status_frame, textvariable=self.status_var, anchor=tk.W).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )
        
        self.progress_var = tk.DoubleVar(value=0)
        ttk.Progressbar(status_frame, variable=self.progress_var, maximum=100, length=200).pack(
            side=tk.RIGHT, padx=5
        )
        
        debug_frame = ttk.Frame(self.main_frame)
        debug_frame.pack(fill=tk.X, side=tk.BOTTOM, before=status_frame, pady=5)
        
        ttk.Button(
            debug_frame, 
            text="Verify PySOFI Compatibility", 
            command=self._check_pysofi_compatibility,
            style="Accent.TButton"
        ).pack(side=tk.RIGHT, padx=10, pady=5)
        
        ttk.Button(
            debug_frame, 
            text="Inspect PySOFI Module", 
            command=self._inspect_pysofi,
            style="Accent.TButton"
        ).pack(side=tk.RIGHT, padx=10, pady=5)
    
    def _setup_event_bindings(self):
        """Set up event bindings."""
        # Window close event
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _make_drop_target(self, widget):
        """Make a widget a drop target for files."""
        widget.drop_target_register(DND_FILES)
        widget.dnd_bind('<<Drop>>', self._on_drop)
    
    def _on_drop(self, event):
        """Handle file drop event."""
        path = event.data
        if path.startswith('{') and path.endswith('}'):
            path = path[1:-1]
        if ' ' in path:
            path = path.split()[0]
        self.file_path_var.set(path)
        self._load_file_from_path(path)
    
    def _load_file(self):
        """Load a file using the file dialog."""
        file_path = filedialog.askopenfilename(
            title="Select your SOFI TIFF stack",
            filetypes=[("TIFF files", "*.tif *.tiff"), ("All files", "*.*")]
        )
        if file_path:
            self._load_file_from_path(file_path)
    
    def _load_file_from_path(self, file_path):
        """Load a file from a path."""
        self.file_path_var.set(file_path)
        
        try:
            # Check file size before loading
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if file_size_mb > 500:  # Limit to 500 MB files
                if not messagebox.askyesno(
                    "Large File Warning", 
                    f"The file is {file_size_mb:.1f} MB, which may cause memory issues.\nDo you want to continue?"
                ):
                    self.update_status("Loading cancelled")
                    return
            
            # Use the data manager to load the file
            success, message = self.data_manager.load_file(file_path)
            
            if not success:
                # Let the user decide if they want to try anyway
                if messagebox.askyesno("Warning", f"{message}\nDo you want to try anyway?"):
                    # Force loading
                    success, message = self.data_manager.load_file(file_path)
                    if not success:
                        messagebox.showerror("Error", message)
                        return
                else:
                    return
            
            # Set the data for the original visualizer
            self.orig_visualizer.set_data(self.data_manager.data)
            
            # Set the max frames for the UI
            self.frames_var.set(min(200, self.data_manager.total_frames))
            
            # Switch to original data tab
            self.notebook.select(self.orig_frame)
            
        except Exception as e:
            self.update_status(f"Error loading file: {str(e)}")
            messagebox.showerror("Error", f"Failed to load TIFF stack: {str(e)}")
            # Reset file path display
            self.file_path_var.set("")
    
    def _run_sofi(self):
        """Run SOFI analysis."""
        if self.data_manager.data is None:
            messagebox.showwarning("No Data", "Please load a TIFF stack first.")
            return
        
        # Disable run button
        self.run_button.configure(state=tk.DISABLED)
        
        try:
            # Get parameters
            parameters = {
                'order': self.order_var.get(),
                'frames': self.frames_var.get(),
                'method': self.method_var.get(),
                'weight': self.weight_var.get(),
                'bleach_correction': self.bleach_var.get(),
                'drift_correction': self.drift_var.get(),
                'deconvolution': self.deconv_var.get()
            }
            
            # Start a thread to run the analysis
            threading.Thread(target=self._run_sofi_thread, args=(parameters,), daemon=True).start()
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
            messagebox.showerror("Error", f"SOFI calculation failed: {str(e)}")
            self.run_button.configure(state=tk.NORMAL)
    
    def _run_sofi_thread(self, parameters):
        """Run SOFI analysis in a separate thread."""
        try:
            # Run SOFI calculation
            self.update_status("Running SOFI analysis...")
            
            # Create DataManager if not already existing
            if not hasattr(self, 'data_manager') or self.data_manager is None:
                self.data_manager = DataManager(
                    status_callback=self.update_status,
                    progress_callback=self.update_progress
                )
                
                # Load file if it hasn't been loaded already
                if not hasattr(self.data_manager, 'file_path') or not self.data_manager.file_path:
                    file_path = self.file_path_var.get()
                    if not file_path:
                        self.update_status("No file selected")
                        return
                        
                    success, message = self.data_manager.load_file(file_path)
                    if not success:
                        self.update_status(f"Failed to load file: {message}")
                        return
            
            # Run SOFI
            success, message, results = self.data_manager.run_sofi(parameters)
            
            # Update UI with results
            if success:
                self.update_status(message)
                if hasattr(self.data_manager, 'sofi_result'):
                    self.sofi_visualizer.set_data(
                        self.data_manager.sofi_result, 
                        is_sofi=True, 
                        order=parameters.get('order', 2)
                    )
                    self.notebook.select(1)  # Switch to SOFI result tab
                    self.save_button.configure(state=tk.NORMAL)
                else:
                    self.update_status("No SOFI result to display")
            else:
                self.update_status(f"SOFI analysis failed: {message}")
                
        except Exception as e:
            self.update_status(f"SOFI analysis error: {str(e)}")
        finally:
            # Re-enable run button
            self.run_button.configure(state=tk.NORMAL)
    
    def _save_result(self):
        """Save the SOFI result."""
        if self.data_manager.sofi_result is None:
            messagebox.showwarning("No Result", "Please run SOFI analysis first.")
            return
        
        save_path = filedialog.asksaveasfilename(
            title="Save SOFI result",
            defaultextension=".tif",
            filetypes=[("TIFF files", "*.tif"), ("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if not save_path:
            return
        
        # Save using the data manager
        success, message = self.data_manager.save_result(save_path)
        
        if not success:
            messagebox.showerror("Error", message)
    
    def _show_help(self):
        """Show help dialog."""
        show_help(self.root)
    
    def _inspect_pysofi(self):
        """Inspect PySOFI module to help with debugging."""
        inspect_pysofi(self.root)
        
    def _check_pysofi_compatibility(self):
        """Check PySOFI compatibility and show results."""
        report = get_compatibility_report()
        
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("PySOFI Compatibility Check")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            frame, 
            text="PySOFI Compatibility Report", 
            font=('Helvetica', 14, 'bold')
        ).pack(pady=(0,10))
        
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_area = tk.Text(
            text_frame, 
            wrap=tk.WORD, 
            yscrollcommand=scrollbar.set,
            font=('Courier', 10), 
            padx=10, 
            pady=10
        )
        text_area.insert(tk.END, report)
        text_area.config(state=tk.DISABLED)
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=text_area.yview)
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            button_frame, 
            text="Copy to Clipboard", 
            command=lambda: self.root.clipboard_append(report)
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            button_frame, 
            text="Close", 
            command=dialog.destroy
        ).pack(side=tk.RIGHT)
    
    def update_status(self, message):
        """Update status message."""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def update_progress(self, value):
        """Update progress bar."""
        self.progress_var.set(value)
        self.root.update_idletasks()
    
    def _on_close(self):
        """Handle window close event."""
        # Clean up resources
        try:
            # Stop any running threads
            if hasattr(self.orig_visualizer, 'is_playing') and self.orig_visualizer.is_playing:
                self.orig_visualizer.is_playing = False
                if self.orig_visualizer.play_thread:
                    self.orig_visualizer.play_thread = None
            
            # Close matplotlib figures
            if hasattr(self.orig_visualizer, 'fig'):
                self.orig_visualizer.fig.clf()
                plt.close(self.orig_visualizer.fig)
            
            if hasattr(self.sofi_visualizer, 'fig'):
                self.sofi_visualizer.fig.clf()
                plt.close(self.sofi_visualizer.fig)
            
        except Exception as e:
            print(f"Error cleaning up: {str(e)}")
        
        # Destroy the window
        self.root.destroy()
    
    def _check_pysofi_on_startup(self):
        """Check PySOFI compatibility on startup and show warnings if needed."""
        if not self.pysofi_available:
            messagebox.showerror(
                "PySOFI Not Found",
                "PySOFI module is not installed. GUIPySOFI requires PySOFI to function.\n\n"
                "Please install PySOFI with: pip install pysofi"
            )
            self.run_button.configure(state=tk.DISABLED)
            self.update_status("PySOFI is required - please install it to use GUIPySOFI")
            return
            
        if not self.pysofi_authentic:
            messagebox.showerror(
                "PySOFI Compatibility Issue",
                "The installed PySOFI package may not be authentic or compatible.\n\n"
                "Please install the official PySOFI package with: pip install pysofi"
            )
            self.run_button.configure(state=tk.DISABLED)
            self.update_status("Compatible PySOFI is required - please install the official package")
            return
        
        # Check for native vs internal implementations
        internal_implementations = []
        for detail in self.pysofi_details:
            if "supported: No" in detail:
                feature = detail.split("supported")[0].strip()
                internal_implementations.append(feature)
        
        if internal_implementations:
            self.update_status(f"Using PySOFI v{self.pysofi_version}")
            
            # Only show a message to inform about internal implementations
            messagebox.showinfo(
                "Feature Implementation",
                f"Your PySOFI version ({self.pysofi_version}) is missing some native features:\n" + 
                '\n'.join([f"- {f}" for f in internal_implementations]) + 
                "\n\nGUIPySOFI will use internal implementations for these features, but it is recommended to " +
                "upgrade your PySOFI package to get the official implementations which may provide better results."
            )
        else:
            self.update_status(f"Using PySOFI v{self.pysofi_version} - All features available natively") 