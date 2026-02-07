"""
GUI launcher for EasyClaude.

Uses tkinter for a simple, always-on-top launcher window.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Callable, Optional
import os
import threading


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
        self._gui_thread: Optional[threading.Thread] = None
        self._running = False

    def show(self, initial_directory: str = ""):
        """
        Show the launcher window in a separate thread.

        Args:
            initial_directory: Initial directory to display
        """
        # Only one GUI at a time
        if self._running:
            return

        self._running = True

        def run_gui():
            try:
                self._show_window(initial_directory)
            finally:
                self._running = False

        # Start GUI in non-daemon thread so it doesn't get killed
        self._gui_thread = threading.Thread(target=run_gui, daemon=False)
        self._gui_thread.start()

    def _show_window(self, initial_directory: str):
        """Create and show the GUI window (runs in GUI thread)."""
        # Create new window
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

        directory_var = tk.StringVar(value=initial_directory)
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

        # Command buttons
        ttk.Label(main_frame, text="Command:").grid(row=2, column=0, sticky=tk.W, pady=(15, 5))

        cmd_frame = ttk.Frame(main_frame)
        cmd_frame.grid(row=3, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E))

        for i, command in enumerate(self.COMMANDS):
            btn = ttk.Button(
                cmd_frame,
                text=command,
                command=lambda c=command, r=root, dv=directory_var, pv=powershell_var: self._do_launch(r, c, dv, pv),
                width=35
            )
            btn.grid(row=i, column=0, pady=3)

        # PowerShell checkbox
        powershell_var = tk.BooleanVar()
        ps_checkbox = ttk.Checkbutton(
            main_frame,
            text="Always use PowerShell",
            variable=powershell_var
        )
        ps_checkbox.grid(row=4, column=0, columnspan=3, pady=(15, 10))

        # Close button
        close_btn = ttk.Button(main_frame, text="Close", command=root.destroy, width=10)
        close_btn.grid(row=5, column=0, columnspan=3, pady=(10, 0))

        # Bind Enter key to first command, Escape to close
        root.bind('<Return>', lambda e: self._do_launch(root, self.COMMANDS[0], directory_var, powershell_var))
        root.bind('<Escape>', lambda e: root.destroy())

        # Focus
        dir_entry.focus()

        # Run the window (blocks until closed)
        root.mainloop()

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

        # Call the launch callback
        if self._launch_callback:
            self._launch_callback(directory, command, use_powershell)

        # Close the window
        root.destroy()

    def destroy(self):
        """Cleanup."""
        self._running = False
