"""Plays a match between two engine versions over UCI.

    python match/runner.py --candidate . --baseline versions/v0 --out results/round01

Each opening in match/openings.epd is played twice, once with each colour.
Every engine gets `go movetime` per move (1000 ms by default). The referee is
this repo's perft-tested engine/board.py. Games end by the rules (mate,
stalemate, threefold repetition, 50-move rule, insufficient material); a
game still running after MAX_PLIES is adjudicated a draw, and an engine that
does not answer within movetime + FORFEIT_SLACK loses on time.

Finished games are appended to <out>/games.jsonl as they complete, so a long
match can be watched, and a restarted match skips games already recorded.
The summary goes to <out>/summary.json and the games to <out>/games.pgn.
"""
import argparse
import json
import os
import queue
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from engine.board import Board, move_to_uci  # noqa: E402
from match.stats import summarize, format_summary  # noqa: E402

MAX_PLIES = 400
FORFEIT_SLACK = 5.0


class Engine:
    def __init__(self, directory):
        self.directory = os.path.abspath(directory)
        self.proc = subprocess.Popen(
            [sys.executable, "-u", os.path.join(self.directory, "chess_engine.py")],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, bufsize=1, cwd=self.directory)
        self.lines = queue.Queue()
        threading.Thread(target=self._read, daemon=True).start()
        self.send("uci")
        self.wait_for("uciok", 30)

    def _read(self):
        for line in self.proc.stdout:
            self.lines.put(line.strip())
        self.lines.put(None)

    def send(self, cmd):
        self.proc.stdin.write(cmd + "\n")
        self.proc.stdin.flush()

    def wait_for(self, prefix, timeout):
        """Returns (line, last_info) or (None, last_info) on timeout/exit."""
        end = time.perf_counter() + timeout
        last_info = None
        while True:
            left = end - time.perf_counter()
            if left <= 0:
                return None, last_info
            try:
                line = self.lines.get(timeout=left)
            except queue.Empty:
                return None, last_info
            if line is None:
                return None, last_info
            if line.startswith("info depth"):
                last_info = line
            if line.startswith(prefix):
                return line, last_info

    def new_game(self):
        self.send("ucinewgame")
        self.send("isready")
        self.wait_for("readyok", 30)

    def close(self):
        try:
            self.send("quit")
            self.proc.wait(timeout=5)
        except Exception:
            self.proc.kill()


def info_depth(info):
    if not info:
        return 0
    parts = info.split()
    return int(parts[parts.index("depth") + 1])


def play_game(index, opening_fen, cand_dir, base_dir, cand_white, movetime_ms):
    cand, base = Engine(cand_dir), Engine(base_dir)
    try:
        cand.new_game()
        base.new_game()
        board = Board(opening_fen)
        white, black = (cand, base) if cand_white else (base, cand)
        moves = []
        result, reason = None, None
        depths = {"candidate": [], "baseline": []}
        overruns = 0
        while result is None:
            if not board.legal_moves():
                if board.in_check():
                    result = "0-1" if board.side == 1 else "1-0"
                    reason = "checkmate"
                else:
                    result, reason = "1/2-1/2", "stalemate"
                break
            if board.is_repetition(2):
                result, reason = "1/2-1/2", "threefold repetition"
                break
            if board.halfmove >= 100:
                result, reason = "1/2-1/2", "fifty-move rule"
                break
            if board.insufficient_material():
                result, reason = "1/2-1/2", "insufficient material"
                break
            if len(moves) >= MAX_PLIES:
                result, reason = "1/2-1/2", f"adjudicated draw after {MAX_PLIES} plies"
                break
            eng = white if board.side == 1 else black
            pos = f"position fen {opening_fen}"
            if moves:
                pos += " moves " + " ".join(moves)
            eng.send(pos)
            t0 = time.perf_counter()
            eng.send(f"go movetime {movetime_ms}")
            line, info = eng.wait_for("bestmove", movetime_ms / 1000 + FORFEIT_SLACK)
            spent = time.perf_counter() - t0
            if spent > movetime_ms / 1000 * 1.2:
                overruns += 1
            loser_white = board.side == 1
            if line is None:
                result = "0-1" if loser_white else "1-0"
                reason = "time forfeit or crash"
                break
            m = board.parse_uci(line.split()[1]) if len(line.split()) > 1 else None
            if m is None:
                result = "0-1" if loser_white else "1-0"
                reason = f"illegal move {line}"
                break
            depths["candidate" if eng is cand else "baseline"].append(info_depth(info))
            moves.append(move_to_uci(m))
            board.make(m)
        if result == "1/2-1/2":
            score = 0.5
        elif (result == "1-0") == cand_white:
            score = 1.0
        else:
            score = 0.0
        avg = {k: round(sum(v) / len(v), 2) if v else 0 for k, v in depths.items()}
        return {"game": index, "pair": index // 2, "candidate_white": cand_white,
                "opening": opening_fen, "moves": moves, "result": result,
                "reason": reason, "score": score, "plies": len(moves),
                "avg_depth": avg, "overruns": overruns}
    finally:
        cand.close()
        base.close()


def pgn(g, cand_name, base_name):
    white, black = (cand_name, base_name) if g["candidate_white"] else (base_name, cand_name)
    b = Board(g["opening"])
    tokens = []
    for i, u in enumerate(g["moves"]):
        if b.side == 1:
            tokens.append(f"{b.fullmove}.")
        elif i == 0:
            tokens.append(f"{b.fullmove}...")
        tokens.append(u)
        b.make(b.parse_uci(u))
    tokens.append(g["result"])
    return (f'[Event "self-play"]\n[Round "{g["game"] + 1}"]\n[White "{white}"]\n'
            f'[Black "{black}"]\n[Result "{g["result"]}"]\n[FEN "{g["opening"]}"]\n'
            f'[SetUp "1"]\n[Termination "{g["reason"]}"]\n\n' + " ".join(tokens) + "\n\n")


def load_openings(path):
    with open(path) as f:
        return [line.split(";")[0].strip() for line in f if line.strip()]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True, help="directory with chess_engine.py")
    ap.add_argument("--baseline", required=True, help="directory with chess_engine.py")
    ap.add_argument("--out", required=True, help="output directory")
    ap.add_argument("--games", type=int, default=200)
    ap.add_argument("--movetime", type=int, default=1000, help="ms per move")
    ap.add_argument("--concurrency", type=int, default=8)
    ap.add_argument("--openings", default=os.path.join(ROOT, "match", "openings.epd"))
    args = ap.parse_args(argv)

    openings = load_openings(args.openings)
    os.makedirs(args.out, exist_ok=True)
    games_path = os.path.join(args.out, "games.jsonl")
    done = {}
    if os.path.exists(games_path):
        with open(games_path) as f:
            for line in f:
                if line.strip():
                    g = json.loads(line)
                    done[g["game"]] = g
    todo = [i for i in range(args.games) if i not in done]
    lock = threading.Lock()
    started = time.time()
    print(f"{len(done)} games already recorded, {len(todo)} to play", flush=True)

    def run(i):
        g = play_game(i, openings[(i // 2) % len(openings)], args.candidate,
                      args.baseline, i % 2 == 0, args.movetime)
        with lock:
            done[i] = g
            with open(games_path, "a") as f:
                f.write(json.dumps(g) + "\n")
            s = summarize(list(done.values()))
            print(f"[{time.time() - started:7.0f}s] game {i + 1}: {g['result']} "
                  f"({g['reason']}, {g['plies']} plies)  |  {format_summary(s)}", flush=True)

    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        list(ex.map(run, todo))

    games = [done[i] for i in sorted(done)]
    s = summarize(games)
    s.update({
        "candidate": os.path.relpath(os.path.abspath(args.candidate), ROOT),
        "baseline": os.path.relpath(os.path.abspath(args.baseline), ROOT),
        "movetime_ms": args.movetime,
        "concurrency": args.concurrency,
        "avg_plies": round(sum(g["plies"] for g in games) / len(games), 1),
        "avg_depth_candidate": round(sum(g["avg_depth"]["candidate"] for g in games) / len(games), 2),
        "avg_depth_baseline": round(sum(g["avg_depth"]["baseline"] for g in games) / len(games), 2),
        "overruns": sum(g["overruns"] for g in games),
        "forfeits": sum(1 for g in games if g["reason"].startswith(("time", "illegal"))),
        "terminations": {},
    })
    for g in games:
        key = g["reason"].split(" after")[0]
        s["terminations"][key] = s["terminations"].get(key, 0) + 1
    with open(os.path.join(args.out, "summary.json"), "w") as f:
        json.dump(s, f, indent=2)
    with open(os.path.join(args.out, "games.pgn"), "w") as f:
        for g in games:
            f.write(pgn(g, "candidate", "baseline"))
    print("FINAL", format_summary(s), flush=True)
    return s


if __name__ == "__main__":
    main()
