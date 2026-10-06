import os

from match.runner import play_game, pgn
from match.stats import elo, summarize

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def games(results):
    """results: list of (pair, score)."""
    return [{"pair": p, "score": s} for p, s in results]


def test_elo_curve():
    assert elo(0.5) == 0
    assert abs(elo(0.75) - 190.85) < 0.1
    assert abs(elo(0.25) + elo(0.75)) < 1e-9


def test_summary_counts_and_interval():
    s = summarize(games([(i // 2, 1 if i % 4 == 0 else 0.5) for i in range(200)]))
    assert (s["wins"], s["draws"], s["losses"]) == (50, 150, 0)
    assert s["score"] == 0.625
    assert s["elo_lo"] < s["elo"] < s["elo_hi"]
    assert s["clear_win"]
    assert sum(s["pentanomial"]) == 100


def test_even_match_is_not_clear():
    s = summarize(games([(i // 2, [1, 0, 0.5, 0.5][i % 4]) for i in range(200)]))
    assert s["elo"] == 0 and not s["clear_win"]


def test_play_one_fast_game():
    fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
    g = play_game(0, fen, ROOT, ROOT, True, 20)
    assert g["result"] in ("1-0", "0-1", "1/2-1/2")
    assert g["plies"] > 0 and not g["reason"].startswith(("time", "illegal"))
    assert pgn(g, "a", "b").startswith('[Event "self-play"]')
