# -*- coding: utf-8 -*-
"""Generate manuscript figures from measured TCM_BO 1.8.0 metrics."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(sys.executable).parent.parent.parent))
from daimon_runtime import setup_plot
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

setup_plot()
OUT = Path(r"D:\2026年\课题\自主课题\身体结构\manuscript\figures")
OUT.mkdir(parents=True, exist_ok=True)

# ---------- Figure 2: metrics panels ----------
# depth: longest asserted subClassOf path, equivalence-merged hierarchy; measured 1.9.17
depth_dist = {1:3, 2:6, 3:29, 4:15, 5:27, 6:100, 7:90, 8:54, 9:98,
              10:689, 11:925, 12:474, 13:474, 14:259, 15:208, 16:136, 17:96}
coverage = pd.DataFrame({
    "Item": ["rdfs:label\nZH / EN", "Textual\ndefinition", "Exact\nsynonym",
             "ICD-11\nmapping", "FMA\nmapping", "SNOMED CT\nmapping",
             "Logical\nrestriction"],
    "Percent": [100.0, 15.2, 0.9, 86.1, 71.6, 16.0, 3.4],
})

fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
ax = axes[0]
df_d = pd.DataFrame({"Hierarchy depth": list(depth_dist.keys()), "Classes": list(depth_dist.values())})
sns.barplot(data=df_d, x="Hierarchy depth", y="Classes", color="#4C72B0", ax=ax)
ax.set_title("A. Class distribution by hierarchy depth (max = 17)")
ax.set_xlabel("Depth level"); ax.set_ylabel("Number of classes")
ax.tick_params(axis='x', labelsize=8)

ax = axes[1]
sns.barplot(data=coverage, x="Item", y="Percent", color="#55A868", ax=ax)
ax.set_title("B. Annotation / mapping / axiom coverage, release 1.9.17 (n = 3,683)")
ax.set_xlabel(""); ax.set_ylabel("Coverage (%)")
ax.tick_params(axis='x', labelsize=8)
for p in ax.patches:
    ax.annotate(f"{p.get_height():.1f}", (p.get_x()+p.get_width()/2, p.get_height()+1),
                ha="center", fontsize=7)
ax.set_ylim(0, 108)
fig.tight_layout()
fig.savefig(OUT / "fig2_metrics.png", dpi=300, bbox_inches="tight")
plt.close(fig)

# ---------- Figure 1: construction pipeline ----------
fig, ax = plt.subplots(figsize=(11, 5.6))
ax.axis("off"); ax.set_xlim(0, 100); ax.set_ylim(0, 56)

def box(x, y, w, h, text, fc="#EAF1FB", ec="#4C72B0", fs=8.6):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.6",
                                fc=fc, ec=ec, lw=1.2))
    ax.text(x+w/2, y+h/2, text, ha="center", va="center", fontsize=fs)

def arrow(x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=14, color="#666666", lw=1.2))

box(2, 42, 20, 10, "TCM body-structure\nterm bank (中医身体结构术语)", "#FDF3E7", "#C4863A")
box(2, 28, 20, 10, "Modern-medicine body-\nstructure term bank (现代医学术语)", "#FDF3E7", "#C4863A")
box(2, 14, 20, 10, "Reference standards\nICD-11 · FMA · SNOMED CT", "#FDF3E7", "#C4863A")
box(30, 28, 20, 24, "Manual curation &\nconceptual modelling\n(Protégé, OWL DL)\n\n· bilingual labels/definitions\n· TCM-specific relations\n  (开窍于 / 在体合 / 相表里 / 志藏于)\n· part–whole & spatial relations")
box(58, 28, 18, 24, "Semi-automatic\nmapping pipeline\n\n· lexical & fuzzy matching\n· identifier assignment\n· expert review")
box(58, 6, 18, 14, "Quality control\n· consistency (DL reasoner)\n· cycle / duplicate checks\n· mapping audit & kappa")
box(84, 28, 14, 24, "TCM-BO\nrelease\n\n3,683 classes\n29 obj. prop.\n612 individuals\nv1.9.17")
arrow(22, 47, 30, 44); arrow(22, 33, 30, 36); arrow(22, 19, 30, 32)
arrow(50, 40, 58, 40); arrow(76, 40, 84, 40)
arrow(67, 28, 67, 20)
fig.savefig(OUT / "fig1_pipeline.png", dpi=300, bbox_inches="tight")
plt.close(fig)

print("saved:", list(OUT.iterdir()))
