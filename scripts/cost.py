import math
# Layout confirmed from samples + Hindsight/unfurl analyses:
# 32b unix seconds | 14b subsecond + '00' | ver 8 | 12b node | 2b variant | 62b random
U="""6aec6686-4d9c-83ed-b905-76a831afef31
6aec66a2-44d4-83ed-b8b6-98eccf6e2d70
6aec66ab-da64-83ed-8b90-b70c1685a603
6aec66be-b140-83eb-be00-98c77bd09c63
6aec67a7-0e30-83ed-827c-a20ea452bc88""".split()
print("Low 2 bits of seg2:", [format(int(u[9:13],16)&3,'02b') for u in U], "(random: P(all five ==00)=1/1024)")
print("Sub-second (14b/16384 s):", [round((int(u[9:13],16)>>2)/16384,4) for u in U])
RAND=62; NODES=3; SUB=14
sec_year=365.25*86400
scen={
 "A: second+subsecond+node known (oracle)": 2**RAND,
 "B: exact second known, node unknown":    2**RAND*2**SUB*NODES,
 "C: creation hour known":                 2**RAND*2**SUB*NODES*3600,
 "D: creation day known":                  2**RAND*2**SUB*NODES*86400,
}
rates={"1e3 req/s":1e3,"1e5 req/s":1e5,"1e7 req/s (botnet)":1e7}
print("\nTARGETED guess: expected requests = space/2; years at rate")
for k,sp in scen.items():
    print(f"  {k}: space=2^{math.log2(sp):.1f}")
    for rn,r in rates.items(): print(f"      {rn}: {sp/2/r/sec_year:.2e} years")
print("\nUNTARGETED (any share, any time): P(hit per guess)=k/(NODES*2^(14+62)) with k=links created per second")
for k in (10,100,1000):
    p=k/(NODES*2**(SUB+RAND))
    for rn,r in rates.items():
        print(f"  k={k}/s, {rn}: expected hits in 1 year = {p*r*sec_year:.2e}")
print("\nWhat residual entropy would the Substack '6% hit rate' imply? bits = -log2(0.06/k_density)")
for k in (10,100,1000):
    print(f"  k={k}/s: ~{math.log2(k/0.06):.1f} bits total per-second space (vs 3-node floor 2^{math.log2(NODES)+SUB+RAND:.1f})")
print("\nBreak-even: residual random bits at which untargeted 1e5 req/s yields >=1 hit/year, k=100/s:")
for b in range(10,64,4):
    hits=100/(NODES*2**(SUB+b))*1e5*sec_year
    print(f"  {b} random bits -> {hits:.2e} hits/yr")
