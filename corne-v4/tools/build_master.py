"""Build the master keymap for the Corne v4 as a VIA keymap target: python3 build_master.py BACKUP.json OUT.json
Layers 0-3 are Base / Fn / Nav / Lighting; layers 4-5 are kept from BACKUP (nothing reaches them).
Matrix: left half rows 0-3, right half rows 4-7. Column 0 is the outer column on both halves, 5 the inner
(T G B / Y H N), 6 the extra inner keys (rows 0-1). Thumbs are row 3 / 7, columns 3 (outer) 4 (middle) 5 (inner)."""
import json, sys, copy
BACKUP, OUT = sys.argv[1:3]
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
SPC_NAV, CMD_H = lt(2, 'Space'), 0x0800 | K['H']

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
    ['LAlt', 'LGui', SPC_NAV], [SPC_NAV, mo(1), 'RGui'],
    ['⏯', '⏭'], ['Vol+', 'Vol−'])

fn = layer(
    [['`', '!', '@', '#', '$', '%'],
     ['~', '&', '[', '{', '(', "'"],
     [T, '\\', '|', ':', '<', ';']],
    [['*', '/', '+', '_', '-', '↑'],
     ['"', ')', '}', ']', '←', '→'],
     ['=', '>', '?', '.', '↓', 'Vol+']],
    [T, T, mo(3)], [mo(3), T, 'Mute'],
    [T, T], ['^', T])

nav = layer(
    [[CMD_H, 'Home', '↑', 'End', T, T],
     ['Enter', '←', '↓', '→', T, T],
     [T, 'PgUp', T, 'PgDn', T, T]],
    [['*', '7', '8', '9', '-', 'Del'],
     ['/', '4', '5', '6', '+', T],
     ['0', '1', '2', '3', '=', T]],
    [T, T, 'Bksp'], ['Bksp', T, '.'],
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
out['keymap'][:4] = [base, fn, nav, light]
out.pop('savedAt', None); out['note'] = 'master keymap target for the Corne v4 (layers 0-3); layers 4-5 kept from the backup'
json.dump(out, open(OUT, 'w'), indent=1)
print('wrote', OUT)
