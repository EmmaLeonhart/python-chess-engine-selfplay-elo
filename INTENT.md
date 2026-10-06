# What this project is for

_Maintained by Claude: a running read of what the user is trying to do. It is
analysis, not a transcript, and it changes as understanding improves._

Work mode started: 2026-10-06 09:08 PST (from `date`; the thirty-minute intake
returned WORK MODE because the user had said nothing since the greeting and
`data_lake/brief.md` was present).

## Current understanding

Build a chess engine in pure Python (standard library only) and make it
stronger through measured self-play, as `data_lake/brief.md` lays out:

1. Move generation that passes standard perft counts (start position and the
   usual test positions, depth 4 or more), a UCI interface, and alpha-beta
   search with iterative deepening, a transposition table and quiescence
   search.
2. A match runner: two engine versions, fixed opening set, both colours,
   1 second a move, at least 200 games a match; report score, Elo difference
   and its error.
3. At least eight improvement rounds: one change each, a full match against
   the previous best, keep it only on a statistically clear win, record the
   result.
4. A results page in the README: every round, the change, score, Elo with
   error bars, and the final engine's strength.

The brief says: "This is a long project; keep going after each round."

## What supports it

- `data_lake/brief.md`, the only material in the folder; it is a concrete
  spec, so it is followed as written.
- The folder name (`crisp-golden-badger`) is generated and says nothing.
- The path (`cleanvibe-practice`) and the opening prompt say this is a
  practice/research project on how cleanvibe sessions work. That is context,
  not a task: the task is the brief.

## Constraints from the user

- **The GitHub repo is public.** Opening prompt: "Create the GitHub repo
  public, not private: this is a public research practice project." The brief
  says the same ("create it **public** ... This overrides the private default
  in CLAUDE.md").
- Opening prompt: "Only use AskUserQuestion if I am clearly here and
  replying." The user has not replied yet, so decisions are made and recorded
  here.
- Standard library only (brief).

## Assumptions

- "Statistically clear margin" means the lower end of the 95% Elo interval
  is above zero (Elo minus 1.96 standard errors > 0), computed from the match
  result with draws counted. Recorded so each round uses the same rule.
- "The usual test positions" means the standard positions from the Chess
  Programming Wiki perft page (start, Kiwipete, positions 3 to 6).
- A 200-game match at 1 s/move takes several hours (about 80 moves a game is
  ~160 s per game, so ~9 hours single-threaded). Matches run games in parallel
  across CPU cores to bring that down; each engine still gets 1 s per move.

## Open questions

- **NEEDS-DECISION (user):** the round 1 match was stopped by Claude Code at
  09:31 PST because the system was critically low on memory, with 39 of 200
  games recorded (+22 =8 -9, Elo +120 [-8, +229]). Claude Code's note says
  not to restart it unasked. The user decides whether to restart (the runner
  resumes from `results/round01/games.jsonl`) and whether to cut memory use
  first (smaller transposition table, fewer parallel games). Rounds 2 on
  wait behind this, since each is played against the round 1 winner.
- At 09:48 PST, 23 `python.exe` processes were still running, probably
  orphaned engine processes from the stopped match. Not killed: the user's
  instructions say not to stop running things unasked.
- If the user turns up, worth confirming the "clear margin" rule above.

## Confidence

High on the goal: the brief is explicit.
