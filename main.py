import os
import sys

from src.core.paths import setup_project_paths
setup_project_paths()

from src.ui.application import Application

if __name__ == "__main__":
    app = Application()
    app.mainloop()
