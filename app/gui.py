"""
GUI launcher for EasyClaude.

Uses tkinter for a simple, always-on-top launcher window.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Callable, Optional
import os
import threading
import time


class LauncherGUI:
    """
    Main launcher GUI window.

    Features:
    - Always-on-top
    - Centered on screen
    - Directory picker + text entry
    - Command selection buttons
    - PowerShell checkbox
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
        self._current_window: Optional[tk.Tk] = None
        self._window_lock = threading.Lock()
        self._window_thread: Optional[threading.Thread] = None
        self._pending_show = False
        self._pending_directory = ""

    def show(self, initial_directory: str = ""):
        """
        Show the launcher window (thread-safe).

        If window is already open, this will update the directory and focus it.
        If window is closed or closing, this will open a new one.

        Args:
            initial_directory: Initial directory to display
        """
        with self._window_lock:
            # Check if there's already a window thread running
            if self._window_thread is not None and self._window_thread.is_alive():
                # Window is already open, just update the pending directory
                # The window will pick it up via polling
                self._pending_directory = initial_directory
                self._pending_show = True
                return

            # No window running, start a new one
            self._pending_directory = initial_directory
            self._pending_show = True
            self._window_thread = threading.Thread(
                target=self._run_window,
                daemon=False,  # Non-daemon to prevent premature termination
                name="GUIWindow"
            )
            self._window_thread.start()

    def _run_window(self):
        """Run the window in a dedicated thread."""
        # Must create Tk instance in the same thread that runs mainloop
        root = tk.Tk()
        root.title("EasyClaude")
        root.resizable(False, False)

        # Make always-on-top
        root.attributes('-topmost', True)

        # Center on screen
        root.update_idletasks()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        width = 500
        height = 350
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        root.geometry(f"{width}x{height}+{x}+{y}")

        # Main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="EasyClaude Launcher",
            font=("", 12, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 15))

        # Directory selection
        ttk.Label(main_frame, text="Directory:").grid(row=1, column=0, sticky=tk.W, pady=5)

        directory_var = tk.StringVar(value=self._pending_directory)
        dir_entry = ttk.Entry(main_frame, textvariable=directory_var, width=40)
        dir_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 5))

        def browse_directory():
            directory = filedialog.askdirectory(
                title="Select working directory",
                initialdir=directory_var.get() or os.getcwd()
            )
            if directory:
                directory_var.set(directory)

        browse_btn = ttk.Button(main_frame, text="Browse...", command=browse_directory, width=10)
        browse_btn.grid(row=1, column=2, sticky=tk.W, pady=5)

        # PowerShell checkbox
        powershell_var = tk.BooleanVar()
        ps_checkbox = ttk.Checkbutton(
            main_frame,
            text="Always use PowerShell",
            variable=powershell_var
        )
        ps_checkbox.grid(row=2, column=0, columnspan=3, pady=(15, 5))

        # Command buttons
        ttk.Label(main_frame, text="Command:").grid(row=3, column=0, sticky=tk.W, pady=(15, 5))

        cmd_frame = ttk.Frame(main_frame)
        cmd_frame.grid(row=4, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E))

        for i, command in enumerate(self.COMMANDS):
            btn = ttk.Button(
                cmd_frame,
                text=command,
                command=lambda c=command, r=root, dv=directory_var, pv=powershell_var: self._do_launch(r, c, dv, pv),
                width=35
            )
            btn.grid(row=i, column=0, pady=3)

        # Close button
        close_btn = ttk.Button(main_frame, text="Close", command=self._request_close, width=10)
        close_btn.grid(row=5, column=0, columnspan=3, pady=(10, 0))

        # Bind Enter key to first command, Escape to close
        root.bind('<Return>', lambda e: self._do_launch(root, self.COMMANDS[0], directory_var, powershell_var))
        root.bind('<Escape>', lambda e: self._request_close())

        # Store reference for update check
        with self._window_lock:
            self._current_window = root
            self._pending_show = False

        # Focus
        dir_entry.focus()
        dir_entry.select_range(0, tk.END)

        # Run the window (blocks until closed)
        try:
            root.mainloop()
        finally:
            # Cleanup
            with self._window_lock:
                self._current_window = None
                self._pending_show = False

    def _check_pending_updates(self, root: tk.Tk, directory_var: tk.StringVar):
        """Check for pending directory updates (called periodically)."""
        with self._window_lock:
            if self._pending_show and self._pending_directory:
                directory_var.set(self._pending_directory)
                self._pending_show = False
                root.lift()
                root.focus_force()

        # Schedule next check
        root.after(100, lambda: self._check_pending_updates(root, directory_var))

    def _do_launch(self, root: tk.Tk, command: str, directory_var: tk.StringVar, powershell_var: tk.BooleanVar):
        """
        Execute launch with current settings and close window.

        Args:
            root: The root window
            command: Command to execute
            directory_var: The directory variable
            powershell_var: The PowerShell checkbox variable
        """
        directory = directory_var.get().strip()

        if not directory:
            messagebox.showwarning(
                "No Directory",
                "Please select a directory first.",
                parent=root
            )
            return

        if not os.path.isdir(directory):
            messagebox.showerror(
                "Invalid Directory",
                f"The directory '{directory}' does not exist.",
                parent=root
            )
            return

        use_powershell = powershell_var.get()

        # Close the window immediately
        self._request_close()

        # Call the launch callback in a separate thread to avoid blocking
        if self._launch_callback:
            def run_callback():
                try:
                    self._launch_callback(directory, command, use_powershell)
                except Exception as e:
                    print(f"Error in launch callback: {e}")

            threading.Thread(target=run_callback, daemon=True).start()

    def _request_close(self):
        """Request the window to close (thread-safe)."""
        with self._window_lock:
            if self._current_window:
                # Schedule the close on the tkinter event loop
                self._current_window.after(0, self._current_window.destroy)

    def destroy(self):
        """Cleanup and close any open window."""
        self._request_close()
        # Wait for the window thread to finish
        if self._window_thread and self._window_thread.is_alive():
            self._window_thread.join(timeout=2.0)


__all__ = ["LauncherGUI"]
