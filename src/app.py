"""
Legacy Entrypoint Redirector for Legion Performance and FPS Monitor.
Seamlessly forwards legacy calls to app_modern.py with zero conflicts.
"""

import os
import sys
import subprocess

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    modern_app = os.path.join(base_dir, "app_modern.py")
    
    if not os.path.exists(modern_app):
        print(f"Error: Could not locate modern application entrypoint at {modern_app}")
        sys.exit(1)
        
    args = [sys.executable, modern_app] + sys.argv[1:]
    
    if sys.platform == "win32":
        subprocess.Popen(args, cwd=os.path.dirname(base_dir))
        sys.exit(0)
    else:
        os.execv(sys.executable, args)

if __name__ == "__main__":
    main()
