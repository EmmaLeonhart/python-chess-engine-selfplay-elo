"""Perft: count leaf nodes of the legal move tree, to check move generation.

Usage: python -m engine.perft [depth] [fen...]   (runs the standard suite
when no FEN is given).
"""
import sys
import time

from engine.board import Board, WHITE, move_to_uci

# Standard positions and counts from the Chess Programming Wiki "Perft Results" page.
SUITE = [
    ("startpos", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
     [20, 400, 8902, 197281, 4865609]),
    ("kiwipete", "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1",
     [48, 2039, 97862, 4085603]),
    ("position3", "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1",
     [14, 191, 2812, 43238, 674624]),
    ("position4", "r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1",
     [6, 264, 9467, 422333]),
    ("position5", "rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8",
     [44, 1486, 62379, 2103487]),
    ("position6", "r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10",
     [46, 2079, 89890, 3894594]),
]


def perft(board, depth):
    if depth == 0:
        return 1
    us = board.side
    ki = 0 if us == WHITE else 1
    total = 0
    for m in board.gen_pseudo():
        board.make(m)
        if not board.attacked(board.kings[ki], -us):
            total += 1 if depth == 1 else perft(board, depth - 1)
        board.unmake()
    return total


def divide(board, depth):
    out = {}
    for m in board.legal_moves():
        board.make(m)
        out[move_to_uci(m)] = perft(board, depth - 1)
        board.unmake()
    return out


def main(argv):
    depth = int(argv[0]) if argv else 4
    if len(argv) > 1:
        fen = " ".join(argv[1:])
        b = Board(fen)
        d = divide(b, depth)
        for k in sorted(d):
            print(k, d[k])
        print("total", sum(d.values()))
        return 0
    ok = True
    for name, fen, counts in SUITE:
        if depth > len(counts):
            continue
        t0 = time.time()
        n = perft(Board(fen), depth)
        good = n == counts[depth - 1]
        ok &= good
        print(f"{name:10s} depth {depth}: {n:>9d} expected {counts[depth - 1]:>9d} "
              f"{'ok' if good else 'FAIL'} ({time.time() - t0:.1f}s)", flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
