"""
Strip modern commentary from the contaminated charyapada.txt.
The actual padas use archaic Old Bengali vocabulary.
Run from: /mnt/c/Users/ebosjoy/Downloads/sanskritdocs/
Usage: python3 clean_charyapada.py
"""

import re
from pathlib import Path

text = Path("charyapada.txt").read_text(encoding="utf-8", errors="replace")
lines = text.split('\n')
print(f"Total lines: {len(lines)}")

# Strategy: find lines that look like actual padas vs. modern commentary
# Padas:
#   - contain archaic Old Bengali words (দোম্বি, কাহ্ন, লুই, সরহ)
#   - contain raga markers like "রাগ", "পটমঞ্জরী"
#   - contain verse-end markers ॥ with Bengali numbers
# Modern commentary:
#   - contains publisher info, page numbers, modern words
#   - contains English or Latin characters mixed with Bengali
#   - contains long prose sentences

# Known siddha names that mark actual padas
SIDDHA_NAMES = [
    'লুইপাদ', 'কাহ্নপাদ', 'সরহপাদ', 'শবরপাদ', 'কুক্কুরিপাদ',
    'বিরুআপাদ', 'গুণ্ডরীপাদ', 'চাটিল্লপাদ', 'ভুসুকুপাদ', 'মহিত্তাপাদ',
    'লুই', 'কাহ্ন', 'সরহ', 'শবর', 'কুক্কুরি', 'ভুসুকু',
    'পটমঞ্জরী', 'দেশাখ', 'গবড়া', 'আরভট্ট', 'বরাড়ী', 'রামক্রী',
    'দেশবরাড়ী', 'ভৈরবী', 'বঙ্গাল', 'গুর্জরী', 'মল্লারী',
]

# Archaic Old Bengali words found in the padas
ARCHAIC_WORDS = [
    'দোম্বি', 'বাজণ', 'কায়া', 'বাহিঅ', 'জাণ', 'নিঅ',
    'ণ', 'ঢেঁকিঅ', 'সুণ', 'বিণু', 'পবণ', 'সহজ',
    'আপণ', 'ছাড়িঅ', 'কমল', 'চন্দণ', 'বাণী', 'মণ',
    'চর্যা', 'পদ',
]

# Find pada boundary lines (contain siddha names + রাগ)
pada_boundaries = []
for i, line in enumerate(lines):
    if any(name in line for name in SIDDHA_NAMES):
        pada_boundaries.append(i)

print(f"Found {len(pada_boundaries)} potential pada boundaries")
if pada_boundaries:
    print("First 5 boundaries:")
    for idx in pada_boundaries[:5]:
        print(f"  line {idx}: {lines[idx][:80]}")
    print("Last 5 boundaries:")
    for idx in pada_boundaries[-5:]:
        print(f"  line {idx}: {lines[idx][:80]}")

# Extract content between first and last pada boundary
if len(pada_boundaries) >= 2:
    start = max(0, pada_boundaries[0] - 2)
    end = min(len(lines), pada_boundaries[-1] + 20)
    pada_lines = lines[start:end]
    
    # Filter: keep lines that are short poetic lines (not long prose)
    # and contain Bengali characters
    clean_lines = []
    for line in pada_lines:
        stripped = line.strip()
        bengali_chars = len(re.findall(r'[\u0980-\u09FF]', stripped))
        latin_chars = len(re.findall(r'[a-zA-Z0-9]', stripped))
        total = len(stripped)
        
        if total == 0:
            clean_lines.append('')
            continue
        
        # Keep if: predominantly Bengali, not too long (prose lines > 200 chars)
        if bengali_chars > 0 and (latin_chars / max(total, 1)) < 0.3:
            if total < 300:  # skip very long prose lines
                clean_lines.append(stripped)
    
    clean_text = '\n'.join(clean_lines)
    tokens = re.findall(r'[\u0980-\u09FF]+', clean_text)
    
    print(f"\nCleaned result: {len(clean_lines)} lines, {len(tokens)} Bengali tokens")
    print("\nSample (first 500 chars):")
    print(clean_text[:500])
    
    # Save
    Path("charyapada_clean.txt").write_text(clean_text, encoding='utf-8')
    print(f"\nSaved: charyapada_clean.txt")
    print(f"Expected: ~3,000-5,000 tokens for 47 padas")
    print(f"Got: {len(tokens)} tokens")
    if len(tokens) > 10000:
        print("WARNING: Still too many tokens - file likely still contains commentary")
    elif len(tokens) < 500:
        print("WARNING: Too few tokens - may have over-filtered")
    else:
        print("OK: Token count looks reasonable for 47 padas")
else:
    print("Could not find pada boundaries. Manual intervention needed.")
    print("\nTop 20 most common Bengali bigrams in the file:")
    all_tokens = re.findall(r'[\u0980-\u09FF]+', text)
    from collections import Counter
    tc = Counter(all_tokens)
    for w, c in tc.most_common(20):
        print(f"  {w}: {c}")
