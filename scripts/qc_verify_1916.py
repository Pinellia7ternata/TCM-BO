# -*- coding: utf-8 -*-
"""1.9.16 验证: ofn 视图重扫推断类型冲突 + 非对称环(含sameAs聚合)"""
import re, io, os, sys, subprocess
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r"D:\2026年\课题\自主课题\身体结构"
SRC = os.path.join(BASE, r"2026 更新protege\TCM_BO_1.9.16.owl")
OFN = os.path.join(BASE, "qc_1916_v.ofn")
subprocess.run([os.path.join(BASE, r"tools\jre\bin\java.exe"), '-Xmx4g', '-jar',
                os.path.join(BASE, r"tools\robot.jar"), 'convert', '--input', SRC,
                '--format', 'ofn', '--output', OFN], check=True, capture_output=True)
ofn = open(OFN, encoding='utf-8').read()
def loc(s):
    m = re.search(r'(TCM_[A-Z]+_\d+)$', s); return m.group(1) if m else s.split(':')[-1]
parent=defaultdict(set); disj=set(); props=defaultdict(lambda:{'dom':set(),'rng':set(),'inv':set(),'sup':set(),'asym':False})
ind_types=defaultdict(set); edges=defaultdict(set); sames=[]
for ln in ofn.split('\n'):
    ln=ln.strip()
    m=re.match(r'SubClassOf\((\S+) (\S+)\)$',ln)
    if m: parent[loc(m.group(1))].add(loc(m.group(2)))
    m=re.match(r'DisjointClasses\(([^)]+)\)$',ln)
    if m:
        mem=[loc(x) for x in m.group(1).split()]
        for i in range(len(mem)):
            for j in range(i+1,len(mem)): disj.add(frozenset((mem[i],mem[j])))
    m=re.match(r'ObjectPropertyDomain\((\S+) (\S+)\)$',ln)
    if m: props[loc(m.group(1))]['dom'].add(loc(m.group(2)))
    m=re.match(r'ObjectPropertyRange\((\S+) (\S+)\)$',ln)
    if m: props[loc(m.group(1))]['rng'].add(loc(m.group(2)))
    m=re.match(r'InverseObjectProperties\((\S+) (\S+)\)$',ln)
    if m: a,b=loc(m.group(1)),loc(m.group(2)); props[a]['inv'].add(b); props[b]['inv'].add(a)
    m=re.match(r'SubObjectPropertyOf\((\S+) (\S+)\)$',ln)
    if m: props[loc(m.group(1))]['sup'].add(loc(m.group(2)))
    m=re.match(r'AsymmetricObjectProperty\((\S+)\)$',ln)
    if m: props[loc(m.group(1))]['asym']=True
    m=re.match(r'ClassAssertion\((\S+) (\S+)\)$',ln)
    if m: ind_types[loc(m.group(2))].add(loc(m.group(1)))
    m=re.match(r'ObjectPropertyAssertion\((\S+) (\S+) (\S+)\)$',ln)
    if m: edges[loc(m.group(1))].add((loc(m.group(2)),loc(m.group(3))))
    m=re.match(r'SameIndividual\((\S+) (\S+)\)$',ln)
    if m: sames.append((loc(m.group(1)),loc(m.group(2))))
anc_cache={}
def anc(x):
    if x in anc_cache: return anc_cache[x]
    seen=set(); st=[x]
    while st:
        c=st.pop()
        if c in seen: continue
        seen.add(c); st.extend(parent.get(c,()))
    anc_cache[x]=seen; return seen
def clash(t1,t2):
    for x in anc(t1):
        for y in anc(t2):
            if frozenset((x,y)) in disj: return (x,y)
    return None
def eff(p):
    dom,rng=set(),set(); seen=set(); st=[p]
    while st:
        q=st.pop()
        if q in seen: continue
        seen.add(q); dom|=props[q]['dom']; rng|=props[q]['rng']; st.extend(props[q]['sup'])
        for iv in props[q]['inv']: rng|=props[iv]['dom']; dom|=props[iv]['rng']
    return dom,rng
infer=defaultdict(set)
for p,es in edges.items():
    dom,rng=eff(p)
    for s,o in es:
        for d in dom: infer[s].add(d)
        for r in rng: infer[o].add(r)
bad=0
for ind in sorted(set(list(ind_types)+list(infer))):
    ts=sorted(ind_types.get(ind,set())|infer.get(ind,set()))
    for i in range(len(ts)):
        for j in range(i+1,len(ts)):
            c=clash(ts[i],ts[j])
            if c: bad+=1; print(f"残余冲突 {ind}: {ts[i]} ⊥ {ts[j]} 经 {c}")
print(f"推断类型冲突: {bad}")
# 非对称环 (含 sameAs 聚合)
cluster=defaultdict(set)
for a,b in sames: cluster[a].add(b); cluster[b].add(a)
def cl(x):
    seen={x}; st=[x]
    while st:
        c=st.pop()
        for y in cluster.get(c,set()):
            if y not in seen: seen.add(y); st.append(y)
    return seen
asym_props=[p for p in props if props[p]['asym']]
viol=0
for p in asym_props:
    pe=edges.get(p,set())
    norm=set()
    for s,o in pe:
        for cs in cl(s):
            for co in cl(o):
                if cs<co or True: norm.add((cs,co))
    nset=set()
    for s,o in pe:
        nset.add((frozenset(cl(s)),frozenset(cl(o))))
    for a,b in nset:
        if a==b: print(f"自环(聚合)[{p[-3:]}]: {a}"); viol+=1
        if (b,a) in nset: print(f"互指(聚合)[{p[-3:]}]: {a} <-> {b}"); viol+=1
print(f"非对称违规(聚合): {viol}")
print(f"sameAs 剩余: {len(sames)}")
