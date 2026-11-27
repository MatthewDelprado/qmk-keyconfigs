"""Build the master keymap for the Corne v4 as a VIA keymap target: python3 build_master.py BACKUP.json OUT.json [standard|split]
standard: thumbs ⌥ ⌘ Space/Nav | Space/Nav Fn ⌘, the closest match to the other boards.
split:    thumbs ⌘⌘ Space/Nav Bksp | Enter/Fn Space/Nav ⇧⇧. The outer keys are macros that tap left ⌘ (or left ⇧) twice, for
          double-tap hotkeys; Fn is held on the Enter thumb.
Layers 0-3 are Base / Nav / Fn / Lighting; layers 4-5 are kept from BACKUP (nothing reaches them). Nav sits below Fn so
that with one Space thumb held (Nav), holding the other Space thumb (tap Backspace, hold Fn) gives the whole Fn layer:
the higher layer wins. (Before 2026-11-27, Fn was layer 1 and Nav layer 2.)
Matrix: left half rows 0-3, right half rows 4-7. Column 0 is the outer column on both halves, 5 the inner
(T G B / Y H N), 6 the extra inner keys (rows 0-1). Thumbs are row 3 / 7, columns 3 (outer) 4 (middle) 5 (inner)."""
import json, sys, copy
BACKUP, OUT = sys.argv[1:3]
THUMBS = sys.argv[3] if len(sys.argv) > 3 else 'standard'
assert THUMBS in ('standard', 'split'), THUMBS
src = json.load(open(BACKUP))

# keycodes (QMK modern numbering)
K = {c: 0x04 + i for i, c in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}
K.update({c: 0x1e + i for i, c in enumerate('1234567890')})
K.update({'Enter': 0x28, 'Esc': 0x29, 'Bksp': 0x2a, 'Tab': 0x2b, 'Space': 0x2c, '-': 0x2d, '=': 0x2e, '[': 0x2f, ']': 0x30, '\\': 0x31,
          ';': 0x33, "'": 0x34, '`': 0x35, ',': 0x36, '.': 0x37, '/': 0x38, 'Home': 0x4a, 'PgUp': 0x4b, 'Del': 0x4c, 'End': 0x4d,
          'PgDn': 0x4e, '→': 0x4f, '←': 0x50, '↓': 0x51, '↑': 0x52, 'Mute': 0xa8, 'Vol+': 0xa9, 'Vol−': 0xaa, '⏭': 0xab, '⏮': 0xac,
          '⏯': 0xae, 'LCtl': 0xe0, 'LSft': 0xe1, 'LAlt': 0xe2, 'LGui': 0xe3, 'RSft': 0xe5, 'RGui': 0xe7,
          'RGB': 0x7820, 'Eff+': 0x7821, 'Eff−': 0x7822, 'Hue+': 0x7823, 'Hue−': 0x7824, 'Sat+': 0x7825, 'Sat−': 0x7826,
          'Bri+': 0x7827, 'Bri−': 0x7828, 'Spd+': 0x7829, 'Spd−': 0x782a})
for a, b in zip('!@#$%^&*()_+{}|:"~<>?', '1234567890-=[]\\;\'`,./'): K[a] = 0x200 | K[b]
_, T = 0x0000, 0x0001                     # does nothing / pass through
def mt(mods, k): return 0x2000 | mods << 8 | K[k]   # mods: 1 ⌃ 2 ⇧ 4 ⌥ 8 ⌘, 0x10 = right hand
def lt(layer, k): return 0x4000 | layer << 8 | K[k]
def mo(layer): return 0x5220 | layer
def k(x): return K[x] if isinstance(x, str) else x
HYPR_ESC, HYPR_ENT = mt(0x0f, 'Esc'), mt(0x0f, 'Enter')
NAV, FN = 1, 2
SPC_NAV, CMD_H = lt(NAV, 'Space'), 0x0800 | K['H']
BKSP_FN = lt(FN, 'Bksp')                  # on Nav: the other Space thumb
ENT_FN, M0, M1 = lt(FN, 'Enter'), 0x7700, 0x7701   # M0 / M1: Vial macros 0 and 1

# Vial macro buffer (NUL-separated). 01 01 kc = tap kc; 01 04 lo hi = delay (lo-1)+(hi-1)*255 ms.
def double_tap(kc): return bytes([1, 1, kc, 1, 4, 21, 1, 1, 1, kc, 0])   # tap, 20 ms, tap
MACROS = double_tap(K['LGui']) + double_tap(K['LSft']) if THUMBS == 'split' else b''

if THUMBS == 'standard':
    THUMB = dict(base=(['LAlt', 'LGui', SPC_NAV], [SPC_NAV, mo(FN), 'RGui']),
                 fn=([T, T, mo(3)], [mo(3), T, 'Mute']), nav=([T, T, BKSP_FN], [BKSP_FN, T, '.']))
else:
    THUMB = dict(base=([M0, SPC_NAV, 'Bksp'], [ENT_FN, SPC_NAV, M1]),     # left inner was Del until 2026-11-27 (changed in Vial)
                 fn=([T, T, mo(3)], [T, T, 'Mute']), nav=([T, BKSP_FN, 'Bksp'], ['Bksp', BKSP_FN, '.']))

def layer(left, right, lthumb, rthumb, lex, rex):
    """left/right: 3 rows of 6 keys, read left-to-right as you look at the board.
    lthumb/rthumb: 3 keys left-to-right. lex/rex: extra keys (top, then second row)."""
    m = [[0] * 7 for _ in range(8)]
    for r in range(3):
        for i, v in enumerate(left[r]): m[r][i] = k(v)              # left: col 0 is outer (leftmost)
        for i, v in enumerate(right[r]): m[4 + r][5 - i] = k(v)     # right: col 5 is inner (leftmost)
    for i, v in enumerate(lthumb): m[3][3 + i] = k(v)               # left thumbs outer -> inner
    for i, v in enumerate(rthumb): m[7][5 - i] = k(v)               # right thumbs inner -> outer
    m[0][6], m[1][6] = k(lex[0]), k(lex[1])
    m[4][6], m[5][6] = k(rex[0]), k(rex[1])
    return m

base = layer(
    [['Tab', 'Q', 'W', 'E', 'R', 'T'],
     [HYPR_ESC, mt(2, 'A'), mt(1, 'S'), mt(4, 'D'), mt(8, 'F'), mt(0x0f, 'G')],
     ['LSft', 'Z', 'X', 'C', 'V', 'B']],
    [['Y', 'U', 'I', 'O', 'P', 'Bksp'],
     [mt(0x0f, 'H'), mt(0x18, 'J'), mt(0x14, 'K'), mt(0x11, 'L'), mt(0x12, ';'), HYPR_ENT],
     ['N', 'M', ',', '.', '/', 'RSft']],
    *THUMB['base'],
    ['⏯', '⏭'], ['Vol+', 'Vol−'])

fn = layer(
    [['`', '!', '@', '#', '$', '%'],
     ['~', '&', '[', '{', '(', "'"],
     [T, '\\', '|', ':', '<', ';']],
    [['*', '/', '+', '_', '-', '↑'],
     ['"', ')', '}', ']', '←', '→'],
     ['=', '>', '?', '.', '↓', 'Vol+']],
    *THUMB['fn'],
    [T, T], ['^', T])

nav = layer(
    # Corne only (2026-11-28): the cluster sits one key right of the master, so → is on F; ⌘H and Enter stay.
    [[CMD_H, T, 'Home', '↑', 'End', T],
     ['Enter', T, '←', '↓', '→', T],
     [T, T, 'PgUp', T, 'PgDn', T]],
    [['*', '7', '8', '9', '-', 'Del'],
     ['/', '4', '5', '6', '+', T],
     ['0', '1', '2', '3', '=', T]],
    *THUMB['nav'],
    [T, T], [T, T])

light = layer(
    [[T, 'Eff−', 'Eff+', 'Hue−', 'Hue+', 'RGB'],
     [T, T, T, 'Sat−', 'Sat+', T],
     [T, T, T, T, T, T]],
    [[T, T, T, 'Bri−', 'Bri+', T],
     [T, T, T, 'Spd−', 'Spd+', T],
     [T, T, T, T, T, T]],
    [T, T, T], [T, T, T],
    [T, T], [T, T])

out = copy.deepcopy(src)
out['keymap'][:4] = [base, nav, fn, light]
size = len(src['macroBufferHex']) // 2
out['macroBufferHex'] = (MACROS + bytes(size - len(MACROS))).hex()
out.pop('savedAt', None); out['note'] = f'master keymap target for the Corne v4 ({THUMBS} thumbs, layers 0-3); layers 4-5 kept from the backup'
json.dump(out, open(OUT, 'w'), indent=1)
print('wrote', OUT)
