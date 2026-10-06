"""UCI protocol front end. The search runs in a worker thread so that
`stop` and `quit` are handled while it thinks."""
import sys
import threading

from engine.board import Board, START_FEN, move_to_uci
from engine.search import Searcher

NAME = "PyBadger"
SAFETY = 0.05  # seconds kept back from each move for process overhead


def allocate(params, side_white):
    """Seconds to spend on this move from the `go` parameters."""
    if "movetime" in params:
        return max(0.01, params["movetime"] / 1000 - SAFETY)
    left = params.get("wtime" if side_white else "btime")
    if left is None:
        return None
    inc = params.get("winc" if side_white else "binc", 0)
    mtg = params.get("movestogo", 30)
    t = left / max(mtg, 1) + inc * 0.8
    return max(0.01, min(t, left * 0.5) / 1000 - SAFETY)


class UCI:
    def __init__(self, out=sys.stdout):
        self.out = out
        self.board = Board()
        self.searcher = Searcher()
        self.thread = None
        self.lock = threading.Lock()

    def send(self, line):
        with self.lock:
            self.out.write(line + "\n")
            self.out.flush()

    def wait(self):
        if self.thread:
            self.thread.join()
            self.thread = None

    def position(self, tokens):
        if not tokens:
            return
        if tokens[0] == "startpos":
            self.board = Board(START_FEN)
            rest = tokens[1:]
        elif tokens[0] == "fen":
            fen_parts = []
            rest = tokens[1:]
            while rest and rest[0] != "moves":
                fen_parts.append(rest.pop(0))
            self.board = Board(" ".join(fen_parts))
        else:
            return
        if rest and rest[0] == "moves":
            for u in rest[1:]:
                m = self.board.parse_uci(u)
                if m is None:
                    self.send(f"info string illegal move {u}")
                    break
                self.board.make(m)

    def go(self, tokens):
        params = {}
        i = 0
        while i < len(tokens):
            key = tokens[i]
            if key in ("wtime", "btime", "winc", "binc", "movestogo", "movetime", "depth", "nodes"):
                params[key] = int(tokens[i + 1])
                i += 2
            else:
                params[key] = True
                i += 1
        movetime = None if "infinite" in params else allocate(params, self.board.side == 1)
        depth = params.get("depth", 64)
        board = self.board

        def run():
            m = self.searcher.search(board, movetime, depth, info=self.send)
            self.send(f"bestmove {move_to_uci(m)}")

        self.wait()
        self.thread = threading.Thread(target=run, daemon=True)
        self.thread.start()

    def handle(self, line):
        tokens = line.split()
        if not tokens:
            return True
        cmd = tokens[0]
        if cmd == "uci":
            self.send(f"id name {NAME}")
            self.send("id author cleanvibe session")
            self.send("uciok")
        elif cmd == "isready":
            self.send("readyok")
        elif cmd == "ucinewgame":
            self.wait()
            self.searcher.new_game()
        elif cmd == "position":
            self.wait()
            self.position(tokens[1:])
        elif cmd == "go":
            self.go(tokens[1:])
        elif cmd == "stop":
            self.searcher.stop = True
            self.wait()
        elif cmd == "quit":
            self.searcher.stop = True
            self.wait()
            return False
        elif cmd == "d":
            self.send(self.board.fen())
        return True

    def loop(self, inp=sys.stdin):
        for line in inp:
            if not self.handle(line.strip()):
                break
        self.searcher.stop = True
        self.wait()


def main():
    UCI().loop()
