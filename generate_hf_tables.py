"""
Generate HuggingFace dataset tables from corpus analysis results.
Run from: /mnt/c/Users/ebosjoy/Downloads/sanskritdocs/
Output: data/documents.csv, data/pairwise_similarities.csv

Usage: python3 generate_hf_tables.py
"""

import os, re, csv
import pandas as pd

# ── Document metadata ─────────────────────────────────────────────────
# Hand-curated from corpus analysis results
DOCUMENTS = [
    # doc_id | title | tradition | century | language | script | source | url | notes
    ("buddhist_tara_21praises",     "Aryataranamaskaraikavimshati Stotra (21 Praises to Tara)",     "Buddhist_Tara",     "8th-12th c.",  "Sanskrit",    "Devanagari", "Vajrayana Buddhist",       "https://sanskritdocuments.org/doc_devii/", 201,  0.0,  5.0, 0.0),
    ("buddhist_tara_108names",      "Aryatara Ashtottarashata Nama Stotra (108 Names)",             "Buddhist_Tara",     "8th-12th c.",  "Sanskrit",    "Devanagari", "Vajrayana Buddhist",       "https://sanskritdocuments.org/doc_devii/", 474,  4.2,  2.1, 0.5),
    ("buddhist_tara_sragdhara",     "Aryatarasragdhara Stotram",                                    "Buddhist_Tara",     "8th-12th c.",  "Sanskrit",    "Devanagari", "Vajrayana Buddhist",       "https://sanskritdocuments.org/doc_devii/", 447,  2.2,  0.0, 0.0),
    ("buddhist_nairatma",           "Nairatmashtaka Stotram",                                       "Buddhist_Tara",     "8th-12th c.",  "Sanskrit",    "Devanagari", "Vajrayana Buddhist",       "https://sanskritdocuments.org/doc_devii/", 64,   0.0,  0.0, 0.0),
    ("buddhist_prajnaparamita",     "Prajnaparamita Stotram",                                       "Buddhist_Tara",     "8th-12th c.",  "Sanskrit",    "Devanagari", "Vajrayana Buddhist",       "https://sanskritdocuments.org/doc_devii/", 187,  0.0,  0.0, 0.0),
    ("buddhist_vajradevi",          "Vajradevi Stotram",                                            "Buddhist_Tara",     "8th-12th c.",  "Sanskrit",    "Devanagari", "Vajrayana Buddhist",       "https://sanskritdocuments.org/doc_devii/", 170,  5.9,  0.0, 0.0),
    ("buddhist_vajrayogini_1",      "Vajrayoginipranamaikavishika",                                 "Buddhist_Tara",     "8th-12th c.",  "Sanskrit",    "Devanagari", "Vajrayana Buddhist",       "https://sanskritdocuments.org/doc_devii/", 152,  6.6,  0.0, 0.0),
    ("buddhist_vajrayogini_2",      "Vajrayoginyah Pindartha Stuti",                                "Buddhist_Tara",     "8th-12th c.",  "Sanskrit",    "Devanagari", "Vajrayana Buddhist",       "https://sanskritdocuments.org/doc_devii/", 157,  6.4,  0.0, 0.0),
    ("buddhist_hevajra_1",          "Hevajra Tantra (excerpts)",                                    "Buddhist_Tara",     "8th-10th c.",  "Sanskrit",    "Latin/IAST", "Vajrayana Buddhist",       "https://www.dsbcproject.org/",             1415, 0.0,  0.0, 0.0),
    ("buddhist_hevajra_sadhana",    "Hevajra Sadhana",                                              "Buddhist_Tara",     "8th-10th c.",  "Sanskrit",    "Latin/IAST", "Vajrayana Buddhist",       "https://www.dsbcproject.org/",             363,  0.0,  0.0, 0.0),
    ("charyapada_core",             "Charyapada (47 padas, core verses)",                           "Charyapada",        "8th-12th c.",  "Old Bengali", "Bengali",    "Mahasiddha authors",       "https://archive.org/search?query=hajar+bacharer+bauddhagan", 843, 40.3, 4.7, 0.1),
    ("bridge_tara_sahasranama_brihannila", "tArAsahasranamastotra from Brihannilatantra",           "Bridge_Tara",       "12th-16th c.", "Sanskrit",    "Devanagari", "Brihannilatantra",         "https://sanskritdocuments.org/doc_devii/", 1710, 2.3,  7.0, 3.0),
    ("bridge_tara_ashtakam",        "Tara Stotram / Nila Sarasvati Ashtakam",                      "Bridge_Tara",       "12th-16th c.", "Sanskrit",    "Devanagari", "Brihannilatantra",         "https://sanskritdocuments.org/doc_devii/", 645,  1.6,  4.7, 3.0),
    ("bridge_tara_shatanama_brihannila", "Tarashatanamastotra from Brihannilatantra",              "Bridge_Tara",       "12th-16th c.", "Sanskrit",    "Devanagari", "Brihannilatantra",         "https://sanskritdocuments.org/doc_devii/", 492,  0.0,  4.1, 4.0),
    ("bridge_tara_sahasranama_3",   "Shri Tara Sahasranama Stotram 3",                             "Bridge_Tara",       "12th-16th c.", "Sanskrit",    "Devanagari", "Mixed Shakta-Buddhist",    "https://sanskritdocuments.org/doc_devii/", 1625, 5.5,  5.5, 1.0),
    ("bridge_tara_takaradi",        "Shri Tara Takaradi Sahasranamastotra",                        "Bridge_Tara",       "12th-16th c.", "Sanskrit",    "Devanagari", "Brahmayamala",             "https://sanskritdocuments.org/doc_devii/", 1342, 2.2,  0.0, 0.0),
    ("bridge_tara_kavacham",        "tArAkavacham",                                                 "Bridge_Tara",       "12th-16th c.", "Sanskrit",    "Devanagari", "Shakta Tara",              "https://sanskritdocuments.org/doc_devii/", 631,  1.6,  0.0, 0.0),
    ("bridge_mahogratara",          "Mahogratara Stuti",                                            "Bridge_Tara",       "12th-16th c.", "Sanskrit",    "Devanagari", "Ugratara tradition",       "https://sanskritdocuments.org/doc_devii/", 171,  5.8,  0.0, 0.0),
    ("bridge_ugratara",             "Shrimad Ugratara Hridayastotram",                              "Bridge_Tara",       "12th-16th c.", "Sanskrit",    "Devanagari", "Ugratara tradition",       "https://sanskritdocuments.org/doc_devii/", 354,  5.6,  0.0, 0.0),
    ("shakta_kali_sahasranama_1",   "Shri Kali Sahasranama Stotram (Kalikulasarvasva)",            "Shakta_Kali",       "14th-18th c.", "Sanskrit",    "Devanagari", "Kalikula",                 "https://sanskritdocuments.org/doc_devii/", 1608, 5.0,  3.7, 0.8),
    ("shakta_kali_sahasranama_2",   "Shri Kali Sahasranama Stotram (Brihannilatantra)",            "Shakta_Kali",       "14th-18th c.", "Sanskrit",    "Devanagari", "Brihannilatantra",         "https://sanskritdocuments.org/doc_devii/", 1608, 5.0,  3.7, 0.8),
    ("shakta_dakshinakalika",       "Dakshinakalika Sahasranama Stotram",                          "Shakta_Kali",       "14th-18th c.", "Sanskrit",    "Devanagari", "Dakshina Kali",            "https://sanskritdocuments.org/doc_devii/", 1076, 6.5,  3.7, 0.6),
    ("shakta_kali_shatanama",       "Shri Kali Shatanama Stotram",                                 "Shakta_Kali",       "14th-18th c.", "Sanskrit",    "Devanagari", "Kalikula",                 "https://sanskritdocuments.org/doc_devii/", 201,  0.0, 10.0, 4.0),
    ("shakta_durga_saptashati",     "Devi Mahatmyam / Durga Saptashati",                           "Shakta_Durga",      "5th-7th c.",   "Sanskrit",    "Latin/IAST", "Markandeya Purana",        "https://gretil.sub.uni-goettingen.de/",    6830, 0.0,  0.0, 0.0),
    ("shakta_mahishasuramardini",   "Shri Mahishasuramardini Ashtottarashata Namavali",            "Shakta_Durga",      "14th-18th c.", "Sanskrit",    "Devanagari", "Shakta Durga",             "https://sanskritdocuments.org/doc_devii/", 324,  0.0,  0.0, 0.0),
    ("vaishnava_gitagovinda",       "Gitagovinda by Jayadeva (12 cantos)",                         "Vaishnava_Sanskrit","12th c.",      "Sanskrit",    "Latin+Deva", "Jayadeva",                 "https://sanskritdocuments.org/sites/giirvaani/", 41164, 0.0, 0.0, 0.0),
    ("vaishnava_srikrishna_kirtan", "Srikrishna Kirtan by Badu Chandidas",                         "Vaishnava_Bengali", "14th-15th c.", "Old Bengali", "Bengali",    "Badu Chandidas",           "https://archive.org/details/SrikrishnaKirtan", 118429, 0.5, 0.9, 1.6),
    ("vaishnava_bhakti_rasamrita",  "Bhakti Rasamrita Sindhu (Bengali translation)",               "Vaishnava_Bengali", "16th c.",      "Bengali",     "Bengali",    "Rupa Goswami / trans.",    "https://archive.org/",                     117726, 1.6, 1.3, 0.8),
    ("vaishnava_chaitanya_charitam","Sri Chaitanya Charitamrita (Bengali)",                        "Vaishnava_Bengali", "16th c.",      "Bengali",     "Bengali",    "Krishnadas Kaviraj",       "https://archive.org/",                     88646, 0.8, 2.3, 3.0),
    ("shakta_ramprasad",            "Kabya Sangraha by Ramprasad Sen (OCR)",                       "Shakta_Padavali",   "18th c.",      "Bengali",     "Bengali",    "Ramprasad Sen",            "https://archive.org/details/998843337",    39067, 2.9, 8.8, 3.0),
    ("baul_lalon",                  "Songs of Lalon Fakir",                                         "Baul_Bengali",      "18th-19th c.", "Bengali",     "Bengali",    "Lalon Shah",               "https://bn.wikisource.org/wiki/লালন_শাহ্", 48372, 1.1, 0.3, 0.2),
    ("baul_gitanjali",              "Gitanjali by Rabindranath Tagore (Bengali original)",          "Baul_Bengali",      "19th c.",      "Bengali",     "Bengali",    "Rabindranath Tagore",      "https://bn.wikisource.org/wiki/গীতাঞ্জলি", 16618, 2.9, 0.7, 0.2),
]

columns = ["doc_id","title","tradition_layer","century_range","language",
           "script","source_tradition","source_url","n_tokens",
           "buddhist_density","shakta_density","sb_ratio"]

os.makedirs("data", exist_ok=True)

df = pd.DataFrame(DOCUMENTS, columns=columns)
df.to_csv("data/documents.csv", index=False, encoding="utf-8")
print(f"Saved: data/documents.csv ({len(df)} rows)")
print(f"\nTradition distribution:")
print(df.groupby("tradition_layer")["doc_id"].count().to_string())

# Also copy similarity matrix
import shutil
if os.path.exists("similarity_matrix.csv"):
    shutil.copy("similarity_matrix.csv", "data/pairwise_similarities.csv")
    sim = pd.read_csv("similarity_matrix.csv", index_col=0)
    print(f"\nSaved: data/pairwise_similarities.csv ({sim.shape[0]}x{sim.shape[1]} matrix)")
else:
    print("\nWARNING: similarity_matrix.csv not found - run analyze_corpus.py first")

print("\nDone. Upload the 'data/' folder to HuggingFace.")
