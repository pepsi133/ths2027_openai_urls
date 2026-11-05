#!/usr/bin/env python3
"""Large-sample entropy tests on ChatGPT UUIDv8 share/conversation ids.

Usage: python3 -I corpus_stats.py uuids.txt [more.txt ...]
Input: one UUID per line, any order, duplicates allowed (deduplicated here).
Layout assumed (checked, not trusted): 32b unix s | 14b subsec + 2b zero | ver 8 | 12b node | 2b var | 62b random.
"""
import sys, math, collections, datetime, re

RX = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-8[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$')

def load(paths):
    s = set()
    for p in paths:
        for line in open(p, encoding='utf-8', errors='replace'):
            u = line.strip().lower()
            if RX.match(u):
                s.add(u)
    return sorted(s)

def fields(u):
    h = u.replace('-', '')
    ts = int(h[0:8], 16); seg2 = int(h[8:12], 16); node = int(h[13:16], 16)
    r = int(h[16:32], 16) & ((1 << 62) - 1)
    return ts, seg2, node, r

def z_binom(k, n, p=0.5):
    return (k - n * p) / math.sqrt(n * p * (1 - p))

def main():
    U = load(sys.argv[1:])
    n = len(U)
    print(f"unique v8 uuids: {n}")
    if n < 20:
        print("too few samples"); return
    F = [fields(u) for u in U]
    ts = [f[0] for f in F]
    print(f"time span: {datetime.datetime.fromtimestamp(min(ts), datetime.timezone.utc):%Y-%m-%d} .. "
          f"{datetime.datetime.fromtimestamp(max(ts), datetime.timezone.utc):%Y-%m-%d}")

    # --- segment 2: low 2 bits, and the pre/post 2024-10-28 ceiling
    low2 = collections.Counter(f[1] & 3 for f in F)
    print(f"\nseg2 low 2 bits: {dict(low2)}  (layout predicts only 0)")
    cut = 1730073600  # 2024-10-28 UTC
    pre = [f[1] >> 2 for f in F if f[0] < cut]; post = [f[1] >> 2 for f in F if f[0] >= cut]
    if pre:  print(f"seg2>>2 before 2024-10-28: n={len(pre)} max={max(pre)} (ns>>16 model predicts <=15258)")
    if post: print(f"seg2>>2 after  2024-10-28: n={len(post)} max={max(post)} mean={sum(post)/len(post):.0f} (uniform predicts ~8191)")

    # --- node distribution over time
    nodes = collections.Counter(f[2] for f in F)
    print(f"\nnode ids seen: {len(nodes)}; top: {[(hex(k), v) for k, v in nodes.most_common(12)]}")
    bym = collections.defaultdict(collections.Counter)
    for f in F:
        bym[datetime.datetime.fromtimestamp(f[0], datetime.timezone.utc).strftime('%Y-%m')][f[2]] += 1
    print("nodes per month (distinct):", {m: len(c) for m, c in sorted(bym.items())})

    # --- 62-bit random field tests
    R = [f[3] for f in F]
    # per-bit frequency
    worst = []
    for b in range(62):
        k = sum((r >> b) & 1 for r in R)
        worst.append((abs(z_binom(k, n)), b, k))
    worst.sort(reverse=True)
    print(f"\nper-bit ones count, 62 bits, n={n}: worst |z| = {worst[0][0]:.2f} at bit {worst[0][1]} (k={worst[0][2]})"
          f"; bits with |z|>3: {sum(1 for w in worst if w[0] > 3)} (expect ~0.17)")
    # nibble chi-square
    chi = 0.0
    for nib in range(15):
        c = collections.Counter((r >> (4 * nib)) & 0xF for r in R)
        e = n / 16
        chi += sum((c[v] - e) ** 2 / e for v in range(16))
    print(f"nibble chi-square (15 nibbles x 15 df = 225 df): {chi:.1f}  (mean 225, sd 21.2; >280 is suspicious)")
    # top 2 bits of the field (bits 60,61) separately since they sit after the variant
    c = collections.Counter((r >> 60) & 3 for r in R)
    print(f"bits 60-61 distribution: {dict(sorted(c.items()))}")
    # serial correlation of consecutive ids ordered by time
    order = sorted(range(n), key=lambda i: (F[i][0], F[i][1]))
    xs = [R[i] / 2 ** 62 for i in order]
    mx = sum(xs) / n
    num = sum((xs[i] - mx) * (xs[i + 1] - mx) for i in range(n - 1))
    den = sum((x - mx) ** 2 for x in xs)
    print(f"lag-1 serial correlation (time order): {num / den:.4f}  (random ~0 +/- {1 / math.sqrt(n):.4f})")
    # counter test: within the same node, fraction of consecutive ids whose 62-bit field increases
    inc = tot = 0
    for a, b in zip(order, order[1:]):
        if F[a][2] == F[b][2]:
            tot += 1; inc += R[b] > R[a]
    if tot: print(f"same-node consecutive pairs: {tot}, fraction increasing {inc / tot:.3f} (counter -> ~1.0, random -> 0.5)")
    # Hamming distance between time-adjacent ids
    hd = [bin(R[a] ^ R[b]).count('1') for a, b in zip(order, order[1:])]
    print(f"Hamming distance time-adjacent (62 bits): mean {sum(hd) / len(hd):.2f}, min {min(hd)}, max {max(hd)} (random 31.0 +/- 3.94)")
    # duplicates and shared prefixes in the random field
    cnt = collections.Counter(r >> 30 for r in R)
    print(f"collisions on top 32 bits of random field: {sum(v - 1 for v in cnt.values() if v > 1)} (birthday expectation {n * (n - 1) / 2 / 2 ** 32:.3f})")
    # same-second groups
    bysec = collections.defaultdict(list)
    for f in F: bysec[f[0]].append(f)
    multi = {k: v for k, v in bysec.items() if len(v) > 1}
    print(f"\nseconds holding >1 id: {len(multi)}")
    for k, v in list(sorted(multi.items()))[:5]:
        print("  ", k, [(hex(x[1]), hex(x[2]), hex(x[3])[:8]) for x in v])

if __name__ == '__main__':
    main()
