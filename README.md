# Bengal Dharma Corpus: Tracing Buddhist, Shakta and Vaishnava Vocabulary Across Centuries

A computational text analysis project exploring how Buddhist Vajrayana vocabulary
survived and transformed across Bengali Shakta, Vaishnava and Baul devotional traditions
over twelve centuries.

**Structured dataset on HuggingFace:** https://huggingface.co/datasets/joyboseroy/bengal-dharma-corpus

---

## What This Project Is About

Scholars of Indian religious history have long argued that the Buddhist Vajrayana
tradition of Bengal (8th to 12th century CE) did not simply disappear when the Pala
dynasty collapsed and the great monasteries like Nalanda and Vikramashila were destroyed.
Instead, Buddhist vocabulary, goddess figures, and devotional practices were gradually
absorbed into the Shakta Tantra tradition and later into the Baul folk religion of Bengal.

The goddess Tara is a good example. In Vajrayana Buddhism, Tara is a bodhisattva of
compassion. In the Shakta tradition of the same region, Tara becomes one of the ten
Mahavidyas, a fierce goddess associated with Kali. In the 18th century, the Bengali
poet Ramprasad Sen addresses Tara and Kali almost interchangeably in his devotional
songs. The Baul singers of Bengal carry forward many themes from the earlier Sahajiya
Buddhist tradition.

This project asks: can we see this process in the words themselves? If Buddhist
vocabulary migrated into Shakta and Baul texts over centuries, can we measure that
migration computationally? And how does the Buddhist-Shakta connection compare to the
parallel Vaishnava tradition, which developed in the same region at the same time?

---

## What I Did

### Step 1: Built a corpus of texts across eight tradition layers

I collected 75 text documents spanning roughly 1,200 years of Bengali and Sanskrit
devotional literature across three major traditions. The eight layers follow a
historical chain:

**Layer 1: Vajrayana Buddhist Tara texts (8th to 12th century, Sanskrit)**
Hymns to Tara, Vajrayogini, Vajradevi, Prajnaparamita. Hevajra Tantra excerpts.
These are the oldest Buddhist Sanskrit sources in the corpus.

**Layer 2: Charyapada (8th to 12th century, Old Bengali)**
The 47 surviving mystical songs attributed to the Buddhist Mahasiddhas. The oldest
known literature in the Bengali language. Written in an archaic form of Bengali
called sandhya bhasha (twilight language).

**Layer 3: Bridge Tara texts (12th to 16th century, Sanskrit)**
Texts that present the Buddhist goddess Tara in an explicitly Shakta framing. The
Brihannilatantra tradition is the main source here. These texts worship Tara as
Nila Sarasvati, a Shakta goddess, using both Buddhist and Shakta vocabulary.

**Layer 4: Vaishnava Sanskrit (12th century, Sanskrit)**
The Gitagovinda by Jayadeva, the foundational Sanskrit Vaishnava poem describing
the love of Radha and Krishna. Serves as the control tradition: same century and
language as the Bridge Tara texts, but a completely separate religious lineage.

**Layer 5: Shakta Kali and Durga texts (14th to 18th century, Sanskrit)**
Two independent Kali Sahasranamas, the Dakshina Kalika Sahasranama, Durga Saptashati,
and related stotras.

**Layer 6: Vaishnava Bengali (14th to 16th century, Bengali)**
Srikrishna Kirtan by Badu Chandidas (14th-15th century Old Bengali), Bhakti
Rasamrita Sindhu Bengali translation (16th century), and the Chaitanya Charitamrita
by Krishnadas Kaviraj (16th century Bengali). Represents the Chaitanya Vaishnava
tradition which developed in Bengal parallel to the Shakta tradition.

**Layer 7: Shakta Padavali (18th century, Bengali)**
The devotional songs of Ramprasad Sen, the great Bengali Shakta poet. His Kabya
Sangraha contains songs addressed to Kali, Tara, Shyama, and other goddess forms.
This text was a scanned image PDF from 1914 and required OCR processing to extract.

**Layer 8: Baul and modern Bengali devotional (18th to 19th century, Bengali)**
Songs of Lalon Fakir, the great Baul mystic, and Rabindranath Tagore's Gitanjali.

### Step 2: Processed the texts

The texts exist in three scripts: Devanagari Unicode (Sanskrit), Bengali Unicode
(Charyapada, Ramprasad, Lalon, Gitanjali, Vaishnava Bengali), and IAST/Roman
transliteration (Hevajra, Devi Mahatmyam, Gitagovinda, and some Tara texts).

The Ramprasad Sen corpus was a 372-page scanned book. I used Tesseract OCR with the
Bengali language model to extract text, producing 39,067 Bengali tokens.

The Charyapada file I initially had was contaminated with modern Bengali commentary
from a critical edition, inflating it to 45,000 tokens. After discovering this problem
I replaced it with a clean reconstruction of the 47 core padas (843 tokens), which
is the correct size for 47 short songs.

### Step 3: Vectorized the texts and computed similarities

I used TF-IDF vectorization with character n-grams of length 3 to 5. Character n-grams
work well for Sanskrit and Bengali because:

- Sanskrit is highly inflected. The same root appears in many forms. Character n-grams
  capture shared root syllables like tar, karun, vajr, bhay without needing a
  morphological analyzer.
- The method is robust to OCR noise, which matters for the Ramprasad material.

I then computed cosine similarity between all document pairs and averaged similarities
within and across tradition groups.

### Step 4: Counted Buddhist and Shakta vocabulary directly

In parallel with the n-gram similarity analysis, I counted specific term lists directly
in each document, normalizing by document length (per 1,000 tokens).

Buddhist terms counted (Devanagari): Buddha, bodhisattva, bodhi, karuna, prajna,
shunya, tathagata, vajra, nairatma, sahaja, mahasukha, yogini, dakini, hevajra.

Shakta terms counted (Devanagari): shakti, shiva, mahadeva, parvati, durga, kali,
mahavidya, tantra, mantra, yantra, kula, shrividya, bhairava.

---

## Results

### The key specificity finding: Buddhist-Shakta versus Vaishnava

The most important result in the corpus is a comparison between traditions.

| Tradition Pair | Cosine Similarity |
|---|---|
| Bridge Tara to Shakta Kali | 0.54 |
| Buddhist Tara to Shakta Kali | 0.44 |
| Buddhist Tara to Vaishnava Sanskrit | 0.06 |
| Bridge Tara to Vaishnava Sanskrit | 0.06 |
| Vaishnava Sanskrit to Shakta Kali | 0.00 |

The Gitagovinda is a 12th-century Sanskrit poem, the same century as many Bridge
Tara texts, the same language, the same broad devotional genre. Its similarity to
Shakta Kali is zero. The Bridge Tara texts are 8.5 times more similar to Shakta
Kali than to Vaishnava Sanskrit. This shows the Buddhist-Shakta vocabulary overlap
is not a generic property of Sanskrit devotional literature. It is specific to
the Buddhist-Shakta transmission chain.

### The Sanskrit transmission chain

| Tradition Pair | Cosine Similarity |
|---|---|
| Buddhist Tara to Bridge Tara | 0.43 |
| Bridge Tara to Shakta Kali | 0.54 |
| Buddhist Tara to Shakta Kali | 0.44 |

The Bridge Tara tradition has moved linguistically further toward the Shakta side
than toward its Buddhist origins.

### The Bengali vernacular chain

| Tradition Pair | Cosine Similarity |
|---|---|
| Shakta Padavali to Baul | 0.40 |
| Charyapada to Baul | 0.31 |
| Vaishnava Bengali to Baul | 0.29 |
| Buddhist Tara (Sanskrit) to Baul | 0.02 |

Both the Buddhist Sahajiya chain (via Charyapada) and the Vaishnava Bengali chain
contribute to Baul vocabulary, with the Buddhist chain (0.31) marginally stronger
than the Vaishnava chain (0.29). The Sanskrit Buddhist tradition has near-zero
overlap with modern Bengali devotional vocabulary.

### Vocabulary migration in the Bridge Tara texts

Three specific Tara texts show Shakta vocabulary outnumbering Buddhist vocabulary
by ratios of 2x to 4x:

| Text | Buddhist/1k | Shakta/1k | Ratio |
|---|---|---|---|
| tArAsahasranamastotra (Brihannilatantra) | 2.3 | 7.0 | 3.0x |
| Tara Stotram / Nila Sarasvati Ashtakam | 1.6 | 4.7 | 3.0x |
| Tarashatanamastotra (Brihannilatantra) | 0.0 | 4.1 | 4.0x+ |

All three migrated texts are from the Brihannilatantra tradition. Tara texts from
other lineages (Brahmayamala, Takaradi) retain Buddhist-dominant vocabulary.

The tradition-level vocabulary gradient across the Sanskrit chain:

| Tradition | Buddhist/1k | Shakta/1k | Ratio |
|---|---|---|---|
| Buddhist Tara | 4.2 | 1.2 | 0.3 (Buddhist dominant) |
| Bridge Tara | 3.6 | 3.2 | 0.9 (near parity) |
| Shakta Kali | 3.8 | 5.8 | 1.5 (Shakta dominant) |

### The Ramprasad finding

Ramprasad Sen's Kabya Sangraha (39,067 Bengali tokens, OCR) gives these counts:

- Kali: 103 mentions
- Tara: 56 mentions
- Ma (mother): 196 mentions
- Shakti: 15 mentions
- Shiva: 35 mentions
- Shunyata (Buddhist emptiness term): 4 mentions

Ramprasad addresses Tara and Kali as interchangeable names for the same goddess,
six centuries after the Pala monasteries were destroyed. Buddhist vocabulary
residue is still present in 18th-century Bengali Kali songs.

---

## Limitations and Caveats

**Script boundaries limit cross-script comparisons.** Character n-grams cannot
bridge Devanagari and Bengali script. A similarity of 0.02 between Sanskrit Buddhist
texts and Baul Bengali is partly a measurement artifact.

**The Charyapada corpus is very small.** The 47 surviving padas are only 843 tokens.

**Several large Bengali text files contain modern commentary.** The Candidas, Bhakti
Rasamrita Sindhu, and Chaitanya Charitamrita files are archive.org full-text dumps
that include scholarly introductions and footnotes alongside the original verses.
Token counts reflect the full file, not just the verse content.

**Similarity is not the same as transmission.** High cosine similarity shows shared
vocabulary but does not prove historical borrowing.

**The term lists are manually constructed** and reflect subjective judgments about
which words belong to which tradition.

**No statistical significance testing.** Similarity scores are point estimates
without confidence intervals. Bootstrap resampling is planned for a future version.

**Ramprasad OCR has 5 to 10 percent character error rate.**

---

## What the Results Suggest (with appropriate caution)

1. The Buddhist-Shakta vocabulary overlap is specific to the Buddhist-Shakta
   transmission chain, not a general property of Sanskrit devotional literature.
   The Gitagovinda (Vaishnava Sanskrit, 12th century) has zero similarity to
   Shakta Kali, while Bridge Tara texts (Buddhist-Shakta, same century) have
   0.54 similarity. This is the strongest evidence the corpus provides.

2. Within the Sanskrit tradition, three Brihannilatantra Tara texts show Shakta
   vocabulary at 2 to 4 times the density of Buddhist vocabulary, measuring the
   vocabulary migration in specific texts.

3. The Bridge Tara tradition sits at vocabulary parity between Buddhist and Shakta,
   consistent with its role as the transitional layer.

4. Ramprasad Sen's Kali songs preserve significant Tara vocabulary six centuries
   after the Pala monasteries were destroyed.

5. Both the Buddhist Sahajiya chain (Charyapada) and the Vaishnava Bengali chain
   contribute to Baul vocabulary, with the Buddhist chain marginally stronger.

---

## Files in This Repository

```
analyze_corpus.py              Main analysis script (handles .txt, .htm, .pdf)
patch_v3.py                    Supplementary: normalized term scores, Devanagari subset
generate_hf_tables.py          Generates HuggingFace dataset CSV tables
charyapada_core.txt            Clean reconstruction of the 47 Charyapada padas
ocr_ramprasad_v2.sh            Shell script for OCR of the Ramprasad PDF
corpus_analysis_results.txt    Full per-document term counts
similarity_matrix.csv          Full pairwise cosine similarity matrix (75x75)
corpus_pca_plot.png            PCA visualization of the corpus
```

The full text corpus files are not included in this repository due to copyright
considerations for modern editions. Sources are documented in the script comments
and in the HuggingFace dataset card.

---

## Dependencies

```bash
pip3 install scikit-learn numpy matplotlib pandas pdfminer.six beautifulsoup4 lxml --break-system-packages
```

For OCR of the Ramprasad PDF:
```bash
wget "https://github.com/tesseract-ocr/tessdata/raw/main/ben.traineddata" \
     -O ~/tessdata/ben.traineddata
bash ocr_ramprasad_v2.sh
```

---

## Related Work

This project builds on the Darshana-Graph knowledge graph of Indian philosophical
traditions: https://github.com/joyboseroy/darshana-graph (arXiv:2606.18222)

---

## License

Code: MIT License
Text reconstructions (Charyapada core): Public domain
Analysis results: CC BY 4.0
