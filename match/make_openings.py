"""Generates the fixed opening set match/openings.epd (rerun only to rebuild it).

Each opening is 8 plies from the start position. At every ply a move is
picked at random (fixed seed) from those scoring within 30 cp of the best at
a depth-2 search, so lines stay plausible. A position is kept if a depth-3
search scores it within 50 cp of equal and it is not a duplicate.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.board import Board, move_to_uci  # noqa: E402
from engine.search import Searcher, INF  # noqa: E402

PLIES = 8
COUNT = 100
SEED = 20261006


def scored_moves(board, depth):
    s = Searcher()
    s.deadline = float("inf")
    s.stop = False
    s.nodes = 0
    out = []
    for m in board.legal_moves():
        board.make(m)
        out.append((-s.negamax(board, depth - 1, -INF, INF, 1), m))
        board.unmake()
    return out


def main():
    rng = random.Random(SEED)
    seen = set()
    lines = []
    while len(lines) < COUNT:
        b = Board()
        moves = []
        for _ in range(PLIES):
            sm = scored_moves(b, 2)
            top = max(sc for sc, _ in sm)
            m = rng.choice([m for sc, m in sm if sc >= top - 30])
            moves.append(move_to_uci(m))
            b.make(m)
        key = " ".join(b.fen().split()[:4])
        if key in seen:
            continue
        s = Searcher()
        s.deadline = float("inf")
        s.stop = False
        s.nodes = 0
        score = s.negamax(b, 3, -INF, INF, 1)
        if abs(score) > 50:
            continue
        seen.add(key)
        lines.append(f"{b.fen()} ; {' '.join(moves)} ; eval {score}")
        print(len(lines), lines[-1], flush=True)
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "openings.epd")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
