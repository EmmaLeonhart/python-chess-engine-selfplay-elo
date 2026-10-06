# Devlog

Finished work, newest last.

## 2026-10-06

- Work mode started at 09:08 PST after the thirty-minute intake (no chat,
  `data_lake/brief.md` present). Wrote `INTENT.md`, created the public repo
  `EmmaLeonhart/python-chess-engine-selfplay-elo` (the first-choice name
  `pure-python-chess-engine-selfplay` already existed on the account and was
  left untouched), filled in `README.md`, ran the cleanvibe update check
  (v2.0.4, already current), and planned the work into `queue.md` and
  `todo.md`.
- Board and move generation (`engine/board.py`): 10x12 mailbox, signed
  piece ints, int-encoded moves, make/unmake with an undo stack, incremental
  Zobrist hash, null move, FEN in/out, repetition and insufficient-material
  checks. Perft (`engine/perft.py`) matches the Chess Programming Wiki counts
  at depth 4 for all six standard positions (start 197,281; Kiwipete
  4,085,603; position 3 43,238; position 4 422,333; position 5 2,103,487;
  position 6 3,894,594). Position 6 failed at first because the FEN was
  typed from memory with two squares wrong; corrected against the CPW page.
- Tests (`tests/test_board.py`, 20 tests: perft at fast depths, FEN round
  trip, hash and unmake checked at every node to depth 2, repetition,
  insufficient material) and CI (`.github/workflows/ci.yml`).
- Perft at depth 5 also matches: start position 4,865,609 (24.6 s),
  position 3 674,624 (4.2 s).
- Baseline engine (version 0): material + simplified piece-square tables
  (`engine/evaluate.py`); negamax alpha-beta with iterative deepening,
  transposition table (dict, mate-score adjusted) and quiescence search
  (`engine/search.py`); ordering is TT move, then captures in generation
  order, then quiets. UCI front end with a search thread (`engine/uci.py`,
  `chess_engine.py`). About 100k nodes/s; depth 4 from the opening in about
  0.35 s. 7 search/UCI tests added (27 total, passing).
- Match tooling: `match/runner.py` (UCI subprocesses, 8 games in parallel
  on the 8 physical cores, both colours per opening, rules-based endings,
  400-ply draw cap, 5 s forfeit slack; writes games.jsonl as games finish,
  so a match can resume), `match/stats.py` (score, Elo, 95% interval from
  pair scores), `match/make_openings.py` and `match/openings.epd` (100
  distinct 8-ply openings, engine-filtered to within 50 cp of equal, fixed
  seed), `match/snapshot.py`. Version 0 frozen as `versions/v0`;
  `versions/BEST` names the current best. 4 match tests (31 total).
