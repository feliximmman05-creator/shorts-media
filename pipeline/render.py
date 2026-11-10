import json, sys, math, random, subprocess, wave
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W_DIR = sys.argv[1]
OUT = sys.argv[2]
FPS, WD, HT, GAP = 30, 1080, 1920, 0.25
segs = json.load(open(f"{W_DIR}/script.json"))
import os
HERE = os.path.dirname(os.path.abspath(__file__))
FONT = f"{HERE}/fonts/Anton.ttf"
BRAND = os.environ.get("BRAND", "INTO THE DARK WEB")
f_rank = ImageFont.truetype(FONT, 260)
f_title = ImageFont.truetype(FONT, 92)
f_cap = ImageFont.truetype(FONT, 104)
f_small = ImageFont.truetype(FONT, 40)

PALETTE = [(255, 70, 90), (90, 200, 255), (140, 255, 140), (255, 180, 60), (210, 130, 255), (255, 220, 40), (255, 70, 90)]

def dur(path):
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()

# timeline
t = 0.0
for s in segs:
    s["start"] = t
    s["len"] = dur(f"{W_DIR}/{s['id']}.wav")
    t += s["len"] + GAP
    s["emo"] = [Image.open(f"{W_DIR}/emoji/{e}.png").convert("RGBA") for e in s["emoji"]]
    words = s["text"].split()
    total = sum(len(w) + 2 for w in words)
    acc, timed = 0.0, []
    for w in words:
        a = acc / total * s["len"]
        acc += len(w) + 2
        timed.append((w, a, acc / total * s["len"]))
    s["words"] = timed
TOTAL = t

# background: dark radial gradient + particles
bg = Image.new("RGB", (WD, HT))
px = bg.load()
for y in range(0, HT, 4):
    for x in range(0, WD, 4):
        d = math.hypot((x - WD / 2) / WD, (y - HT / 2) / HT)
        v = max(0, int(38 - d * 50))
        for dy in range(4):
            for dx in range(4):
                px[x + dx, y + dy] = (v // 2, v // 3, v)
random.seed(7)
parts = [(random.uniform(0, WD), random.uniform(0, HT), random.uniform(1.5, 4), random.uniform(10, 40)) for _ in range(70)]

def ease_out_back(x):
    c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def center_text(d, y, text, font, fill, stroke=8):
    w = d.textlength(text, font=font)
    d.text(((WD - w) / 2, y), text, font=font, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))

def wrap(d, text, font, maxw):
    lines, cur = [], ""
    for w in text.split():
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=font) <= maxw: cur = trial
        else: lines.append(cur); cur = w
    lines.append(cur)
    return lines

GLOW = {}

def frame(tt):
    seg = segs[-1]
    for s in segs:
        if s["start"] <= tt < s["start"] + s["len"] + GAP: seg = s; break
    lt = tt - seg["start"]
    acc = PALETTE[segs.index(seg) % len(PALETTE)]
    im = bg.copy()
    d = ImageDraw.Draw(im, "RGBA")
    for (x, y, r, sp) in parts:
        yy = (y - tt * sp) % HT
        d.ellipse([x - r, yy - r, x + r, yy + r], fill=acc + (70,))
    # glow ring
    if acc not in GLOW:
        g = Image.new("RGBA", (WD, HT), (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse([WD / 2 - 380, 1000 - 380, WD / 2 + 380, 1000 + 380], fill=acc + (60,))
        GLOW[acc] = g.filter(ImageFilter.GaussianBlur(90))
    im.paste(GLOW[acc], (0, 0), GLOW[acc])
    d = ImageDraw.Draw(im, "RGBA")
    # rank number pop
    p = min(1, lt / 0.45)
    sc = max(0.01, ease_out_back(p))
    top = 210
    if seg["rank"]:
        fr = ImageFont.truetype(FONT, max(10, int(260 * sc)))
        center_text(d, top + (260 - 260 * sc) / 2, seg["rank"], fr, acc, 10)
        ty = top + 330
    else:
        ty = top + 40
    for i, line in enumerate(wrap(d, seg["title"], f_title, 960)):
        center_text(d, ty + i * 105, line, f_title, (255, 255, 255), 7)
    # emojis
    n = len(seg["emo"])
    for i, e in enumerate(seg["emo"]):
        ep = min(1, max(0, (lt - 0.15 - i * 0.2) / 0.5))
        es = ease_out_back(ep) if ep > 0 else 0
        if es <= 0.02: continue
        size = int((420 if n == 1 else 360) * es)
        bob = math.sin(tt * 3 + i * 1.7) * 18
        rot = math.sin(tt * 2 + i) * 8
        img = e.resize((size, size)).rotate(rot, resample=Image.BICUBIC)
        cx = WD / 2 + (0 if n == 1 else (-200 if i == 0 else 200))
        cy = 1000 + bob + (0 if n == 1 else (-40 if i == 0 else 60))
        im.paste(img, (int(cx - img.width / 2), int(cy - img.height / 2)), img)
    # captions: show 3-word chunk, highlight current word
    words = seg["words"]
    cur = max(0, min(len(words) - 1, next((i for i, (_, a, b) in enumerate(words) if a <= lt < b), len(words) - 1)))
    cs = (cur // 3) * 3
    chunk = words[cs:cs + 3]
    d = ImageDraw.Draw(im, "RGBA")
    texts = [w for w, _, _ in chunk]
    lines = wrap(d, " ".join(texts).upper(), f_cap, 980)
    y = 1440
    idx = 0
    for line in lines:
        lw = d.textlength(line, font=f_cap)
        x = (WD - lw) / 2
        for w in line.split():
            col = (255, 230, 40) if cs + idx == cur and lt < seg["len"] else (255, 255, 255)
            d.text((x, y), w, font=f_cap, fill=col, stroke_width=9, stroke_fill=(0, 0, 0))
            x += d.textlength(w + " ", font=f_cap)
            idx += 1
        y += 125
    # progress bar + watermark
    d.rectangle([0, HT - 14, WD * tt / TOTAL, HT], fill=acc + (255,))
    center_text(d, HT - 120, BRAND, f_small, (255, 255, 255, 140), 3)
    return im

# audio concat with gaps
lst = f"{W_DIR}/audio_list.txt"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"anullsrc=r=24000:cl=mono", "-t", str(GAP), f"{W_DIR}/gap.wav"], check=True)
with open(lst, "w") as f:
    for s in segs:
        f.write(f"file '{W_DIR}/{s['id']}.wav'\nfile '{W_DIR}/gap.wav'\n")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c:a", "pcm_s16le", f"{W_DIR}/voice.wav"], check=True)

proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{WD}x{HT}", "-r", str(FPS), "-i", "-",
                         "-i", f"{W_DIR}/voice.wav", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
                         "-c:a", "aac", "-b:a", "160k", "-af", "loudnorm=I=-14:TP=-1.5", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
nf = int(TOTAL * FPS)
for i in range(nf):
    proc.stdin.write(frame(i / FPS).tobytes())
proc.stdin.close(); proc.wait()
print("done", round(TOTAL, 2), "s", nf, "frames")
