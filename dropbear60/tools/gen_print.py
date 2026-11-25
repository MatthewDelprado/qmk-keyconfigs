"""Printable sheet of the Dropbear's live VIA keymap: python3 gen_print.py DUMP.json OUT.html
DUMP.json comes from qk-alice/tools/dump.cjs (VIA protocol 12 keycodes). Bottom row is drawn as
the Hot Rod / Pink Slip HHKB case shows it."""
import json, sys, html
DUMP, OUT = sys.argv[1:3]
QMK = '/Users/matthewdelprado/Documents/git/GMK/keyboards/kkatano/bakeneko60/keyboard.json'
d = json.load(open(DUMP)); km = d['keymap']
geo = json.load(open(QMK))['layouts']['LAYOUT_60_ansi_split_bs_rshift']['layout']
keys = [(k['x'], k['y'], k.get('w', 1), tuple(k['matrix'])) for k in geo if k['matrix'][0] < 4]
# HHKB bottom row: blocker 1.5, ⌥ 1, ⌘ 1.5, Space 7, ⌘ 1.5, ⌃ 1, blocker 1.5
keys += [(1.5, 4, 1, (4, 1)), (2.5, 4, 1.5, (4, 2)), (4, 4, 7, (4, 6)), (11, 4, 1.5, (4, 11)), (12.5, 4, 1, (4, 12))]
BASIC = {0x28:'Enter',0x29:'Esc',0x2a:'Bksp',0x2b:'Tab',0x2c:'Space',0x2d:'-',0x2e:'=',0x2f:'[',0x30:']',0x31:'\\',0x33:';',0x34:"'",0x35:'`',
 0x36:',',0x37:'.',0x38:'/',0x49:'Ins',0x4a:'Home',0x4b:'PgUp',0x4c:'Del',0x4d:'End',0x4e:'PgDn',0x4f:'→',0x50:'←',0x51:'↓',0x52:'↑',
 0xa8:'Mute',0xa9:'Vol+',0xaa:'Vol−',0xab:'⏭',0xac:'⏮',0xae:'⏯',0xe0:'⌃',0xe1:'⇧',0xe2:'⌥',0xe3:'⌘',0xe4:'⌃',0xe5:'⇧',0xe6:'⌥',0xe7:'⌘'}
for i in range(26): BASIC[0x04+i] = chr(65+i)
for i in range(10): BASIC[0x1e+i] = '1234567890'[i]
for i in range(12): BASIC[0x3a+i] = f'F{i+1}'
UNSH = {'1':'!','2':'@','3':'#','4':'$','5':'%','6':'^','7':'&','8':'*','9':'(','0':')','-':'_','=':'+','[':'{',']':'}','\\':'|',';':':',"'":'"','`':'~',',':'<','.':'>','/':'?'}
NAMES = {1:'Fn', 2:'Nav', 3:'Spare'}
def mods(m):
    if m & 0x0f == 0x0f: return 'Hyper'
    return ''.join(s for b, s in ((1,'⌃'),(2,'⇧'),(4,'⌥'),(8,'⌘')) if m & b)
def label(v):
    """-> (main, hold-text, kind, shifted corner legend)"""
    if v == 0: return ('', '', 'none', '')
    if v == 1: return ('', '', '', '')
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
W, H = 15, 5
def board(lid, title, how, held):
    out = []
    for x, y, w, (r, c) in keys:
        m, s, t, sh = label(km[lid][r][c])
        if (r, c) in held: m, s, t, sh = held[(r, c)], 'held', 'held', ''
        cls = t + (' empty' if not m and t not in ('none',) else '')
        em = f'<em>{html.escape(sh)}</em>' if sh else ''
        sm = ' class=sm' if len(m) > 4 else ''
        out.append(f'<div class="k {cls}" style="left:{x/W*100:.3f}%;top:{y/H*100:.3f}%;width:{w/W*100:.3f}%;height:{100/H:.3f}%"><span>{em}<b{sm}>{html.escape(m)}</b><i>{html.escape(s)}</i></span></div>')
    return f'<section><h3>{title}<small>{how}</small></h3><div class="kb">{"".join(out)}</div></section>'
body = (board(0, 'Base', 'always on', {}) + board(1, 'Fn', 'hold Fn (right of Right Shift)', {(3, 13): 'Fn'})
        + board(2, 'Nav', 'hold Space', {(4, 6): 'Space'}))
open(OUT, 'w').write(f'''<!doctype html><meta charset=utf-8><title>Dropbear keymap</title><style>
@page{{size:letter landscape;margin:.4in}}*{{box-sizing:border-box}}body{{font:11px -apple-system,"Helvetica Neue",sans-serif;color:#111;margin:0;background:#fff}}
header{{display:flex;justify-content:space-between;align-items:baseline;border-bottom:1.5px solid #111;padding-bottom:4px;margin-bottom:10px}}header h1{{font-size:17px;margin:0}}header p{{margin:0;color:#555}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:14px 22px}}h3{{font-size:13px;margin:0 0 4px}}h3 small{{font-weight:400;color:#666;margin-left:8px;font-size:10.5px}}
.kb{{position:relative;width:100%;aspect-ratio:15/5}}.k{{position:absolute;padding:1.5px}}
.k span{{position:relative;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;border:1px solid #999;border-radius:4px;background:#fff;text-align:center;line-height:1.05;overflow:hidden}}
.k em{{position:absolute;top:1.5px;left:3px;font-style:normal;font-size:8px;color:#666;line-height:1}}.k b{{font-size:12px;font-weight:600}}.k b.sm{{font-size:9.5px}}.k i{{font-style:normal;font-size:7.5px;color:#555;margin-top:1px}}
.k.mod span{{background:#ececec}}.k.act span{{background:#e3edf9;border-color:#8fb0d8}}.k.held span{{background:#222;color:#fff;border-color:#222}}.k.held i{{color:#ccc}}
.k.empty span{{border-style:dashed;border-color:#ccc;background:#fff}}.k.none span{{background:#f6f6f6;border-color:#ddd}}
footer{{margin-top:12px;color:#444;font-size:10px;line-height:1.45}}footer b{{color:#111}}
.legend{{display:flex;gap:12px;margin-top:6px}}.legend span{{display:inline-flex;align-items:center;gap:4px}}.legend i{{display:inline-block;width:14px;height:10px;border:1px solid #999;border-radius:2px}}
</style><header><h1>Dropbear 60 · Hot Rod / Pink Slip · master keymap</h1><p>QMK + VIA · read off the board {d["savedAt"][:10]}</p></header>
<div class="grid">{body}<section><h3>Notes</h3><footer style="margin:0">
<b>Small text</b> is the hold action; the corner legend is what Shift + that key types. Dashed keys pass through to Base.
Home row mods: A ⇧, S ⌃, D ⌥, F ⌘ and J ⌘, K ⌥, L ⌃, ; ⇧, with Flow Tap 150 ms (a mod key pressed right after another key is always a tap).
Hyper on Esc (Caps position), Enter, G and H. Fn has every symbol on the letter rows with mirrored brackets ([ ] on S L, &#123; &#125; on D K, ( ) on F J),
HHKB arrows on [ ; ' /, media on F7–F12, ⏭ on Backspace and ⏯ on Enter. Nav has Backspace on Esc, arrows, Home/End and PgUp/PgDn on the left and a numpad on the right, with . on the right ⌘. Both Shifts stay Shift on Nav.
Layer 3 is spare (no lighting on this board). Bootloader: hold the top-left key while plugging in.
<div class="legend"><span><i style="background:#ececec"></i>modifier / layer</span><span><i style="background:#e3edf9;border-color:#8fb0d8"></i>action</span><span><i style="background:#222;border-color:#222"></i>held to reach this layer</span><span><i style="border-style:dashed"></i>pass-through</span></div>
</footer></section></div>''')
print('wrote', OUT)
