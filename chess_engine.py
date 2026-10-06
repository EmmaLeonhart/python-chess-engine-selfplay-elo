"""UCI engine entry point: python chess_engine.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.uci import main  # noqa: E402

if __name__ == "__main__":
    main()
