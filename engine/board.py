"""Board representation, move generation and make/unmake.

10x12 mailbox: square index = 21 + file + 10 * rank, so a1 = 21, h1 = 28,
a8 = 91, h8 = 98. The two border rows/columns hold OFF so sliders and
knights stop without bounds checks. Pieces are signed ints: white positive,
black negative; side to move is WHITE (1) or BLACK (-1).

A move is an int: from | to << 7 | promo << 14 | flag << 17.
"""
import random

EMPTY, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING = 0, 1, 2, 3, 4, 5, 6
OFF = 7
WHITE, BLACK = 1, -1

KNIGHT_DIRS = (21, 19, 12, 8, -8, -12, -19, -21)
BISHOP_DIRS = (11, 9, -9, -11)
ROOK_DIRS = (10, -10, 1, -1)
KING_DIRS = BISHOP_DIRS + ROOK_DIRS

FLAG_EP, FLAG_CASTLE, FLAG_DOUBLE = 1, 2, 4
WK, WQ, BK, BQ = 1, 2, 4, 8

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
PIECE_CHARS = {PAWN: "p", KNIGHT: "n", BISHOP: "b", ROOK: "r", QUEEN: "q", KING: "k"}
CHAR_PIECES = {c: p for p, c in PIECE_CHARS.items()}


def square(file, rank):
    return 21 + file + 10 * rank


def sq_name(s):
    return "abcdefgh"[(s - 21) % 10] + str((s - 21) // 10 + 1)


def parse_sq(name):
    return square("abcdefgh".index(name[0]), int(name[1]) - 1)


def file_of(s):
    return (s - 21) % 10


def rank_of(s):
    return (s - 21) // 10


SQUARES = [square(f, r) for r in range(8) for f in range(8)]

E1, G1, C1, H1, A1 = parse_sq("e1"), parse_sq("g1"), parse_sq("c1"), parse_sq("h1"), parse_sq("a1")
E8, G8, C8, H8, A8 = parse_sq("e8"), parse_sq("g8"), parse_sq("c8"), parse_sq("h8"), parse_sq("a8")

# rights &= CASTLE_MASK[from] & CASTLE_MASK[to] after every move.
CASTLE_MASK = [15] * 120
CASTLE_MASK[E1] = 15 & ~(WK | WQ)
CASTLE_MASK[H1] = 15 & ~WK
CASTLE_MASK[A1] = 15 & ~WQ
CASTLE_MASK[E8] = 15 & ~(BK | BQ)
CASTLE_MASK[H8] = 15 & ~BK
CASTLE_MASK[A8] = 15 & ~BQ

_rng = random.Random(20261006)
ZPIECE = [[_rng.getrandbits(64) for _ in range(120)] for _ in range(13)]  # index piece + 6
ZCASTLE = [_rng.getrandbits(64) for _ in range(16)]
ZEP = [_rng.getrandbits(64) for _ in range(120)]
ZSIDE = _rng.getrandbits(64)


def make_move(fr, to, promo=0, flag=0):
    return fr | (to << 7) | (promo << 14) | (flag << 17)


def move_from(m):
    return m & 127


def move_to(m):
    return (m >> 7) & 127


def move_promo(m):
    return (m >> 14) & 7


def move_flag(m):
    return m >> 17


def move_to_uci(m):
    if not m:
        return "0000"
    s = sq_name(m & 127) + sq_name((m >> 7) & 127)
    promo = (m >> 14) & 7
    if promo:
        s += PIECE_CHARS[promo]
    return s


class Board:
    def __init__(self, fen=START_FEN):
        self.set_fen(fen)

    # ----- setup -----
    def set_fen(self, fen):
        parts = fen.split()
        while len(parts) < 6:
            parts.append(["w", "-", "-", "0", "1"][len(parts) - 1])
        b = [OFF] * 120
        for s in SQUARES:
            b[s] = EMPTY
        self.kings = [0, 0]  # [white, black]
        rows = parts[0].split("/")
        for i, row in enumerate(rows):
            rank = 7 - i
            f = 0
            for c in row:
                if c.isdigit():
                    f += int(c)
                else:
                    p = CHAR_PIECES[c.lower()]
                    piece = p if c.isupper() else -p
                    s = square(f, rank)
                    b[s] = piece
                    if p == KING:
                        self.kings[0 if piece > 0 else 1] = s
                    f += 1
        self.board = b
        self.side = WHITE if parts[1] == "w" else BLACK
        c = 0
        for ch in parts[2]:
            c |= {"K": WK, "Q": WQ, "k": BK, "q": BQ}.get(ch, 0)
        self.castling = c
        self.ep = 0 if parts[3] == "-" else parse_sq(parts[3])
        self.halfmove = int(parts[4])
        self.fullmove = int(parts[5])
        self.stack = []
        self.hash = self.compute_hash()

    def compute_hash(self):
        h = 0
        for s in SQUARES:
            p = self.board[s]
            if p:
                h ^= ZPIECE[p + 6][s]
        h ^= ZCASTLE[self.castling]
        if self.ep:
            h ^= ZEP[self.ep]
        if self.side == BLACK:
            h ^= ZSIDE
        return h

    def fen(self):
        rows = []
        for rank in range(7, -1, -1):
            row = ""
            empty = 0
            for f in range(8):
                p = self.board[square(f, rank)]
                if p == EMPTY:
                    empty += 1
                    continue
                if empty:
                    row += str(empty)
                    empty = 0
                c = PIECE_CHARS[abs(p)]
                row += c.upper() if p > 0 else c
            if empty:
                row += str(empty)
            rows.append(row)
        cast = "".join(ch for bit, ch in ((WK, "K"), (WQ, "Q"), (BK, "k"), (BQ, "q")) if self.castling & bit) or "-"
        ep = sq_name(self.ep) if self.ep else "-"
        side = "w" if self.side == WHITE else "b"
        return f"{'/'.join(rows)} {side} {cast} {ep} {self.halfmove} {self.fullmove}"

    # ----- attacks -----
    def attacked(self, s, by):
        """Is square s attacked by side `by`?"""
        b = self.board
        if by == WHITE:
            if b[s - 9] == PAWN or b[s - 11] == PAWN:
                return True
        else:
            if b[s + 9] == -PAWN or b[s + 11] == -PAWN:
                return True
        kn = KNIGHT * by
        for d in KNIGHT_DIRS:
            if b[s + d] == kn:
                return True
        k = KING * by
        for d in KING_DIRS:
            if b[s + d] == k:
                return True
        q = QUEEN * by
        bi = BISHOP * by
        for d in BISHOP_DIRS:
            t = s + d
            x = b[t]
            while x == EMPTY:
                t += d
                x = b[t]
            if x == bi or x == q:
                return True
        r = ROOK * by
        for d in ROOK_DIRS:
            t = s + d
            x = b[t]
            while x == EMPTY:
                t += d
                x = b[t]
            if x == r or x == q:
                return True
        return False

    def in_check(self, side=None):
        if side is None:
            side = self.side
        return self.attacked(self.kings[0 if side == WHITE else 1], -side)

    # ----- move generation -----
    def gen_pseudo(self, captures_only=False):
        """Pseudo-legal moves (may leave own king in check).

        With captures_only, returns captures plus queen promotions.
        """
        b = self.board
        us = self.side
        moves = []
        add = moves.append
        fwd = 10 * us
        if us == WHITE:
            start_lo, start_hi, promo_lo, promo_hi = 31, 38, 91, 98
        else:
            start_lo, start_hi, promo_lo, promo_hi = 81, 88, 21, 28
        for s in SQUARES:
            p = b[s]
            if p == EMPTY or (p > 0) != (us > 0):
                continue
            a = p if p > 0 else -p
            if a == PAWN:
                t = s + fwd
                if b[t] == EMPTY:
                    if promo_lo <= t <= promo_hi:
                        add(s | (t << 7) | (QUEEN << 14))
                        if not captures_only:
                            add(s | (t << 7) | (ROOK << 14))
                            add(s | (t << 7) | (BISHOP << 14))
                            add(s | (t << 7) | (KNIGHT << 14))
                    elif not captures_only:
                        add(s | (t << 7))
                        if start_lo <= s <= start_hi and b[t + fwd] == EMPTY:
                            add(s | ((t + fwd) << 7) | (FLAG_DOUBLE << 17))
                for t in (s + fwd - 1, s + fwd + 1):
                    q = b[t]
                    if q != OFF and q * us < 0:
                        if promo_lo <= t <= promo_hi:
                            add(s | (t << 7) | (QUEEN << 14))
                            add(s | (t << 7) | (ROOK << 14))
                            add(s | (t << 7) | (BISHOP << 14))
                            add(s | (t << 7) | (KNIGHT << 14))
                        else:
                            add(s | (t << 7))
                    elif t == self.ep:
                        add(s | (t << 7) | (FLAG_EP << 17))
            elif a == KNIGHT or a == KING:
                for d in (KNIGHT_DIRS if a == KNIGHT else KING_DIRS):
                    t = s + d
                    q = b[t]
                    if q == EMPTY:
                        if not captures_only:
                            add(s | (t << 7))
                    elif q != OFF and q * us < 0:
                        add(s | (t << 7))
            else:
                dirs = BISHOP_DIRS if a == BISHOP else ROOK_DIRS if a == ROOK else KING_DIRS
                for d in dirs:
                    t = s + d
                    q = b[t]
                    while q == EMPTY:
                        if not captures_only:
                            add(s | (t << 7))
                        t += d
                        q = b[t]
                    if q != OFF and q * us < 0:
                        add(s | (t << 7))
        if not captures_only and self.castling:
            them = -us
            if us == WHITE:
                if (self.castling & WK and b[E1 + 1] == EMPTY and b[E1 + 2] == EMPTY
                        and not self.attacked(E1, them) and not self.attacked(E1 + 1, them)
                        and not self.attacked(E1 + 2, them)):
                    add(E1 | (G1 << 7) | (FLAG_CASTLE << 17))
                if (self.castling & WQ and b[E1 - 1] == EMPTY and b[E1 - 2] == EMPTY
                        and b[E1 - 3] == EMPTY and not self.attacked(E1, them)
                        and not self.attacked(E1 - 1, them) and not self.attacked(E1 - 2, them)):
                    add(E1 | (C1 << 7) | (FLAG_CASTLE << 17))
            else:
                if (self.castling & BK and b[E8 + 1] == EMPTY and b[E8 + 2] == EMPTY
                        and not self.attacked(E8, them) and not self.attacked(E8 + 1, them)
                        and not self.attacked(E8 + 2, them)):
                    add(E8 | (G8 << 7) | (FLAG_CASTLE << 17))
                if (self.castling & BQ and b[E8 - 1] == EMPTY and b[E8 - 2] == EMPTY
                        and b[E8 - 3] == EMPTY and not self.attacked(E8, them)
                        and not self.attacked(E8 - 1, them) and not self.attacked(E8 - 2, them)):
                    add(E8 | (C8 << 7) | (FLAG_CASTLE << 17))
        return moves

    def legal_moves(self):
        us = self.side
        ki = 0 if us == WHITE else 1
        res = []
        for m in self.gen_pseudo():
            self.make(m)
            if not self.attacked(self.kings[ki], -us):
                res.append(m)
            self.unmake()
        return res

    # ----- make / unmake -----
    def make(self, m):
        b = self.board
        fr = m & 127
        to = (m >> 7) & 127
        promo = (m >> 14) & 7
        flag = m >> 17
        us = self.side
        p = b[fr]
        cap = b[to]
        h = self.hash
        self.stack.append((m, cap, self.castling, self.ep, self.halfmove, h))
        if self.ep:
            h ^= ZEP[self.ep]
        h ^= ZCASTLE[self.castling]
        b[fr] = EMPTY
        h ^= ZPIECE[p + 6][fr]
        if cap:
            h ^= ZPIECE[cap + 6][to]
        np = promo * us if promo else p
        b[to] = np
        h ^= ZPIECE[np + 6][to]
        ep = 0
        if flag:
            if flag == FLAG_EP:
                cs = to - 10 * us
                h ^= ZPIECE[-PAWN * us + 6][cs]
                b[cs] = EMPTY
            elif flag == FLAG_DOUBLE:
                ep = fr + 10 * us
            else:  # castle
                if to > fr:
                    rf, rt = fr + 3, fr + 1
                else:
                    rf, rt = fr - 4, fr - 1
                r = b[rf]
                b[rf] = EMPTY
                b[rt] = r
                h ^= ZPIECE[r + 6][rf] ^ ZPIECE[r + 6][rt]
        if p == KING * us:
            self.kings[0 if us == WHITE else 1] = to
        self.castling &= CASTLE_MASK[fr] & CASTLE_MASK[to]
        h ^= ZCASTLE[self.castling]
        if ep:
            h ^= ZEP[ep]
        self.ep = ep
        if cap or p == PAWN * us:
            self.halfmove = 0
        else:
            self.halfmove += 1
        if us == BLACK:
            self.fullmove += 1
        self.side = -us
        self.hash = h ^ ZSIDE

    def unmake(self):
        m, cap, castling, ep, halfmove, h = self.stack.pop()
        b = self.board
        us = -self.side
        self.side = us
        fr = m & 127
        to = (m >> 7) & 127
        flag = m >> 17
        p = PAWN * us if (m >> 14) & 7 else b[to]
        b[fr] = p
        b[to] = cap
        if flag:
            if flag == FLAG_EP:
                b[to - 10 * us] = -PAWN * us
            elif flag == FLAG_CASTLE:
                if to > fr:
                    rf, rt = fr + 3, fr + 1
                else:
                    rf, rt = fr - 4, fr - 1
                b[rf] = b[rt]
                b[rt] = EMPTY
        if p == KING * us:
            self.kings[0 if us == WHITE else 1] = fr
        self.castling = castling
        self.ep = ep
        self.halfmove = halfmove
        self.hash = h
        if us == BLACK:
            self.fullmove -= 1

    def make_null(self):
        h = self.hash
        self.stack.append((0, 0, self.castling, self.ep, self.halfmove, h))
        if self.ep:
            h ^= ZEP[self.ep]
        self.ep = 0
        self.halfmove += 1
        self.side = -self.side
        self.hash = h ^ ZSIDE

    def unmake_null(self):
        _, _, castling, ep, halfmove, h = self.stack.pop()
        self.side = -self.side
        self.castling = castling
        self.ep = ep
        self.halfmove = halfmove
        self.hash = h

    # ----- game state helpers -----
    def parse_uci(self, text):
        """The legal move with this UCI spelling, or None."""
        text = text.strip().lower()
        for m in self.legal_moves():
            if move_to_uci(m) == text:
                return m
        return None

    def is_repetition(self, count=1):
        """True if the current position occurred `count` times before,
        looking back only as far as the last irreversible move."""
        h = self.hash
        seen = 0
        stack = self.stack
        i = len(stack) - 2
        stop = len(stack) - self.halfmove
        while i >= stop and i >= 0:
            if stack[i][5] == h:
                seen += 1
                if seen >= count:
                    return True
            i -= 2
        return False

    def insufficient_material(self):
        minors = []
        for s in SQUARES:
            p = self.board[s]
            if p == EMPTY:
                continue
            a = abs(p)
            if a == KING:
                continue
            if a in (PAWN, ROOK, QUEEN):
                return False
            minors.append((a, (file_of(s) + rank_of(s)) % 2))
        if len(minors) <= 1:
            return True
        # Only bishops, all on the same colour of square.
        return all(a == BISHOP for a, _ in minors) and len({c for _, c in minors}) == 1
