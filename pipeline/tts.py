import json, sys, soundfile as sf
from kokoro_onnx import Kokoro
WORK, MODEL = sys.argv[1], sys.argv[2]
k = Kokoro(f"{MODEL}/kokoro.onnx", f"{MODEL}/voices.bin")
for s in json.load(open(f"{WORK}/script.json")):
    a, sr = k.create(s["text"], voice="am_michael", speed=1.12, lang="en-us")
    sf.write(f"{WORK}/{s['id']}.wav", a, sr)
    print(s["id"], round(len(a) / sr, 2))
