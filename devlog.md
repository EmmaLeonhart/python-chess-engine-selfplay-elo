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
