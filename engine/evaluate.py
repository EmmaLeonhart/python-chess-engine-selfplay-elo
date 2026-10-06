"""Static evaluation, in centipawns from the side to move's point of view.

Material plus the piece-square tables of Tomasz Michniewski's "Simplified
Evaluation Function" (Chess Programming Wiki). The king uses the middlegame
table and the endgame table, blended by game phase (non-pawn material:
knight and bishop 1, rook 2, queen 4, 24 at the start).
"""
from engine.board import SQUARES, WHITE, file_of, rank_of

VALUES = {1: 100, 2: 320, 3: 330, 4: 500, 5: 900, 6: 0}

# Tables are written as seen from White, rank 8 first.
TABLES = {
    1: [
        0, 0, 0, 0, 0, 0, 0, 0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
        5, 5, 10, 25, 25, 10, 5, 5,
        0, 0, 0, 20, 20, 0, 0, 0,
        5, -5, -10, 0, 0, -10, -5, 5,
        5, 10, 10, -20, -20, 10, 10, 5,
        0, 0, 0, 0, 0, 0, 0, 0],
    2: [
        -50, -40, -30, -30, -30, -30, -40, -50,
        -40, -20, 0, 0, 0, 0, -20, -40,
        -30, 0, 10, 15, 15, 10, 0, -30,
        -30, 5, 15, 20, 20, 15, 5, -30,
        -30, 0, 15, 20, 20, 15, 0, -30,
        -30, 5, 10, 15, 15, 10, 5, -30,
        -40, -20, 0, 5, 5, 0, -20, -40,
        -50, -40, -30, -30, -30, -30, -40, -50],
    3: [
        -20, -10, -10, -10, -10, -10, -10, -20,
        -10, 0, 0, 0, 0, 0, 0, -10,
        -10, 0, 5, 10, 10, 5, 0, -10,
        -10, 5, 5, 10, 10, 5, 5, -10,
        -10, 0, 10, 10, 10, 10, 0, -10,
        -10, 10, 10, 10, 10, 10, 10, -10,
        -10, 5, 0, 0, 0, 0, 5, -10,
        -20, -10, -10, -10, -10, -10, -10, -20],
    4: [
        0, 0, 0, 0, 0, 0, 0, 0,
        5, 10, 10, 10, 10, 10, 10, 5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        0, 0, 0, 5, 5, 0, 0, 0],
    5: [
        -20, -10, -10, -5, -5, -10, -10, -20,
        -10, 0, 0, 0, 0, 0, 0, -10,
        -10, 0, 5, 5, 5, 5, 0, -10,
        -5, 0, 5, 5, 5, 5, 0, -5,
        0, 0, 5, 5, 5, 5, 0, -5,
        -10, 5, 5, 5, 5, 5, 0, -10,
        -10, 0, 5, 0, 0, 0, 0, -10,
        -20, -10, -10, -5, -5, -10, -10, -20],
    6: [
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -20, -30, -30, -40, -40, -30, -30, -20,
        -10, -20, -20, -20, -20, -20, -20, -10,
        20, 20, 0, 0, 0, 0, 20, 20,
        20, 30, 10, 0, 0, 10, 30, 20],
}

KING_END = [
    -50, -40, -30, -20, -20, -30, -40, -50,
    -30, -20, -10, 0, 0, -10, -20, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -30, 0, 0, 0, 0, -30, -30,
    -50, -30, -30, -30, -30, -30, -30, -50]

PHASE = [0, 0, 1, 1, 2, 4, 0, 0, 0, 0, 0, 0, 0]  # by abs(piece); index 7+ unused
MAX_PHASE = 24

# PST[piece + 6][square]: material + table, signed (white positive).
PST = [[0] * 120 for _ in range(13)]
for _p, _table in TABLES.items():
    for _s in SQUARES:
        _f, _r = file_of(_s), rank_of(_s)
        PST[_p + 6][_s] = VALUES[_p] + _table[(7 - _r) * 8 + _f]
        PST[-_p + 6][_s] = -(VALUES[_p] + _table[_r * 8 + _f])


# King tables, signed like PST: KING_MG/KING_EG[0] white, [1] black.
KING_MG = [[0] * 120, [0] * 120]
KING_EG = [[0] * 120, [0] * 120]
for _s in SQUARES:
    _f, _r = file_of(_s), rank_of(_s)
    KING_MG[0][_s] = TABLES[6][(7 - _r) * 8 + _f]
    KING_MG[1][_s] = -TABLES[6][_r * 8 + _f]
    KING_EG[0][_s] = KING_END[(7 - _r) * 8 + _f]
    KING_EG[1][_s] = -KING_END[_r * 8 + _f]
    PST[6 + 6][_s] = 0
    PST[-6 + 6][_s] = 0


def evaluate(board):
    b = board.board
    score = 0
    phase = 0
    for s in SQUARES:
        p = b[s]
        if p:
            score += PST[p + 6][s]
            phase += PHASE[p if p > 0 else -p]
    if phase > MAX_PHASE:
        phase = MAX_PHASE
    wk, bk = board.kings
    mg = KING_MG[0][wk] + KING_MG[1][bk]
    eg = KING_EG[0][wk] + KING_EG[1][bk]
    score += (mg * phase + eg * (MAX_PHASE - phase)) // MAX_PHASE
    return score if board.side == WHITE else -score
