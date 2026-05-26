# Matt's Keyboards

Custom QMK keymaps for Matt's keyboards. Source files live here; the QMK firmware clone used to build them is at `~/Documents/git/GMK`.

## Build & flash any keymap

```bash
# Copy the keymap into the QMK tree, compile, then flash
cp -r pretty-paddy ~/Documents/git/GMK/keyboards/idyllic/pizzapad/keymaps/matt
qmk compile -kb idyllic/pizzapad -km matt
qmk flash   -kb idyllic/pizzapad -km matt
```

---

## Keyboard Directory

| Nickname(s) | Folder | QMK path | Notes |
|---|---|---|---|
| pretty paddy, pretty pad, paddy pad, pizza pad | `pretty-paddy/` | `keyboards/idyllic/pizzapad` | 3×3 ortho, RP2040 (Seeed XIAO), sold by MechStock AU |

---

## Repo structure

```
pretty-paddy/
├── keymap.c       — QMK keymap source
├── config.h       — tap/hold timing settings
├── rules.mk       — build flags
├── KEYMAP.md      — full layout + Raycast setup reference
└── firmware/
    ├── idyllic_pizzapad_matt.uf2            — latest built firmware
    └── idyllic_pizzapad_default_RESTORE.uf2 — factory restore
```
