#!/bin/bash
# Ramprasad Sen OCR - v2
# Fixed tessdata path, processes page by page (Ctrl+C safe)
# Run from: /mnt/c/Users/ebosjoy/Downloads/sanskritdocs/
# Time: ~15-20 min for full book

PDF="Kabya Sangraha - Ramprasad Sen.pdf"
OUTPUT="ramprasad_sen_ocr.txt"
TMPDIR="/tmp/rp_ocr"
TESSDATA="$HOME/tessdata"

# ── Step 1: Get Bengali tessdata ───────────────────────────────────────
mkdir -p "$TESSDATA"
if [ ! -f "$TESSDATA/ben.traineddata" ]; then
    echo "Downloading Bengali tessdata (~1.8MB)..."
    wget -q --show-progress \
        "https://github.com/tesseract-ocr/tessdata/raw/main/ben.traineddata" \
        -O "$TESSDATA/ben.traineddata" \
    || curl -L -o "$TESSDATA/ben.traineddata" \
        "https://github.com/tesseract-ocr/tessdata/raw/main/ben.traineddata"
    echo "Downloaded."
else
    echo "Bengali tessdata already present."
fi

# ── Step 2: Verify tessdata works ─────────────────────────────────────
TESSDATA_PREFIX="$TESSDATA" tesseract --list-langs 2>&1 | grep -q ben \
    && echo "Tesseract Bengali: OK" \
    || { echo "ERROR: Bengali tessdata not found at $TESSDATA"; exit 1; }

# ── Step 3: OCR page by page ──────────────────────────────────────────
mkdir -p "$TMPDIR"
> "$OUTPUT"   # clear/create output file

echo ""
echo "OCR starting - pages 40 to 372 (songs begin ~p40)"
echo "Output: $OUTPUT"
echo "Press Ctrl+C to stop - partial output will be saved."
echo ""

for page in $(seq 40 372); do
    # Convert single page to PNG
    pdftoppm -f $page -l $page -r 250 "$PDF" "$TMPDIR/pg" 2>/dev/null
    IMG="$TMPDIR/pg-$(printf '%03d' $page).ppm"

    if [ ! -f "$IMG" ]; then
        # pdftoppm zero-pads to total page width (372 = 3 digits)
        IMG=$(ls "$TMPDIR"/pg-*.ppm 2>/dev/null | head -1)
    fi

    [ -f "$IMG" ] || continue

    # OCR
    TESSDATA_PREFIX="$TESSDATA" tesseract "$IMG" "$TMPDIR/out" \
        -l ben --psm 6 2>/dev/null

    # Append to output
    [ -f "$TMPDIR/out.txt" ] && cat "$TMPDIR/out.txt" >> "$OUTPUT"

    # Cleanup
    rm -f "$IMG" "$TMPDIR/out.txt"

    # Progress every 10 pages
    if [ $((($page - 40) % 10)) -eq 0 ]; then
        lines=$(wc -l < "$OUTPUT")
        echo "  Page $page/372 done  ($lines lines so far)"
    fi
done

# ── Step 4: Stats ─────────────────────────────────────────────────────
echo ""
echo "=== Done ==="
python3 - << 'PY'
import re, sys
try:
    text = open("ramprasad_sen_ocr.txt", encoding="utf-8").read()
    tokens = re.findall(r'[\u0980-\u09FF]+', text)
    from collections import Counter
    tc = Counter(tokens)
    print(f"Bengali tokens : {len(tokens):,}")
    print(f"Unique tokens  : {len(set(tokens)):,}")
    print(f"File size      : {len(text):,} chars")
    print()
    terms = ['কালী','শ্যামা','তারা','দুর্গা','শক্তি','শিব','মা','দেবী',
             'ভবানী','আনন্দ','করুণা','শূন্য','সহজ']
    print("Key terms:")
    for t in terms:
        if tc[t]: print(f"  {t}: {tc[t]}")
except Exception as e:
    print(f"Stats error: {e}")
PY

