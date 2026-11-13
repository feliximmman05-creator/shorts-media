import json, sys, re
s = json.load(open(sys.argv[1]))
codes = set()
HEX = re.compile(r"^[0-9a-f]{4,5}(-[0-9a-f]{4,5})*$")
for b in [s["hook"]] + s["beats"]:
    if b.get("prop"): codes.add(b["prop"])
    codes |= set(b.get("set") or [])
    for sh in b.get("shots") or []:
        for a in sh.get("actors") or []:
            if HEX.match(str(a.get("art", ""))): codes.add(a["art"])
if not any(b.get("shots") for b in [s["hook"]] + s["beats"]): codes.add(s["hook"].get("prop", "1f4a5"))
if s.get("hidden"): codes.add(s["hidden"]["emoji"])
if (s.get("look") or {}).get("hat"): codes.add(s["look"]["hat"])
print(" ".join(sorted(codes)))
