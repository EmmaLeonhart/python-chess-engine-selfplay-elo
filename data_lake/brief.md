# Brief

A chess engine in pure Python (standard library only), improved by
measured self-play. This is a long project; keep going after each round.

1. Move generation that passes the standard perft counts (start position
   and the usual test positions, depth 4 or more), a UCI interface, and
   alpha-beta search with iterative deepening, a transposition table and
   quiescence search.
2. A match runner: two engine versions play each other from a fixed set of
   opening positions, both colours, with a time control of 1 second a move,
   at least 200 games a match. Report score, Elo difference and its error.
3. Improvement rounds. Each round: make one change to the search or the
   evaluation, play a full match against the previous best, keep the change
   only if it wins by a statistically clear margin, and record the result.
   Do at least eight rounds. A match takes a long time; let it run, and
   record each one when it finishes.
4. A results page in the README: every round, what changed, the score and
   the Elo with error bars, and the final engine's strength.

## The GitHub repo is public

This project is part of public research on how cleanvibe sessions work, so
its transcripts are meant to be shown. When work mode creates the GitHub
repo, create it **public** (`gh repo create <name> --public --source=. --push`),
not private. This overrides the private default in CLAUDE.md.
