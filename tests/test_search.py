import io

from engine.board import Board, move_to_uci
from engine.search import Searcher, MATE_BOUND
from engine.uci import UCI, allocate


def best(fen, depth):
    return move_to_uci(Searcher().search(Board(fen), max_depth=depth))


def test_mate_in_one():
    assert best("6k1/5ppp/8/8/8/8/5PPP/R5K1 w - - 0 1", 3) == "a1a8"


def test_mate_score_and_board_restored():
    # Qb8 is mate; the search must report a mate score and restore the board.
    s = Searcher()
    b = Board("6k1/5ppp/8/8/8/8/1Q3PPP/1R4K1 w - - 0 1")
    s.search(b, max_depth=4)
    assert b.fen() == "6k1/5ppp/8/8/8/8/1Q3PPP/1R4K1 w - - 0 1"  # board restored
    assert s.negamax(b, 4, -10**6, 10**6, 0) > MATE_BOUND


def test_wins_hanging_queen():
    assert best("4k3/8/8/3q4/8/8/8/3QK3 w - - 0 1", 2) == "d1d5"


def test_no_legal_moves_at_root():
    assert Searcher().search(Board("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1"), max_depth=2) == 0


def test_timeout_restores_board():
    b = Board("r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1")
    fen = b.fen()
    m = Searcher().search(b, movetime=0.2)
    assert m in b.legal_moves()
    assert b.fen() == fen and not b.stack


def test_allocate():
    assert abs(allocate({"movetime": 1000}, True) - 0.95) < 1e-9
    assert allocate({"wtime": 60000, "btime": 1000}, True) > allocate({"wtime": 60000, "btime": 1000}, False)


def test_uci_session():
    out = io.StringIO()
    u = UCI(out)
    u.loop(io.StringIO("uci\nisready\nposition startpos moves e2e4\ngo depth 2\nisready\nquit\n"))
    text = out.getvalue()
    assert "uciok" in text and "readyok" in text
    line = [l for l in text.splitlines() if l.startswith("bestmove")][0]
    b = Board()
    b.make(b.parse_uci("e2e4"))
    assert b.parse_uci(line.split()[1]) is not None
