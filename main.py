"""Detective's Evidence Board - entry point.

Run with:  python main.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.app import App


def main():
    app = App()
    app.run()


if __name__ == "__main__":
    main()
