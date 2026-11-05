"""Adversarial recompute of scripts/cost.py under attacker-favorable assumptions.
Layout: 32b seconds | 14b sub-second + 00 | ver 8 | 12b node | 2b variant | 62b random."""
import math
Y=365.25*86400
def years(space,rate): return space/2/rate/Y
print("== Node count correction: Hindsight table lists 7 current nodes (1000-1006), not 3 ==")
for nodes in (3,7):
    sp=2**62*2**14*nodes
    print(f"  nodes={nodes}: second known -> space 2^{math.log2(sp):.2f}; years at 1e7 req/s = {years(sp,1e7):.2e}")
print("\n== Most attacker-favorable: node fixed, sub-second known, exact second known ==")
for rate in (1e7,1e8,1e9):
    print(f"  rate {rate:.0e}: 2^62 -> {years(2**62,rate):.3e} years per targeted link")
print("\n== Flip points: random bits b at which expected time to one targeted hit drops to T ==")
for T,name in ((Y,'1 year'),(7*86400,'1 week'),(86400,'1 day'),(3600,'1 hour')):
    for rate in (1e7,1e8):
        b=math.log2(2*rate*T)
        print(f"  {name:7s} at {rate:.0e} req/s: b = {b:.1f} bits")
print("\n== Untargeted break-even (author's '~32 bits'): k links/s, rate R, 1 hit/year, nodes N ==")
for k,R,N in ((100,1e5,3),(100,1e5,7),(1000,1e7,7),(1000,1e8,1)):
    # hits/yr = k/(N*2^(14+b)) * R * Y = 1
    b=math.log2(k*R*Y/N)-14
    print(f"  k={k}, R={R:.0e}, N={N}: break-even b = {b:.1f} bits")
print("\n== Sub-second oracle check on own 5 links (from backend-api create_time) ==")
d=[+5.0,+5.3,+4.3,+5.2,+5.2]
print(f"  create_time - (id_seconds + id_frac/16384): {d} ms; spread {max(d)-min(d):.1f} ms")
p=(0.012)**5
print(f"  P(5 random 14-bit values all land within a 12 ms window of create_time) ~ {p:.1e}")
