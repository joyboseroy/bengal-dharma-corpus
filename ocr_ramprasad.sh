#!/bin/bash
# Full OCR of Ramprasad Sen Kabya Sangraha
# Run this from: /mnt/c/Users/ebosjoy/Downloads/sanskritdocs/
# Requires: tesseract, Bengali tessdata, pdftoppm
#
# Install Bengali tessdata first:
#   wget -q "https://github.com/tesseract-ocr/tessdata/raw/main/ben.traineddata" \
#        -O /usr/share/tesseract-ocr/5/tessdata/ben.traineddata
# OR use local tessdata:
#   export TESSDATA_PREFIX=/path/to/tessdata/

PDF="Kabya Sangraha - Ramprasad Sen.pdf"
OUTDIR="/tmp/ramprasad_pages"
OUTPUT="ramprasad_sen_ocr.txt"
TESSDATA="${TESSDATA_PREFIX:-/home/joyboseroy/tessdata}"

mkdir -p "$OUTDIR"

# Download Bengali tessdata if needed
if [ ! -f "$TESSDATA/ben.traineddata" ]; then
    mkdir -p "$TESSDATA"
    echo "Downloading Bengali tessdata..."
    wget -q "https://github.com/tesseract-ocr/tessdata/raw/main/ben.traineddata" \
         -O "$TESSDATA/ben.traineddata"
fi

echo "OCR of Ramprasad Sen - pages 40-372 (skip front matter)"
> "$OUTPUT"

for start in $(seq 40 10 372); do
    end=$((start + 9))
    [ $end -gt 372 ] && end=372
    echo -n "Pages $start-$end... "

    pdftoppm -f $start -l $end -r 300 "$PDF" "$OUTDIR/p_" 2>/dev/null

    for img in "$OUTDIR"/p_*.ppm; do
        [ -f "$img" ] || continue
        TESSDATA_PREFIX="$TESSDATA" tesseract "$img" "${img%.ppm}" \
            -l ben --psm 6 2>/dev/null
        cat "${img%.ppm}.txt" >> "$OUTPUT"
        rm "$img" "${img%.ppm}.txt" 2>/dev/null
    done
    echo "done"
done

echo ""
python3 -c "
import re
text = open('$OUTPUT', encoding='utf-8').read()
tokens = re.findall(r'[\u0980-\u09FF]+', text)
print(f'Done! Bengali tokens: {len(tokens):,}, Unique: {len(set(tokens)):,}')
"
