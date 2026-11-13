#!/usr/bin/env bash
# Usage: pipeline/make_short.sh <work_dir_with_script.json> <output.mp4>
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$(cd "$1" && pwd)"; OUT="$2"
MODEL="${MODEL_DIR:-$HOME/.cache/kokoro}"
mkdir -p "$MODEL" "$WORK/emoji"
pip install --break-system-packages -q kokoro-onnx soundfile cairosvg pillow >/dev/null 2>&1
REL=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
[ -s "$MODEL/kokoro.onnx" ] || curl -sSLf -o "$MODEL/kokoro.onnx" "$REL/kokoro-v1.0.onnx"
[ -s "$MODEL/voices.bin" ]  || curl -sSLf -o "$MODEL/voices.bin"  "$REL/voices-v1.0.bin"
# emoji art (Twemoji, CC-BY 4.0); unknown codes fall back to a star
for c in $(python3 "$HERE/emoji_codes.py" "$WORK/script.json") 2b50; do
  [ -s "$WORK/emoji/$c.png" ] && continue
  FP=$(python3 -c "import json,sys,urllib.parse;p=json.load(open(sys.argv[1])).get(sys.argv[2]);print(urllib.parse.quote(p) if p else '')" "$HERE/fluent_index.json" "$c")
  if [ -n "$FP" ] && curl -sSLf -o "$WORK/emoji/$c.png" "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/$FP"; then
    continue  # glossy 3D art (Microsoft Fluent Emoji, MIT)
  fi
  if curl -sSLf -o "$WORK/emoji/$c.svg" "https://raw.githubusercontent.com/jdecked/twemoji/main/assets/svg/$c.svg"; then
    python3 -c "import cairosvg,sys;cairosvg.svg2png(url=sys.argv[1],write_to=sys.argv[2],output_width=520,output_height=520)" "$WORK/emoji/$c.svg" "$WORK/emoji/$c.png"
  else echo "missing emoji $c, using star"; fi
done
for c in $(python3 "$HERE/emoji_codes.py" "$WORK/script.json"); do
  [ -s "$WORK/emoji/$c.png" ] || cp "$WORK/emoji/2b50.png" "$WORK/emoji/$c.png"
done
python3 "$HERE/tts.py" "$WORK" "$MODEL"
# scripts with "shots" use the scene renderer (full-screen drawn scenes); old scripts still use stickman.py
if python3 -c "import json,sys;s=json.load(open(sys.argv[1]));sys.exit(0 if s['hook'].get('shots') else 1)" "$WORK/script.json"; then
  python3 "$HERE/scenes.py" "$WORK" "$OUT"
else
  python3 "$HERE/stickman.py" "$WORK" "$OUT"
fi
