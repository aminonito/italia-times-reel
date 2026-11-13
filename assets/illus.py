# Stile "ILLUSTRATO": illustrazione piatta su fondo crema, contorni blu notte,
# numeri chiave rossi dentro cornici, barre, linee del tempo, icone e omini piatti.
# Sottotitoli blu notte sotto l'illustrazione, parola attiva in rosso.
# Asset opzionale: /home/claude/mapassets/italia_map.json (sagoma Italia, ISTAT CC BY).
import json, math, random, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from dark import font, ease, ease_io, PB, PS

W, H, FPS = 1080, 1920, 30
CREAM = (243, 237, 227); PAPER = (252, 249, 243)
NAVY = (27, 42, 74); RED = (214, 58, 52); BLUE = (86, 132, 196); LBLUE = (190, 210, 234)
GREY = (150, 146, 140); GOLD = (232, 178, 62); GREEN = (58, 150, 100); SKIN = (240, 200, 165)
OUT = 6   # spessore contorno

_BG = None
def bg():
    global _BG
    if _BG is None:
        rng = np.random.default_rng(7)
        a = np.zeros((H, W, 3), np.float32) + np.array(CREAM, np.float32)
        a += rng.normal(0, 2.2, (H, W, 1))
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * 0.42) / H) ** 2)
        a -= (np.clip(r - 0.35, 0, 1) * 30)[..., None]
        _BG = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    return _BG

def _pop(age, d=0.3):
    if age < 0: return 0.0
    u = min(1.0, age / d)
    return (0.6 + 0.4 * ease(u)) + 0.12 * math.sin(math.pi * u) if u < 1 else 1.0

def rich(d, xy, text, size, base=NAVY, accent=RED, fnt=PB, alpha=255, anchor="mm"):
    """testo centrato con *parole* in rosso; righe separate da \\n"""
    f = font(fnt, size); x0, y0 = xy; lh = int(size * 1.12)
    lines = text.split("\n"); y = y0 - lh * (len(lines) - 1) / 2
    for line in lines:
        parts = [p for p in re.split(r"(\*[^*]+\*)", line) if p]
        tw = sum(d.textlength(p.strip("*"), font=f) for p in parts)
        x = x0 - tw / 2
        for p in parts:
            c = accent if p.startswith("*") else base
            d.text((x, y), p.strip("*"), font=f, fill=c + (alpha,), anchor="lm")
            x += d.textlength(p.strip("*"), font=f)
        y += lh

# ---------------- icone piatte (disegnate a 2x e ridotte) ----------------
_ic = {}
def icon_img(kind, size, color=None, mood="neutral"):
    key = (kind, size, color, mood)
    if key in _ic: return _ic[key]
    S = size * 2; im = Image.new("RGBA", (S, int(S * 1.2)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    o = max(2, int(S * 0.035)); N = NAVY + (255,)
    def P(*c): return [v * S for v in c]
    if kind == "coins":
        for j in range(5):
            y = S * (0.88 - j * 0.12)
            d.ellipse([S * .16, y - S * .09, S * .84, y + S * .09], fill=GOLD + (255,), outline=N, width=o)
        d.text((S * .5, S * .40), "€", font=font(PB, int(S * .16)), fill=NAVY + (255,), anchor="mm")
    elif kind == "bank":
        d.polygon([(S*.08, S*.36), (S*.5, S*.08), (S*.92, S*.36)], fill=PAPER + (255,), outline=N, width=o)
        d.rectangle(P(.12, .36, .88, .44), fill=PAPER + (255,), outline=N, width=o)
        for x in (.18, .38, .58, .78):
            d.rectangle(P(x, .46, x + .06, .80), fill=PAPER + (255,), outline=N, width=o)
        d.rectangle(P(.08, .82, .92, .92), fill=(color or BLUE) + (255,), outline=N, width=o)
        d.text((S * .5, S * .27), "€", font=font(PB, int(S * .14)), fill=N, anchor="mm")
    elif kind == "clock":
        d.ellipse(P(.08, .08, .92, .92), fill=PAPER + (255,), outline=N, width=int(o * 1.6))
        for h in range(12):
            a = h * math.pi / 6; r1, r2 = .34, .38
            d.line([(S*(.5+r1*math.sin(a)), S*(.5-r1*math.cos(a))), (S*(.5+r2*math.sin(a)), S*(.5-r2*math.cos(a)))], fill=N, width=o)
        d.line([(S*.5, S*.5), (S*.5, S*.22)], fill=N, width=int(o*1.3)); d.line([(S*.5, S*.5), (S*.70, S*.58)], fill=(color or RED) + (255,), width=int(o*1.3))
        d.ellipse(P(.46, .46, .54, .54), fill=N)
    elif kind == "bills":
        for j, (dx, dy, r) in enumerate([(0, .1, 0), (.04, .0, 0)]):
            d.rounded_rectangle(P(.06 + dx, .30 + dy, .90 + dx, .70 + dy), int(S * .04), fill=(150, 196, 150, 255), outline=N, width=o)
            d.ellipse(P(.38 + dx, .40 + dy, .58 + dx, .60 + dy), outline=N, width=o)
        d.text((S * .52, S * .50), "€", font=font(PB, int(S * .14)), fill=N, anchor="mm")
    elif kind in ("up", "down"):
        c = (color or RED) + (255,)
        if kind == "down": pts = [(.36, .06), (.64, .06), (.64, .56), (.84, .56), (.5, .94), (.16, .56), (.36, .56)]
        else: pts = [(.36, .94), (.64, .94), (.64, .44), (.84, .44), (.5, .06), (.16, .44), (.36, .44)]
        d.polygon([(x * S, y * S) for x, y in pts], fill=c, outline=N, width=o)
    elif kind == "doc":
        for j in range(3):
            dx = j * .05
            d.rectangle(P(.18 + dx, .08 + dx, .78 + dx, .88 + dx), fill=PAPER + (255,), outline=N, width=o)
        for k in range(5):
            y = .30 + k * .1
            d.line([(S*.30, S*y + S*.10), (S*.80, S*y + S*.10)], fill=GREY + (255,), width=o)
    elif kind == "flag":
        d.line([(S*.14, S*.06), (S*.14, S*.96)], fill=N, width=int(o*1.3))
        for k, c in enumerate([(0, 146, 70), PAPER, (206, 43, 55)]):
            d.rectangle(P(.16 + k * .24, .10, .40 + k * .24, .52), fill=c + (255,))
        d.rectangle(P(.16, .10, .88, .52), outline=N, width=o)
    elif kind == "person":   # omino piatto, abito blu notte; mood: neutral / sad / happy
        body = (color or NAVY) + (255,)
        d.rounded_rectangle(P(.18, .62, .82, 1.18), int(S * .16), fill=body, outline=N, width=o)
        d.polygon([(S*.43, S*.62), (S*.57, S*.62), (S*.5, S*.80)], fill=PAPER + (255,))
        d.polygon([(S*.47, S*.66), (S*.53, S*.66), (S*.5, S*.84)], fill=RED + (255,))
        d.ellipse(P(.26, .12, .74, .60), fill=SKIN + (255,), outline=N, width=o)
        d.chord(P(.24, .08, .76, .44), 180, 360, fill=(70, 52, 40, 255))
        for ex in (.41, .59): d.ellipse(P(ex - .025, .34, ex + .025, .39), fill=N)
        if mood == "sad": d.arc(P(.40, .45, .60, .56), 200, 340, fill=N, width=o)
        elif mood == "happy": d.arc(P(.40, .40, .60, .50), 20, 160, fill=N, width=o)
        else: d.line([(S*.43, S*.48), (S*.57, S*.48)], fill=N, width=o)
    im = im.resize((size, int(size * 1.2)), Image.LANCZOS); _ic[key] = im
    return im

# ---------------- sagoma Italia ----------------
_IT = {}
def italy_img(width, fill=LBLUE, hl=None, hlcol=RED):
    key = (width, fill, hl, hlcol)
    if key in _IT: return _IT[key]
    M = json.load(open("/home/claude/mapassets/italia_map.json"))
    cos = math.cos(math.radians(42)); lon0, lon1, lat0, lat1 = 6.5, 18.6, 36.6, 47.1
    sc = width * 2 / ((lon1 - lon0) * cos); hgt = int((lat1 - lat0) * sc)
    im = Image.new("RGBA", (width * 2, hgt), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    def polys(g): return [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
    for pass_ in (0, 1):
        for name, g in M["regions"].items():
            for p in polys(g):
                pts = [((x - lon0) * cos * sc, (lat1 - y) * sc) for x, y in p[0]]
                if len(pts) < 3: continue
                if pass_ == 0: d.polygon([(x + 10, y + 12) for x, y in pts], fill=NAVY + (255,))
                else:
                    c = hlcol if hl and any(name.startswith(h) for h in hl) else fill
                    d.polygon(pts, fill=c + (255,), outline=NAVY + (255,), width=4)
    im = im.resize((width, hgt // 2), Image.LANCZOS); _IT[key] = im
    return im

# ---------------- scena ----------------
class Scene:
    def __init__(self, dur):
        self.dur = dur; self.items = []; self.sfx = []; self.footer = ""
    def _add(self, sfx=None, **kw):
        kw.setdefault("t1", None); self.items.append(kw)
        if sfx: self.sfx.append((kw["t0"], sfx))
    def card(self, big, xy, t0, t1=None, sub="", w=760, h=None, size=150, count=None, color=RED, sfx="pop"):
        """cornice con numero grande rosso; count=(da, a, formato) per contatore animato"""
        self._add(k="card", big=big, sub=sub, xy=xy, t0=t0, t1=t1, w=w, h=h or (size * 1.25 + (70 if sub else 0) + 50),
                  size=size, count=count, color=color, sfx=sfx)
    def title(self, text, xy, t0, t1=None, size=64):
        """testo blu notte con *parole* rosse"""
        self._add(k="title", text=text, xy=xy, t0=t0, t1=t1, size=size, sfx="soft")
    def icon(self, kind, xy, t0, t1=None, size=160, color=None, mood="neutral", bob=True, sfx="pop"):
        self._add(k="icon", kind=kind, xy=xy, t0=t0, t1=t1, size=size, color=color, mood=mood, bob=bob, sfx=sfx)
    def people(self, n, xy, t0, t1=None, size=110, mood="neutral", step=0.08, hl=0, hlcol=RED):
        self._add(k="people", n=n, xy=xy, t0=t0, t1=t1, size=size, mood=mood, step=step, hl=hl, hlcol=hlcol, sfx="pop")
    def italy(self, xy, t0, t1=None, width=620, hl=None):
        self._add(k="italy", xy=xy, t0=t0, t1=t1, width=width, hl=tuple(hl) if hl else None, sfx="whoosh_soft")
    def bars(self, data, box, t0, t1=None, vmax=None, ref=None, step=0.25, unit=""):
        """data=[(etichetta, valore, colore, testo_valore)], box=(x0,y0,x1,y1); ref=(valore, testo) linea tratteggiata"""
        self._add(k="bars", data=data, box=box, t0=t0, t1=t1, vmax=vmax or max(v for _, v, _, _ in data) * 1.12,
                  ref=ref, step=step, sfx="whoosh_soft")
        for j in range(len(data)): self.sfx.append((t0 + j * step + 0.5, "pop"))
    def timeline(self, nodes, y, t0, t1=None, step=0.6, x0=170, x1=910):
        """nodes=[(sopra, sotto, colore, tempo_opz)]"""
        self._add(k="timeline", nodes=nodes, y=y, t0=t0, t1=t1, step=step, x0=x0, x1=x1)
        for j, n in enumerate(nodes): self.sfx.append(((n[3] if len(n) > 3 else t0 + j * step), "pop"))
    def stamp(self, text, xy, t0, t1=None, size=54, color=RED, rot=-8):
        self._add(k="stamp", text=text, xy=xy, t0=t0, t1=t1, size=size, color=color, rot=rot, sfx="ding")
    def cta(self, t0, text="Salvalo."):
        self._add(k="cta", text=text, t0=t0, sfx="ding")

def _alpha(it, t, fade=0.22):
    if t < it["t0"]: return 0.0
    a = ease((t - it["t0"]) / fade)
    if it.get("t1") is not None and t > it["t1"]: a *= max(0.0, 1 - (t - it["t1"]) / 0.22)
    return a

def _fadeimg(im, a):
    if a >= 0.99: return im
    im = im.copy(); im.putalpha(im.getchannel("A").point(lambda q: int(q * a))); return im

def _paste(lay, im, cx, cy, s=1.0, a=1.0):
    if s != 1.0: im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)
    lay.alpha_composite(_fadeimg(im, a), (int(cx - im.width / 2), int(cy - im.height / 2)))

def _card_img(it, t):
    w, h = int(it["w"]), int(it["h"])
    im = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([12, 14, w + 12, h + 14], 34, fill=NAVY + (255,))
    d.rounded_rectangle([0, 0, w, h], 34, fill=PAPER + (255,), outline=NAVY + (255,), width=OUT)
    big = it["big"]
    if it["count"]:
        a, b, fmt = it["count"]; u = ease((t - it["t0"]) / 1.1)
        big = fmt(a + (b - a) * u)
    f = font(PB, it["size"])
    while d.textlength(big, font=f) > w - 60 and f.size > 40: f = font(PB, f.size - 6)
    cy = h / 2 - (32 if it["sub"] else 0)
    d.text((w / 2, cy), big, font=f, fill=it["color"] + (255,), anchor="mm")
    if it["sub"]: rich(d, (w / 2, h - 58), it["sub"], 40, fnt=PB)
    return im

def render(sc, t):
    img = bg().copy(); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for it in sc.items:
        a = _alpha(it, t)
        if a <= 0.01: continue
        k = it["k"]; age = t - it["t0"]; al = int(255 * a)
        if k == "card":
            _paste(lay, _card_img(it, t), *it["xy"], s=_pop(age), a=a)
        elif k == "title":
            tl = Image.new("RGBA", (W, 400), (0, 0, 0, 0)); rich(ImageDraw.Draw(tl), (W / 2, 200), it["text"], it["size"])
            _paste(lay, tl, it["xy"][0], it["xy"][1] + 30 * (1 - ease(age / 0.3)), a=a)
        elif k == "icon":
            im = icon_img(it["kind"], it["size"], it["color"], it["mood"])
            bob = 6 * math.sin(2 * math.pi * (t * 0.7 + it["xy"][0] * 0.003)) if it["bob"] else 0
            _paste(lay, im, it["xy"][0], it["xy"][1] + bob, s=_pop(age), a=a)
        elif k == "people":
            n, sz = it["n"], it["size"]; gap = sz * 1.02; x0 = it["xy"][0] - gap * (n - 1) / 2
            for j in range(n):
                tj = it["t0"] + j * it["step"]
                if t < tj: continue
                col = it["hlcol"] if j < it["hl"] else None
                im = icon_img("person", sz, col, it["mood"])
                _paste(lay, im, x0 + j * gap, it["xy"][1], s=_pop(t - tj, 0.25), a=a)
        elif k == "italy":
            im = italy_img(it["width"], hl=it["hl"])
            _paste(lay, im, it["xy"][0], it["xy"][1] + 40 * (1 - ease(age / 0.5)), a=a)
        elif k == "bars":
            x0, y0, x1, y1 = it["box"]; n = len(it["data"]); bw = (x1 - x0) / n
            d.line([(x0 - 10, y1), (x1 + 10, y1)], fill=NAVY + (al,), width=OUT)
            if it["ref"]:
                rv, rt = it["ref"]; ry = y1 - (y1 - y0) * rv / it["vmax"]; ra = int(al * ease((age - 0.3) / 0.4))
                for xx in range(int(x0 - 10), int(x1 + 10), 34): d.line([(xx, ry), (min(xx + 18, x1 + 10), ry)], fill=RED + (ra,), width=5)
                d.text((x1 + 10, ry - 14), rt, font=font(PB, 34), fill=RED + (ra,), anchor="rb")
            for j, (lab, v, col, vt) in enumerate(it["data"]):
                u = ease_io((t - it["t0"] - j * it["step"]) / 0.7)
                if u <= 0: continue
                cx = x0 + bw * (j + 0.5); hh = (y1 - y0) * v / it["vmax"] * u; ww = bw * 0.56
                if hh > 14: d.rectangle([cx - ww / 2 + 8, y1 - hh + 10, cx + ww / 2 + 8, y1], fill=NAVY + (al,))
                if hh > 2: d.rectangle([cx - ww / 2, y1 - hh, cx + ww / 2, y1], fill=col + (al,), outline=NAVY + (al,), width=min(OUT, int(hh / 2)))
                d.text((cx, y1 + 46), lab, font=font(PB, 40), fill=NAVY + (al,), anchor="mm")
                if u > 0.85: d.text((cx, y1 - hh - 44), vt, font=font(PB, 52), fill=col + (al,), anchor="mm")
        elif k == "timeline":
            nodes = it["nodes"]; n = len(nodes); y = it["y"]
            xs = [it["x0"] + (it["x1"] - it["x0"]) * j / max(1, n - 1) for j in range(n)]
            ts = [nd[3] if len(nd) > 3 else it["t0"] + j * it["step"] for j, nd in enumerate(nodes)]
            for j in range(n - 1):
                u = ease_io((t - ts[j]) / max(0.2, ts[j + 1] - ts[j]))
                if u > 0: d.line([(xs[j], y), (xs[j] + (xs[j + 1] - xs[j]) * u, y)], fill=NAVY + (al,), width=OUT + 2)
            for j, nd in enumerate(nodes):
                if t < ts[j]: continue
                s = _pop(t - ts[j]); r = 56 * s; col = nd[2]
                d.ellipse([xs[j] - r + 6, y - r + 8, xs[j] + r + 6, y + r + 8], fill=NAVY + (al,))
                d.ellipse([xs[j] - r, y - r, xs[j] + r, y + r], fill=col + (al,), outline=NAVY + (al,), width=OUT)
                rich(d, (xs[j], y - 112), nd[0], 46, base=NAVY, alpha=al)
                d.text((xs[j], y + 104), nd[1], font=font(PB, 38), fill=NAVY + (al,), anchor="mm")
        elif k == "stamp":
            f = font(PB, it["size"]); tw = int(d.textlength(it["text"], font=f))
            st = Image.new("RGBA", (tw + 80, int(it["size"] * 1.9)), (0, 0, 0, 0)); ds = ImageDraw.Draw(st)
            ds.rounded_rectangle([6, 6, st.width - 6, st.height - 6], 18, outline=it["color"] + (255,), width=8)
            ds.text((st.width / 2, st.height / 2), it["text"], font=f, fill=it["color"] + (255,), anchor="mm")
            st = st.rotate(it["rot"], expand=True, resample=Image.BICUBIC)
            _paste(lay, st, *it["xy"], s=1.0 + 0.6 * (1 - ease(age / 0.22)), a=a)
        elif k == "cta":
            d.rectangle([0, 0, W, H], fill=CREAM + (int(235 * a),))
            d.text((W / 2, 800), it["text"], font=font(PB, 130), fill=RED + (al,), anchor="mm")
            d.text((W / 2, 920), "Seguici: ogni giorno i tuoi soldi, spiegati.", font=font(PS, 40), fill=NAVY + (al,), anchor="mm")
    img.alpha_composite(lay)
    return img
