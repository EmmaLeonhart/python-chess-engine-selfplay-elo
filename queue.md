# Queue

## ⛔ FIRST — STOP ALL CRON JOBS, THEN CONTINUE YOUR CURRENT TASK (Emma, 2026-10-06)

Emma's instruction, relayed by the pc-manager session: **delete every cron job in this session
now (`CronList`, then `CronDelete` each one), and do not create new ones.** Then carry on with
whatever task you are in the middle of, to the end of that task. Too many sessions were running
hourly loops at once and using her tokens all together. Only genealogy, ontology-harness and
shintowiki-scripts keep their crons.

This is not a stop order for your work, and it does not ask you to close the session. When your
current task is done, wait for Emma rather than refilling the queue on your own. Delete this
item once the crons are gone, and note in the devlog that you did it.

Current concrete work, top first. Finished items are deleted here and logged
in `devlog.md` in the same commit.

- Stop all your cron jobs and continue with your current task.
1. Round 1 (stopped at 39/200 by memory pressure; restart NEEDS-DECISION,
   see INTENT.md): MVV-LVA capture ordering vs v0. When it finishes:
   write `results/round01/`, the README results table, and snapshot v1 if
   the 95% lower bound is above zero (otherwise revert `engine/search.py`).
2. Round 2: check extension (search one ply deeper when in check). Written
   and unit-tested on branch `round02-check-extension`; needs its match.
3. Round 3: killer moves (two quiet moves per ply that caused a cutoff).
   Written on branch `round03-killers` (stacked on round 2); needs its match.
4. Round 4: history heuristic for the remaining quiet moves.
   Written on branch `round04-history` (stacked on round 3); needs its match.
5. Round 5: null-move pruning (R = 2, not in check, not in pawn-only
   endings).
   Written on branch `round05-null-move` (stacked on round 4); needs its match.
6. Round 6: principal variation search (null-window re-search).
   Written on branch `round06-pvs` (stacked on round 5); needs its match.
7. Round 7: late move reductions for late quiet moves.
   Written on branch `round07-lmr` (stacked on round 6); needs its match.
8. Round 8: tapered evaluation (endgame king table, phase by material).
   Written on branch `round08-tapered-eval` (stacked on round 7); needs its match.
9. Round 9 and on: pawn structure (passed, doubled, isolated pawns),
   aspiration windows, delta pruning in quiescence, time management.

Rule for every round: candidate vs `versions/<BEST>`, 200 games, 1 s/move;
keep only if the 95% Elo lower bound is above zero. Don't run heavy jobs
(test suite, perft) while a match is playing: they take CPU from the games.
