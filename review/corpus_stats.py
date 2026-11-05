"""Large-sample check of the 62-bit random field on archived share-link IDs.
Input: Wayback CDX rows 'original_url wayback_timestamp' (one per line), one or more files.
Run: python3 -I review/corpus_stats.py file1 [file2 ...]"""
import re,sys,math,datetime,collections
UU=re.compile(r'/share/(?:e/)?([0-9a-f]{8})-([0-9a-f]{4})-([0-9a-f]{4})-([0-9a-f]{4})-([0-9a-f]{12})(?![0-9a-f])',re.I)
ids={} ; ver=collections.Counter()
for fn in sys.argv[1:]:
    for line in open(fn,errors='replace'):
        parts=line.split()
        if not parts: continue
        m=UU.search(parts[0])
        if not m: continue
        h=''.join(m.groups()).lower()
        ver[h[12]]+=1
        cap=parts[1] if len(parts)>1 else None
        ids.setdefault(h,cap)
print("distinct share UUIDs:",len(ids)," version nibble counts:",dict(sorted(ver.items())))
v8=[(h,c) for h,c in ids.items() if h[12]=='8' and int(h[16],16)>>2==2]
print("UUIDv8 with RFC variant:",len(v8))
if not v8: sys.exit()
# timestamps
ts=[int(h[:8],16) for h,_ in v8]
d=lambda t: datetime.datetime.fromtimestamp(t,datetime.timezone.utc).strftime('%Y-%m-%d')
print("embedded time range:",d(min(ts)),"to",d(max(ts)))
# capture-vs-embedded sanity (embedded must not exceed first capture)
late=0; chk=0
for h,c in v8:
    if c and len(c)>=14:
        chk+=1
        capt=datetime.datetime.strptime(c[:14],'%Y%m%d%H%M%S').replace(tzinfo=datetime.timezone.utc).timestamp()
        if int(h[:8],16)>capt+60: late+=1
print(f"embedded time later than first capture (+60s): {late}/{chk}")
# low 2 bits of seg2
low=collections.Counter(int(h[8:12],16)&3 for h,_ in v8)
print("low 2 bits of seg2:",dict(low))
# sub-second uniformity (14-bit >> 4 = 1024 buckets)
sub=[int(h[8:12],16)>>2 for h,_ in v8]
print("sub-second 14-bit: min",min(sub),"max",max(sub))
# node
node=collections.Counter(int(h[13:16],16) for h,_ in v8)
print("node values:",len(node)," top:",node.most_common(12))
# per-year node sets
by=collections.defaultdict(set)
for h,_ in v8: by[d(int(h[:8],16))[:7]].add(int(h[13:16],16))
for k in sorted(by): print("  ",k,sorted(by[k])[:20],"..." if len(by[k])>20 else "")
# 62-bit random field: hex[16:32] minus variant bits
R=[int(h[16:32],16)&((1<<62)-1) for h,_ in v8]
n=len(R)
ones=[0]*62
for r in R:
    for b in range(62):
        if r>>b&1: ones[b]+=1
sd=math.sqrt(n*0.25)
z=[(o-n/2)/sd for o in ones]
print(f"per-bit ones (n={n}): max |z| = {max(abs(x) for x in z):.2f}; bits with |z|>3: {[i for i,x in enumerate(z) if abs(x)>3]}")
print("  expected max |z| over 62 bits under H0 ~ 2.4-2.9")
chi=sum(((o-n/2)**2)/(n/4) for o in ones)
print(f"  chi-square(62 dof) for bit frequencies: {chi:.1f} (mean 62, sd 11.1)")
# adjacent-bit correlation within an ID
pairs=0; eq=0
for r in R:
    for b in range(61):
        pairs+=1; eq+= ((r>>b)&1)==((r>>(b+1))&1)
print(f"adjacent-bit equality: {eq/pairs:.4f} (random 0.5000, sd {0.5/math.sqrt(pairs):.4f})")
# byte-value chi-square over the 7 full bytes of the 62-bit field
bc=collections.Counter()
for r in R:
    for k in range(7): bc[(r>>(8*k))&0xff]+=1
tot=sum(bc.values()); e=tot/256
chi=sum(((bc[v]-e)**2)/e for v in range(256))
print(f"byte-value chi-square(255 dof): {chi:.1f} (mean 255, sd 22.6)")
# duplicates / collisions in the 62-bit field
print("duplicate 62-bit fields:",n-len(set(R)))
# sorted-by-time: Hamming between time-adjacent IDs on same node (counter/LCG would show low or structured distance)
v8s=sorted(v8,key=lambda x:(int(x[0][13:16],16),int(x[0][:8],16),int(x[0][8:12],16)))
hd=[]
for (a,_),(b,_) in zip(v8s,v8s[1:]):
    if a[13:16]==b[13:16] and abs(int(a[:8],16)-int(b[:8],16))<=60:
        ra=int(a[16:],16)&((1<<62)-1); rb=int(b[16:],16)&((1<<62)-1)
        hd.append(bin(ra^rb).count('1'))
if hd:
    print(f"Hamming between same-node IDs within 60 s: n={len(hd)}, mean {sum(hd)/len(hd):.2f} (random 31.0 sd 3.94), min {min(hd)}, max {max(hd)}")
# xor-difference / arithmetic-difference test for LCG-like structure on time-adjacent same-node pairs
dif=[]
for (a,_),(b,_) in zip(v8s,v8s[1:]):
    if a[13:16]==b[13:16] and abs(int(a[:8],16)-int(b[:8],16))<=60:
        ra=int(a[16:],16)&((1<<62)-1); rb=int(b[16:],16)&((1<<62)-1)
        dif.append((rb-ra)%(1<<62))
if dif:
    c=collections.Counter(dif).most_common(1)[0]
    print(f"most common arithmetic difference among {len(dif)} adjacent pairs occurs {c[1]} times (counter/LCG would repeat)")
# same-second pairs
ss=collections.Counter(h[:8]+h[13:16] for h,_ in v8)
print("same-second same-node groups:",sum(1 for v in ss.values() if v>1))
