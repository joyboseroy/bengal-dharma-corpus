"""
Bengal Dharma Corpus Analysis — v2
Handles: .txt (Devanagari/Latin/Bengali), .htm/.html, .pdf (via pdfminer)

Usage:
  cd /mnt/c/Users/ebosjoy/Downloads/sanskritdocs
  pip3 install scikit-learn numpy matplotlib pandas pdfminer.six beautifulsoup4 lxml --break-system-packages
  python3 analyze_corpus.py

Outputs:
  corpus_analysis_results.txt
  similarity_matrix.csv
  corpus_pca_plot.png
"""

import os, re, sys
from pathlib import Path
from collections import Counter

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA

CORPUS_DIR = Path(".")

# ── TRADITION MAP ─────────────────────────────────────────────────────────────
# Keys are substrings matched case-insensitively against filename stem
TRADITION_MAP = {
    # Layer 1: Pure Vajrayana Buddhist
    "aryataranamaskaraikavimshati": "Buddhist_Tara",
    "arya tara stutih":            "Buddhist_Tara",
    "aryatarasragdhara":           "Buddhist_Tara",
    "aryatara ashtottarashata":    "Buddhist_Tara",
    "shrItArAdhyAnam":             "Buddhist_Tara",
    "shritaradhyanam":             "Buddhist_Tara",
    "prajnaparamita":              "Buddhist_Tara",
    "nairatma":                    "Buddhist_Tara",
    "vajradevi":                   "Buddhist_Tara",
    "vajrayoginipranamaikavishika":"Buddhist_Tara",
    "vajrayoginyah pindartha":     "Buddhist_Tara",
    "vasudhara":                   "Buddhist_Tara",
    "hevajra":                     "Buddhist_Tara",
    "aryamanjushrimula":           "Buddhist_Tara",   # HTM files
    "aryamanjujzrimulakalpam": "Buddhist_Tara",

    # Layer 2: Charyapada — Old Bengali Buddhist (8th-12th c.)
"charyapada_core":  "Charyapada",   # MUST come before "charyapada"
"charyapada":       "Charyapada",
"charypada":        "Charyapada", 

    # Layer 3: Bridge Tara (Buddhist Tara in Shakta framing)
    "nila sarasvati":              "Bridge_Tara",
    "nilasarasvati":               "Bridge_Tara",
    "tara stotram or tara ashtakam":"Bridge_Tara",
    "tarakavacham":                "Bridge_Tara",
    "tarasahasranamastotra":       "Bridge_Tara",
    "shri tara sahasranama":       "Bridge_Tara",
    "shri tara shatanama":         "Bridge_Tara",
    "shri tara takaradi":          "Bridge_Tara",
    "shri tarashatanama":          "Bridge_Tara",
    "tarashatanamastotra":         "Bridge_Tara",
    "mahogratara":                 "Bridge_Tara",
    "ugratara":                    "Bridge_Tara",

    # Layer 4: Shakta Kali
    "shri kali sahasranama":       "Shakta_Kali",
    "dakshinakalika":              "Shakta_Kali",
    "shri kali shatanama":         "Shakta_Kali",
    "shri kali tandava":           "Shakta_Kali",
    "kali stava brahmakritam":     "Shakta_Kali",
    "dakshaprokta kali":           "Shakta_Kali",

    # Layer 4: Shakta Durga
    "devi mahatmyam":              "Shakta_Durga",
    "durga saptashati":            "Shakta_Durga",
    "durgastutiH":                 "Shakta_Durga",
    "durgastutiessence":           "Shakta_Durga",
    "markandeya":                  "Shakta_Durga",
    "mahishasuramardini":          "Shakta_Durga",
    "bhagavatIpadya":              "Shakta_Durga",
    "part of bhagavati":           "Shakta_Durga",

    # Layer 5: Shakta Padavali (Bengali, 18th c.)
    "ramprasad":                   "Shakta_Padavali",
    "kabya sangraha":              "Shakta_Padavali",

"gitagovinda":              "Vaishnava_Sanskrit",
"bhakti rasamrita sindhu":  "Vaishnava_Bengali",
"bhakti_rasamrita":         "Vaishnava_Bengali",
"chaitanya charita":        "Vaishnava_Bengali",
"sri chaitanya":            "Vaishnava_Bengali",
"srikrishna kirtan":        "Vaishnava_Bengali",
"candidas krishna":         "Vaishnava_Bengali",

    # Layer 6: Baul / Modern Bengali
    "lalan":                       "Baul_Bengali",
    "lalon":                       "Baul_Bengali",
    "gitanjali":                   "Baul_Bengali",
    "geetanjali":                  "Baul_Bengali",
}

TRADITION_COLORS = {
    "Buddhist_Tara":    "#1a5fa8",
    "Charyapada":       "#7b3fa8",
    "Bridge_Tara":      "#2e9e6e",
    "Shakta_Kali":      "#c0392b",
    "Shakta_Durga":     "#8e44ad",
    "Shakta_Padavali":  "#e67e22",
    "Baul_Bengali":     "#16a085",
    "Unknown":          "#888888",
}

TRADITION_ORDER = [
    "Buddhist_Tara", "Charyapada", "Bridge_Tara",
    "Shakta_Kali", "Shakta_Durga", "Shakta_Padavali", "Baul_Bengali",
]

# ── TERM LISTS ────────────────────────────────────────────────────────────────
BUDDHIST_TERMS = [
    "बुद्ध", "बोधिसत्त्व", "बोधि", "करुणा", "प्रज्ञा", "शून्य", "तथागत",
    "वज्र", "नैरात्म", "सहज", "महासुख", "योगिनी", "डाकिनी", "हेवज्र",
    "तारा", "चर्या",
]
SHAKTA_TERMS = [
    "शक्ति", "शिव", "महादेव", "पार्वती", "दुर्गा", "काली", "महाविद्या",
    "तन्त्र", "मन्त्र", "यन्त्र", "कुल", "श्रीविद्या", "भैरव",
]
SHARED_TERMS = [
    "करुणा", "मोक्ष", "मुक्ति", "भय", "रक्षा", "सिद्धि",
    "नमः", "देवी", "माता", "अम्बा", "श्री", "लोक",
]
# Bengali terms for Charyapada / Baul layers
BENGALI_BUDDHIST = ["বোধি", "করুণা", "শূন্য", "সহজ", "বজ্র", "তারা"]
BENGALI_SHAKTA   = ["কালী", "দুর্গা", "শক্তি", "শিব", "তন্ত্র"]
BENGALI_BAUL     = ["মন", "প্রেম", "আত্মা", "গুরু", "সাধন", "ভক্তি"]


# ── FILE LOADERS ──────────────────────────────────────────────────────────────
def load_txt(path):
    return path.read_text(encoding="utf-8", errors="replace")

def load_htm(path):
    try:
        from bs4 import BeautifulSoup
        html = path.read_text(encoding="utf-8", errors="replace")
        soup = BeautifulSoup(html, "lxml")
        return soup.get_text(separator=" ")
    except ImportError:
        # fallback: strip tags with regex
        text = path.read_text(encoding="utf-8", errors="replace")
        return re.sub(r'<[^>]+>', ' ', text)

import logging
logging.getLogger("pdfminer").setLevel(logging.ERROR)
def load_pdf(path):
    try:
        from pdfminer.high_level import extract_text
        return extract_text(str(path))
    except ImportError:
        print(f"  [WARN] pdfminer not installed — skipping {path.name}")
        print(f"         pip3 install pdfminer.six --break-system-packages")
        return ""
    except Exception as e:
        print(f"  [WARN] PDF read error {path.name}: {e}")
        return ""

def load_file(path):
    ext = path.suffix.lower()
    if ext == ".txt":
        return load_txt(path)
    elif ext in (".htm", ".html"):
        return load_htm(path)
    elif ext == ".pdf":
        return load_pdf(path)
    return ""


# ── CLASSIFY ──────────────────────────────────────────────────────────────────
def classify(stem):
    sl = stem.lower().replace("_", " ")
    for key in sorted(TRADITION_MAP.keys(), key=len, reverse=True):
        if key.lower() in sl:
            return TRADITION_MAP[key]
    return "Unknown"

# ── TOKEN EXTRACTION ──────────────────────────────────────────────────────────
def script_profile(text):
    deva  = len(re.findall(r'[\u0900-\u097F]', text))
    bengali = len(re.findall(r'[\u0980-\u09FF]', text))
    latin = len(re.findall(r'[a-zA-Z]', text))
    return deva, bengali, latin

def extract_tokens(stem, text):
    deva, bengali, latin = script_profile(text)
    dominant = max(deva, bengali, latin)
    if dominant == deva:
        tokens = re.findall(r'[\u0900-\u097F]+', text)
        tokens = [t for t in tokens if not re.fullmatch(r'[\u0966-\u096F।॥]+', t)]
        return tokens, "devanagari"
    elif dominant == bengali:
        tokens = re.findall(r'[\u0980-\u09FF]+', text)
        tokens = [t for t in tokens if not re.fullmatch(r'[\u09E6-\u09EF।॥]+', t)]
        return tokens, "bengali"
    else:
        stopwords = {'the','and','for','that','this','with','from','are',
                     'was','her','his','she','not','but','have','you',
                     'all','who','may','thy','thee','unto','upon','which'}
        tokens = [w.lower() for w in re.findall(r'[a-zA-Z]{3,}', text)
                  if w.lower() not in stopwords]
        return tokens, "latin"


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    print("="*72)
    print("  BENGAL DHARMA CORPUS ANALYSIS  v2")
    print("  Buddhist Tara → Charyapada → Bridge → Shakta → Baul")
    print("="*72)

    extensions = {".txt", ".htm", ".html", ".pdf"}
    paths = sorted(p for p in CORPUS_DIR.iterdir()
                   if p.suffix.lower() in extensions
                   and not p.name.startswith("corpus_")
                   and not p.name.startswith("similarity_")
                   and p.name != "analyze_corpus.py")

    records = []
    corpus_strings = []

    print(f"\nLoading {len(paths)} files...\n")

    for path in paths:
        text = load_file(path)
        if not text.strip():
            print(f"  EMPTY  {path.name}")
            continue

        tokens, script = extract_tokens(path.stem, text)
        if len(tokens) < 10:
            print(f"  SKIP   {path.name} (only {len(tokens)} tokens)")
            continue

        tradition = classify(path.stem)
        char_str  = " ".join(tokens)

        # Term counts — use appropriate list by script
        if script == "bengali":
            b_score  = sum(text.count(t) for t in BENGALI_BUDDHIST)
            s_score  = sum(text.count(t) for t in BENGALI_SHAKTA)
            sh_score = sum(text.count(t) for t in BENGALI_BAUL)
        else:
            tc = Counter(tokens)
            b_score  = sum(tc[t] for t in BUDDHIST_TERMS)
            s_score  = sum(tc[t] for t in SHAKTA_TERMS)
            sh_score = sum(tc[t] for t in SHARED_TERMS)

        record = {
            "stem": path.stem,
            "name": path.name[:48],
            "tradition": tradition,
            "script": script,
            "n_tokens": len(tokens),
            "char_str": char_str,
            "b_score": b_score,
            "s_score": s_score,
            "sh_score": sh_score,
        }
        records.append(record)
        corpus_strings.append(char_str)

        print(f"  {path.name[:50]:52} {tradition:18} {script:11}"
              f"  tok={len(tokens):5}  B={b_score:3}  S={s_score:3}  Sh={sh_score:3}")

    if len(records) < 3:
        print("\nToo few documents. Check file paths.")
        sys.exit(1)

    # ── TF-IDF ────────────────────────────────────────────────────────────
    print("\n" + "="*72)
    print("  TF-IDF VECTORIZATION (char 3-5 grams)")
    print("="*72)

    vec = TfidfVectorizer(
        analyzer='char_wb', ngram_range=(3, 5),
        min_df=1, max_features=25000, sublinear_tf=True,
    )
    tfidf = vec.fit_transform(corpus_strings)
    sim   = cosine_similarity(tfidf)
    stems = [r["stem"] for r in records]

    pd.DataFrame(sim, index=stems, columns=stems).to_csv("similarity_matrix.csv")
    print("Saved: similarity_matrix.csv\n")

    # ── CROSS-TRADITION AVERAGES ───────────────────────────────────────────
    def avg(tA, tB):
        iA = [i for i,r in enumerate(records) if r["tradition"]==tA]
        iB = [i for i,r in enumerate(records) if r["tradition"]==tB]
        if not iA or not iB:
            return None
        vals = [sim[i][j] for i in iA for j in iB if i!=j]
        return np.mean(vals) if vals else None

    pairs = [
        ("Buddhist_Tara",   "Charyapada",      "Buddhist Tara  →  Charyapada"),
        ("Buddhist_Tara",   "Bridge_Tara",     "Buddhist Tara  →  Bridge Tara"),
        ("Charyapada",      "Bridge_Tara",     "Charyapada     →  Bridge Tara"),
        ("Bridge_Tara",     "Shakta_Kali",     "Bridge Tara    →  Shakta Kali"),
        ("Buddhist_Tara",   "Shakta_Kali",     "Buddhist Tara  →  Shakta Kali"),
        ("Buddhist_Tara",   "Shakta_Durga",    "Buddhist Tara  →  Shakta Durga"),
        ("Bridge_Tara",     "Shakta_Durga",    "Bridge Tara    →  Shakta Durga"),
        ("Shakta_Kali",     "Shakta_Durga",    "Kali           →  Durga (within Shakta)"),
        ("Shakta_Kali",     "Shakta_Padavali", "Shakta Kali    →  Shakta Padavali"),
        ("Shakta_Padavali", "Baul_Bengali",    "Shakta Padavali→  Baul"),
        ("Charyapada",      "Baul_Bengali",    "Charyapada     →  Baul (long arc)"),
        ("Buddhist_Tara",   "Baul_Bengali",    "Buddhist Tara  →  Baul (full arc)"),
        ("Bridge_Tara",     "Vaishnava_Sanskrit", "Bridge Tara    →  Vaishnava Sanskrit"),
("Buddhist_Tara",   "Vaishnava_Sanskrit", "Buddhist Tara  →  Vaishnava Sanskrit"),
("Shakta_Kali",     "Vaishnava_Bengali",  "Shakta Kali    →  Vaishnava Bengali"),
("Vaishnava_Bengali","Baul_Bengali",      "Vaishnava Bengali → Baul"),
("Vaishnava_Sanskrit","Shakta_Kali",      "Vaishnava Sanskrit → Shakta Kali"),
    ]

    print("\n--- Cross-tradition cosine similarity (avg) ---\n")
    result_lines = []
    for tA, tB, label in pairs:
        v = avg(tA, tB)
        if v is not None:
            bar = "█" * int(v * 50)
            line = f"  {label:48} {v:.4f}  {bar}"
        else:
            trad_a_count = sum(1 for r in records if r["tradition"]==tA)
            trad_b_count = sum(1 for r in records if r["tradition"]==tB)
            line = f"  {label:48} N/A (A:{trad_a_count} docs, B:{trad_b_count} docs)"
        print(line)
        result_lines.append(line)

    # ── SYNCRETISM SUMMARY ────────────────────────────────────────────────
    print("\n--- Per-file term scores ---\n")
    print(f"  {'FILE':50} {'TRADITION':18} {'Buddhist':8} {'Shakta':6} {'Shared/Baul':11}")
    print("  " + "-"*100)
    sync_lines = []
    for r in records:
        line = (f"  {r['stem'][:50]:52} {r['tradition']:18}"
                f"  {r['b_score']:7}  {r['s_score']:5}  {r['sh_score']:10}")
        print(line)
        sync_lines.append(line)

    # Key finding: which Bridge Tara texts have more Shakta than Buddhist terms?
    print("\n--- KEY FINDING: Bridge Tara texts — Buddhist vs Shakta vocabulary ---\n")
    bridge = [r for r in records if r["tradition"] == "Bridge_Tara"]
    for r in sorted(bridge, key=lambda x: x["s_score"] - x["b_score"], reverse=True):
        ratio = r["s_score"] / max(r["b_score"], 1)
        flag = "  *** MIGRATED" if ratio >= 2 else ""
        print(f"  {r['stem'][:45]:47}  B={r['b_score']:3}  S={r['s_score']:3}"
              f"  Shakta/Buddhist ratio={ratio:.1f}{flag}")

    # ── SAVE RESULTS ──────────────────────────────────────────────────────
    with open("corpus_analysis_results.txt", "w", encoding="utf-8") as f:
        f.write("BENGAL DHARMA CORPUS ANALYSIS v2\n" + "="*72 + "\n\n")
        f.write("CROSS-TRADITION SIMILARITIES\n\n")
        f.write("\n".join(result_lines))
        f.write("\n\nPER-FILE TERM SCORES\n\n")
        f.write("\n".join(sync_lines))
    print("\nSaved: corpus_analysis_results.txt")

    # ── PCA PLOT ──────────────────────────────────────────────────────────
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches

        n_components = min(2, tfidf.shape[0] - 1, tfidf.shape[1] - 1)
        pca    = PCA(n_components=2, random_state=42)
        coords = pca.fit_transform(tfidf.toarray())

        fig, axes = plt.subplots(1, 2, figsize=(18, 8))

        # ── Left: PCA scatter ──────────────────────────────────────────
        ax = axes[0]
        for i, r in enumerate(records):
            color = TRADITION_COLORS.get(r["tradition"], "#888")
            marker = "o" if r["script"] == "devanagari" else \
                     "s" if r["script"] == "bengali" else "^"
            ax.scatter(coords[i,0], coords[i,1], color=color,
                       marker=marker, s=90, zorder=3, alpha=0.85)
            ax.annotate(r["stem"][:28], (coords[i,0], coords[i,1]),
                        fontsize=6.5, ha='left', va='bottom',
                        xytext=(3,3), textcoords='offset points')

        patches = [mpatches.Patch(color=c, label=t)
                   for t,c in TRADITION_COLORS.items() if t!="Unknown"]
        ax.legend(handles=patches, fontsize=8, loc='upper left')
        ax.set_title("PCA — TF-IDF char n-grams\n(○=Devanagari  □=Bengali  △=Latin)",
                     fontsize=10)
        ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)")
        ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)")
        ax.grid(True, alpha=0.3)

        # ── Right: Syncretism heatmap bar chart ────────────────────────
        ax2 = axes[1]
        traditions_present = [t for t in TRADITION_ORDER
                              if any(r["tradition"]==t for r in records)]
        b_avgs  = [np.mean([r["b_score"]  for r in records if r["tradition"]==t]) or 0
                   for t in traditions_present]
        s_avgs  = [np.mean([r["s_score"]  for r in records if r["tradition"]==t]) or 0
                   for t in traditions_present]
        sh_avgs = [np.mean([r["sh_score"] for r in records if r["tradition"]==t]) or 0
                   for t in traditions_present]

        x = np.arange(len(traditions_present))
        w = 0.25
        ax2.bar(x - w, b_avgs,  w, label="Buddhist terms", color="#1a5fa8", alpha=0.8)
        ax2.bar(x,     s_avgs,  w, label="Shakta terms",   color="#c0392b", alpha=0.8)
        ax2.bar(x + w, sh_avgs, w, label="Shared/Baul",    color="#2e9e6e", alpha=0.8)
        ax2.set_xticks(x)
        ax2.set_xticklabels([t.replace("_","\n") for t in traditions_present],
                            fontsize=8)
        ax2.set_ylabel("Avg term count per document")
        ax2.set_title("Vocabulary Syncretism by Tradition\n(Buddhist vs Shakta term density)")
        ax2.legend(fontsize=8)
        ax2.grid(True, alpha=0.3, axis='y')

        fig.suptitle("Bengali Dharma Corpus: Tracing Buddhist→Shakta Vocabulary Drift",
                     fontsize=12, fontweight='bold')
        fig.tight_layout()
        fig.savefig("corpus_pca_plot.png", dpi=150)
        print("Saved: corpus_pca_plot.png")

    except Exception as e:
        print(f"Plot error: {e}")

    print("\n" + "="*72)
    print("  DONE")
    print("  Files: similarity_matrix.csv  corpus_analysis_results.txt  corpus_pca_plot.png")
    print("="*72)


if __name__ == "__main__":
    main()
