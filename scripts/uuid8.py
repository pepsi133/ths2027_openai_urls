import datetime, itertools, math, statistics
U = """6aec6686-4d9c-83ed-b905-76a831afef31
6aec66a2-44d4-83ed-b8b6-98eccf6e2d70
6aec66ab-da64-83ed-8b90-b70c1685a603
6aec66be-b140-83eb-be00-98c77bd09c63
6aec67a7-0e30-83ed-827c-a20ea452bc88""".split()

def bits(u): return bin(int(u.replace('-',''),16))[2:].zfill(128)
rows=[]
print("idx  ts(UTC)               seg2    ver  seg3  var  seg4(14b) seg5(48b)")
for i,u in enumerate(U):
    h=u.replace('-','')
    ts=int(h[0:8],16); s2=int(h[8:12],16); ver=int(h[12],16); s3=int(h[13:16],16)
    var=int(h[16],16)>>2; s4=int(h[16:20],16)&0x3fff; s5=int(h[20:32],16)
    t=datetime.datetime.fromtimestamp(ts,datetime.timezone.utc)
    rows.append((ts,s2,ver,s3,var,s4,s5))
    print(f"{i}  {t:%Y-%m-%d %H:%M:%S} {ts}  {s2:04x}  {ver:x}  {s3:03x}  {var:02b}  {s4:04x}      {s5:012x}")

# 48-bit ms interpretation check (UUIDv7-style)
ms=int(U[0].replace('-','')[:12],16)
print("\n48-bit prefix as ms since epoch ->", ms, "=", ms/1000/86400/365.25, "years: NOT a v7 ms timestamp")
# 32s + 16-bit fraction interpretation
print("seg2 as fraction of a second (s2/65536):", [round(r[1]/65536,4) for r in rows])

# Residual 78 bits = seg2(16) + seg4 low 14 + seg5 48
def resid(r): return (r[1]<<62)|(r[5]<<48)|r[6]
R=[resid(r) for r in rows]
print("\nHamming distance between consecutive residual 78-bit fields:")
for a,b in zip(R,R[1:]): print("  ", bin(a^b).count('1'))
print("All pairs:", [bin(a^b).count('1') for a,b in itertools.combinations(R,2)])
n=78; mean=n/2; sd=math.sqrt(n/4)
print(f"Random expectation: {mean} +/- {sd:.2f} per pair (binomial n=78,p=.5)")
# Monotonic / counter check per field
for name,idx in (("seg2",1),("seg4",5),("seg5",6)):
    v=[r[idx] for r in rows]
    d=[b-a for a,b in zip(v,v[1:])]
    print(f"{name}: values={[hex(x) for x in v]} deltas={d} monotonic={'yes' if all(x>0 for x in d) or all(x<0 for x in d) else 'no'}")
# bit-position frequency across the 5 samples (weak with n=5, but detect stuck bits)
B=[bin(x)[2:].zfill(78) for x in R]
stuck=[p for p in range(78) if len({b[p] for b in B})==1]
print(f"\nBit positions constant across all 5 samples: {len(stuck)} (random expectation {78*2*(0.5**5):.1f})")
ones=sum(b.count('1') for b in B); print(f"Ones fraction: {ones}/{5*78} = {ones/(5*78):.3f}")
