"""
GUI launcher for EasyClaude.

Uses tkinter for a simple, always-on-top launcher window.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Callable, Optional
import os
import threading
from pathlib import Path


class LauncherGUI:
    """
    Main launcher GUI window.

    Features:
    - Always-on-top
    - Centered on screen
    - Directory picker + text entry
    - Command selection buttons
    - PowerShell checkbox
    - Thread-safe GUI operations
    """

    # Available commands
    COMMANDS = [
        "claude",
        "claude --continue",
        "claude --dangerously-skip-permissions",
    ]

    def __init__(self, launch_callback: Callable[[str, str, bool], None]):
        """
        Initialize the launcher GUI.

        Args:
            launch_callback: Callback function(directory, command, use_powershell)
        """
        self._launch_callback = launch_callback
        self._root: Optional[tk.Tk] = None
        self._directory_var: Optional[tk.StringVar] = None
        self._powershell_var: Optional[tk.BooleanVar] = None
        self._selected_command: Optional[str] = None
        self._lock = threading.Lock()
        self._pending_show = None
        self._initial_directory = ""

    def _create_widgets(self):
        """Create all GUI widgets."""
        # Main frame with padding
        main_frame = ttk.Frame(
            self._root,
            padding="20"
        )
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Title
        title_label = ttk.Label(
            main_frame,
            text="EasyClaude Launcher",
            font=("", 12, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 15))

        # Directory selection
        dir_label = ttk.Label(main_frame, text="Directory:")
        dir_label.grid(row=1, column=0, sticky=tk.W, pady=5)

        self._directory_var = tk.StringVar()
        dir_entry = ttk.Entry(
            main_frame,
            textvariable=self._directory_var,
            width=40
        )
        dir_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 5))

        browse_btn = ttk.Button(
            main_frame,
            text="Browse...",
            command=self._browse_directory,
            width=10
        )
        browse_btn.grid(row=1, column=2, sticky=tk.W, pady=5)

        # Command buttons
        cmd_label = ttk.Label(main_frame, text="Command:")
        cmd_label.grid(row=2, column=0, sticky=tk.W, pady=(15, 5))

        cmd_frame = ttk.Frame(main_frame)
        cmd_frame.grid(row=3, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E))

        for i, command in enumerate(self.COMMANDS):
            btn = ttk.Button(
                cmd_frame,
                text=command,
                command=lambda c=command: self._launch(c),
                width=35
            )
            btn.grid(row=i, column=0, pady=3)

        # PowerShell checkbox
        self._powershell_var = tk.BooleanVar()
        ps_checkbox = ttk.Checkbutton(
            main_frame,
            text="Always use PowerShell",
            variable=self._powershell_var
        )
        ps_checkbox.grid(row=4, column=0, columnspan=3, pady=(15, 10))

        # Close button
        close_btn = ttk.Button(
            main_frame,
            text="Close",
            command=self.hide,
            width=10
        )
        close_btn.grid(row=5, column=0, columnspan=3, pady=(10, 0))

        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        self._root.columnconfigure(0, weight=1)
        self._root.rowconfigure(0, weight=1)

        # Bind Enter key
        self._root.bind('<Return>', lambda e: self._launch(self.COMMANDS[0]))
        self._root.bind('<Escape>', lambda e: self.hide())

    def _browse_directory(self):
        """Open directory picker dialog."""
        directory = filedialog.askdirectory(
            title="Select working directory",
            initialdir=self._directory_var.get() or os.getcwd()
        )
        if directory:
            self._directory_var.set(directory)

    def _launch(self, command: str):
        """
        Execute launch with current settings.

        Args:
            command: Command to execute
        """
        directory = self._directory_var.get().strip()

        if not directory:
            messagebox.showwarning(
                "No Directory",
                "Please select a directory first.",
                parent=self._root
            )
            return

        if not os.path.isdir(directory):
            messagebox.showerror(
                "Invalid Directory",
                f"The directory '{directory}' does not exist.",
                parent=self._root
            )
            return

        use_powershell = self._powershell_var.get()

        # Call the launch callback
        if self._launch_callback:
            self._launch_callback(directory, command, use_powershell)
            self.hide()

    def show(self, initial_directory: str = ""):
        """
        Show the launcher window.

        Thread-safe: Can be called from any thread.

        Args:
            initial_directory: Initial directory to display
        """
        with self._lock:
            self._pending_show = initial_directory or self._initial_directory

        if self._root is None:
            self._create_window()
            # Start the tkinter event loop in a separate thread
            self._start_event_loop()

        # Schedule the show operation on the main thread
        if self._root:
            self._root.after(0, self._show_on_main_thread)

    def _show_on_main_thread(self):
        """Show the window - must be called from the main tkinter thread."""
        with self._lock:
            initial_directory = self._pending_show
            self._pending_show = None

        if initial_directory:
            self._directory_var.set(initial_directory)

        # Make sure window is visible (deiconify in case it was withdrawn)
        self._root.deiconify()

        # Center window on screen
        self._center_window()

        # Bring to front and focus
        self._root.lift()
        self._root.attributes('-topmost', True)
        self._root.after_idle(lambda: self._root.attributes('-topmost', False))
        self._root.focus_force()

    def _start_event_loop(self):
        """Start the tkinter event loop in a separate thread."""
        def run_loop():
            try:
                self._root.mainloop()
            except Exception as e:
                # Log error but don't crash
                pass

        thread = threading.Thread(target=run_loop, daemon=True)
        thread.start()

    def hide(self):
        """Hide the launcher window (thread-safe)."""
        if self._root:
            # Schedule hide on main thread
            self._root.after(0, self._root.withdraw)

    def _create_window(self):
        """Create the main window."""
        self._root = tk.Tk()
        self._root.title("EasyClaude")
        self._root.resizable(False, False)

        # Make window always-on-top when shown
        self._root.attributes('-topmost', True)

        # Create widgets
        self._create_widgets()

    def _center_window(self):
        """Center the window on the screen."""
        if self._root is None:
            return

        self._root.update_idletasks()

        # Get window dimensions
        width = self._root.winfo_width()
        height = self._root.winfo_height()

        # Get screen dimensions
        screen_width = self._root.winfo_screenwidth()
        screen_height = self._root.winfo_screenheight()

        # Calculate position
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        # Position window
        self._root.geometry(f"+{x}+{y}")

    def destroy(self):
        """Destroy the window and cleanup."""
        if self._root:
            self._root.destroy()
            self._root = None
