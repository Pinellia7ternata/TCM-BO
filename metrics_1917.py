# -*- coding: utf-8 -*-
"""TCM_BO metrics via ElementTree (robust to nested anonymous class expressions).
Per-IRI aggregation over owl:Class declarations; measures 1.9.17."""
import io, sys
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from pathlib import Path
import xml.etree.ElementTree as ET

NS = "http://OntoTCM.org.cn/ontologies/"
BASE = Path(r"D:\2026年\课题\自主课题\身体结构\2026 更新protege")
RDF = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}'
RDFS = '{http://www.w3.org/2000/01/rdf-schema#}'
OWL = '{http://www.w3.org/2002/07/owl#}'
XML = '{http://www.w3.org/XML/1998/namespace}'

def measure(ver):
    tree = ET.parse(str(BASE / f"TCM_BO_{ver}.owl"))
    root = tree.getroot()
    decl_class, decl_ind = set(), set()
    objprops = 0
    tags = defaultdict(set)          # iri -> direct child local names
    zh, en = defaultdict(bool), defaultdict(bool)
    parents = defaultdict(set)       # iri -> parent IRIs (resource subClassOf only)
    for child in root:
        about = child.get(RDF + 'about')
        tag = child.tag.split('}')[-1]
        if tag == 'Class' and about:
            decl_class.add(about)
        elif tag == 'NamedIndividual' and about:
            decl_ind.add(about)
        elif tag == 'ObjectProperty':
            objprops += 1
        if not (about and about.startswith(NS)):
            continue
        for sub in child:
            stag = sub.tag.split('}')[-1]
            tags[about].add(stag)
            if sub.tag == RDFS + 'label':
                lang = sub.get(XML + 'lang')
                if lang == 'zh-cn': zh[about] = True
                elif lang == 'en': en[about] = True
            elif sub.tag == RDFS + 'subClassOf':
                p = sub.get(RDF + 'resource')
                if p and p.startswith(NS):
                    parents[about].add(p)
    n = len(decl_class)
    def has(t): return sum(1 for iri in decl_class if t in tags.get(iri, set()))
    # depth via longest path over equivalence-merged graph
    uf = {}
    def find(x):
        uf.setdefault(x, x)
        while uf[x] != x: uf[x] = uf[uf[x]]; x = uf[x]
        return x
    for child in root:
        about = child.get(RDF + 'about')
        if child.tag == OWL + 'Class' and about:
            for sub in child:
                if sub.tag == OWL + 'equivalentClass':
                    p = sub.get(RDF + 'resource')
                    if p:
                        ra, rb = find(about), find(p)
                        if ra != rb: uf[rb] = ra
    # also EquivalentClasses via rdf:Description? (none observed) — skip
    sub = defaultdict(set)
    for c in decl_class:
        rc = find(c)
        for p in parents.get(c, ()):
            rp = find(p)
            if rp != rc: sub[rc].add(rp)
    dmax = {}
    def depth(c, stack=()):
        c = find(c)
        if c in dmax: return dmax[c]
        ps = sub.get(c, ())
        if not ps or c in stack:
            dmax[c] = 1; return 1
        dmax[c] = 1 + max(depth(p, stack + (c,)) for p in ps)
        return dmax[c]
    dist = defaultdict(int)
    for c in decl_class: dist[depth(c)] += 1
    multi = sum(1 for c in decl_class if len(sub.get(find(c), ())) > 1)
    return dict(classes=n, inds=len(decl_ind), objprops=objprops,
                zh=sum(1 for iri in decl_class if zh[iri]), en=sum(1 for iri in decl_class if en[iri]),
                icd=has('ICD11ID_data'), fma=has('FMAID'), sno=has('SNOMEDID'),
                syn=has('TCM_TO_0000036'), defin=has('TCM_TO_0000035'),
                depth=dict(sorted(dist.items())), multi=multi)

for ver in ("1.9.17",):
    r = measure(ver)
    n = r["classes"]
    print(f"== {ver}: classes={n} individuals={r['inds']} objprops={r['objprops']}")
    print(f"   zh={r['zh']} ({r['zh']/n*100:.1f}%)  en={r['en']} ({r['en']/n*100:.1f}%)")
    print(f"   definition={r['defin']} ({r['defin']/n*100:.1f}%)  synonym={r['syn']} ({r['syn']/n*100:.1f}%)")
    print(f"   ICD={r['icd']} ({r['icd']/n*100:.1f}%)  FMA={r['fma']} ({r['fma']/n*100:.1f}%)  SNOMED={r['sno']} ({r['sno']/n*100:.1f}%)")
    print(f"   multi-parent={r['multi']}")
    print(f"   depth(longest)={r['depth']}")
