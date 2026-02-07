"""
GUI launcher for EasyClaude.

Compact, thread-safe Tkinter UI for selecting a directory and command.
"""

from __future__ import annotations

import logging
import os
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Callable, Optional

from . import config

logger = logging.getLogger(__name__)


class LauncherGUI:
    """
    Main launcher GUI window.

    Designed to stay compact and readable without control overflow.
    """

    COMMANDS = [
        "claude",
        "claude --continue",
        "claude --dangerously-skip-permissions",
    ]

    COMMON_COMMANDS = [
        "claude",
        "claude --continue",
        "claude --dangerously-skip-permissions",
        "claude --continue --dangerously-skip-permissions",
        "claude --plan",
    ]

    def __init__(self, launch_callback: Callable[[str, str], None]):
        self._launch_callback = launch_callback
        self._root: Optional[tk.Tk] = None
        self._lock = threading.Lock()
        self._initialized = False
        self._command_queue: queue.Queue = queue.Queue()
        self._launch_threads: list[threading.Thread] = []

    def _ensure_initialized(self) -> None:
        """Ensure the GUI is created once on the main thread."""
        if self._initialized:
            return

        with self._lock:
            if self._initialized:
                return

            self._root = tk.Tk()
            self._root.title("EasyClaude")
            self._root.resizable(False, False)
            self._root.withdraw()
            self._root.attributes("-topmost", True)

            self._configure_styles()
            self._build_layout()
            self._center_window(width=560, height=400)

            self._root.bind("<Return>", lambda e: self._launch_custom_command())
            self._root.bind("<Escape>", lambda e: self.hide())
            self._root.bind("<Alt-d>", lambda e: self._focus_directory_field())
            self._root.bind("<Alt-D>", lambda e: self._focus_directory_field())
            self._root.protocol("WM_DELETE_WINDOW", self.hide)

            self._process_command_queue()
            self._initialized = True

    def _configure_styles(self) -> None:
        """Set consistent compact styling for controls."""
        if not self._root:
            return
        style = ttk.Style(self._root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("EC.TFrame", padding=0)
        style.configure("EC.TLabel", font=("Segoe UI", 10))
        style.configure("EC.Subtle.TLabel", font=("Segoe UI", 9))
        style.configure("EC.TButton", font=("Segoe UI", 9), padding=(10, 6))
        style.configure("EC.Primary.TButton", font=("Segoe UI Semibold", 9), padding=(12, 7))
        style.configure("EC.TCheckbutton", font=("Segoe UI", 9))
        style.configure("EC.TEntry", font=("Segoe UI", 10))
        style.configure("EC.TCombobox", font=("Segoe UI", 10))

    def _build_layout(self) -> None:
        """Build a compact grid-based UI without fixed oversized controls."""
        if not self._root:
            return

        self._root.columnconfigure(0, weight=1)
        self._root.rowconfigure(0, weight=1)

        main = ttk.Frame(self._root, style="EC.TFrame", padding=14)
        main.grid(row=0, column=0, sticky="nsew")
        main.columnconfigure(0, weight=1)

        heading = ttk.Label(main, text="Launch Claude", style="EC.TLabel")
        heading.grid(row=0, column=0, sticky="w")

        dir_label = ttk.Label(main, text="Working Directory", style="EC.Subtle.TLabel")
        dir_label.grid(row=1, column=0, sticky="w", pady=(10, 4))

        dir_row = ttk.Frame(main, style="EC.TFrame")
        dir_row.grid(row=2, column=0, sticky="ew")
        dir_row.columnconfigure(0, weight=1)

        self._directory_var = tk.StringVar()
        self._dir_combobox = ttk.Combobox(
            dir_row,
            textvariable=self._directory_var,
            values=[],
            style="EC.TCombobox",
        )
        self._dir_combobox.grid(row=0, column=0, sticky="ew")
        self._dir_combobox.bind("<<ComboboxSelected>>", self._on_directory_selected)

        browse_btn = ttk.Button(
            dir_row,
            text="Browse...",
            style="EC.TButton",
            command=lambda: self._browse_directory(self._directory_var),
        )
        browse_btn.grid(row=0, column=1, padx=(8, 0))

        cmd_label = ttk.Label(main, text="Command", style="EC.Subtle.TLabel")
        cmd_label.grid(row=3, column=0, sticky="w", pady=(12, 4))

        self._custom_cmd_var = tk.StringVar(value=self.COMMON_COMMANDS[0])
        self._custom_cmd_combo = ttk.Combobox(
            main,
            textvariable=self._custom_cmd_var,
            values=self.COMMON_COMMANDS,
            style="EC.TCombobox",
        )
        self._custom_cmd_combo.grid(row=4, column=0, sticky="ew")

        presets_label = ttk.Label(main, text="Quick Presets", style="EC.Subtle.TLabel")
        presets_label.grid(row=5, column=0, sticky="w", pady=(12, 4))

        preset_row = ttk.Frame(main, style="EC.TFrame")
        preset_row.grid(row=6, column=0, sticky="ew")
        preset_row.columnconfigure((0, 1, 2), weight=1)

        ttk.Button(
            preset_row,
            text="Standard",
            style="EC.TButton",
            command=lambda: self._set_command_and_launch(self.COMMANDS[0]),
        ).grid(row=0, column=0, sticky="ew", padx=(0, 4))

        ttk.Button(
            preset_row,
            text="Continue",
            style="EC.TButton",
            command=lambda: self._set_command_and_launch(self.COMMANDS[1]),
        ).grid(row=0, column=1, sticky="ew", padx=4)

        ttk.Button(
            preset_row,
            text="Skip Permissions",
            style="EC.TButton",
            command=lambda: self._set_command_and_launch(self.COMMANDS[2]),
        ).grid(row=0, column=2, sticky="ew", padx=(4, 0))

        actions = ttk.Frame(main, style="EC.TFrame")
        actions.grid(row=7, column=0, sticky="ew", pady=(14, 0))
        actions.columnconfigure(0, weight=1)
        actions.columnconfigure(1, weight=0)
        actions.columnconfigure(2, weight=0)

        ttk.Button(
            actions,
            text="Launch",
            style="EC.Primary.TButton",
            command=self._launch_custom_command,
        ).grid(row=0, column=1, sticky="e", padx=(0, 8))

        ttk.Button(
            actions,
            text="Close",
            style="EC.TButton",
            command=self.hide,
        ).grid(row=0, column=2, sticky="e")

    def _center_window(self, width: int, height: int) -> None:
        if not self._root:
            return
        self._root.update_idletasks()
        screen_w = self._root.winfo_screenwidth()
        screen_h = self._root.winfo_screenheight()
        x = max((screen_w - width) // 2, 0)
        y = max((screen_h - height) // 2, 0)
        self._root.geometry(f"{width}x{height}+{x}+{y}")

    def _process_command_queue(self) -> None:
        """Process pending cross-thread show/hide commands."""
        try:
            while True:
                cmd = self._command_queue.get_nowait()
                cmd_name = cmd.get("cmd")
                if cmd_name == "show":
                    self._populate_directory_combobox()

                    directory = cmd.get("directory", "")
                    if directory:
                        self._directory_var.set(directory)

                    self._root.deiconify()
                    self._root.lift()
                    self._root.focus_force()
                elif cmd_name == "hide":
                    self._root.withdraw()
        except queue.Empty:
            pass

        if self._root:
            self._root.after(50, self._process_command_queue)

    def _populate_directory_combobox(self) -> None:
        """Refresh recent directory suggestions from config."""
        if not hasattr(self, "_dir_combobox"):
            return
        cfg = config.get_config()
        # Use new directory_history field, extract paths from DirectoryEntry objects
        paths = [entry.path for entry in cfg.directory_history]
        self._dir_combobox["values"] = paths

    def _update_recent_directories(self, directory: str) -> None:
        """Store and deduplicate recent directories."""
        if not directory or not os.path.isdir(directory):
            return

        config.add_directory_to_history(directory)

    def _on_directory_selected(self, event: tk.Event) -> None:
        """Handle directory selection from history dropdown."""
        selected = self._directory_var.get().strip()
        if selected and os.path.isdir(selected):
            logger.debug("Directory selected from history: %s", selected)

    def _focus_directory_field(self) -> None:
        """Focus the directory combobox for keyboard input."""
        if hasattr(self, "_dir_combobox") and self._dir_combobox:
            self._dir_combobox.focus_set()
            self._dir_combobox.select_range(0, tk.END)

    def show(self, initial_directory: str = "") -> None:
        """Show the launcher window (thread-safe)."""
        self._ensure_initialized()
        self._command_queue.put(
            {
                "cmd": "show",
                "directory": initial_directory,
            }
        )

    def hide(self) -> None:
        """Hide the launcher window (thread-safe)."""
        if not self._root:
            return
        try:
            self._root.withdraw()
        except tk.TclError:
            self._command_queue.put({"cmd": "hide"})

    def _browse_directory(self, directory_var: tk.StringVar) -> None:
        """Open directory picker and update entry on selection."""
        current = directory_var.get()
        initial = current if current and os.path.isdir(current) else os.getcwd()
        selected = filedialog.askdirectory(
            title="Select Working Directory",
            initialdir=initial,
            parent=self._root,
            mustexist=True,
        )
        if selected:
            directory_var.set(selected)

    def _set_command_and_launch(self, command: str) -> None:
        """Set command field and launch immediately."""
        self._custom_cmd_var.set(command)
        self._do_launch(command)

    def _launch_custom_command(self) -> None:
        """Launch using the command from combobox/entry."""
        command = self._custom_cmd_var.get().strip() or "claude"
        self._do_launch(command)

    def _do_launch(self, command: str) -> None:
        """Validate inputs and invoke launch callback in background thread."""
        directory = self._directory_var.get().strip()
        if not directory:
            messagebox.showwarning("No Directory", "Please select a directory first.", parent=self._root)
            return
        if not os.path.isdir(directory):
            messagebox.showerror(
                "Invalid Directory",
                f"The directory '{directory}' does not exist.",
                parent=self._root,
            )
            return

        self._update_recent_directories(directory)
        self._populate_directory_combobox()
        self.hide()

        if not self._launch_callback:
            return

        def run_callback() -> None:
            try:
                self._launch_callback(directory, command)
            except Exception as exc:
                logger.error("Error in launch callback: %s", exc, exc_info=True)
            finally:
                with self._lock:
                    if threading.current_thread() in self._launch_threads:
                        self._launch_threads.remove(threading.current_thread())

        thread = threading.Thread(target=run_callback, daemon=False)
        with self._lock:
            self._launch_threads.append(thread)
        thread.start()

    def update(self) -> None:
        """Process pending Tk events."""
        if self._root and self._initialized:
            try:
                self._root.update()
            except tk.TclError:
                pass
            except Exception as exc:
                logger.debug("Exception in GUI update(): %s", exc)

    def destroy(self) -> None:
        """Cleanup and close window."""
        with self._lock:
            threads = list(self._launch_threads)
        for thread in threads:
            if thread.is_alive():
                thread.join(timeout=2.0)

        if self._root:
            try:
                self._root.destroy()
            except tk.TclError:
                pass
            except Exception as exc:
                logger.warning("Error during GUI destroy: %s", exc)
            self._root = None
        self._initialized = False


__all__ = ["LauncherGUI"]

