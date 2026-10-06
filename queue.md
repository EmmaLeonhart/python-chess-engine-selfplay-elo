# Queue

Current concrete work, top first. Finished items are deleted here and logged
in `devlog.md` in the same commit.

1. Round 1 (stopped at 39/200 by memory pressure; restart NEEDS-DECISION,
   see INTENT.md): MVV-LVA capture ordering vs v0. When it finishes:
   write `results/round01/`, the README results table, and snapshot v1 if
   the 95% lower bound is above zero (otherwise revert `engine/search.py`).
2. Round 2: check extension (search one ply deeper when in check). Written
   and unit-tested on branch `round02-check-extension`; needs its match.
3. Round 3: killer moves (two quiet moves per ply that caused a cutoff).
4. Round 4: history heuristic for the remaining quiet moves.
5. Round 5: null-move pruning (R = 2, not in check, not in pawn-only
   endings).
6. Round 6: principal variation search (null-window re-search).
7. Round 7: late move reductions for late quiet moves.
8. Round 8: tapered evaluation (endgame king table, phase by material).
9. Round 9 and on: pawn structure (passed, doubled, isolated pawns),
   aspiration windows, delta pruning in quiescence, time management.

Rule for every round: candidate vs `versions/<BEST>`, 200 games, 1 s/move;
keep only if the 95% Elo lower bound is above zero. Don't run heavy jobs
(test suite, perft) while a match is playing: they take CPU from the games.
