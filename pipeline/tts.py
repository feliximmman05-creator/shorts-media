import json, sys, soundfile as sf
from kokoro_onnx import Kokoro

WORK, MODEL = sys.argv[1], sys.argv[2]
spec = json.load(open(f"{WORK}/script.json"))
texts = [spec["hook"]["text"]] + [b["text"] for b in spec["beats"]]
k = Kokoro(f"{MODEL}/kokoro.onnx", f"{MODEL}/voices.bin")
for i, t in enumerate(texts):
    a, sr = k.create(t, voice="am_michael", speed=1.15, lang="en-us")
    sf.write(f"{WORK}/seg{i}.wav", a, sr)
    print(f"seg{i}", round(len(a) / sr, 2))
