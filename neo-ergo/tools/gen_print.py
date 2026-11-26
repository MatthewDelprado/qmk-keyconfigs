"""Printable sheet of a Neo Ergo keymap: python3 gen_print.py KEYMAP.json OUT.html [current|master] [COMPARE.json]
KEYMAP.json is a VIA dump (qk-alice/tools/dump.cjs) or a target from build_master.py (VIA protocol 12 keycodes).
Key positions come from Neo Studio's VIA definition, with the layout options stored in KEYMAP.json.
With COMPARE.json, every key that differs from it gets an orange outline (what applying KEYMAP.json would change)."""
from datetime import datetime
import json, sys, html, math, os
SRC, OUT = sys.argv[1:3]
MODE = sys.argv[3] if len(sys.argv) > 3 else 'current'
CMP = json.load(open(sys.argv[4]))['keymap'] if len(sys.argv) > 4 else None
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(SRC)); km = d['keymap']
defn = json.load(open(os.path.join(HERE, '../backup/neo-ergo-wired-via-definition.json')))
kle, labels = defn['layouts']['keymap'], defn['layouts']['labels']

# --- layout options: VIA packs them with the last label in the lowest bits
bits = [max(1, math.ceil(math.log2(len(l) - 1))) if isinstance(l, list) else 1 for l in labels]
opts, v = {}, d.get('layoutOptions', 0)
for i in reversed(range(len(labels))):
    opts[i] = v & ((1 << bits[i]) - 1); v >>= bits[i]

# --- KLE -> key list (x, y, w, h, r, rx, ry, (row, col)) for the chosen options
keys, raw, cur = [], [], dict(x=0, y=0, r=0, rx=0, ry=0, w=1, h=1)
for row in kle:
    for it in row:
        if isinstance(it, dict):
            if 'r' in it: cur['r'] = it['r']
            if 'rx' in it: cur['rx'] = it['rx']; cur['x'] = it['rx']; cur['y'] = cur['ry']
            if 'ry' in it: cur['ry'] = it['ry']; cur['x'] = cur['rx']; cur['y'] = it['ry']
            cur['x'] += it.get('x', 0); cur['y'] += it.get('y', 0)
            cur['w'] = it.get('w', cur['w']); cur['h'] = it.get('h', cur['h'])
            continue
        parts = it.split('\n')
        opt = tuple(map(int, parts[3].split(','))) if len(parts) > 3 and parts[3] else None
        r, c = map(int, parts[0].split(','))
        raw.append((cur['x'], cur['y'], cur['w'], cur['h'], cur['r'], cur['rx'], cur['ry'], (r, c), opt))
        cur['x'] += cur['w']; cur['w'] = cur['h'] = 1
    cur['y'] += 1; cur['x'] = cur['rx']
# Like VIA, move the chosen option's keys onto option 0's spot (top-left corner of each group's keys).
def origin(g, v):
    ks = [k for k in raw if k[8] == (g, v)]; return min(k[0] for k in ks), min(k[1] for k in ks)
for k in raw:
    x, y, w, h, r, rx, ry, rc, opt = k
    if opt is None: keys.append(k[:8]); continue
    g, v = opt
    if opts.get(g) != v: continue
    (x0, y0), (x1, y1) = origin(g, 0), origin(g, v)
    keys.append((x + x0 - x1, y + y0 - y1, w, h, r, rx, ry, rc))

def corners(k):
    x, y, w, h, r, rx, ry, _ = k; a = math.radians(r)
    for px, py in ((x, y), (x + w, y), (x, y + h), (x + w, y + h)):
        dx, dy = px - rx, py - ry
        yield rx + dx * math.cos(a) - dy * math.sin(a), ry + dx * math.sin(a) + dy * math.cos(a)
pts = [p for k in keys for p in corners(k)]
X0, Y0 = min(p[0] for p in pts), min(p[1] for p in pts)
VW, VH = max(p[0] for p in pts) - X0, max(p[1] for p in pts) - Y0

# --- keycode -> label (QMK modern keycodes)
BASIC = {0x28:'Enter',0x29:'Esc',0x2a:'Bksp',0x2b:'Tab',0x2c:'Space',0x2d:'-',0x2e:'=',0x2f:'[',0x30:']',0x31:'\\',0x33:';',0x34:"'",0x35:'`',
 0x36:',',0x37:'.',0x38:'/',0x39:'Caps',0x46:'PrtSc',0x49:'Ins',0x4a:'Home',0x4b:'PgUp',0x4c:'Del',0x4d:'End',0x4e:'PgDn',0x4f:'→',0x50:'←',0x51:'↓',0x52:'↑',
 0x64:'ISO \\',0xa8:'Mute',0xa9:'Vol+',0xaa:'Vol−',0xab:'⏭',0xac:'⏮',0xae:'⏯',0xe0:'⌃',0xe1:'⇧',0xe2:'⌥',0xe3:'⌘',0xe4:'⌃',0xe5:'⇧',0xe6:'⌥',0xe7:'⌘'}
for i in range(26): BASIC[0x04 + i] = chr(65 + i)
for i in range(10): BASIC[0x1e + i] = '1234567890'[i]
for i in range(12): BASIC[0x3a + i] = f'F{i+1}'
SPECIAL = {0x7c00:'Boot', 0x7013:'NKRO', 0x7820:'RGB', 0x7821:'Effect +', 0x7822:'Effect −', 0x7823:'Hue +', 0x7824:'Hue −',
 0x7825:'Sat +', 0x7826:'Sat −', 0x7827:'Bri +', 0x7828:'Bri −', 0x7829:'Speed +', 0x782a:'Speed −'}
UNSH = {'1':'!','2':'@','3':'#','4':'$','5':'%','6':'^','7':'&','8':'*','9':'(','0':')','-':'_','=':'+','[':'{',']':'}','\\':'|',';':':',"'":'"','`':'~',',':'<','.':'>','/':'?'}
NAMES = {1:'Nav', 2:'Fn', 3:'Lighting'} if MODE == 'master' else {1:'L1', 2:'L2', 3:'L3'}
# The master has Nav on 1 and Fn on 2; the old keymap's Fn-like layer was 1, so compare across that swap.
CMP_LAYER = [0, 2, 1, 3] if MODE == 'master' else [0, 1, 2, 3]
def mods(m):
    if m & 0x0f == 0x0f: return 'Hyper'
    side = 'R' if m & 0x10 else ''
    return side + ''.join(s for b, s in ((1,'⌃'),(2,'⇧'),(4,'⌥'),(8,'⌘')) if m & b)
def label(v):
    """-> (main, hold text, kind, shifted corner legend)"""
    if v == 0: return ('', '', 'none', '')
    if v == 1: return ('', '', '', '')
    if v in SPECIAL: return (SPECIAL[v], '', 'act', '')
    if 0x7700 <= v < 0x7720: return (f'M{v - 0x7700}', 'macro', 'act', '')
    if v < 0x100:
        b = BASIC.get(v, f'0x{v:02x}')
        kind = 'mod' if b in '⌃⇧⌥⌘' else 'act' if len(b) > 1 or b in '←→↑↓⏭⏮⏯' else 'key'
        return (b, '', kind, UNSH.get(b, ''))
    if v < 0x2000:
        m, b = v >> 8, BASIC.get(v & 0xff, '?')
        if m == 2 and b in UNSH: return (UNSH[b], '', 'key', '')
        return (mods(m) + b, '', 'act', '')
    if v < 0x4000:
        b = BASIC.get(v & 0xff, '?'); return (b, 'hold ' + mods((v >> 8) & 0x1f), 'key', UNSH.get(b, ''))
    if v < 0x5000:
        b = BASIC.get(v & 0xff, '?'); return (b, 'hold ' + NAMES.get((v >> 8) & 0xf, '?'), 'key', '')
    if 0x5220 <= v < 0x5240: return (NAMES.get(v & 0x1f, '?'), 'hold', 'mod', '')
    return (f'0x{v:04x}', '', 'act', '')

FILL = {'mod': '#ececec', 'act': '#e3edf9', 'held': '#222', 'none': '#f6f6f6', 'key': '#fff', '': '#fff'}
STROKE = {'act': '#8fb0d8', 'held': '#222', 'none': '#ddd', '': '#ccc'}
def board(lid, title, how, held):
    out, n = [], 0
    for k in keys:
        x, y, w, h, r, rx, ry, (row, col) = k
        m, s, t, sh = label(km[lid][row][col])
        changed = CMP is not None and CMP[CMP_LAYER[lid]][row][col] != km[lid][row][col]
        if (row, col) in held: m, s, t, sh = held[(row, col)], 'held', 'held', ''
        n += changed
        dash = ' stroke-dasharray="3 2"' if t == '' else ''
        fg = '#fff' if t == 'held' else '#111'
        cx, cy = x + w / 2, y + h / 2
        fs = 0.24 if len(m) > 5 else 0.3 if len(m) > 3 else 0.36
        g = [f'<rect x="{x+.04:.3f}" y="{y+.04:.3f}" width="{w-.08:.3f}" height="{h-.08:.3f}" rx=".1" fill="{FILL.get(t, "#fff")}" stroke="{STROKE.get(t, "#999")}" stroke-width=".025"{dash}/>']
        if changed:
            g.append(f'<rect x="{x+.06:.3f}" y="{y+.06:.3f}" width="{w-.12:.3f}" height="{h-.12:.3f}" rx=".09" fill="none" stroke="#e8590c" stroke-width=".07"/>')
        if m:
            g.append(f'<text x="{cx:.3f}" y="{cy + (0 if s else .1):.3f}" font-size="{fs}" font-weight="600" fill="{fg}" text-anchor="middle">{html.escape(m)}</text>')
        if s:
            g.append(f'<text x="{cx:.3f}" y="{cy + .3:.3f}" font-size=".18" fill="{"#ccc" if t == "held" else "#555"}" text-anchor="middle">{html.escape(s)}</text>')
        if sh:
            g.append(f'<text x="{x + .14:.3f}" y="{y + .3:.3f}" font-size=".2" fill="#666">{html.escape(sh)}</text>')
        rot = f' transform="rotate({r} {rx} {ry})"' if r else ''
        out.append(f'<g{rot}>{"".join(g)}</g>')
    svg = f'<svg viewBox="{X0-.05:.3f} {Y0-.05:.3f} {VW+.1:.3f} {VH+.1:.3f}" font-family="-apple-system,Helvetica Neue,sans-serif">{"".join(out)}</svg>'
    ch = f' · <span class=chg>{n} change{"s" if n != 1 else ""}</span>' if CMP is not None else ''
    return f'<section><h3>{title}<small>{how}{ch}</small></h3>{svg}</section>'

if MODE == 'master':
    head = 'Neo Ergo · master keymap'
    body = (board(0, 'Base', 'always on', {})
            + board(2, 'Fn', 'hold Fn (right of Right Shift, or either Fn on the left column), or hold both Space halves', {(3, 14): 'Fn'})
            + board(1, 'Nav', 'hold either Space', {(4, 6): 'Space'})
            + board(3, 'Lighting', 'hold Fn, then either Space', {(3, 14): 'Fn', (4, 6): 'Space'}))
    notes = '''<b>Small text</b> is the hold action; the corner legend is what Shift + that key types. Dashed keys pass through to Base.
<b>Orange outline</b> = changes from what's on the board now. Same as the master: home row mods (A ⇧, S ⌃, D ⌥, F ⌘ / J ⌘, K ⌥, L ⌃, ; ⇧), Hyper on Esc, Enter, G and H,
symbols on Fn with mirrored brackets, HHKB arrows on Fn, media on Fn's top row and right edge, numpad on Nav. Both Space halves hold Nav; with one held, the other is Backspace on a tap and Fn on a hold (Fn is the higher layer, so it wins over Nav).
Neo Ergo extras, kept as they are now: the left column (Vol +, Vol −, ⏯ that holds Fn, Fn), ⌃ bottom-left, the right-hand B, and ← (hold ⌥) and → (hold ⌃) bottom-right.
Lighting drives the underglow (rgblight) with the same key spots as the master, plus NKRO on G. VIA can't set Flow Tap, so the home row mods run on this firmware's tapping term.'''
else:
    head = 'Neo Ergo · current keymap'
    body = ''.join(board(l, ['Base', 'Layer 1', 'Layer 2', 'Layer 3'][l], '', {}) for l in range(4))
    notes = 'As read off the board, before the master.'

open(OUT, 'w').write(f'''<!doctype html><meta charset=utf-8><title>Neo Ergo keymap</title><style>
@page{{size:letter landscape;margin:.4in}}*{{box-sizing:border-box}}body{{font:11px -apple-system,"Helvetica Neue",sans-serif;color:#111;margin:0;background:#fff}}
header{{display:flex;justify-content:space-between;align-items:baseline;border-bottom:1.5px solid #111;padding-bottom:4px;margin-bottom:10px}}header h1{{font-size:17px;margin:0}}header p{{margin:0;color:#555}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px 22px}}h3{{font-size:13px;margin:0 0 4px}}h3 small{{font-weight:400;color:#666;margin-left:8px;font-size:10.5px}}.chg{{color:#e8590c;font-weight:600}}
svg{{width:100%;display:block}}footer{{margin-top:10px;color:#444;font-size:10px;line-height:1.45}}footer b{{color:#111}}
.legend{{display:flex;gap:12px;margin-top:6px}}.legend span{{display:inline-flex;align-items:center;gap:4px}}.legend i{{display:inline-block;width:14px;height:10px;border:1px solid #999;border-radius:2px}}
</style><header><h1>{head}</h1><p>{"read off the board " + datetime.fromisoformat(d["savedAt"].replace("Z", "+00:00")).astimezone().strftime("%Y-%m-%d") if "savedAt" in d else "target, not yet on the board"}</p></header>
<div class="grid">{body}</div><footer>{notes}
<div class="legend"><span><i style="background:#ececec"></i>modifier / layer</span><span><i style="background:#e3edf9;border-color:#8fb0d8"></i>action</span><span><i style="background:#222;border-color:#222"></i>held to reach this layer</span><span><i style="border-style:dashed"></i>pass-through</span><span><i style="border:2px solid #e8590c"></i>changes</span></div>
</footer>''')
print('wrote', OUT)
