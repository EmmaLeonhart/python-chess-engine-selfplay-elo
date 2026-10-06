"""Freezes the current engine as versions/<name>/ so later matches play
against a fixed program:  python match/snapshot.py v1"""
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def snapshot(name):
    dest = os.path.join(ROOT, "versions", name)
    if os.path.exists(dest):
        raise SystemExit(f"{dest} already exists")
    shutil.copytree(os.path.join(ROOT, "engine"), os.path.join(dest, "engine"),
                    ignore=shutil.ignore_patterns("__pycache__", "perft.py"))
    shutil.copy(os.path.join(ROOT, "chess_engine.py"), dest)
    print("wrote", dest)


if __name__ == "__main__":
    snapshot(sys.argv[1])
