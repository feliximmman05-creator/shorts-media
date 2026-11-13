"""Scene renderer for What If Shorts (replaces stickman.py for scripts that use "shots").

Usage: python3 scenes.py <work_dir> <out.mp4>      (add --lint to only validate script.json)
work_dir holds script.json, seg0.wav..segN.wav (from tts.py) and emoji/<code>.png.

Every beat is one or more full-screen SHOTS. A shot = background + moving actors + effects + camera.
Frame 0 is already the event (cold open). No permanent title, no watermark, no outro.
The last 0.2s blends back into frame 0 so the replay loops.
"""
import json, os, sys, math, random, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
LINT = "--lint" in sys.argv
args = [a for a in sys.argv[1:] if not a.startswith("--")]
WORK, OUT = args[0], (args[1] if len(args) > 1 else None)
FPS, WD, HT, SR = 30, 1080, 1920, 24000
FONT = f"{HERE}/fonts/Anton.ttf"
VOICE_START, GAP, TAIL = 0.25, 0.10, 0.35
GROUND_Y, WATER_Y = 1340, 1250
spec = json.load(open(f"{WORK}/script.json"))
random.seed(len(json.dumps(spec)))

BGS = {  # sky top, sky bottom, stars, ground colour, style
    "space": ((3, 4, 16), (22, 16, 56), True, None, None),
    "sky_day": ((70, 150, 245), (190, 225, 255), False, None, "clouds"),
    "sky_night": ((6, 10, 34), (36, 44, 96), True, None, None),
    "sunset": ((90, 40, 120), (255, 150, 90), False, None, "clouds"),
    "storm": ((26, 30, 42), (72, 78, 94), False, None, "clouds_dark"),
    "ocean": ((90, 170, 250), (205, 235, 255), False, None, "water"),
    "ocean_night": ((6, 10, 34), (30, 44, 96), True, None, "water"),
    "deep": ((8, 70, 120), (2, 10, 30), False, None, "rays"),
    "city_day": ((100, 170, 250), (205, 230, 255), False, (72, 76, 88), "city"),
    "city_night": ((8, 12, 36), (40, 48, 92), True, (22, 26, 40), "city"),
    "ground": ((100, 175, 250), (200, 232, 255), False, (88, 165, 80), "hills"),
    "desert": ((250, 170, 100), (255, 228, 170), False, (224, 184, 116), "dunes"),
    "ice": ((150, 200, 240), (225, 240, 255), False, (235, 245, 252), "ice"),
    "lava": ((30, 8, 8), (110, 26, 12), False, (40, 14, 12), "lava"),
    "moon_surface": ((2, 2, 10), (16, 16, 36), True, (150, 150, 160), "craters"),
    "body": ((6, 22, 40), (10, 46, 70), False, None, "grid"),
    "cells": ((120, 16, 36), (60, 6, 20), False, None, "cells"),
}
PROC = {"earth", "sun", "moon", "planet", "mars", "asteroid", "blackhole", "person", "body"}
EARTH_STATES = {"normal", "frozen", "burnt", "dry", "dark", "dark_off", "flooded"}
ORGANS = {"heart", "brain", "lungs", "stomach", "bones", "blood", "eyes"}
POSES = {"stand", "arms_up", "run", "fall", "float"}
FXS = {"flash", "shake", "quake", "shockwave", "explosion", "embers", "snow", "rain", "debris", "smoke", "fire", "aurora",
       "crack", "speedlines", "bubbles", "lightning", "dust", "freeze", "heat", "dark", "flood", "stars_streak", "lights_out",
       "meteors", "plasma"}
CAMS = {"push", "pull", "pan_l", "pan_r", "tilt_up", "tilt_down", "static"}

# ---------------------------------------------------------------- helpers
_fc = {}
def font(sz):
    sz = max(8, int(sz))
    if sz not in _fc: _fc[sz] = ImageFont.truetype(FONT, sz)
    return _fc[sz]
def clamp(x, a=0.0, b=1.0): return min(b, max(a, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def ease_back(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
EASES = {"inout": ease, "in": lambda x: clamp(x) ** 2.4, "out": lambda x: 1 - (1 - clamp(x)) ** 2.4, "linear": clamp}
def rgb(c, default=(255, 255, 255)):
    if c is None: return default
    if isinstance(c, str): c = c.lstrip("#"); return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
    return tuple(int(v) for v in c[:3])
def XY(pt): return pt[0] * WD, pt[1] * HT
def fade(sp, a):
    if a >= .995: return sp
    sp = sp.copy(); sp.putalpha(sp.getchannel("A").point(lambda v: int(v * clamp(a)))); return sp
def paste_c(im, sp, cx, cy):
    x, y = int(cx - sp.width / 2), int(cy - sp.height / 2)
    if im.mode != "RGBA": im.paste(sp, (x, y), sp); return
    x0, y0, x1, y1 = max(0, x), max(0, y), min(im.width, x + sp.width), min(im.height, y + sp.height)
    if x1 > x0 and y1 > y0: im.alpha_composite(sp.crop((x0 - x, y0 - y, x1 - x, y1 - y)), (x0, y0))
_glow = {}
def glow(im, cx, cy, r, col, a=1.0):
    r = int(max(4, r))
    if col not in _glow:
        yy, xx = np.mgrid[0:128, 0:128]; rr = np.sqrt((xx - 63.5) ** 2 + (yy - 63.5) ** 2) / 64
        al = (np.clip(1 - rr, 0, 1) ** 2 * 255).astype(np.uint8)
        _glow[col] = Image.fromarray(np.dstack([np.full((128, 128, 3), col, np.uint8), al]), "RGBA")
    paste_c(im, fade(_glow[col].resize((2 * r, 2 * r), Image.BILINEAR), a), cx, cy)
class Soft:
    """Quarter-res layer that is blurred then composited: soft fire, plasma, smoke."""
    def __init__(self, blur=3.5):
        self.im = Image.new("RGBA", (WD // 4, HT // 4), (0, 0, 0, 0)); self.d = ImageDraw.Draw(self.im); self.blur = blur; self.used = False
    def circle(self, x, y, r, col):
        self.d.ellipse([(x - r) / 4, (y - r) / 4, (x + r) / 4, (y + r) / 4], fill=col); self.used = True
    def apply(self, im):
        if self.used:
            L = self.im.filter(ImageFilter.GaussianBlur(self.blur)).resize((WD, HT), Image.BICUBIC); im.paste(L, (0, 0), L)
def center_text(d, cy, text, f, fill, stroke, maxw=960):
    lines, cur = [], ""
    for w in text.split():
        tr = (cur + " " + w).strip()
        if d.textlength(tr, font=f) <= maxw: cur = tr
        else: lines.append(cur); cur = w
    lines.append(cur)
    lh = f.size * 1.08; y = cy - lh * len(lines) / 2
    for ln in lines:
        d.text(((WD - d.textlength(ln, font=f)) / 2, y), ln, font=f, fill=fill, stroke_width=stroke, stroke_fill=(15, 15, 15))
        y += lh

# ---------------------------------------------------------------- script -> shots, lint
segs = [dict(kind="hook", **spec["hook"])] + [dict(kind="beat", **b) for b in spec["beats"]]
def norm_fx(f):
    f = {"name": f} if isinstance(f, str) else dict(f)
    f.setdefault("t", 0.0); return f
problems, warnings = [], []
for si, s in enumerate(segs):
    name = "hook" if si == 0 else f"beat {si}"
    if not s.get("shots"): problems.append(f"{name}: needs a 'shots' list"); s["shots"] = []
    for k, sh in enumerate(s["shots"]):
        w = f"{name} shot {k + 1}"
        if sh.get("bg") not in BGS: problems.append(f"{w}: unknown bg {sh.get('bg')!r} (use one of {sorted(BGS)})")
        sh["fx"] = [norm_fx(f) for f in sh.get("fx") or []]
        for f in sh["fx"]:
            if f["name"] not in FXS: problems.append(f"{w}: unknown fx {f['name']!r} (use one of {sorted(FXS)})")
        if sh.get("cam", "push") not in CAMS: problems.append(f"{w}: unknown cam {sh.get('cam')!r} (use one of {sorted(CAMS)})")
        sh.setdefault("actors", [])
        for a in sh["actors"]:
            art = a.get("art", "")
            if art not in PROC and not os.path.exists(f"{WORK}/emoji/{art}.png") and not LINT:
                problems.append(f"{w}: actor art {art!r} is neither built-in {sorted(PROC)} nor a downloaded emoji code")
            if art == "earth" and (a.get("state", "normal") not in EARTH_STATES or a.get("state_to", "normal") not in EARTH_STATES):
                problems.append(f"{w}: earth state must be one of {sorted(EARTH_STATES)}")
            if art == "person" and a.get("pose", "stand") not in POSES: problems.append(f"{w}: person pose must be one of {sorted(POSES)}")
            if art == "body":
                o = a.get("organ") or []; a["organ"] = [o] if isinstance(o, str) else o
                for x in a["organ"]:
                    if x not in ORGANS: problems.append(f"{w}: body organ must be from {sorted(ORGANS)}")
            a.setdefault("at", [.5, .5])
        moving = any(a.get("to") or a.get("size_to") or a.get("spin") or a.get("state_to") or a.get("count") for a in sh["actors"])
        if not sh["fx"] and not moving: warnings.append(f"{w}: nothing moves (add a 'to', 'size_to', 'spin' or an fx)")
    sigs = [json.dumps([sh.get("bg"), [a.get("art") for a in sh["actors"]]]) for sh in s["shots"]]
    if si > 0 and segs[si - 1]["shots"] and s["shots"] and \
            json.dumps([segs[si - 1]["shots"][-1].get("bg"), [a.get("art") for a in segs[si - 1]["shots"][-1]["actors"]]]) == sigs[0]:
        warnings.append(f"{name}: first shot looks the same as the previous beat's last shot (change bg or actors)")
h0 = segs[0]["shots"][0] if segs[0]["shots"] else None
if h0 is not None:
    if not h0["actors"]: problems.append("hook shot 1: needs at least one actor (the event itself must be on screen in frame 0)")
    if not any(f["name"] in ("explosion", "flash", "shockwave", "quake", "shake", "plasma", "lightning", "fire", "crack", "flood", "freeze", "heat",
                             "lights_out", "meteors", "debris", "dark") for f in h0["fx"]):
        warnings.append("hook shot 1: add a strong fx (explosion, shockwave, plasma, quake...) so the first second already shows the consequence")
    if any(a.get("art") == "person" and a.get("size", .3) > .5 for a in h0["actors"]):
        warnings.append("hook shot 1: the person should be small (scale reference), the event should fill the frame")
if len(spec["hook"].get("screen", "").split()) > 6: warnings.append("hook.screen: keep it to 6 words or fewer")
for w in warnings: print("WARNING:", w)
if problems:
    for p in problems: print("ERROR:", p)
    sys.exit(2)
if LINT:
    print("lint ok,", sum(len(s["shots"]) for s in segs), "shots"); sys.exit(0)

import soundfile as sf
t = VOICE_START
for i, s in enumerate(segs):
    a, sr = sf.read(f"{WORK}/seg{i}.wav", dtype="float32")
    if a.ndim > 1: a = a.mean(1)
    assert sr == SR, sr
    s["audio"], s["start"], s["len"] = a, t, len(a) / SR
    t += s["len"] + GAP
TOTAL = t - GAP + TAIL
NF = int(TOTAL * FPS)
SHOTS = []
for i, s in enumerate(segs):
    s["win0"] = 0.0 if i == 0 else s["start"] - GAP / 2
    s["win1"] = TOTAL if i == len(segs) - 1 else segs[i + 1]["start"] - GAP / 2
    tot = sum(sh.get("w", 1) for sh in s["shots"]); acc = s["win0"]
    for sh in s["shots"]:
        dur = (s["win1"] - s["win0"]) * sh.get("w", 1) / tot
        sh["t0"], sh["t1"], sh["seg"], sh["id"] = acc, acc + dur, i, len(SHOTS); acc += dur
        SHOTS.append(sh)
SHOTS[-1]["t1"] = TOTAL + 1

# ---------------------------------------------------------------- audio: voice + bed + sfx
audio = np.zeros(int(TOTAL * SR) + SR, dtype=np.float32)
for s in segs:
    i0 = int(s["start"] * SR); audio[i0:i0 + len(s["audio"])] += s["audio"]
rng = np.random.default_rng(3)
def sfx_add(t0, sig, vol):
    i0 = int(max(0, t0) * SR); n = min(len(sig), len(audio) - i0)
    if n > 0: audio[i0:i0 + n] += sig[:n] * vol
def s_impact():
    n = int(SR * .6); tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * (75 - 35 * tt) * tt) * np.exp(-tt * 7) + rng.normal(0, 1, n) * np.exp(-tt * 30) * .5).astype(np.float32)
def s_whoosh():
    n = int(SR * .24); w = np.convolve(rng.normal(0, 1, n), np.ones(12) / 12, "same")
    return (w * np.sin(np.linspace(0, np.pi, n)) ** 2).astype(np.float32)
def s_pop():
    n = int(SR * .08); tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * 880 * tt * (1 + tt * 6)) * np.exp(-tt * 45)).astype(np.float32)
def s_rumble(dur):
    n = int(SR * dur); w = np.convolve(rng.normal(0, 1, n), np.ones(160) / 160, "same") * 9
    return (w * np.sin(np.linspace(0, np.pi, n)) ** .5).astype(np.float32)
vpk = float(np.max(np.abs(audio))) or 1
audio /= vpk
tt_ = np.arange(len(audio)) / SR
bed = (np.sin(2 * np.pi * 55 * tt_) + .6 * np.sin(2 * np.pi * 82.5 * tt_ + 1) + .4 * np.sin(2 * np.pi * 110.4 * tt_)) * (.6 + .4 * np.sin(2 * np.pi * .23 * tt_))
audio += (bed * .035).astype(np.float32)
for sh in SHOTS:
    D = min(sh["t1"], TOTAL) - sh["t0"]
    if sh["id"] > 0: sfx_add(sh["t0"] - .05, s_whoosh(), .10)
    for f in sh["fx"]:
        tf = sh["t0"] + f["t"] * D
        if f["name"] in ("explosion", "shockwave", "flash", "lightning"): sfx_add(tf, s_impact(), .5)
        if f["name"] in ("quake", "shake"): sfx_add(tf, s_rumble(min(D * (1 - f["t"]), 2.5)), .35)
    if sh.get("pop") or sh.get("counter"): sfx_add(sh["t0"] + .08, s_pop(), .2)
voice_env = np.sqrt(np.convolve(audio ** 2, np.ones(int(SR * .05)) / int(SR * .05), mode="same"))

KW = set(w.lower() for w in spec.get("keyword", "").split())
for s in segs:
    words = s["text"].split(); tot = sum(len(w) + 2 for w in words); acc = 0; s["words"] = []
    for w in words:
        a = acc / tot * s["len"]; acc += len(w) + 2
        s["words"].append((w, s["start"] + a, s["start"] + acc / tot * s["len"]))

# ---------------------------------------------------------------- backgrounds
_bg, _city, _aur = {}, {}, {}
def bg_static(name):
    if name in _bg: return _bg[name]
    top, bot, stars, gnd, style = BGS[name]
    k = np.linspace(0, 1, HT)[:, None, None]
    arr = (np.array(top)[None, None, :] * (1 - k) + np.array(bot)[None, None, :] * k).repeat(WD, axis=1)
    im = Image.fromarray(arr.astype(np.uint8), "RGB"); d = ImageDraw.Draw(im, "RGBA"); r = random.Random(name)
    if stars:
        for _ in range(220):
            x, y, q = r.uniform(0, WD), r.uniform(0, GROUND_Y if gnd else HT), r.choice([1.5, 2, 2.5, 3.5])
            d.ellipse([x - q, y - q, x + q, y + q], fill=(255, 255, 255, r.randint(110, 255)))
    if style in ("clouds", "clouds_dark"):
        lay = Image.new("RGBA", (WD, HT), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        col = (255, 255, 255, 190) if style == "clouds" else (20, 22, 30, 220)
        for _ in range(7 if style == "clouds" else 16):
            cx, cy = r.uniform(0, WD), r.uniform(120, 900)
            for _ in range(6):
                ox, oy, q = r.uniform(-150, 150), r.uniform(-30, 30), r.uniform(50, 110)
                ld.ellipse([cx + ox - q * 1.5, cy + oy - q, cx + ox + q * 1.5, cy + oy + q], fill=col)
        lay = lay.filter(ImageFilter.GaussianBlur(14)); im.paste(lay, (0, 0), lay)
    if style == "rays":
        lay = Image.new("RGBA", (WD, HT), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        for _ in range(7):
            x = r.uniform(-100, WD); w = r.uniform(60, 180)
            ld.polygon([(x, 0), (x + w, 0), (x + w + 380, HT), (x + 300, HT)], fill=(190, 240, 255, 26))
        lay = lay.filter(ImageFilter.GaussianBlur(20)); im.paste(lay, (0, 0), lay)
    if style == "grid":
        for gx in range(0, WD, 90): d.line([(gx, 0), (gx, HT)], fill=(90, 200, 255, 22), width=2)
        for gy in range(0, HT, 90): d.line([(0, gy), (WD, gy)], fill=(90, 200, 255, 22), width=2)
    if gnd:
        if style == "hills":
            d.ellipse([-300, GROUND_Y - 150, 700, GROUND_Y + 300], fill=(70, 150, 72)); d.ellipse([400, GROUND_Y - 110, 1500, GROUND_Y + 300], fill=(78, 158, 76))
        if style == "dunes":
            d.ellipse([-200, GROUND_Y - 130, 640, GROUND_Y + 220], fill=(236, 196, 128)); d.ellipse([420, GROUND_Y - 90, 1320, GROUND_Y + 220], fill=(214, 172, 104))
        if style == "city":
            night = name == "city_night"; x = -20; wins = []
            for layer, (hmin, hmax, colr) in enumerate([((300, 760, (30, 36, 60) if night else (150, 168, 196))), ((160, 520, (44, 52, 78) if night else (176, 190, 212)))]):
                x = -20 - layer * 37
                while x < WD:
                    w = r.randint(90, 170); h = r.randint(hmin, hmax)
                    d.rectangle([x, GROUND_Y - h, x + w - 8, GROUND_Y], fill=colr)
                    for wy in range(GROUND_Y - h + 22, GROUND_Y - 24, 44):
                        for wx in range(x + 14, x + w - 26, 30):
                            if r.random() < .55:
                                if night: wins.append((wx, wy, r.random()))
                                else: d.rectangle([wx, wy, wx + 13, wy + 20], fill=(225, 236, 250))
                    x += w
            _city[name] = wins
        d.rectangle([0, GROUND_Y, WD, HT], fill=gnd)
        if style == "craters":
            for _ in range(16):
                cx, cy, q = r.uniform(0, WD), r.uniform(GROUND_Y + 40, HT - 80), r.uniform(20, 80)
                d.ellipse([cx - q, cy - q * .35, cx + q, cy + q * .35], fill=(118, 118, 130))
        if style == "ice":
            for _ in range(12):
                x0, y0 = r.uniform(0, WD), r.uniform(GROUND_Y + 20, HT)
                d.line([(x0, y0), (x0 + r.uniform(-200, 200), y0 + r.uniform(20, 120))], fill=(170, 210, 240), width=4)
            for x0 in range(-50, WD, 210):
                h = r.uniform(120, 330); d.polygon([(x0, GROUND_Y), (x0 + 110, GROUND_Y - h), (x0 + 230, GROUND_Y)], fill=(210, 232, 250))
        if style == "lava":
            for _ in range(11):
                x0, y0 = r.uniform(0, WD), r.uniform(GROUND_Y + 10, HT); pts = [(x0, y0)]
                for _ in range(5): pts.append((pts[-1][0] + r.uniform(-140, 140), pts[-1][1] + r.uniform(30, 110)))
                d.line(pts, fill=(255, 120, 20), width=12); d.line(pts, fill=(255, 220, 90), width=4)
    _bg[name] = im
    return im

def water(d, T, level, night=False, alpha=255):
    cols = [(20, 70, 150), (28, 96, 185), (40, 122, 212), (70, 150, 230)] if not night else [(6, 20, 60), (10, 32, 84), (16, 44, 104), (24, 58, 124)]
    for k, col in enumerate(cols):
        base = level + k * 46; pts = [(0, HT)]
        for x in range(0, WD + 41, 40):
            pts.append((x, base + 20 * math.sin(x * .011 + T * (1.6 + k * .5) + k * 1.7) + 9 * math.sin(x * .027 - T * 2.3 + k)))
        pts.append((WD, HT)); d.polygon(pts, fill=col + (alpha,))
    for x in range(0, WD, 150):
        y = level + 60 + 14 * math.sin(x * .011 + T * 1.6)
        d.arc([x + 20 * math.sin(T + x), y, x + 90 + 20 * math.sin(T + x), y + 30], 200, 340, fill=(220, 240, 255, 150), width=4)

_cellsp = None
def bg_dynamic(im, d, sh, u, p, T):
    global _cellsp
    name = sh["bg"]; style = BGS[name][4]
    if style == "water": water(d, T, WATER_Y, night=name == "ocean_night")
    if style == "city" and name == "city_night":
        lo = next((f for f in sh["fx"] if f["name"] == "lights_out"), None)
        off = ease((p - lo["t"]) / max(.05, (1 - lo["t"]) * .75)) if lo else 0
        for wx, wy, q in _city[name]:
            if q > off * 1.02: d.rectangle([wx, wy, wx + 13, wy + 20], fill=(255, 218, 120, 235))
    if style == "cells":
        if _cellsp is None:
            c = Image.new("RGBA", (300, 300), (0, 0, 0, 0)); cd = ImageDraw.Draw(c)
            cd.ellipse([20, 20, 280, 280], fill=(235, 70, 90, 200)); cd.ellipse([95, 95, 205, 205], fill=(150, 20, 40, 220))
            _cellsp = [c.filter(ImageFilter.GaussianBlur(5)).resize((s_, s_), Image.BILINEAR) for s_ in (150, 230, 330)]
        r = random.Random(sh["id"])
        for i in range(13):
            x0, y0, sp, k = r.uniform(0, WD), r.uniform(0, HT), r.uniform(30, 110), r.randrange(3)
            paste_c(im, _cellsp[k], (x0 + sp * T) % (WD + 400) - 200, y0 + 50 * math.sin(T * .8 + i))

# ---------------------------------------------------------------- procedural art
ED = 600  # earth base diameter
_yy, _xx = np.mgrid[0:ED, 0:ED]
_nx, _ny = (_xx - ED / 2 + .5) / (ED / 2), (_yy - ED / 2 + .5) / (ED / 2)
_r2 = _nx ** 2 + _ny ** 2
E_MASK = _r2 <= 1
_nz = np.sqrt(np.clip(1 - _r2, 0, 1))
TW, TH = 1800, 600
E_IV = np.clip(((np.arcsin(np.clip(_ny, -1, 1)) / math.pi + .5) * TH).astype(int), 0, TH - 1)
E_IU = ((np.arcsin(np.clip(_nx / np.maximum(np.sqrt(np.clip(1 - _ny ** 2, 1e-6, 1)), 1e-3), -1, 1)) / (2 * math.pi)) * TW).astype(int)
E_SHADE = np.clip(.3 + .85 * (-.45 * _nx - .4 * _ny + .8 * _nz), 0, 1.15)[:, :, None]
E_ALPHA = (np.clip((1 - np.sqrt(_r2)) * ED / 2, 0, 1) * 255).astype(np.uint8)
EPAL = {  # ocean, land, land2, ice, cloud alpha, atmosphere
    "normal": ((28, 100, 200), (70, 160, 80), (190, 170, 110), (245, 250, 255), 105, (90, 170, 255)),
    "frozen": ((150, 200, 235), (235, 245, 250), (210, 230, 245), (255, 255, 255), 70, (190, 230, 255)),
    "burnt": ((38, 18, 14), (92, 30, 20), (255, 120, 30), (60, 30, 20), 0, (255, 110, 30)),
    "dry": ((184, 144, 92), (150, 110, 62), (204, 172, 112), (224, 204, 172), 0, (240, 190, 120)),
    "dark": ((12, 26, 70), (26, 44, 58), (26, 44, 58), (50, 64, 92), 0, (70, 130, 255)),
    "dark_off": ((8, 16, 44), (12, 20, 28), (12, 20, 28), (26, 34, 52), 0, (50, 90, 190)),
    "flooded": ((28, 100, 200), (40, 118, 206), (34, 108, 204), (245, 250, 255), 105, (90, 170, 255)),
}
_etex = {}
def earth_tex(state):
    if state in _etex: return _etex[state]
    oc, la, la2, ice, cl, _ = EPAL[state]
    im = Image.new("RGB", (TW, TH), oc); d = ImageDraw.Draw(im, "RGBA"); r = random.Random(7); lights = []
    for c in range(11):
        cx, cy = r.uniform(0, TW), r.uniform(TH * .22, TH * .78)
        for k in range(16):
            ox, oy, q = r.gauss(0, 95), r.gauss(0, 65), r.uniform(26, 84)
            col = la2 if r.random() < .22 else la
            for wx in (-TW, 0, TW): d.ellipse([cx + ox - q + wx, cy + oy - q * .8, cx + ox + q + wx, cy + oy + q * .8], fill=col)
            for _ in range(6): lights.append((cx + ox + r.gauss(0, q * .5), cy + oy + r.gauss(0, q * .4), r.choice([2, 3, 3, 4, 5])))
    for x in range(0, TW, 60):
        d.ellipse([x - 60, -50 - r.uniform(0, 20), x + 60, 42 + r.uniform(0, 26)], fill=ice); d.ellipse([x - 60, TH - 40 - r.uniform(0, 22), x + 60, TH + 50], fill=ice)
    im = im.filter(ImageFilter.GaussianBlur(2.2)); d = ImageDraw.Draw(im, "RGBA")
    if cl:
        for _ in range(30):
            cx, cy = r.uniform(0, TW), r.uniform(60, TH - 60)
            for k in range(4):
                ox, q = r.uniform(-90, 90), r.uniform(9, 20)
                for wx in (-TW, 0, TW): d.ellipse([cx + ox - q * 2.4 + wx, cy - q + k * 4, cx + ox + q * 2.4 + wx, cy + q + k * 4], fill=(255, 255, 255, cl))
    if state == "dark":
        for x, y, q in lights:
            for wx in (-TW, 0, TW): d.ellipse([x - q + wx, y - q, x + q + wx, y + q], fill=(255, 220, 120, 255))
    _etex[state] = np.asarray(im).astype(np.float32)
    return _etex[state]
def earth_sprite(T, a, p):
    off = int((T * a.get("rot_speed", 40) + 300) % TW)
    iu = (E_IU + off) % TW
    st, st2 = a.get("state", "normal"), a.get("state_to")
    arr = earth_tex(st)[E_IV, iu]
    if st2 and st2 != st:
        k = ease((p - a.get("delay", 0)) / max(.05, a.get("over", 1 - a.get("delay", 0))))
        arr = arr * (1 - k) + earth_tex(st2)[E_IV, iu] * k
    flat = st.startswith("dark")
    arr = arr * (np.clip(E_SHADE, .8, 1.15) if flat else E_SHADE)
    disc = Image.fromarray(np.dstack([np.clip(arr, 0, 255).astype(np.uint8), E_ALPHA]), "RGBA")
    pad = 90; sp = Image.new("RGBA", (ED + 2 * pad, ED + 2 * pad), (0, 0, 0, 0))
    glow(sp, sp.width / 2, sp.height / 2, ED / 2 + pad, EPAL[st2 if st2 and p > .6 else st][5], .8 if flat else .6)
    sp.alpha_composite(disc, (pad, pad))
    return sp, (ED + 2 * pad) / ED

_sun = {}
def sun_sprite(T, a):
    if not _sun:
        n = 720; yy, xx = np.mgrid[0:n, 0:n]; dx, dy = (xx - n / 2) / (n / 2), (yy - n / 2) / (n / 2)
        rr = np.sqrt(dx ** 2 + dy ** 2); th = np.arctan2(dy, dx)
        core = np.clip(rr / .5, 0, 1)[:, :, None]
        colr = np.array([255, 250, 205])[None, None, :] * (1 - core ** 2) + np.array([255, 170, 30])[None, None, :] * core ** 2
        al = np.where(rr <= .5, 1, np.exp(-(rr - .5) * 6.5) * .85)
        _sun["core"] = Image.fromarray(np.dstack([colr, np.clip(al, 0, 1) * 255]).astype(np.uint8), "RGBA")
        rays = np.clip(.5 + .3 * np.sin(th * 9 + 1) + .3 * np.sin(th * 17 + 2) + .25 * np.sin(th * 5), 0, 1) * np.clip(1 - (rr - .45) / .5, 0, 1) * (rr > .44)
        _sun["rays"] = Image.fromarray(np.dstack([np.full((n, n, 3), (255, 150, 40)), np.clip(rays, 0, 1) * 235]).astype(np.uint8), "RGBA")
    sp = _sun["rays"].rotate(T * 14 % 360, resample=Image.BILINEAR)
    r2 = _sun["rays"].rotate(-T * 9 % 360, resample=Image.BILINEAR)
    sp.alpha_composite(fade(r2, .6)); sp.alpha_composite(_sun["core"])
    return sp, 2.0 * (1 + .02 * math.sin(T * 5))

_sp = {}
def disc_sprite(kind, col):
    key = (kind, col)
    if key in _sp: return _sp[key]
    n = 520; r = random.Random(kind + str(col)); im = Image.new("RGBA", (n, n), (0, 0, 0, 0)); d = ImageDraw.Draw(im, "RGBA")
    if kind == "asteroid":
        pts = [(n / 2 + math.cos(k / 14 * 2 * math.pi) * n * r.uniform(.36, .48), n / 2 + math.sin(k / 14 * 2 * math.pi) * n * r.uniform(.36, .48)) for k in range(14)]
        d.polygon(pts, fill=(104, 94, 88)); msk = im.getchannel("A")
        for _ in range(12):
            cx, cy, q = r.uniform(110, n - 110), r.uniform(110, n - 110), r.uniform(16, 54)
            d.ellipse([cx - q, cy - q, cx + q, cy + q], fill=(70, 62, 58)); d.arc([cx - q, cy - q, cx + q, cy + q], 20, 200, fill=(140, 128, 120), width=5)
        sh = Image.new("RGBA", (n, n), (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse([n * .25, n * .25, n * 1.3, n * 1.3], fill=(0, 0, 0, 110))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(30))); im.putalpha(msk)
    elif kind == "blackhole":
        glow(im, n / 2, n / 2, n / 2, (255, 150, 40), .9)
        d.ellipse([n * .06, n * .36, n * .94, n * .64], outline=(255, 200, 110), width=22); d.ellipse([n * .12, n * .40, n * .88, n * .60], outline=(255, 240, 200), width=8)
        d.ellipse([n * .27, n * .27, n * .73, n * .73], fill=(0, 0, 0, 255)); d.arc([n * .25, n * .25, n * .75, n * .75], 180, 360, fill=(255, 190, 90), width=10)
    else:
        base = {"moon": (176, 176, 186), "mars": (196, 88, 52)}.get(kind, col)
        d.ellipse([10, 10, n - 10, n - 10], fill=base); msk = im.getchannel("A")
        if kind == "planet":
            for y in range(30, n, 62):
                k = r.uniform(.72, 1.2); d.rectangle([0, y, n, y + r.uniform(18, 42)], fill=tuple(int(clamp(v * k, 0, 255)) for v in base))
        else:
            for _ in range(15):
                cx, cy, q = r.uniform(60, n - 60), r.uniform(60, n - 60), r.uniform(14, 52)
                d.ellipse([cx - q, cy - q, cx + q, cy + q], fill=tuple(int(v * .78) for v in base))
        im = im.filter(ImageFilter.GaussianBlur(1.5))
        sh = Image.new("RGBA", (n, n), (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse([n * .22, n * .2, n * 1.35, n * 1.35], fill=(0, 0, 0, 150))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(40))); im.putalpha(msk)
    _sp[key] = im
    return im
def emoji_sprite(code):
    if code not in _sp: _sp[code] = Image.open(f"{WORK}/emoji/{code}.png").convert("RGBA")
    return _sp[code]

PJ = {  # person joints, unit = height, origin = feet centre, y up negative
    "stand": dict(head=(0, -.88), neck=(0, -.76), hip=(0, -.42), lh=(-.13, -.44), rh=(.13, -.44), lf=(-.07, 0), rf=(.07, 0)),
    "arms_up": dict(head=(0, -.88), neck=(0, -.76), hip=(0, -.42), lh=(-.2, -1.0), rh=(.2, -1.0), lf=(-.09, 0), rf=(.09, 0)),
    "fall": dict(head=(0, -.88), neck=(0, -.76), hip=(0, -.42), lh=(-.28, -.9), rh=(.28, -.86), lf=(-.2, -.04), rf=(.2, -.02)),
}
def draw_person(im, cx, cy, h, a, T, rot):
    pose = a.get("pose", "stand"); J = dict(PJ.get(pose, PJ["fall" if pose == "float" else "stand"]))
    if pose == "run":
        s_ = math.sin(T * 13)
        J.update(lf=(-.18 * s_, -.04 * abs(s_)), rf=(.18 * s_, -.04 * abs(s_)), lh=(.16 * s_, -.5), rh=(-.16 * s_, -.5), head=(.05, -.87), neck=(.03, -.76))
    if pose in ("fall", "float"):
        w = .04 * math.sin(T * 7); J["lh"] = (J["lh"][0], J["lh"][1] + w); J["rh"] = (J["rh"][0], J["rh"][1] - w)
    SS = 2; pad = int(h * .75); L = Image.new("RGBA", (2 * pad * SS, 2 * pad * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    def P(j):
        x, y = J[j][0] * h, (J[j][1] + .5) * h
        return ((pad + x * ca - y * sa) * SS, (pad + x * sa + y * ca) * SS)
    shirt, pants, skin, OL = rgb(a.get("color"), (255, 122, 26)), (34, 48, 90), (217, 162, 122), (24, 20, 26)
    def seg(p, q, w, col):
        for ww, cc in ((w + h * .035, OL), (w, col)):
            d.line([p, q], fill=cc, width=int(ww * SS))
            for z in (p, q): d.ellipse([z[0] - ww * SS / 2, z[1] - ww * SS / 2, z[0] + ww * SS / 2, z[1] + ww * SS / 2], fill=cc)
    seg(P("hip"), P("lf"), h * .075, pants); seg(P("hip"), P("rf"), h * .075, pants)
    seg(P("neck"), P("lh"), h * .06, shirt); seg(P("neck"), P("rh"), h * .06, shirt)
    seg(P("neck"), P("hip"), h * .17, shirt)
    hx, hy = P("head"); R = h * .115 * SS
    d.ellipse([hx - R - h * .02 * SS, hy - R - h * .02 * SS, hx + R + h * .02 * SS, hy + R + h * .02 * SS], fill=OL); d.ellipse([hx - R, hy - R, hx + R, hy + R], fill=skin)
    d.chord([hx - R, hy - R * 1.05, hx + R, hy + R * .6], 180, 360, fill=(42, 29, 20))
    L = L.resize((2 * pad, 2 * pad), Image.LANCZOS)
    paste_c(im, L, cx, cy)

def draw_body(im, cx, cy, w, a, T, p, alpha):
    s_ = w / 600; W_, H_ = int(600 * s_), int(1400 * s_)
    L = Image.new("RGBA", (W_, H_), (0, 0, 0, 0)); d = ImageDraw.Draw(L, "RGBA")
    col = rgb(a.get("color"), (90, 200, 255)); organs = a.get("organ") or []
    def S(x, y): return (x * s_, y * s_)
    def limb(pts, wd, c):
        d.line([S(*q) for q in pts], fill=c, width=int(wd * s_), joint="curve")
        for q in pts: x, y = S(*q); r = wd * s_ / 2; d.ellipse([x - r, y - r, x + r, y + r], fill=c)
    skin = col + (95,)
    limb([(300, 330), (300, 720)], 230, skin)
    limb([(190, 350), (120, 600), (95, 830)], 70, skin); limb([(410, 350), (480, 600), (505, 830)], 70, skin)
    limb([(245, 760), (235, 1050), (230, 1330)], 95, skin); limb([(355, 760), (365, 1050), (370, 1330)], 95, skin)
    limb([(300, 250), (300, 300)], 70, skin); d.ellipse([S(205, 40)[0], S(205, 40)[1], S(395, 250)[0], S(395, 250)[1]], fill=skin)
    L = L.filter(ImageFilter.GaussianBlur(max(1, 3 * s_))); d = ImageDraw.Draw(L, "RGBA")
    og = a.get("organ_scale", 1) + (a.get("organ_scale_to", a.get("organ_scale", 1)) - a.get("organ_scale", 1)) * ease(p)
    bps = a.get("bpm", 75) / 60
    if "bones" in organs:
        b = (240, 244, 250, 235)
        limb([(300, 270), (300, 740)], 16, b)
        for y in range(360, 600, 44): d.arc([S(215, y - 30)[0], S(215, y - 30)[1], S(385, y + 40)[0], S(385, y + 40)[1]], 180, 360, fill=b, width=max(2, int(11 * s_)))
        limb([(200, 350), (128, 600), (100, 820)], 15, b); limb([(400, 350), (472, 600), (500, 820)], 15, b)
        limb([(250, 760), (238, 1050), (232, 1320)], 20, b); limb([(350, 760), (362, 1050), (368, 1320)], 20, b)
        limb([(235, 750), (365, 750)], 34, b); d.ellipse([S(232, 70)[0], S(232, 70)[1], S(368, 225)[0], S(368, 225)[1]], outline=b, width=max(2, int(13 * s_)))
    if "blood" in organs:
        r = random.Random(5)
        for path in ([(300, 430), (190, 360), (125, 600), (100, 820)], [(300, 430), (410, 360), (475, 600), (500, 820)], [(300, 430), (300, 740), (240, 1050), (232, 1320)],
                     [(300, 740), (360, 1050), (368, 1320)], [(300, 430), (300, 260), (300, 130)]):
            limb(path, 12, (230, 40, 50, 230))
            for k in range(5):
                q = (T * bps * .5 + k / 5) % 1 * (len(path) - 1); i = int(q); f = q - i
                x, y = path[i][0] + (path[i + 1][0] - path[i][0]) * f, path[i][1] + (path[i + 1][1] - path[i][1]) * f
                d.ellipse([S(x - 11, y - 11)[0], S(x - 11, y - 11)[1], S(x + 11, y + 11)[0], S(x + 11, y + 11)[1]], fill=(255, 150, 150, 255))
    if "lungs" in organs:
        br = 1 + .09 * math.sin(T * 2.2)
        for sx in (-1, 1):
            x = 300 + sx * 62; rw, rh = 50 * br * og, 105 * br * og
            d.ellipse([S(x - rw, 470 - rh)[0], S(x - rw, 470 - rh)[1], S(x + rw, 470 + rh)[0], S(x + rw, 470 + rh)[1]], fill=(255, 150, 170, 235), outline=(255, 215, 225), width=max(2, int(6 * s_)))
    if "stomach" in organs:
        d.ellipse([S(270 - 70 * og, 640 - 55 * og)[0], S(0, 640 - 55 * og)[1], S(270 + 85 * og, 0)[0], S(0, 640 + 60 * og)[1]], fill=(255, 176, 70, 240), outline=(255, 226, 150), width=max(2, int(6 * s_)))
    if "heart" in organs:
        beat = 1 + .16 * max(0, math.sin(T * bps * 2 * math.pi)) ** 3; q = 44 * og * beat; hx, hy = 325, 455
        glow(L, *S(hx, hy), q * 3.2 * s_, (255, 50, 60), .8)
        for sx in (-1, 1): d.ellipse([S(hx + sx * q * .5 - q * .62, hy - q)[0], S(0, hy - q)[1], S(hx + sx * q * .5 + q * .62, 0)[0], S(0, hy + q * .3)[1]], fill=(240, 30, 50, 255))
        d.polygon([S(hx - q * 1.1, hy - q * .1), S(hx + q * 1.1, hy - q * .1), S(hx, hy + q * 1.25)], fill=(240, 30, 50, 255))
    if "brain" in organs:
        q = og * (1 + .03 * math.sin(T * 6)); glow(L, *S(300, 135), 150 * q * s_, (255, 120, 200), .7)
        d.ellipse([S(300 - 78 * q, 135 - 62 * q)[0], S(0, 135 - 62 * q)[1], S(300 + 78 * q, 0)[0], S(0, 135 + 58 * q)[1]], fill=(255, 150, 190, 255), outline=(255, 220, 235), width=max(2, int(6 * s_)))
        for k in range(4): d.arc([S(300 - 60 * q + k * 26 * q, 0)[0], S(0, 100 - 20 * q)[1], S(300 - 20 * q + k * 26 * q, 0)[0], S(0, 170 + 10 * q)[1]], 90 + k * 40, 300 + k * 40, fill=(200, 80, 130), width=max(2, int(6 * s_)))
    if "eyes" in organs:
        for sx in (-1, 1):
            glow(L, *S(300 + sx * 42, 135), 60 * og * s_, (255, 255, 255), .9); x, y = S(300 + sx * 42, 135); r = 15 * og * s_
            d.ellipse([x - r * 1.5, y - r, x + r * 1.5, y + r], fill=(255, 255, 255, 255)); d.ellipse([x - r * .6, y - r * .6, x + r * .6, y + r * .6], fill=(20, 30, 60, 255))
    paste_c(im, fade(L, alpha), cx, cy)

# ---------------------------------------------------------------- actors
def draw_actor(im, a, sh, u, D, p, T):
    art = a["art"]; delay = a.get("delay", 0); over = max(.02, a.get("over", 1 - delay))
    if p < a.get("appear", 0) or p >= a.get("vanish", 9): return
    k = EASES.get(a.get("ease", "inout"), ease)((p - delay) / over)
    x0, y0 = XY(a["at"]); x1, y1 = XY(a.get("to", a["at"]))
    s0 = a.get("size", .3); s1 = a.get("size_to", s0)
    ua = u - a.get("appear", 0) * D
    enter = a.get("enter", "none"); ek = 1; al = 1
    if enter == "pop": ek = ease_back(ua / .28)
    if enter == "fade": al = clamp(ua / .35)
    n = int(a.get("count", 1)); r = random.Random(sh["id"] * 131 + sum(map(ord, art)))
    tr = a.get("trail")
    if tr and (x1, y1) != (x0, y0) and 0 < k < 1:  # soft fire/smoke trails behind every copy
        dx, dy = x1 - x0, y1 - y0; Ld = math.hypot(dx, dy); dx, dy = dx / Ld, dy / Ld; soft = Soft(3); r2 = random.Random(sh["id"] * 131 + sum(map(ord, art)))
        for i in range(n):
            ox = oy = 0; sf_ = 1; ki = k
            if n > 1:
                sp = a.get("spread", .35); ox, oy = r2.uniform(-sp, sp) * WD, r2.uniform(-sp, sp) * HT * .7
                sf_ = r2.uniform(.55, 1.1); r2.uniform(0, 360); ph = r2.uniform(0, .3)
                ki = EASES.get(a.get("ease", "inout"), ease)((p - delay - ph * over) / (over * (1 - ph) + 1e-6))
            if not 0 < ki < 1: continue
            cx, cy = x0 + (x1 - x0) * ki + ox, y0 + (y1 - y0) * ki + oy; size = (s0 + (s1 - s0) * ki) * sf_ * WD
            for lay, (col, wd) in enumerate(((((200, 50, 20, 210), 1.0), ((255, 140, 30, 235), .7), ((255, 236, 170, 255), .4)) if tr == "fire" else (((60, 60, 66, 190), 1.0),))):
                for j in range(16, -1, -1):
                    q = size * .34 * wd * (1 - j / 19); jx = math.sin(T * 23 + j * 1.7 + i) * size * .05
                    soft.circle(cx - dx * j * size * .2 * (1.1 - lay * .25) - dy * jx, cy - dy * j * size * .2 * (1.1 - lay * .25) + dx * jx, q, col)
        soft.apply(im)
    for i in range(n):
        ki = k
        ox = oy = 0; sf_ = 1; rot0 = 0
        if n > 1:
            sp = a.get("spread", .35); ox, oy = r.uniform(-sp, sp) * WD, r.uniform(-sp, sp) * HT * .7
            sf_ = r.uniform(.55, 1.1); rot0 = r.uniform(0, 360); ph = r.uniform(0, .3)
            ki = EASES.get(a.get("ease", "inout"), ease)((p - delay - ph * over) / (over * (1 - ph) + 1e-6))
        cx, cy = x0 + (x1 - x0) * ki + ox, y0 + (y1 - y0) * ki + oy
        size = (s0 + (s1 - s0) * ki) * sf_ * ek * WD
        if a.get("bob"): cy += a["bob"] * 40 * math.sin(T * 2.2 + i)
        if a.get("shake"): cx += random.uniform(-1, 1) * a["shake"] * 22; cy += random.uniform(-1, 1) * a["shake"] * 22
        if size < 4: continue
        rot = a.get("rot", 0) + rot0 + a.get("spin", 0) * u
        if a.get("glow"): glow(im, cx, cy, size * 1.1, rgb(a["glow"]), .8 * al)
        if art == "person": draw_person(im, cx, cy, size, a, T + i, rot); continue
        if art == "body": draw_body(im, cx, cy, size, a, T, p, al); continue
        scale = 1.0
        if art == "earth": sp_, scale = earth_sprite(T, a, p)
        elif art == "sun": sp_, scale = sun_sprite(T, a)
        elif art in ("moon", "mars", "planet", "asteroid", "blackhole"): sp_ = disc_sprite(art, rgb(a.get("color"), (120, 150, 220)))
        else: sp_ = emoji_sprite(art)
        px_ = int(size * scale)
        if px_ > 2600: px_ = 2600
        sp_ = sp_.resize((px_, px_), Image.BILINEAR)
        if rot and art not in ("earth", "sun", "moon", "mars", "planet"): sp_ = sp_.rotate(-rot, resample=Image.BILINEAR)
        if a.get("flip"): sp_ = sp_.transpose(Image.FLIP_LEFT_RIGHT)
        paste_c(im, fade(sp_, al), cx, cy)

# ---------------------------------------------------------------- effects
def fx_at(f, default=(.5, .5)): return XY(f.get("at", default))
def aurora_sprite():
    if "a" not in _aur:
        w, h = 700, 1000; yy, xx = np.mgrid[0:h, 0:w]
        al = np.clip(np.sin(xx / w * math.pi) ** 2 * np.clip(1 - yy / h, 0, 1) ** 1.3 * (.6 + .4 * np.sin(xx * .09)), 0, 1)
        colr = np.array([60, 255, 150])[None, None, :] * (1 - (yy / h)[:, :, None] * .6) + np.array([170, 80, 255])[None, None, :] * (yy / h)[:, :, None] * .6
        _aur["a"] = Image.fromarray(np.dstack([colr, al * 190]).astype(np.uint8), "RGBA").filter(ImageFilter.GaussianBlur(8))
    return _aur["a"]

def fx_pre(im, sh, u, D, p, T):
    d = ImageDraw.Draw(im, "RGBA"); r = random.Random(sh["id"] + 11)
    for f in sh["fx"]:
        n = f["name"]; e = u - f["t"] * D
        if e < 0: continue
        if n == "aurora":
            sp = aurora_sprite(); a = clamp(e / .8)
            for k in range(4):
                x = 140 + k * 270 + 70 * math.sin(T * .7 + k * 1.9); s2 = sp.resize((int(520 + 90 * math.sin(T * .9 + k)), 950), Image.BILINEAR)
                paste_c(im, fade(s2, a * (.7 + .3 * math.sin(T * 1.7 + k))), x, 520 + 30 * math.sin(T + k))
        if n == "meteors":
            for k in range(int(f.get("amount", 7))):
                ph = (e * r.uniform(.5, .9) + r.random()) % 1; x = r.uniform(0, WD * 1.4) - ph * 900; y = -100 + ph * 1500 * r.uniform(.6, 1)
                for j in range(9): d.ellipse([x + j * 22 - 9 + j, y - j * 30 - 9 + j, x + j * 22 + 9 - j, y - j * 30 + 9 - j], fill=(255, 220 - j * 12, 120 - j * 10, 240 - j * 24))
        if n == "stars_streak":
            for k in range(70):
                ang = r.uniform(0, 2 * math.pi); q = ((e * r.uniform(.6, 1.6) + r.random()) % 1) ** 2 * 1300; ln = 30 + q * .25
                d.line([(540 + math.cos(ang) * q, 900 + math.sin(ang) * q), (540 + math.cos(ang) * (q + ln), 900 + math.sin(ang) * (q + ln))], fill=(255, 255, 255, 200), width=4)
        if n == "lightning":
            for k in range(3):
                ts = r.uniform(0, max(.1, D - f["t"] * D - .3)); x = r.uniform(120, WD - 120); pts = [(x, 0)]
                for j in range(9): pts.append((pts[-1][0] + r.uniform(-90, 90), pts[-1][1] + r.uniform(90, 170)))
                if 0 <= e - ts < .22: d.line(pts, fill=(200, 220, 255, 180), width=26); d.line(pts, fill=(255, 255, 255, 255), width=9)

def fx_post(im, sh, u, D, p, T):
    d = ImageDraw.Draw(im, "RGBA"); r = random.Random(sh["id"] + 23); shx = shy = 0.0; tints = []; flash = 0.0
    for f in sh["fx"]:
        n = f["name"]; e = u - f["t"] * D; amt = f.get("amount", 1)
        if e < 0: continue
        q = clamp(e / max(.05, D - f["t"] * D))
        if n == "plasma":
            x0, y0 = fx_at(f, (.5, .2)); x1, y1 = XY(f.get("to", (.5, .8))); col = rgb(f.get("color"), (255, 150, 30))
            soft = Soft(6); pts = []
            for k in range(90):
                ph = r.random(); pos = q * 1.2 - ph * .6; w = r.gauss(0, .5); sz = r.uniform(.5, 1.2)
                if not 0 < pos < 1: continue
                w *= (30 + 170 * pos) * amt; px, py = x0 + (x1 - x0) * pos, y0 + (y1 - y0) * pos
                L = math.hypot(x1 - x0, y1 - y0) or 1; px += -(y1 - y0) / L * w + 12 * math.sin(T * 9 + k); py += (x1 - x0) / L * w + 12 * math.cos(T * 7 + k)
                pts.append((px, py, (22 + 50 * pos) * sz * amt))
            for px, py, rad in pts: soft.circle(px, py, rad * 1.5, (200, 50, 20, 170))
            for px, py, rad in pts: soft.circle(px, py, rad, col + (235,))
            for px, py, rad in pts: soft.circle(px, py, rad * .45, (255, 244, 200, 255))
            soft.apply(im); d = ImageDraw.Draw(im, "RGBA")
        if n == "flood": water(d, T, HT - (HT - HT * f.get("level", .42)) * ease(q))
        if n == "fire":
            base = fx_at(f, (.5, 1.0))[1]
            for li, (col, hgt) in enumerate((((230, 60, 20, 235), 1.0), ((255, 140, 30, 240), .7), ((255, 226, 110, 245), .4))):
                pts = [(0, base + 10)]
                for x in range(0, WD + 31, 30):
                    h = (150 + 130 * math.sin(x * .021 + T * 6 + li) + 90 * math.sin(x * .047 - T * 9 + li * 2)) * hgt * amt * clamp(e / .4 + .3)
                    pts.append((x, base - max(10, h)))
                pts.append((WD, base + 10)); d.polygon(pts, fill=col)
        if n in ("embers", "snow", "bubbles", "dust"):
            col = {"embers": (255, 150, 40), "snow": (255, 255, 255), "bubbles": (200, 240, 255), "dust": (160, 120, 80)}[n]
            for k in range(int(70 * amt)):
                sp = r.uniform(.25, .7); ph = (e * sp + r.random()) % 1; x = r.uniform(0, WD) + 50 * math.sin(T * 2 + k); rad = r.uniform(4, 11)
                y = HT * ph if n == "snow" else HT * (1 - ph)
                if n == "dust": x = (r.uniform(0, WD) + e * 500 * sp) % WD; rad *= 3
                if n == "bubbles": d.ellipse([x - rad * 2, y - rad * 2, x + rad * 2, y + rad * 2], outline=col + (190,), width=3)
                else: d.ellipse([x - rad, y - rad, x + rad, y + rad], fill=col + (90 if n == "dust" else 220,))
        if n == "rain":
            for k in range(int(130 * amt)):
                ph = (e * r.uniform(1.6, 2.6) + r.random()) % 1; x = r.uniform(-200, WD + 200); y = HT * ph
                d.line([(x - y * .18, y), (x - y * .18 - 12, y + 62)], fill=(200, 220, 255, 150), width=3)
        if n == "debris":
            for k in range(int(26 * amt)):
                ph = (e * r.uniform(.5, 1.3) + r.random()) % 1; x = -150 + ph * (WD + 300); y = r.uniform(200, 1500) + 90 * math.sin(T * 3 + k); sz = r.uniform(14, 46); ang = T * r.uniform(3, 9) + k
                pts = [(x + math.cos(ang + j * 2.1) * sz * (1 if j % 2 else .6), y + math.sin(ang + j * 2.1) * sz) for j in range(4)]
                d.polygon(pts, fill=r.choice([(60, 54, 50, 255), (110, 96, 84, 255), (150, 150, 158, 255)]))
            for k in range(22):
                ph = (e * r.uniform(1.5, 2.5) + r.random()) % 1; y = r.uniform(100, 1600); x = -200 + ph * (WD + 400)
                d.line([(x, y), (x + 170, y)], fill=(255, 255, 255, 90), width=4)
        if n == "smoke":
            x0, y0 = fx_at(f, (.5, .75))
            soft = Soft(6)
            for k in range(int(18 * amt)):
                ph = (e * r.uniform(.15, .35) + r.random()) % 1; x = x0 + r.uniform(-160, 160) + 60 * math.sin(T + k); y = y0 - ph * 950; rad = 60 + ph * 190
                soft.circle(x, y, rad, (38, 36, 40, int(210 * (1 - ph) * clamp(e / .5))))
            soft.apply(im); d = ImageDraw.Draw(im, "RGBA")
        if n == "speedlines":
            for k in range(46):
                if r.random() < .5 and int(T * 14 + k) % 2: continue
                ang = r.uniform(0, 2 * math.pi); r0 = r.uniform(520, 760); r1 = 1300
                d.polygon([(540 + math.cos(ang) * r0, 900 + math.sin(ang) * r0), (540 + math.cos(ang - .012) * r1, 900 + math.sin(ang - .012) * r1),
                           (540 + math.cos(ang + .012) * r1, 900 + math.sin(ang + .012) * r1)], fill=(255, 255, 255, 170))
        if n == "crack":
            x0, y0 = fx_at(f, (.5, .6)); col = rgb(f.get("color"), (20, 16, 18)); hot = f.get("color") is not None
            for b in range(int(6 * amt)):
                ang = b / 6 * 2 * math.pi + r.uniform(-.3, .3); pts = [(x0, y0)]
                for j in range(9):
                    ang += r.uniform(-.55, .55); stp = r.uniform(60, 130) * amt; pts.append((pts[-1][0] + math.cos(ang) * stp, pts[-1][1] + math.sin(ang) * stp))
                m = max(2, int(len(pts) * ease(clamp(e / (.5 * max(.4, D))))) + 1)
                if hot: d.line(pts[:m], fill=(255, 230, 150, 120), width=34)
                d.line(pts[:m], fill=col + (255,), width=16); d.line(pts[:m], fill=((255, 240, 200) if hot else (90, 84, 88)) + (255,), width=4)
        if n == "shockwave" and e < 1.3:
            x0, y0 = fx_at(f); rad = 40 + 1500 * (1 - (1 - e / 1.3) ** 2.2) * amt; a = int(255 * (1 - e / 1.3)); col = rgb(f.get("color"), (255, 255, 255))
            d.ellipse([x0 - rad, y0 - rad * .8, x0 + rad, y0 + rad * .8], outline=col + (a,), width=int(8 + 30 * (1 - e / 1.3)))
            shk = 24 * math.exp(-e * 4); shx += random.uniform(-shk, shk); shy += random.uniform(-shk, shk)
        if n == "explosion":
            x0, y0 = fx_at(f); k = 1 - (1 - clamp(e / .7)) ** 3; a = clamp(1.25 - e / 1.3)
            if a > 0:
                soft = Soft(4)
                for col, m in (((70, 40, 36), 1.12), ((200, 40, 20), 1.0), ((255, 130, 20), .78), ((255, 220, 90), .52), ((255, 255, 235), .27)):
                    rad = (70 + 560 * k) * m * amt
                    for j in range(9):
                        ang = j / 9 * 2 * math.pi + m * 3; ox, oy = math.cos(ang) * rad * .45, math.sin(ang) * rad * .45; rj = rad * (.55 + .2 * math.sin(j * 2.3 + m * 7))
                        soft.circle(x0 + ox, y0 + oy, rj, col + (int(245 * clamp(a)),))
                soft.apply(im); d = ImageDraw.Draw(im, "RGBA")
                for j in range(26):
                    ang = r.uniform(0, 2 * math.pi); q0 = (200 + 1500 * r.uniform(.4, 1) * e) * amt
                    d.line([(x0 + math.cos(ang) * q0, y0 + math.sin(ang) * q0), (x0 + math.cos(ang) * (q0 + 80), y0 + math.sin(ang) * (q0 + 80))], fill=(255, 230, 150, int(255 * a)), width=8)
            flash = max(flash, .85 * (1 - e / .2)); shk = 30 * math.exp(-e * 4); shx += random.uniform(-shk, shk); shy += random.uniform(-shk, shk)
        if n == "flash": flash = max(flash, .9 * (1 - e / .28))
        if n == "lightning":
            r2 = random.Random(sh["id"] + 11)
            for k in range(3):
                ts = r2.uniform(0, max(.1, D - f["t"] * D - .3)); [r2.uniform(0, 1) for _ in range(19)]
                if 0 <= e - ts < .1: flash = max(flash, .5)
        if n in ("shake", "quake"):
            a = (14 if n == "shake" else 34) * amt; shx += random.uniform(-a, a); shy += random.uniform(-a, a)
        if n == "freeze": tints.append(((190, 230, 255), .5 * ease(q)))
        if n == "heat": tints.append(((255, 60, 20), (.1 + .25 * ease(q)) * (.85 + .15 * math.sin(T * 8))))
        if n == "dark": tints.append(((0, 0, 0), .8 * ease(q) * amt))
        if n == "dust": tints.append(((150, 110, 70), .28))
    for col, a in tints:
        if a > .01: im = Image.blend(im, Image.new("RGB", (WD, HT), col), clamp(a))
    if flash > .01: im = Image.blend(im, Image.new("RGB", (WD, HT), (255, 255, 255)), clamp(flash))
    return im, shx, shy

_yy, _xx = np.mgrid[0:HT, 0:WD]
_rv = np.sqrt(((_xx - WD / 2) / (WD * .75)) ** 2 + ((_yy - HT / 2) / (HT * .7)) ** 2)
VIGNETTE = Image.fromarray(np.dstack([np.zeros((HT, WD, 3), np.uint8), (np.clip(_rv - .55, 0, 1) * 190).astype(np.uint8)]), "RGBA")
del _yy, _xx, _rv

def scene(T):
    sh = next((s for s in SHOTS if s["t0"] <= T < s["t1"]), SHOTS[-1])
    u = T - sh["t0"]; D = min(sh["t1"], TOTAL) - sh["t0"]; p = clamp(u / D)
    im = bg_static(sh["bg"]).copy()
    bg_dynamic(im, ImageDraw.Draw(im, "RGBA"), sh, u, p, T)
    fx_pre(im, sh, u, D, p, T)
    for a in sh["actors"]: draw_actor(im, a, sh, u, D, p, T)
    im, shx, shy = fx_post(im, sh, u, D, p, T)
    cam = sh.get("cam", "push"); fx_, fy_ = XY(sh.get("focus", (.5, .47)))
    z = {"push": 1.0 + .13 * p, "pull": 1.15 - .13 * p, "static": 1.02 + .02 * p}.get(cam, 1.13)
    if cam == "pan_l": fx_ += (.5 - p) * 130
    if cam == "pan_r": fx_ -= (.5 - p) * 130
    if cam == "tilt_up": fy_ += (.5 - p) * 220
    if cam == "tilt_down": fy_ -= (.5 - p) * 220
    if sh["id"] > 0: z += .07 * math.exp(-u * 10)
    if shx or shy: z = max(z, 1.05)
    cw, ch = WD / z, HT / z
    x0 = min(max(fx_ - cw / 2 + shx, 0), WD - cw); y0 = min(max(fy_ - ch / 2 + shy, 0), HT - ch)
    im = im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((WD, HT), Image.BILINEAR)
    im.paste(VIGNETTE, (0, 0), VIGNETTE)
    return im, sh, u, D

def label(text, col):
    f = font(96); tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    while tmp.textlength(text, font=f) > 880 and f.size > 50: f = font(f.size - 6)
    w = int(tmp.textlength(text, font=f)) + 70
    im = Image.new("RGBA", (w + 20, 170), (0, 0, 0, 0)); dd = ImageDraw.Draw(im)
    dd.rounded_rectangle([10, 15, w + 10, 155], 28, fill=col + (255,), outline=(0, 0, 0), width=8)
    dd.text((45, 22 + (96 - f.size) * .6), text, font=f, fill=(20, 20, 20))
    return im.rotate(random.choice([-4, -2, 2, 4]), resample=Image.BICUBIC, expand=True)
PALETTE = [(255, 214, 102), (130, 210, 255), (170, 235, 160), (255, 170, 170), (205, 180, 255), (255, 200, 140)]
for sh in SHOTS:
    sh["label"] = label(str(sh["pop"]).upper(), PALETTE[sh["id"] % len(PALETTE)]) if sh.get("pop") else None
HOOK_TXT = spec["hook"].get("screen", "").upper()
ASK = (spec.get("ask") or "").upper()
LOOP_T = TOTAL - .2
F0 = None

def frame(T):
    global F0
    im, sh, u, D = scene(T)
    if F0 is None: F0 = scene(0.0)[0]
    if T > LOOP_T: im = Image.blend(im, F0, ease((T - LOOP_T) / .2))
    d = ImageDraw.Draw(im, "RGBA")
    seg = segs[sh["seg"]]
    if HOOK_TXT and (T < 1.9 or T > LOOP_T):  # written hook: big for the first 1.9s only, never a permanent title
        k = (.7 + .3 * ease_back(T / .16)) if T < .16 else (1 - ease((T - 1.6) / .3) if T < 1.9 else ease((T - LOOP_T) / .2))
        if k > .05: center_text(d, 330, HOOK_TXT, font(138 * k), (255, 222, 40), int(12 * k) + 2)
    elif sh.get("counter") and T < LOOP_T:
        c = sh["counter"]; k = EASES["out"](u / max(.3, D * .7)); v = c.get("from", 0) + (c["to"] - c.get("from", 0)) * k
        txt = f"{v:,.{c.get('decimals', 0)}f}" + (" " + c["unit"].upper() if c.get("unit") else "")
        f = font(150)
        while d.textlength(txt, font=f) > 960 and f.size > 70: f = font(f.size - 8)
        center_text(d, 330, txt, f, (255, 255, 255), 12)
    elif sh["label"] is not None and u < 1.7 and T < LOOP_T:
        lk = ease_back(u / .25); L = sh["label"]
        if lk < .98: L = L.resize((max(2, int(L.width * lk)), max(2, int(L.height * lk))))
        paste_c(im, L, WD / 2, 330)
    elif ASK and LOOP_T - 2.4 < T < LOOP_T:
        f = font(64); d.rounded_rectangle([60, 230, WD - 60, 430], 30, fill=(10, 10, 14, 200)); center_text(d, 330, ASK, f, (255, 255, 255), 0, maxw=900)
    ws = seg["words"]
    cur = next((n for n, (_, a, b2) in enumerate(ws) if a <= T < b2), None)
    if cur is None: cur = len(ws) - 1 if T >= ws[-1][1] else 0
    cs = (cur // 3) * 3; chunk = ws[cs:cs + 3]
    f = font(100); line = " ".join(w for w, _, _ in chunk).upper()
    while d.textlength(line, font=f) > 980 and f.size > 60: f = font(f.size - 8)
    x = (WD - d.textlength(line, font=f)) / 2; y = 1335 + (1 - ease_back((T - chunk[0][1]) / .12)) * 30
    for n, (w, a, b2) in enumerate(chunk):
        clean = w.lower().strip(".,!?;:'\"")
        colr = (255, 222, 40) if cs + n == cur and a <= T < b2 + .15 else ((120, 230, 120) if clean in KW else (255, 255, 255))
        d.text((x, y), w.upper(), font=f, fill=colr, stroke_width=10, stroke_fill=(15, 15, 15))
        x += d.textlength(w.upper() + " ", font=f)
    return im

# ---------------------------------------------------------------- encode + contact sheet
mix = f"{WORK}/mix.wav"
mxv = np.max(np.abs(audio)) or 1
sf.write(mix, (audio / mxv * .9)[:int(TOTAL * SR)], SR)
proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{WD}x{HT}", "-r", str(FPS), "-i", "-",
                         "-i", mix, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                         "-c:a", "aac", "-b:a", "160k", "-af", "loudnorm=I=-14:TP=-1.5", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
want = {0: None}
for sh in SHOTS: want[int((sh["t0"] + (min(sh["t1"], TOTAL) - sh["t0"]) * .6) * FPS)] = None
for n in range(NF):
    fr = frame(n / FPS).convert("RGB")
    if n in want: want[n] = fr.resize((270, 480), Image.BILINEAR)
    proc.stdin.write(fr.tobytes())
proc.stdin.close(); proc.wait()
thumbs = [v for _, v in sorted(want.items()) if v is not None]
cols = min(6, len(thumbs)); rows = -(-len(thumbs) // cols)
sheet = Image.new("RGB", (cols * 270, rows * 480))
for i, th in enumerate(thumbs): sheet.paste(th, ((i % cols) * 270, (i // cols) * 480))
sheet.save(f"{WORK}/check.jpg", quality=85)
print("done", round(TOTAL, 2), "s", NF, "frames", len(SHOTS), "shots; contact sheet:", f"{WORK}/check.jpg (frame 0 first, then one frame per shot)")
