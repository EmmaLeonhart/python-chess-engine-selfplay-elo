# Queue

Current concrete work, top first. Finished items are deleted here and logged
in `devlog.md` in the same commit.

1. Match runner `match/runner.py`: plays two engine versions over UCI
   subprocesses from a fixed opening set, both colours, 1 s/move, >= 200
   games, parallel games; adjudicates mate/stalemate/50-move/threefold/
   insufficient material; writes PGN and a JSON result; reports score, Elo
   difference and 95% error.
2. Opening set `match/openings.epd`: a fixed list of balanced positions
   (100 positions x 2 colours = 200 games).
3. Engine versioning: frozen snapshots under `versions/vN/` so the "previous
   best" is a fixed program each round.
4. Round 1: first change, full match, record result in `results/` and README.
