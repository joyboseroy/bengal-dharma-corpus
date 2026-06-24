# Bengali Dharma Corpus: Tracing Buddhist and Shakta Vocabulary Across Centuries

A computational text analysis project exploring whether Buddhist Vajrayana vocabulary
survived into Bengali Shakta and Baul devotional traditions.

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
migration computationally?

---

## What I Did

### Step 1: Built a corpus of texts across six tradition layers

I collected 48 text documents spanning roughly 1,200 years of Bengali devotional
literature. The six layers follow a historical chain:

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

**Layer 4: Shakta Kali texts (14th to 18th century, Sanskrit)**
Two independent Kali Sahasranamas (1000 names of Kali), the Dakshina Kalika
Sahasranama, and related Kali stotras.

**Layer 5: Shakta Padavali (18th century, Bengali)**
The devotional songs of Ramprasad Sen, the great Bengali Shakta poet. His Kabya
Sangraha contains songs addressed to Kali, Tara, Shyama, and other goddess forms.
This text was a scanned image PDF from 1914 and required OCR processing to extract.

**Layer 6: Baul and modern Bengali devotional (18th to 19th century, Bengali)**
Songs of Lalon Fakir, the great Baul mystic, and Rabindranath Tagore's Gitanjali.

### Step 2: Processed the texts

The texts exist in three scripts: Devanagari Unicode (Sanskrit), Bengali Unicode
(Charyapada, Ramprasad, Lalon, Gitanjali), and IAST/Roman transliteration (Hevajra,
Devi Mahatmyam, and some Tara texts).

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

### The Sanskrit transmission chain

Looking only at Devanagari texts, which avoids cross-script comparison noise:

| Tradition Pair | Cosine Similarity |
|---|---|
| Buddhist Tara to Bridge Tara | 0.29 |
| Bridge Tara to Shakta Kali | 0.40 |
| Buddhist Tara to Shakta Kali | 0.31 |

The Bridge Tara cluster sits closer to Shakta Kali than to the Buddhist Tara texts
it derives from. This means the Bridge Tara tradition has linguistically moved further
toward the Shakta side than toward its Buddhist origins.

### The Bengali vernacular chain

| Tradition Pair | Cosine Similarity |
|---|---|
| Charyapada to Baul | 0.30 |
| Shakta Padavali to Baul | 0.41 |
| Buddhist Tara (Sanskrit) to Baul | 0.02 |

The Sanskrit Buddhist corpus has almost no lexical overlap with Baul Bengali (0.02).
This is partly a script effect since Devanagari and Bengali characters produce no
shared n-grams. But it also reflects a real historical gap: the Sanskrit Buddhist
tradition did not directly influence Baul vocabulary. The Old Bengali Charyapada
shows moderate similarity to Baul (0.30), which is more meaningful since both are
in Bengali script.

### Vocabulary migration in the Bridge Tara texts

Three specific Tara texts show Shakta vocabulary outnumbering Buddhist vocabulary
by ratios of 2x to 4x:

| Text | Buddhist/1k | Shakta/1k | Ratio |
|---|---|---|---|
| tArAsahasranamastotra (Brihannilatantra) | 2.3 | 7.0 | 3.0x |
| Tara Stotram / Nila Sarasvati Ashtakam | 1.6 | 4.7 | 3.0x |
| Tarashatanamastotra (Brihannilatantra) | 0.0 | 4.1 | 4.0x+ |

All three migrated texts are from the Brihannilatantra, a specific tantric tradition
known for absorbing the Buddhist Tara into Shakta worship. Other Tara texts from
different sources (Brahmayamala, Akshobhyasamhita) retain Buddhist-dominant vocabulary.

The tradition-level gradient across the Sanskrit chain:

| Tradition | Buddhist terms/1k | Shakta terms/1k | Ratio |
|---|---|---|---|
| Buddhist Tara | 4.2 | 1.2 | 0.3 (Buddhist dominant) |
| Bridge Tara | 3.6 | 3.2 | 0.9 (near parity) |
| Shakta Kali | 3.8 | 5.8 | 1.5 (Shakta dominant) |

The Bridge Tara tradition sits at almost exactly equal Buddhist and Shakta vocabulary,
which matches its historical role as the transitional layer between the two traditions.

### The Ramprasad finding

Ramprasad Sen's Kabya Sangraha (39,067 Bengali tokens, OCR) gives these counts:

- Kali mentioned 103 times
- Tara mentioned 56 times
- Ma (mother) mentioned 196 times
- Shakti mentioned 15 times
- Shiva mentioned 35 times
- Shunyata (emptiness, Buddhist term) mentioned 4 times

Ramprasad addresses Tara and Kali as interchangeable names for the same goddess.
The Shakta/Buddhist term ratio is 3.0, meaning he uses three times more Shakta
vocabulary than Buddhist vocabulary. But the Buddhist residue remains clearly present,
particularly in the continued use of Tara as a goddess name alongside Kali.

---

## Limitations and Caveats

**Script boundaries limit cross-script comparisons.** Character n-grams cannot
bridge Devanagari and Bengali script. A similarity of 0.02 between Sanskrit Buddhist
texts and Baul Bengali is partly a measurement artifact, not purely a historical
finding.

**The Charyapada corpus is very small.** The 47 surviving padas are only 843 tokens.
Similarity calculations with such a small document are less stable than with larger
corpora.

**Similarity is not the same as transmission.** High cosine similarity between two
traditions shows shared vocabulary but does not prove historical borrowing. The same
vocabulary could arise from a common source, parallel development, or genre conventions
shared across Indian devotional literature.

**The term lists are manually constructed.** The Buddhist and Shakta term lists
reflect my judgment about which words belong to each tradition. Many terms (tara,
sahaja, tantra, dakini) have been used in both traditions and their classification
is disputed.

**No statistical significance testing.** The similarity scores are point estimates
with no confidence intervals or hypothesis tests. Future work should add bootstrap
resampling to establish whether observed differences are statistically meaningful.

**The Ramprasad OCR has 5 to 10 percent character error rate.** This may affect
specific term counts but is unlikely to change the tradition-level ratios significantly.

---

## What the Results Suggest (with appropriate caution)

The analysis is consistent with (but does not prove) the historically argued Buddhist
to Shakta transmission in Bengal. Specifically:

1. Within the Sanskrit tradition, texts associated with the Brihannilatantra show
   measurably more Shakta vocabulary than Buddhist vocabulary, even though they are
   nominally Tara texts. This matches the historical identification of the
   Brihannilatantra as a key site of Buddhist to Shakta absorption.

2. The Bridge Tara tradition sits at vocabulary parity between Buddhist and Shakta,
   which is consistent with its role as a transitional layer.

3. Ramprasad Sen's Kali songs preserve significant Tara vocabulary, supporting the
   view that Tara and Kali were treated as forms of the same goddess in 18th-century
   Bengal.

4. The Sanskrit Buddhist tradition has very low lexical overlap with Baul Bengali,
   suggesting the transmission from Buddhism to Baul ran through the vernacular
   Charyapada tradition rather than the Sanskrit textual tradition.

---

## Files in This Repository

```
analyze_corpus.py          Main analysis script
patch_v3.py                Supplementary analysis with normalized scores
charyapada_core.txt        Clean reconstruction of the 47 Charyapada padas
ocr_ramprasad_v2.sh        Shell script for OCR of the Ramprasad PDF
corpus_analysis_results.txt Full per-document term counts
similarity_matrix.csv      Full pairwise cosine similarity matrix (50x50)
corpus_pca_plot.png        PCA visualization of the corpus
```

The full text corpus files (Sanskrit stotras, Ramprasad OCR, Lalon songs, Gitanjali)
are not included in this repository due to copyright considerations for modern editions.
Sources are documented in the script comments.

---

## Dependencies

```bash
pip3 install scikit-learn numpy matplotlib pandas pdfminer.six beautifulsoup4 lxml --break-system-packages
```

For OCR of the Ramprasad PDF:
```bash
# Tesseract with Bengali language model
wget "https://github.com/tesseract-ocr/tessdata/raw/main/ben.traineddata" \
     -O ~/tessdata/ben.traineddata
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
