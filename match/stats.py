"""Match statistics: score, Elo difference and its 95% interval.

Games are played in pairs (same opening, colours swapped), so the error is
computed from the pair scores ("pentanomial" model), which accounts for the
correlation inside a pair. The trinomial (per-game) interval is reported too.
"""
import math

Z95 = 1.959964


def elo(score):
    """Elo difference for an expected score in (0, 1)."""
    score = min(max(score, 1e-6), 1 - 1e-6)
    return -400 * math.log10(1 / score - 1)


def interval(mean, sd, n):
    if n < 2:
        return float("-inf"), float("inf")
    se = sd / math.sqrt(n)
    return elo(mean - Z95 * se), elo(mean + Z95 * se)


def summarize(games):
    """`games`: dicts with 'pair' (opening index) and 'score' (1, 0.5, 0 for
    the candidate). Returns a dict of results."""
    n = len(games)
    if not n:
        return {"games": 0}
    w = sum(1 for g in games if g["score"] == 1)
    d = sum(1 for g in games if g["score"] == 0.5)
    l = n - w - d
    mean = (w + 0.5 * d) / n
    var = (w * (1 - mean) ** 2 + d * (0.5 - mean) ** 2 + l * mean ** 2) / n
    tri_lo, tri_hi = interval(mean, math.sqrt(var), n)

    pairs = {}
    for g in games:
        pairs.setdefault(g["pair"], []).append(g["score"])
    full = [sum(v) / 2 for v in pairs.values() if len(v) == 2]
    penta = [0] * 5
    for v in pairs.values():
        if len(v) == 2:
            penta[int(sum(v) * 2)] += 1
    if len(full) >= 2:
        pm = sum(full) / len(full)
        pvar = sum((x - pm) ** 2 for x in full) / len(full)
        lo, hi = interval(pm, math.sqrt(pvar), len(full))
    else:
        lo, hi = tri_lo, tri_hi
    e = elo(mean)
    return {
        "games": n, "wins": w, "draws": d, "losses": l,
        "score": round(mean, 4),
        "elo": round(e, 1),
        "elo_lo": round(lo, 1), "elo_hi": round(hi, 1),
        "elo_err": round((hi - lo) / 2, 1),
        "trinomial_lo": round(tri_lo, 1), "trinomial_hi": round(tri_hi, 1),
        "pentanomial": penta,  # pair scores 0, 0.5, 1, 1.5, 2
        "clear_win": lo > 0,
    }


def format_summary(s):
    if not s.get("games"):
        return "no games"
    return (f"{s['games']} games  +{s['wins']} ={s['draws']} -{s['losses']}  "
            f"score {s['score'] * 100:.1f}%  Elo {s['elo']:+.1f} "
            f"[{s['elo_lo']:+.1f}, {s['elo_hi']:+.1f}] (95%, pairs {s['pentanomial']})  "
            f"{'CLEAR WIN' if s['clear_win'] else 'not clear'}")
