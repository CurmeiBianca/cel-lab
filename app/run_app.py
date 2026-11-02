"""Pornește interfața CelLab: python run_app.py"""
import os
import subprocess
import sys

cale_ui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui.py")
subprocess.run([sys.executable, "-m", "streamlit", "run", cale_ui])
