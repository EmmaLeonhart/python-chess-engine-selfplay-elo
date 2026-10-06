import pytest

from engine.board import Board, START_FEN, move_to_uci
from engine.perft import SUITE, perft

# Depths that run in a few seconds each; the full depth-4/5 run is
# `python -m engine.perft 4` (results recorded in devlog.md).
FAST = {"startpos": 4, "kiwipete": 3, "position3": 4, "position4": 3,
        "position5": 3, "position6": 3}


@pytest.mark.parametrize("name,fen,counts", SUITE, ids=[s[0] for s in SUITE])
def test_perft(name, fen, counts):
    depth = FAST[name]
    assert perft(Board(fen), depth) == counts[depth - 1]


@pytest.mark.parametrize("fen", [s[1] for s in SUITE])
def test_fen_round_trip(fen):
    b = Board(fen)
    assert Board(b.fen()).fen() == b.fen()


def walk(board, depth):
    """Every reachable node: incremental hash and make/unmake agree with a fresh board."""
    if depth == 0:
        return
    for m in board.legal_moves():
        before = board.fen()
        board.make(m)
        assert board.hash == Board(board.fen()).hash, move_to_uci(m)
        walk(board, depth - 1)
        board.unmake()
        assert board.fen() == before


@pytest.mark.parametrize("fen", [s[1] for s in SUITE])
def test_hash_and_unmake(fen):
    walk(Board(fen), 2)


def test_parse_uci_and_repetition():
    b = Board(START_FEN)
    for u in ["g1f3", "g8f6", "f3g1", "f6g8"]:
        b.make(b.parse_uci(u))
    assert b.is_repetition()
    assert not b.is_repetition(2)
    for u in ["g1f3", "g8f6", "f3g1", "f6g8"]:
        b.make(b.parse_uci(u))
    assert b.is_repetition(2)
    assert b.parse_uci("e2e5") is None


def test_insufficient_material():
    assert Board("8/8/4k3/8/8/3K4/8/8 w - - 0 1").insufficient_material()
    assert Board("8/8/4k3/8/8/3KN3/8/8 w - - 0 1").insufficient_material()
    assert not Board("8/8/4k3/8/8/3KP3/8/8 w - - 0 1").insufficient_material()
    assert not Board("8/8/4kn2/8/8/3KN3/8/8 w - - 0 1").insufficient_material()
