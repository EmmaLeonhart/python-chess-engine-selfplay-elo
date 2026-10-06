# Queue

Current concrete work, top first. Finished items are deleted here and logged
in `devlog.md` in the same commit.

1. Search in `engine/search.py`: alpha-beta (negamax) with iterative
   deepening, transposition table, quiescence search, time control.
2. Evaluation in `engine/evaluate.py`: material plus piece-square tables
   (the baseline, version 0).
3. UCI front end `engine/uci.py` plus `chess_engine.py` entry point
   (uci, isready, ucinewgame, position, go movetime/wtime/btime, stop, quit).
4. Match runner `match/runner.py`: plays two engine versions over UCI
   subprocesses from a fixed opening set, both colours, 1 s/move, >= 200
   games, parallel games; adjudicates mate/stalemate/50-move/threefold/
   insufficient material; writes PGN and a JSON result; reports score, Elo
   difference and 95% error.
5. Opening set `match/openings.epd`: a fixed list of balanced positions
   (100 positions x 2 colours = 200 games).
6. Engine versioning: frozen snapshots under `versions/vN/` so the "previous
   best" is a fixed program each round.
7. Round 1: first change, full match, record result in `results/` and README.
