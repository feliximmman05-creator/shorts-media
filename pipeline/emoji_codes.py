import json, sys
s = json.load(open(sys.argv[1]))
codes = {s["hook"].get("prop", "1f4a5")} | {b["prop"] for b in s["beats"] if b.get("prop")}
if s.get("hidden"): codes.add(s["hidden"]["emoji"])
for b in [s["hook"]] + s["beats"]: codes |= set(b.get("set") or [])
print(" ".join(sorted(codes)))
