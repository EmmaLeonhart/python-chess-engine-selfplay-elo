"""Search: negamax alpha-beta with iterative deepening, a transposition
table and quiescence search.

Move ordering: transposition-table move, then captures and promotions by
MVV-LVA (most valuable victim, then least valuable attacker), then the two
killer moves of this ply (quiet moves that last caused a cutoff here), then
the other quiet moves by history score (cutoffs they caused, weighted by
depth squared, halved at each new search). Check extension: one ply deeper when in check.
"""
import time

from engine.board import WHITE, FLAG_EP, move_to_uci
from engine.evaluate import evaluate

INF = 1_000_000
MATE = 100_000
MATE_BOUND = MATE - 1000  # scores beyond this are mates
EXACT, LOWER, UPPER = 0, 1, 2
TT_MAX = 1_000_000
NULL_R = 2


class Timeout(Exception):
    pass


def score_to_tt(score, ply):
    if score > MATE_BOUND:
        return score + ply
    if score < -MATE_BOUND:
        return score - ply
    return score


def score_from_tt(score, ply):
    if score > MATE_BOUND:
        return score - ply
    if score < -MATE_BOUND:
        return score + ply
    return score


def capture_key(board, m):
    """MVV-LVA sort key (larger first); en passant counts as a pawn capture."""
    v = board[(m >> 7) & 127]
    a = board[m & 127]
    return (v if v > 0 else -v or 1) * 10 - (a if a > 0 else -a) + ((m >> 14) & 7) * 10


def uci_score(score):
    if score > MATE_BOUND:
        return f"mate {(MATE - score + 1) // 2}"
    if score < -MATE_BOUND:
        return f"mate -{(MATE + score) // 2}"
    return f"cp {score}"


class Searcher:
    def __init__(self):
        self.tt = {}
        self.history = [0] * 32768  # quiet-move cutoff credit by (side, from, to)
        self.stop = False  # set from another thread to abort

    def new_game(self):
        self.tt.clear()
        self.history = [0] * 32768

    def search(self, board, movetime=None, max_depth=64, info=None):
        """Best move for `board`. `movetime` in seconds (None = until depth)."""
        start = time.perf_counter()
        self.deadline = start + movetime if movetime else float("inf")
        self.stop = False
        self.nodes = 0
        self.killers = [[0, 0] for _ in range(130)]
        self.history = [h >> 1 for h in self.history]
        if len(self.tt) > TT_MAX:
            self.tt.clear()
        legal = board.legal_moves()
        if not legal:
            return 0
        best = legal[0]
        base = len(board.stack)
        for depth in range(1, max_depth + 1):
            self.root_best = 0
            try:
                score = self.negamax(board, depth, -INF, INF, 0)
            except Timeout:
                while len(board.stack) > base:
                    if board.stack[-1][0]:
                        board.unmake()
                    else:
                        board.unmake_null()
                break
            if self.root_best:
                best = self.root_best
            elapsed = time.perf_counter() - start
            if info:
                nps = int(self.nodes / elapsed) if elapsed > 0 else 0
                info(f"info depth {depth} score {uci_score(score)} nodes {self.nodes} "
                     f"nps {nps} time {int(elapsed * 1000)} pv {move_to_uci(best)}")
            if abs(score) > MATE_BOUND:
                break
            # The next iteration usually costs several times this one.
            if movetime and elapsed > movetime * 0.5:
                break
        return best

    @staticmethod
    def has_pieces(b):
        """Does the side to move have a knight, bishop, rook or queen?"""
        us = b.side
        for p in b.board:
            if p != 7 and 1 < p * us < 6:
                return True
        return False

    def check_time(self):
        if self.stop or time.perf_counter() > self.deadline:
            raise Timeout

    def negamax(self, b, depth, alpha, beta, ply):
        self.nodes += 1
        if self.nodes & 1023 == 0:
            self.check_time()
        if ply and (b.halfmove >= 100 or b.is_repetition()):
            return 0
        in_check = b.in_check()
        if in_check:
            depth += 1  # check extension
        if depth <= 0:
            return self.qsearch(b, alpha, beta, ply)
        key = b.hash
        tt_move = 0
        e = self.tt.get(key)
        if e:
            edepth, eflag, escore, tt_move = e
            if ply and edepth >= depth:
                escore = score_from_tt(escore, ply)
                if eflag == EXACT:
                    return escore
                if eflag == LOWER and escore >= beta:
                    return escore
                if eflag == UPPER and escore <= alpha:
                    return escore
        board = b.board
        # Null-move pruning: if passing still fails high at reduced depth,
        # a real move will too. Not in check, not twice in a row, and not
        # without pieces (zugzwang in pawn endings).
        if (ply and not in_check and depth >= 3 and beta < MATE_BOUND
                and b.stack and b.stack[-1][0] and self.has_pieces(b)):
            b.make_null()
            score = -self.negamax(b, depth - 1 - NULL_R, -beta, -beta + 1, ply + 1)
            b.unmake_null()
            if score >= beta:
                return beta
        moves = b.gen_pseudo()
        caps = []
        quiets = []
        first = []
        for m in moves:
            if m == tt_move:
                first.append(m)
            elif board[(m >> 7) & 127] or (m >> 14) & 7 or (m >> 17) == FLAG_EP:
                caps.append(m)
            else:
                quiets.append(m)
        us = b.side
        ki = 0 if us == WHITE else 1
        kings = b.kings
        best = -INF
        best_move = 0
        alpha0 = alpha
        legal = 0
        caps.sort(key=lambda m: capture_key(board, m), reverse=True)
        k0, k1 = killers = self.killers[ply]
        hist = self.history
        hside = 16384 if us == WHITE else 0
        front = [k for k in (k0, k1) if k and k in quiets]
        quiets = [m for m in quiets if m != k0 and m != k1]
        quiets.sort(key=lambda m: hist[hside | (m & 16383)], reverse=True)
        quiets = front + quiets
        for m in first + caps + quiets:
            quiet = not (board[(m >> 7) & 127] or (m >> 14) & 7 or (m >> 17) == FLAG_EP)
            b.make(m)
            if b.attacked(kings[ki], -us):
                b.unmake()
                continue
            legal += 1
            if legal == 1:
                score = -self.negamax(b, depth - 1, -beta, -alpha, ply + 1)
            else:
                # Late move reduction: a late quiet move that does not give
                # check is first searched one ply shallower.
                if (legal > 3 and depth >= 3 and quiet and not in_check
                        and m != k0 and m != k1 and not b.in_check()):
                    score = -self.negamax(b, depth - 2, -alpha - 1, -alpha, ply + 1)
                else:
                    score = alpha + 1
                # Principal variation search: prove the move is no better
                # with a null window, re-search only if it is.
                if score > alpha:
                    score = -self.negamax(b, depth - 1, -alpha - 1, -alpha, ply + 1)
                if alpha < score < beta:
                    score = -self.negamax(b, depth - 1, -beta, -alpha, ply + 1)
            b.unmake()
            if score > best:
                best = score
                best_move = m
                if ply == 0:
                    self.root_best = m
                if score > alpha:
                    alpha = score
                    if alpha >= beta:
                        if (not board[(m >> 7) & 127] and not (m >> 14) & 7
                                and (m >> 17) != FLAG_EP):
                            hist[hside | (m & 16383)] += depth * depth
                            if m != k0:
                                killers[1] = k0
                                killers[0] = m
                        break
        if not legal:
            return -MATE + ply if in_check else 0
        flag = LOWER if best >= beta else EXACT if best > alpha0 else UPPER
        self.tt[key] = (depth, flag, score_to_tt(best, ply), best_move)
        return best

    def qsearch(self, b, alpha, beta, ply):
        self.nodes += 1
        if self.nodes & 1023 == 0:
            self.check_time()
        best = evaluate(b)
        if best >= beta:
            return best
        if best > alpha:
            alpha = best
        us = b.side
        ki = 0 if us == WHITE else 1
        kings = b.kings
        board = b.board
        caps = b.gen_pseudo(True)
        caps.sort(key=lambda m: capture_key(board, m), reverse=True)
        for m in caps:
            b.make(m)
            if b.attacked(kings[ki], -us):
                b.unmake()
                continue
            score = -self.qsearch(b, -beta, -alpha, ply + 1)
            b.unmake()
            if score > best:
                best = score
                if score > alpha:
                    alpha = score
                    if alpha >= beta:
                        break
        return best
