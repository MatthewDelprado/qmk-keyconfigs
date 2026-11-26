"""Build the master keymap for the Neo Ergo (wired) as a VIA target: python3 build_master.py BACKUP.json OUT.json
Matrix 5x15 from Neo Studio's VIA definition (backup/neo-ergo-wired-via-definition.json), with the layout options
already on the board: split Backspace, 60%-mode Right Shift (1.75u Shift + 1u Fn), 2.25u split spaces, 1.5u bottom right.

Master (Kara, HHKB) position -> Neo Ergo matrix:
  row 0: c0-c6 -> r0 c0-c6; c7-c12 -> r0 c8-c13 (r0c7 is no key); \\ -> r1c14, Del -> r0c14 (split Backspace)
  row 1: Tab..] -> r1 c1-c13; Backspace (1.5u) -> r2c13
  row 2: Esc..' -> r2 c1-c12; Enter -> r2c14
  row 3: Shift Z X C V B -> r3 c1-c6; N M , . / Shift Fn -> r3 c8-c14 (r3c7 is the right-hand B)
  row 4: ⌥ ⌘ -> r4c2 r4c3; Space -> both halves r4c6 r4c7; ⌘ -> r4c10; ⌃ -> r4c14 (keeps its → tap)
Board-only keys: the left column r1c0-r4c0, left ⌃ r4c1, right-hand B r3c7, ← / hold ⌥ r4c12.
Layers: 0 Base, 1 Nav, 2 Fn, 3 Lighting (rgblight underglow). Nav sits below Fn so that with one Space half held
(Nav), holding the other half (tap Backspace, hold Fn) gives the whole Fn layer: the higher layer wins.
Macros are left as they are."""
import json, sys, copy
BACKUP, OUT = sys.argv[1:3]
src = json.load(open(BACKUP))

K = {c: 0x04 + i for i, c in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}
K.update({c: 0x1e + i for i, c in enumerate('1234567890')})
K.update({'Enter': 0x28, 'Esc': 0x29, 'Bksp': 0x2a, 'Tab': 0x2b, 'Space': 0x2c, '-': 0x2d, '=': 0x2e, '[': 0x2f, ']': 0x30, '\\': 0x31,
          ';': 0x33, "'": 0x34, '`': 0x35, ',': 0x36, '.': 0x37, '/': 0x38, 'Ins': 0x49, 'Home': 0x4a, 'PgUp': 0x4b, 'Del': 0x4c, 'End': 0x4d,
          'PgDn': 0x4e, '→': 0x4f, '←': 0x50, '↓': 0x51, '↑': 0x52, 'Mute': 0xa8, 'Vol+': 0xa9, 'Vol−': 0xaa, '⏭': 0xab, '⏮': 0xac,
          '⏯': 0xae, 'LCtl': 0xe0, 'LSft': 0xe1, 'LAlt': 0xe2, 'LGui': 0xe3, 'RSft': 0xe5, 'RGui': 0xe7,
          'RGB': 0x7820, 'Eff+': 0x7821, 'Eff−': 0x7822, 'Hue+': 0x7823, 'Hue−': 0x7824, 'Sat+': 0x7825, 'Sat−': 0x7826,
          'Bri+': 0x7827, 'Bri−': 0x7828, 'Spd+': 0x7829, 'Spd−': 0x782a, 'NKRO': 0x7013})
for i in range(12): K[f'F{i+1}'] = 0x3a + i
for a, b in zip('!@#$%^&*()_+{}|:"~<>?', '1234567890-=[]\\;\'`,./'): K[a] = 0x200 | K[b]
T = 0x0001                                  # pass through to Base
def mt(mods, k): return 0x2000 | mods << 8 | K[k]   # mods: 1 ⌃ 2 ⇧ 4 ⌥ 8 ⌘, 0x10 = right hand, 0x0f = Hyper
def lt(layer, k): return 0x4000 | layer << 8 | K[k]
def mo(layer): return 0x5220 | layer
def k(x): return K[x] if isinstance(x, str) else x
NAV, FN = 1, 2
SPC_NAV, SPC_LIGHT, CMD_H = lt(NAV, 'Space'), lt(3, 'Space'), 0x0800 | K['H']
BKSP_FN = lt(FN, 'Bksp')                    # on Nav: the other Space half

def neo(rows, left_col, extra):
    """rows: the master's 5 rows (HHKB positions, same shape as the master page); returns a 5x15 Neo matrix.
    left_col: keys for r1c0..r4c0. extra: {(r, c): key} for the board-only keys."""
    m = [[T] * 15 for _ in range(5)]
    r0, r1, r2, r3, r4 = rows
    for c in range(7): m[0][c] = k(r0[c])
    for c in range(7, 13): m[0][c + 1] = k(r0[c])
    m[1][14], m[0][14] = k(r0[13]), k(r0[14])
    for c in range(13): m[1][c + 1] = k(r1[c])
    m[2][13] = k(r1[13])
    for c in range(12): m[2][c + 1] = k(r2[c])
    m[2][14] = k(r2[12])
    for c in range(6): m[3][c + 1] = k(r3[c])
    for c in range(6, 13): m[3][c + 2] = k(r3[c])
    alt, cmd, spl, spr, rcmd, rctl = r4
    m[4][2], m[4][3], m[4][6], m[4][7], m[4][10], m[4][14] = k(alt), k(cmd), k(spl), k(spr), k(rcmd), k(rctl)
    for i, v in enumerate(left_col): m[1 + i][0] = k(v)
    for (r, c), v in extra.items(): m[r][c] = k(v)
    return m

base = neo([
    ['Esc', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '\\', 'Del'],
    ['Tab', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[', ']', 'Bksp'],
    [mt(0x0f, 'Esc'), mt(2, 'A'), mt(1, 'S'), mt(4, 'D'), mt(8, 'F'), mt(0x0f, 'G'),
     mt(0x0f, 'H'), mt(0x18, 'J'), mt(0x14, 'K'), mt(0x11, 'L'), mt(0x12, ';'), "'", mt(0x0f, 'Enter')],
    ['LSft', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/', 'RSft', mo(FN)],
    ['LAlt', 'LGui', SPC_NAV, SPC_NAV, 'RGui', mt(0x11, '→')]],
    ['Vol+', 'Vol−', lt(FN, '⏯'), mo(FN)],
    {(4, 1): 'LCtl', (3, 7): 'B', (4, 12): mt(0x14, '←')})

fn = neo([
    ['`', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', '⏮', '⏯', '⏭', 'F10', 'Vol−', 'Vol+', 'Ins', 'Del'],
    ['`', '!', '@', '#', '$', '%', '*', '/', '+', '_', '-', '↑', '^', '⏭'],
    ['~', '&', '[', '{', '(', "'", '"', ')', '}', ']', '←', '→', '⏯'],
    [T, '\\', '|', ':', '<', ';', '=', '>', '?', '.', '↓', 'Vol+', T],
    [T, T, SPC_LIGHT, SPC_LIGHT, 'Mute', 'Vol−']],
    ['⏭', '⏮', T, T],
    {(3, 7): ';', (3, 14): mo(FN)})            # Fn stays Fn while held

nav = neo([
    ['Bksp'] + [T] * 14,
    [CMD_H, 'Home', '↑', 'End', T, T, '*', '7', '8', '9', '-', T, T, T],
    ['Enter', '←', '↓', '→', T, T, '/', '4', '5', '6', '+', T, T],
    [T, 'PgUp', T, 'PgDn', T, T, '0', '1', '2', '3', '=', T, T],
    [T, T, BKSP_FN, BKSP_FN, '.', T]],        # with one Space half held, the other is Backspace / hold Fn
    [T, T, T, T], {})

light = neo([
    [T, 'Eff−', 'Eff+', 'Hue−', 'Hue+', 'RGB', T, T, T, T, T, 'Bri−', 'Bri+', T, T],
    [T, T, T, 'Sat−', 'Sat+', T, T, T, T, T, T, 'Spd−', 'Spd+', T],
    [T, T, T, T, T, 'NKRO', T, T, T, T, T, T, T],
    [T] * 13,
    [T, T, T, T, T, T]],
    [T, T, T, T], {})

# Matrix spots with no key in this layout keep whatever the board has now.
NOKEY = [(0, 7), (4, 0 + 4), (4, 5), (4, 8), (4, 9), (4, 11), (4, 13)]
layers = [base, nav, fn, light]
SRC_LAYER = [0, 2, 1, 3]                    # the backup's layers were 0 Base, 1 Fn, 2 Nav, 3 Lighting
for l, m in enumerate(layers):
    for r, c in NOKEY: m[r][c] = src['keymap'][SRC_LAYER[l]][r][c]
out = copy.deepcopy(src)
out['keymap'] = layers
out.pop('savedAt', None); out['note'] = 'master keymap target for the Neo Ergo (wired); macros kept from the backup'
json.dump(out, open(OUT, 'w'), indent=1)
print('wrote', OUT)
