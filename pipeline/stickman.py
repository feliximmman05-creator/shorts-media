"""Stick man Short renderer.

Usage: python3 stickman.py <work_dir> <out.mp4>
work_dir holds script.json, seg0.wav..segN.wav (from tts.py) and emoji/<code>.png.

Triple hook: 0.0s stick man slams a prop (impact, shake, flash) = visual hook;
0.0-1.5s big centered 3-5 word text = written hook; voice starts at 0.7s = verbal hook.
Camera cuts / pose changes about every 1.8s. Ends by returning to the opening pose and
text position so the replay loops cleanly. No outro, no progress bar.
"""
import json, os, sys, math, random, subprocess
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
WORK, OUT = sys.argv[1], sys.argv[2]
FPS, WD, HT, SR = 30, 1080, 1920, 24000
FONT = f"{HERE}/fonts/Anton.ttf"
BRAND = os.environ.get("BRAND", "INTO THE DARK WEB")
VOICE_START, GAP, TAIL = 0.7, 0.10, 0.30
POSE_EVERY, BLEND = 1.8, 0.16
spec = json.load(open(f"{WORK}/script.json"))
random.seed(len(json.dumps(spec)))

_fc = {}
def font(sz):
    sz = max(8, int(sz))
    if sz not in _fc:
        _fc[sz] = ImageFont.truetype(FONT, sz)
    return _fc[sz]

def ease(x):
    x = min(1, max(0, x)); return x * x * (3 - 2 * x)

def ease_back(x):
    x = min(1, max(0, x)); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

# ---------------------------------------------------------------- poses
# units: hip at (0,0), y down; 1 unit = S px
S, HIPX, HIPY = 520, 540, 1120
BASE = dict(neck=(0, -.55), head=(0, -.72), le=(-.14, -.33), lh=(-.18, -.1), re=(.14, -.33), rh=(.18, -.1),
            lk=(-.08, .22), lf=(-.12, .46), rk=(.08, .22), rf=(.12, .46), hipy=(0, 0))
def P(**kw):
    d = dict(BASE); d.update(kw); return d
POSES = {
    "idle": P(),
    "talk": P(re=(.22, -.42), rh=(.3, -.58)),
    "explain": P(le=(-.22, -.4), lh=(-.32, -.3), re=(.22, -.4), rh=(.32, -.3)),
    "point": P(re=(.25, -.5), rh=(.48, -.56), head=(.03, -.72)),
    "shock": P(le=(-.25, -.6), lh=(-.1, -.82), re=(.25, -.6), rh=(.1, -.82), lk=(-.14, .2), lf=(-.22, .45), rk=(.14, .2), rf=(.22, .45)),
    "shrug": P(le=(-.24, -.33), lh=(-.34, -.5), re=(.24, -.33), rh=(.34, -.5), head=(0, -.71)),
    "facepalm": P(re=(.2, -.48), rh=(.04, -.72), head=(0, -.7)),
    "celebrate": P(le=(-.2, -.72), lh=(-.32, -.95), re=(.2, -.72), rh=(.32, -.95), lk=(-.14, .15), lf=(-.1, .4), rk=(.14, .15), rf=(.1, .4), hipy=(0, -.08)),
    "think": P(re=(.2, -.38), rh=(.06, -.6), le=(-.02, -.3), lh=(.14, -.36), head=(.02, -.72)),
    "sad": P(neck=(0, -.53), head=(0, -.66), le=(-.1, -.3), lh=(-.12, -.05), re=(.1, -.3), rh=(.12, -.05), hipy=(0, .02)),
    "hold": P(re=(.22, -.48), rh=(.3, -.7)),
    "raise": P(le=(-.13, -.7), lh=(-.03, -.9), re=(.13, -.7), rh=(.03, -.9)),
    "slam": P(neck=(.06, -.52), head=(.1, -.68), le=(.05, -.33), lh=(.28, -.12), re=(.16, -.32), rh=(.34, -.1),
              lk=(-.12, .18), lf=(-.16, .44), rk=(.14, .16), rf=(.2, .44), hipy=(0, .05)),
    "run": P(),
}
HOLD_AT = {"raise": "both", "slam": "rh", "hold": "rh"}
FACE = {"shock": "shock", "celebrate": "happy", "sad": "sad", "facepalm": "sad", "slam": "shock"}

def lerp_pose(a, b, k):
    return {j: (a[j][0] + (b[j][0] - a[j][0]) * k, a[j][1] + (b[j][1] - a[j][1]) * k) for j in a}

# ---------------------------------------------------------------- audio
segs = [dict(kind="hook", **spec["hook"])] + [dict(kind="beat", **b) for b in spec["beats"]]
t = VOICE_START
for i, s in enumerate(segs):
    a, sr = sf.read(f"{WORK}/seg{i}.wav", dtype="float32")
    if a.ndim > 1: a = a.mean(1)
    assert sr == SR, sr
    s["audio"], s["start"], s["len"] = a, t, len(a) / SR
    t += s["len"] + GAP
TOTAL = t - GAP + TAIL
NF = int(TOTAL * FPS)
for i, s in enumerate(segs):
    s["win0"] = 0.0 if i == 0 else s["start"] - GAP / 2
    s["win1"] = TOTAL if i == len(segs) - 1 else segs[i + 1]["start"] - GAP / 2

audio = np.zeros(int(TOTAL * SR) + SR, dtype=np.float32)
for s in segs:
    i0 = int(s["start"] * SR); audio[i0:i0 + len(s["audio"])] += s["audio"]
voice_env = np.sqrt(np.convolve(audio ** 2, np.ones(int(SR * .05)) / int(SR * .05), mode="same"))
peak = max(1e-6, float(np.percentile(voice_env[voice_env > 1e-4], 95)) if (voice_env > 1e-4).any() else 1)

def sfx_add(t0, sig, vol):
    i0 = int(t0 * SR); n = min(len(sig), len(audio) - i0)
    if n > 0: audio[i0:i0 + n] += sig[:n] * vol
rng = np.random.default_rng(3)
def impact():
    n = int(SR * .45); tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * (70 - 30 * tt) * tt) * np.exp(-tt * 9) + rng.normal(0, 1, n) * np.exp(-tt * 40) * .5).astype(np.float32)
def whoosh():
    n = int(SR * .22); w = np.convolve(rng.normal(0, 1, n), np.ones(12) / 12, "same")
    return (w * np.sin(np.linspace(0, np.pi, n)) ** 2).astype(np.float32)
def pop():
    n = int(SR * .08); tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * 880 * tt * (1 + tt * 6)) * np.exp(-tt * 45)).astype(np.float32)

# ---------------------------------------------------------------- timeline (pose keyframes)
SLAM_T = 0.22
keys = [(0.0, "raise", 1.0), (SLAM_T, "slam", 1.12)]
cam_close = False
for i, s in enumerate(segs):
    seq = [spec["hook"].get("pose", "point")] if s["kind"] == "hook" else (s.get("poses") or ["talk", "explain"])
    t0 = max(s["win0"], SLAM_T + 0.9) if i == 0 else s["win0"]
    k = 0
    while t0 < s["win1"] - 0.6:
        cam_close = not cam_close
        keys.append((t0, seq[k % len(seq)], 1.22 if cam_close else 1.0))
        if i > 0 or k > 0: sfx_add(t0, whoosh(), .05)
        k += 1; t0 += POSE_EVERY
END_T = TOTAL - 0.38
keys = [k for k in keys if k[0] < END_T - .3] + [(END_T, "raise", 1.0)]
sfx_add(SLAM_T, impact(), .55)

def key_at(tt):
    idx = max(i for i, k in enumerate(keys) if k[0] <= tt)
    return idx, keys[idx]

# ---------------------------------------------------------------- assets
def emoji(code, size):
    p = f"{WORK}/emoji/{code}.png"
    im = Image.open(p).convert("RGBA") if os.path.exists(p) else Image.open(f"{WORK}/emoji/2b50.png").convert("RGBA")
    return im.resize((size, size), Image.LANCZOS)
hook_prop = emoji(spec["hook"].get("prop", "1f4a5"), 230)
for s in segs[1:]:
    s["prop_im"] = emoji(s["prop"], 250) if s.get("prop") else None
default_scene = spec.get("scene", "paper")
for i, s in enumerate(segs):
    if i == 0: s["scene"] = spec["hook"].get("scene") or (spec["beats"][0].get("scene") if spec["beats"] else None) or default_scene
    else: s["scene"] = s.get("scene") or segs[i - 1]["scene"]
    src = spec["hook"] if i == 0 else s
    s["set_im"] = [emoji(c, 460 if j == 0 else 340) for j, c in enumerate((src.get("set") or [])[:2])]
ROLE = (spec.get("role") or "").upper()
hidden = spec.get("hidden")
hidden_im = emoji(hidden["emoji"], 105) if hidden else None

PALETTE = [(255, 214, 102), (130, 210, 255), (170, 235, 160), (255, 170, 170), (205, 180, 255), (255, 200, 140)]
bg = Image.new("RGB", (WD, HT), (246, 241, 231))
d = ImageDraw.Draw(bg)
for y in range(40, HT, 60):
    for x in range(40, WD, 60):
        d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(226, 219, 205))
SCENES = {  # sky top, sky bottom, ground, stars, ground style
    "paper": ((246, 241, 231), (246, 241, 231), None, False, None),
    "space": ((4, 6, 22), (30, 22, 70), None, True, None),
    "moon": ((2, 2, 10), (20, 20, 40), (150, 150, 160), True, "craters"),
    "earth": ((10, 20, 60), (40, 90, 170), None, True, "planet"),
    "city": ((110, 170, 250), (205, 230, 255), (70, 72, 82), False, "skyline"),
    "night": ((8, 12, 36), (40, 48, 92), (24, 30, 44), True, "skyline"),
    "vice": ((120, 40, 140), (255, 140, 110), (46, 38, 62), False, "skyline"),
    "desert": ((250, 170, 100), (255, 228, 170), (226, 186, 118), False, "dunes"),
    "grass": ((110, 180, 250), (200, 232, 255), (92, 168, 82), False, None),
    "ocean": ((120, 190, 250), (210, 238, 255), (36, 108, 190), False, "waves"),
    "lab": ((52, 62, 84), (88, 98, 122), (38, 42, 54), False, "grid"),
    "factory": ((70, 66, 64), (120, 110, 100), (50, 48, 46), False, "grid"),
    "stadium": ((110, 170, 250), (205, 230, 255), (192, 86, 62), False, "track"),
}
GROUND_Y = 1372
_yy, _xx = np.mgrid[0:HT, 0:WD]
_r = np.sqrt(((_xx - WD / 2) / (WD * .75)) ** 2 + ((_yy - HT / 2) / (HT * .7)) ** 2)
VIGNETTE = Image.fromarray(np.dstack([np.zeros((HT, WD, 3), np.uint8), (np.clip(_r - .55, 0, 1) * 200).astype(np.uint8)]), "RGBA")
del _yy, _xx, _r
_scene = {}
def scene_bg(name):
    name = name if name in SCENES else "paper"
    if name in _scene: return _scene[name]
    top, bot, gnd, stars, style = SCENES[name]
    if name == "paper":
        im = bg.copy()
    else:
        k = np.linspace(0, 1, HT)[:, None, None]
        arr = (np.array(top)[None, None, :] * (1 - k) + np.array(bot)[None, None, :] * k).repeat(WD, axis=1)
        im = Image.fromarray(arr.astype(np.uint8), "RGB")
    d = ImageDraw.Draw(im, "RGBA")
    rnd = random.Random(name)
    if stars:
        for _ in range(160):
            x, y, r = rnd.uniform(0, WD), rnd.uniform(0, GROUND_Y if gnd else HT), rnd.choice([1.5, 2, 2.5, 3.5])
            d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, rnd.randint(120, 255)))
    if style == "skyline":
        x = 0
        while x < WD:
            w = rnd.randint(70, 150); h = rnd.randint(180, 520)
            col = {"night": (40, 48, 70, 255), "vice": (70, 30, 90, 255)}.get(name, (150, 165, 190, 255))
            d.rectangle([x, GROUND_Y - h, x + w - 8, GROUND_Y], fill=col)
            for wy in range(GROUND_Y - h + 20, GROUND_Y - 20, 40):
                for wx in range(x + 12, x + w - 20, 28):
                    if rnd.random() < .5: d.rectangle([wx, wy, wx + 12, wy + 18], fill=(255, 220, 120, 200) if name in ("night", "vice") else (220, 230, 245, 255))
            x += w
    if name == "vice":
        d.ellipse([WD / 2 - 260, 620, WD / 2 + 260, 1140], fill=(255, 200, 90, 230))
        for k in range(6): d.rectangle([WD / 2 - 270, 900 + k * 40, WD / 2 + 270, 912 + k * 40], fill=(255, 120, 120, 255))
    if style == "planet":
        d.ellipse([-300, 1250, WD + 300, 2900], fill=(40, 120, 220))
        for _ in range(9):
            cx, cy = rnd.uniform(0, WD), rnd.uniform(1330, 1800)
            d.ellipse([cx - 150, cy - 50, cx + 150, cy + 50], fill=(80, 170, 90))
    if gnd:
        d.rectangle([0, GROUND_Y, WD, HT], fill=gnd)
        if style == "craters":
            for _ in range(14):
                cx, cy, r = rnd.uniform(0, WD), rnd.uniform(GROUND_Y + 40, HT - 80), rnd.uniform(20, 70)
                d.ellipse([cx - r, cy - r * .35, cx + r, cy + r * .35], fill=(120, 120, 132))
        if style == "grid":
            for gx in range(-WD, 2 * WD, 120):
                d.line([(WD / 2 + (gx - WD / 2) * .25, GROUND_Y), (gx, HT)], fill=(255, 255, 255, 30), width=3)
            for gy in (1420, 1500, 1620, 1780): d.line([(0, gy), (WD, gy)], fill=(255, 255, 255, 30), width=3)
        if style == "track":
            for gy in (1440, 1540, 1660): d.line([(0, gy), (WD, gy)], fill=(255, 255, 255, 140), width=6)
        if style == "waves":
            for gy in range(GROUND_Y + 40, HT, 70):
                for gx in range(0, WD, 120): d.arc([gx, gy, gx + 120, gy + 40], 200, 340, fill=(200, 230, 255, 160), width=5)
        if style == "dunes":
            d.ellipse([-200, GROUND_Y - 120, 600, GROUND_Y + 200], fill=gnd); d.ellipse([400, GROUND_Y - 80, 1300, GROUND_Y + 200], fill=gnd)
        d.line([(0, GROUND_Y), (WD, GROUND_Y)], fill=(0, 0, 0, 90), width=5)
    _scene[name] = im
    return im
def is_dark(name):
    t = SCENES.get(name, SCENES["paper"])[0]; return sum(t) < 330

_blob = {}
def blob(col):
    if col not in _blob:
        g = Image.new("RGBA", (WD, HT), (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse([WD / 2 - 360, 1000 - 380, WD / 2 + 360, 1000 + 380], fill=col + (150,))
        _blob[col] = g.filter(ImageFilter.GaussianBlur(70))
    return _blob[col]

def label(text, col):
    f = font(96)
    tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    w = int(tmp.textlength(text, font=f)) + 70
    im = Image.new("RGBA", (w + 20, 170), (0, 0, 0, 0))
    dd = ImageDraw.Draw(im)
    dd.rounded_rectangle([10, 15, w + 10, 155], 28, fill=col + (255,), outline=(0, 0, 0), width=8)
    dd.text((45, 22), text, font=f, fill=(20, 20, 20))
    return im.rotate(random.choice([-5, -3, 3, 5]), resample=Image.BICUBIC, expand=True)
for i, s in enumerate(segs):
    s["col"] = PALETTE[i % len(PALETTE)]
    s["label"] = label(s["pop"].upper(), s["col"]) if s.get("pop") else None
    if s.get("pop"): sfx_add(s["win0"] + .05, pop(), .25)

# word timings (character-proportional inside each spoken segment)
KW = set(w.lower() for w in spec.get("keyword", "").split())
for s in segs:
    words = s["text"].split(); tot = sum(len(w) + 2 for w in words); acc = 0; s["words"] = []
    for w in words:
        a = acc / tot * s["len"]; acc += len(w) + 2
        s["words"].append((w, s["start"] + a, s["start"] + acc / tot * s["len"]))

# ---------------------------------------------------------------- drawing
BOX = (100, 470, 980, 1470)  # region for the supersampled stick man layer
SS = 2
def to_px(pt, hipy):
    return (HIPX + pt[0] * S, HIPY + (pt[1] + hipy) * S)

STYLE = spec.get("style", "stick")
LOOK = dict(skin="#f2c79b", hair="#2b211c", shirt="#2f6fd6", pants="#2d3142", hair_style="short", hat=None)
LOOK.update(spec.get("look") or {})
def _rgb(h): h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
HEAD_R = (.16 if STYLE == "cartoon" else .115) * S
_hat = None
if STYLE == "cartoon" and LOOK.get("hat"):
    _hp = f"{WORK}/emoji/{LOOK['hat']}.png"
    if os.path.exists(_hp): _hat = Image.open(_hp).convert("RGBA")

def draw_cartoon(layer, layer_draw, pose, tt, face, mouth):
    ox, oy = BOX[0], BOX[1]
    hy = pose["hipy"][1]
    pts = {j: to_px(pose[j], hy) for j in pose if j != "hipy"}
    hip = (HIPX, HIPY + hy * S)
    OL = (34, 26, 30); skin, hair, shirt, pants = (_rgb(LOOK[k]) for k in ("skin", "hair", "shirt", "pants"))
    c = lambda p: ((p[0] - ox) * SS, (p[1] - oy) * SS)
    def seg(a, b, w, col, outline=10):
        for ww, cc in ((w + outline, OL), (w, col)):
            layer_draw.line([c(a), c(b)], fill=cc, width=int(ww * SS))
            for q in (a, b):
                r = ww * SS / 2; x, y = c(q); layer_draw.ellipse([x - r, y - r, x + r, y + r], fill=cc)
    def dot(q, r, col, outline=6):
        x, y = c(q)
        layer_draw.ellipse([x - (r + outline) * SS, y - (r + outline) * SS, x + (r + outline) * SS, y + (r + outline) * SS], fill=OL)
        layer_draw.ellipse([x - r * SS, y - r * SS, x + r * SS, y + r * SS], fill=col)
    # legs + shoes
    for k, f in (("lk", "lf"), ("rk", "rf")):
        seg(hip, pts[k], 40, pants); seg(pts[k], pts[f], 36, pants)
        fx, fy = c(pts[f]); w, h = 46 * SS, 22 * SS
        layer_draw.ellipse([fx - w - 6 * SS, fy - h - 6 * SS, fx + w + 6 * SS, fy + h + 6 * SS], fill=OL)
        layer_draw.ellipse([fx - w, fy - h, fx + w, fy + h], fill=(52, 50, 60))
    # body (capsule)
    sh = (pts["neck"][0], pts["neck"][1] + .06 * S)
    seg(sh, (hip[0], hip[1] - .02 * S), .25 * S, shirt, 12)
    # arms: sleeve to elbow, skin forearm, round hand
    for side, e, h in ((-1, "le", "lh"), (1, "re", "rh")):
        shoulder = (pts["neck"][0] + side * .085 * S, pts["neck"][1] + .07 * S)
        seg(shoulder, pts[e], 34, shirt); seg(pts[e], pts[h], 28, skin); dot(pts[h], 20, skin)
    # neck + head
    seg(pts["neck"], (pts["neck"][0], pts["neck"][1] + .04 * S), 34, skin)
    hx, hyy = pts["head"]; R = HEAD_R
    for dx in (-1, 1): dot((hx + dx * R * .98, hyy + R * .05), 18, skin)
    dot((hx, hyy), R, skin, 7)
    hs = LOOK.get("hair_style", "short")
    x0, y0 = c((hx - R - 4, hyy - R - 8)); x1, y1 = c((hx + R + 4, hyy + R * .9))
    if hs in ("short", "long", "spiky"):
        layer_draw.chord([x0, y0, x1, y1], 180, 360, fill=hair)
        layer_draw.ellipse([*c((hx - R * .2, hyy - R * 1.02)), *c((hx + R * .95, hyy - R * .35))], fill=hair)
        if hs == "long":
            for dx in (-1, 1):
                a = (hx + dx * R * .92, hyy - R * .1); b = (hx + dx * R * .98, hyy + R * 1.1)
                layer_draw.line([c(a), c(b)], fill=hair, width=int(R * .38 * SS))
        if hs == "spiky":
            for i in range(5):
                bx = hx - R * .8 + i * R * .4
                layer_draw.polygon([c((bx - R * .2, hyy - R * .7)), c((bx, hyy - R * 1.35)), c((bx + R * .2, hyy - R * .7))], fill=hair)
    # face
    blink = (tt % 3.3) < 0.1 and face != "shock"
    for sx in (-1, 1):
        ex, ey = hx + sx * R * .36 + R * .05, hyy + R * .05
        rx, ry = R * .2, R * (.26 if face == "shock" else .22)
        if blink:
            layer_draw.line([c((ex - rx, ey)), c((ex + rx, ey))], fill=OL, width=6 * SS)
        else:
            layer_draw.ellipse([*c((ex - rx, ey - ry)), *c((ex + rx, ey + ry))], fill=(255, 255, 255), outline=OL, width=4 * SS)
            pr = R * (.08 if face == "shock" else .11)
            px, py = ex + R * .05, ey + R * .03
            layer_draw.ellipse([*c((px - pr, py - pr)), *c((px + pr, py + pr))], fill=(25, 22, 30))
            layer_draw.ellipse([*c((px - pr * .2, py - pr * .7)), *c((px + pr * .25, py - pr * .25))], fill=(255, 255, 255))
        by = ey - ry - R * (.16 if face == "shock" else .1)
        tilt = -.06 * R * sx if face == "sad" else (.05 * R * sx if face == "shock" else 0)
        layer_draw.line([c((ex - rx, by + tilt)), c((ex + rx, by - tilt))], fill=hair if hs != "bald" else OL, width=7 * SS)
        layer_draw.ellipse([*c((ex - R * .14, ey + R * .3)), *c((ex + R * .14, ey + R * .42))], fill=(255, 140, 140))
    mx, my = hx + R * .05, hyy + R * .58
    if face == "shock":
        layer_draw.ellipse([*c((mx - R * .12, my - R * .1)), *c((mx + R * .12, my + R * .18))], fill=(110, 30, 40), outline=OL, width=4 * SS)
    elif face == "sad":
        layer_draw.arc([*c((mx - R * .2, my)), *c((mx + R * .2, my + R * .25))], 200, 340, fill=OL, width=6 * SS)
    else:
        h = R * (.04 + mouth * .26); w = R * (.22 if face == "happy" else .18)
        if h < R * .07:
            layer_draw.arc([*c((mx - w, my - R * .16)), *c((mx + w, my + R * .06))], 20, 160, fill=OL, width=6 * SS)
        else:
            layer_draw.chord([*c((mx - w, my - h * .5)), *c((mx + w, my + h))], 0, 180, fill=(110, 30, 40), outline=OL, width=4 * SS)
    if _hat is not None:
        hw = int(R * 1.7 * SS); hat = _hat.resize((hw, hw), Image.LANCZOS)
        layer.paste(hat, (int((hx - ox) * SS - hw / 2), int((hyy - R * 1.55 - oy) * SS - hw / 2 + hw * .25)), hat)
    return pts

def draw_stickman(layer_draw, pose, tt, face, mouth):
    ox, oy = BOX[0], BOX[1]
    hy = pose["hipy"][1]
    pts = {j: to_px(pose[j], hy) for j in pose if j != "hipy"}
    hip = (HIPX, HIPY + hy * S)
    def L(a, b, w=22, col=(20, 20, 20)):
        layer_draw.line([((a[0] - ox) * SS, (a[1] - oy) * SS), ((b[0] - ox) * SS, (b[1] - oy) * SS)], fill=col, width=int(w * SS))
        for p in (a, b):
            r = w * SS / 2
            layer_draw.ellipse([(p[0] - ox) * SS - r, (p[1] - oy) * SS - r, (p[0] - ox) * SS + r, (p[1] - oy) * SS + r], fill=col)
    bones = [(pts["neck"], hip)] + [(pts[a], pts[b]) for a, b in (("neck", "le"), ("le", "lh"), ("neck", "re"), ("re", "rh"), ("lk", "lf"), ("rk", "rf"))] + [(hip, pts["lk"]), (hip, pts["rk"])]
    for a, b in bones: L(a, b, 34, (255, 255, 255))
    hx0, hy0 = pts["head"]; R0 = .115 * S + 7
    layer_draw.ellipse([(hx0 - R0 - ox) * SS, (hy0 - R0 - oy) * SS, (hx0 + R0 - ox) * SS, (hy0 + R0 - oy) * SS], fill=(255, 255, 255))
    for a, b in bones: L(a, b)
    hx, hyy = pts["head"]; R = .115 * S
    c = lambda x, y: ((x - ox) * SS, (y - oy) * SS)
    x0, y0 = c(hx - R, hyy - R); x1, y1 = c(hx + R, hyy + R)
    layer_draw.ellipse([x0, y0, x1, y1], fill=(255, 255, 255), outline=(20, 20, 20), width=10 * SS)
    blink = (tt % 3.3) < 0.1 and face != "shock"
    er = (.024 if face == "shock" else .015) * S
    for sx in (-1, 1):
        ex, ey = hx + sx * .04 * S + .008 * S, hyy - .015 * S
        if blink:
            layer_draw.line([c(ex - er, ey), c(ex + er, ey)], fill=(20, 20, 20), width=5 * SS)
        else:
            layer_draw.ellipse([*c(ex - er, ey - er), *c(ex + er, ey + er)], fill=(20, 20, 20))
    mx, my = hx + .008 * S, hyy + .05 * S
    if face == "shock":
        r = .028 * S; layer_draw.ellipse([*c(mx - r * .8, my - r), *c(mx + r * .8, my + r)], fill=(20, 20, 20))
    elif face == "sad":
        layer_draw.arc([*c(mx - .035 * S, my), *c(mx + .035 * S, my + .05 * S)], 200, 340, fill=(20, 20, 20), width=5 * SS)
    else:
        h = .006 * S + mouth * .045 * S; w = .03 * S + (0.012 * S if face == "happy" else 0)
        if h < .01 * S:
            layer_draw.arc([*c(mx - w, my - .03 * S), *c(mx + w, my + .015 * S)], 20, 160, fill=(20, 20, 20), width=5 * SS)
        else:
            layer_draw.ellipse([*c(mx - w, my - h * .4), *c(mx + w, my + h)], fill=(20, 20, 20))
    return pts

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

HOOK_TXT = spec["hook"]["screen"].upper()
BAIT = "SPOT THE HIDDEN ITEM? COMMENT WHAT IT WAS" if hidden else None

def frame(tt):
    seg = next((s for s in segs if s["win0"] <= tt < s["win1"]), segs[-1])
    idx, (kt, pname, zoom) = key_at(tt)
    prev = keys[idx - 1] if idx > 0 else keys[idx]
    k = ease((tt - kt) / BLEND)
    pose = lerp_pose(POSES[prev[1]], POSES[pname], k)
    z = prev[2] + (zoom - prev[2]) * k
    z += 0.07 * math.exp(-(tt - kt) * 10)  # punch-in on every cut
    z += min(.04, .02 * (tt - kt))  # slow push-in within each shot
    # life: breathing, gesture wiggle, running legs
    br = .008 * math.sin(tt * 2 * math.pi * .8)
    for j in ("neck", "head"): pose[j] = (pose[j][0], pose[j][1] + br)
    speaking = any(s["start"] <= tt < s["start"] + s["len"] for s in segs)
    if speaking and pname in ("talk", "explain", "point"):
        pose["rh"] = (pose["rh"][0] + .02 * math.sin(tt * 9), pose["rh"][1] + .02 * math.cos(tt * 7))
    if pname == "run":
        a = math.sin(tt * 12) * k
        pose.update(lk=(.12 * a, .2), lf=(.25 * a, .42 - .05 * abs(a)), rk=(-.12 * a, .2), rf=(-.25 * a, .42 - .05 * abs(a)),
                    le=(-.12 * a + .02, -.35), lh=(-.2 * a + .08, -.2), re=(.12 * a + .02, -.35), rh=(.2 * a + .08, -.2), hipy=(0, -.03 * abs(a)),
                    neck=(.06, -.54), head=(.09, -.71))
    face = FACE.get(pname, "happy" if pname in ("celebrate",) else "normal")
    i = int(tt * SR); mouth = min(1, float(voice_env[min(i, len(voice_env) - 1)]) / peak) if speaking else 0

    im = bg.copy()
    sseg = segs[0] if tt >= END_T else seg
    im = scene_bg(sseg["scene"]).copy()
    si = segs.index(sseg)
    if si > 0 and segs[si - 1]["scene"] != sseg["scene"] and tt - sseg["win0"] < .35:
        kk = ease((tt - sseg["win0"]) / .35)
        old = scene_bg(segs[si - 1]["scene"])
        mix = Image.new("RGB", (WD, HT)); mix.paste(old, (int(-kk * WD), 0)); mix.paste(im, (int((1 - kk) * WD), 0)); im = mix
    if sseg["scene"] == "paper":
        b = blob(sseg["col"]); im.paste(b, (0, 0), b)
    for j, sp in enumerate(sseg["set_im"]):
        drift = math.sin(tt * .6 + j) * 14
        k_in = ease((tt - sseg["win0"]) / .4) if sseg is not segs[0] else 1
        x = (255 if j == 0 else 845) + drift; y = (GROUND_Y - sp.height / 2 + 30 if j == 0 else 700)
        y += (1 - k_in) * 120
        im.paste(sp, (int(x - sp.width / 2), int(y - sp.height / 2)), sp)
    d = ImageDraw.Draw(im, "RGBA")
    if sseg["scene"] == "paper":
        d.line([(150, 1372), (930, 1372)], fill=(60, 55, 50), width=6)
    d.ellipse([HIPX - 150, 1360, HIPX + 150, 1386], fill=(0, 0, 0, 60))
    layer = Image.new("RGBA", ((BOX[2] - BOX[0]) * SS, (BOX[3] - BOX[1]) * SS), (0, 0, 0, 0))
    if STYLE == "cartoon": pts = draw_cartoon(layer, ImageDraw.Draw(layer), pose, tt, face, mouth)
    else: pts = draw_stickman(ImageDraw.Draw(layer), pose, tt, face, mouth)
    layer = layer.resize((BOX[2] - BOX[0], BOX[3] - BOX[1]), Image.LANCZOS)
    im.paste(layer, (BOX[0], BOX[1]), layer)
    if ROLE:
        hx, hyy = pts["head"]; f = font(46); tw = d.textlength(ROLE, font=f)
        x0, y0 = hx - tw / 2 - 20, hyy - HEAD_R - (150 if _hat is not None else 92)
        d.rounded_rectangle([x0, y0, x0 + tw + 40, y0 + 66], 16, fill=(15, 15, 15, 235), outline=(255, 255, 255), width=4)
        d.text((x0 + 20, y0 + 4), ROLE, font=f, fill=(255, 222, 40))
    # props
    hold = HOLD_AT.get(pname) if k > .5 else HOLD_AT.get(prev[1])
    prop = hook_prop if (tt < segs[0]["win1"] or tt >= END_T) else seg.get("prop_im")
    if prop is not None:
        if hold == "both":
            cx = (pts["lh"][0] + pts["rh"][0]) / 2; cy = (pts["lh"][1] + pts["rh"][1]) / 2 - prop.height * .42
        elif hold == "rh":
            cx, cy = pts["rh"][0] + 40, pts["rh"][1] - prop.height * .35
        else:
            cx, cy = 840, 760 + 22 * math.sin(tt * 3)
        pi = prop
        pop_k = ease_back((tt - seg["win0"]) / .35) if seg["kind"] == "beat" else 1
        if pop_k < .98:
            sz = max(4, int(prop.width * pop_k)); pi = prop.resize((sz, sz))
        im.paste(pi, (int(cx - pi.width / 2), int(cy - pi.height / 2)), pi)
    # impact lines on the slam
    if SLAM_T <= tt < SLAM_T + .3:
        ix, iy = pts["rh"]; a = 1 - (tt - SLAM_T) / .3
        for n in range(10):
            ang = n * math.pi / 5 + .3
            r0, r1 = 150, 150 + 120 * a
            d.line([(ix + math.cos(ang) * r0, iy + math.sin(ang) * r0), (ix + math.cos(ang) * r1, iy + math.sin(ang) * r1)], fill=(20, 20, 20, int(255 * a)), width=10)
    # hidden item (comment bait)
    if hidden and segs[1 + hidden["beat"]]["win0"] + .6 <= tt < segs[1 + hidden["beat"]]["win0"] + 1.4:
        im.paste(hidden_im, (95, 905), hidden_im)

    # camera: zoom toward head when close, shake after the slam
    focus = (540, 860) if zoom > 1.1 else (540, 990)
    shx = shy = 0
    if SLAM_T <= tt < SLAM_T + .3:
        a = (1 - (tt - SLAM_T) / .3) * 26; shx, shy = random.uniform(-a, a), random.uniform(-a, a)
    if z > 1.001 or shx:
        cw, ch = WD / z, HT / z
        x0 = min(max(focus[0] - cw / 2 + shx, 0), WD - cw); y0 = min(max(focus[1] - ch / 2 + shy, 0), HT - ch)
        im = im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((WD, HT), Image.BILINEAR)
    im.paste(VIGNETTE, (0, 0), VIGNETTE)
    d = ImageDraw.Draw(im, "RGBA")

    # ---------------- UI layer (not zoomed)
    # written hook: big + centered 0-1.5s, then title at top; returns to center at the end (loop)
    if tt < 1.5: m = 0
    elif tt < 1.8: m = ease((tt - 1.5) / .3)
    elif tt < END_T: m = 1
    else: m = 1 - ease((tt - END_T) / .3)
    pop_in = .7 + .3 * ease_back(tt / .18) if tt < .18 else 1
    size = (150 + (80 - 150) * m) * (pop_in if m == 0 else 1)
    if tt >= END_T: size = 80 + (105 - 80) * (1 - m)  # end exactly where frame 0 starts
    cy = 360 + (210 - 360) * m
    col = (255, 222, 40) if m < .5 else (255, 255, 255)
    center_text(d, cy, HOOK_TXT, font(size), col, int(12 - 4 * m))
    if seg.get("label") is not None and tt - seg["win0"] < 1.5 and tt < END_T:
        lk = ease_back((tt - seg["win0"]) / .25)
        L = seg["label"]
        if lk < .98:
            L = L.resize((max(2, int(L.width * lk)), max(2, int(L.height * lk))))
        im.paste(L, (int((WD - L.width) / 2), int(415 - L.height / 2)), L)
    if BAIT and seg is segs[-1] and tt < END_T and tt - seg["win0"] > 1.6:
        center_text(d, 335, BAIT, font(56), (255, 255, 255), 6, maxw=760)
    # captions: 3-word chunks, current word yellow, keyword green
    ws = seg["words"]
    cur = next((n for n, (_, a, b2) in enumerate(ws) if a <= tt < b2), None)
    if cur is None: cur = len(ws) - 1 if tt >= ws[-1][1] else 0
    cs = (cur // 3) * 3
    chunk = ws[cs:cs + 3]
    f = font(104); line = " ".join(w for w, _, _ in chunk).upper()
    while d.textlength(line, font=f) > 1000 and f.size > 60: f = font(f.size - 8)
    x = (WD - d.textlength(line, font=f)) / 2; y = 1440
    ck = ease_back((tt - chunk[0][1]) / .12) if chunk else 1
    y += (1 - ck) * 30
    for n, (w, a, b2) in enumerate(chunk):
        clean = w.lower().strip(".,!?;:'\"")
        colr = (255, 222, 40) if cs + n == cur and a <= tt < b2 + .15 else ((120, 230, 120) if clean in KW else (255, 255, 255))
        d.text((x, y), w.upper(), font=f, fill=colr, stroke_width=10, stroke_fill=(15, 15, 15))
        x += d.textlength(w.upper() + " ", font=f)
    center_text(d, HT - 110, BRAND, font(38), (235, 235, 235, 170) if is_dark(seg["scene"]) else (40, 40, 40, 150), 0)
    # white flash on impact
    if SLAM_T <= tt < SLAM_T + .08:
        im = Image.blend(im, Image.new("RGB", (WD, HT), (255, 255, 255)), .55 * (1 - (tt - SLAM_T) / .08))
    return im

# ---------------------------------------------------------------- encode
voice_path = f"{WORK}/mix.wav"
mx = np.max(np.abs(audio)) or 1
sf.write(voice_path, (audio / mx * .9)[:int(TOTAL * SR)], SR)
proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{WD}x{HT}", "-r", str(FPS), "-i", "-",
                         "-i", voice_path, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                         "-c:a", "aac", "-b:a", "160k", "-af", "loudnorm=I=-14:TP=-1.5", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
for n in range(NF):
    proc.stdin.write(frame(n / FPS).convert("RGB").tobytes())
proc.stdin.close(); proc.wait()
print("done", round(TOTAL, 2), "s", NF, "frames", len(keys), "cuts")
