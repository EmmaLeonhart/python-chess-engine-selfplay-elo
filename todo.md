# Todo

Longer-horizon goals from `data_lake/brief.md`. Pulled into `queue.md` as
concrete steps when they come up.

- At least eight improvement rounds, each one change, kept only if the 95%
  Elo interval is above zero. Candidate changes, roughly in expected-value
  order: MVV-LVA move ordering, killer moves, history heuristic, null-move
  pruning, late move reductions, principal variation search, aspiration
  windows, check extension, passed-pawn / pawn-structure terms, king safety,
  mobility, tapered (middlegame/endgame) evaluation, delta pruning in
  quiescence, faster move generation (more nodes per second).
- A results page in the README: every round, what changed, score, Elo with
  error bars, and the final engine's strength (against version 0, and an
  estimate of absolute strength if one can be made with standard-library
  tools only).
- Keep going after round eight, as the brief says ("keep going after each
  round").
