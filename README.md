# python-chess-engine-selfplay-elo

A chess engine in pure Python (standard library only), made stronger one
change at a time. A change is kept only if it wins a 200-game self-play match
against the previous best by a statistically clear margin.

> Started with [cleanvibe](https://github.com/EmmaLeonhart/cleanvibe) on 2026-10-06.
> The brief is in `data_lake/brief.md`; the current reading of it is in `INTENT.md`.

## Status

In progress: move generation and perft come first, then the UCI interface and
search, then the match runner, then the improvement rounds.

## Results

_No rounds played yet._ Each round will be listed here with what changed, the
match score, and the Elo difference with its 95% error bar.

## Working on it

Run `cleanvibe` in this folder (or double-click `!runClaude.bat` on Windows) to
open a new Claude session here. It starts with Remote Control on, so you can
continue from the Claude app or web. Earlier sessions are in `sessions/`.
