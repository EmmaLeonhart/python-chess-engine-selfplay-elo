# Queue

Current concrete work, top first. Finished items are deleted here and logged
in `devlog.md` in the same commit.

1. Board representation and legal move generation in `engine/board.py`
   (mailbox 0x88 or 10x12; castling, en passant, promotion, make/unmake,
   FEN in/out, Zobrist hashing).
2. Perft tests in `tests/test_perft.py`: start position and the CPW
   positions 2 to 6, depth 4 or more (depths that are too slow in Python run
   as a separate `perft` script, not in CI).
3. CI: `.github/workflows/ci.yml` runs pytest on push and PR.
4. Search in `engine/search.py`: alpha-beta (negamax) with iterative
   deepening, transposition table, quiescence search, time control.
5. Evaluation in `engine/evaluate.py`: material plus piece-square tables
   (the baseline, version 0).
6. UCI front end `engine/uci.py` plus `chess_engine.py` entry point
   (uci, isready, ucinewgame, position, go movetime/wtime/btime, stop, quit).
7. Match runner `match/runner.py`: plays two engine versions over UCI
   subprocesses from a fixed opening set, both colours, 1 s/move, >= 200
   games, parallel games; adjudicates mate/stalemate/50-move/threefold/
   insufficient material; writes PGN and a JSON result; reports score, Elo
   difference and 95% error.
8. Opening set `match/openings.epd`: a fixed list of balanced positions
   (100 positions x 2 colours = 200 games).
9. Engine versioning: frozen snapshots under `versions/vN/` so the "previous
   best" is a fixed program each round.
10. Round 1: first change, full match, record result in `results/` and README.
