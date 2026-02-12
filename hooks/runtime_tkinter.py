"""
Runtime hook for PyInstaller to set up Tcl/Tk environment variables.
This ensures tkinter can find its library files in the frozen application.
"""
import os
import sys

# Set TCL_LIBRARY and TK_LIBRARY environment variables
# These must be set before tkinter is imported
if getattr(sys, 'frozen', False):
    # Running in a PyInstaller bundle
    bundle_dir = sys._MEIPASS

    tcl_lib = os.path.join(bundle_dir, 'tcl')
    tk_lib = os.path.join(bundle_dir, 'tk')

    if os.path.exists(tcl_lib):
        os.environ['TCL_LIBRARY'] = tcl_lib
    if os.path.exists(tk_lib):
        os.environ['TK_LIBRARY'] = tk_lib
