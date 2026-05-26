# Matt's Keyboards — QMK Keyconfig Repo

Custom QMK keymaps for Matt's keyboards. Source files live here; the QMK firmware clone used to build them is at `~/Documents/git/GMK`.

---

## Keyboard Directory

| Nickname(s) | Folder | QMK path | MCU | Layout | Notes |
|---|---|---|---|---|---|
| pretty paddy, pretty pad, paddy pad, pizza pad | `pretty-paddy/` | `keyboards/idyllic/pizzapad` | RP2040 (Seeed XIAO) | 3×3 ortho (9 keys) | Sold by MechStock AU. VIA name: "Pizza Pad". |

---

## Repo Structure

Each keyboard gets its own folder:

```
<keyboard-name>/
├── keymap.c       — QMK keymap source
├── config.h       — tap/hold timing overrides
├── rules.mk       — build feature flags
├── KEYMAP.md      — layout reference + Raycast/app setup guide
└── firmware/
    ├── <board>_matt.uf2              — latest built firmware (ready to flash)
    └── <board>_default_RESTORE.uf2  — factory restore backup
```

---

## Build & Flash Workflow

```bash
# 1. Copy keymap into the QMK tree
cp -r <keyboard-folder>/* ~/Documents/git/GMK/keyboards/<qmk-path>/keymaps/matt/

# 2. Compile
qmk compile -kb <qmk-path> -km matt

# 3. Flash (enter bootloader first — see keyboard's KEYMAP.md)
qmk flash -kb <qmk-path> -km matt

# 4. Copy the built .uf2 back here for safekeeping
cp ~/Documents/git/GMK/<board>_matt.uf2 <keyboard-folder>/firmware/
```

After any change: rebuild, test, copy .uf2 back, commit, push.

---

## QMK Agent Instructions

The following are hard-won lessons from building the Pretty Paddy keymap. Apply them to all future keyboard configs.

### 1. LT() only accepts basic keycodes as the tap action

`LT(layer, kc)` — `kc` must be a basic keycode (value ≤ 0xFF). **`HYPR(KC_x)` is a modifier-stacked keycode and will NOT work.** QMK silently strips the modifiers and sends just the bare key — e.g. `LT(layer, HYPR(KC_1))` sends `1`, not `Hyper+1`.

**Fix:** Use an inert placeholder basic keycode inside `LT()` and intercept the tap in `process_record_user()`:

```c
// In layout:
LT(_MY_LAYER, KC_F22)   // KC_F22 is the placeholder

// In process_record_user():
case LT(_MY_LAYER, KC_F22):
    if (record->tap.count && record->event.pressed) {
        tap_code16(HYPR(KC_1));   // send the real output
        return false;
    }
    break;
```

Good placeholder keycodes (basic, safe on macOS, unlikely to trigger anything):
- `KC_F22`, `KC_F23`, `KC_F24` — extended F-keys, macOS ignores
- `KC_SCRL` — scroll lock, macOS ignores
- `KC_PAUSE` — pause key, macOS ignores

Never reuse the same placeholder for two different keys.

### 2. Shared layers for symmetric anchor pairs

When two keys act as mutual chord anchors (hold either one, tap the other), **give them the SAME layer**.

With `HOLD_ON_OTHER_KEY_PRESS`, pressing the second key while the first is held immediately registers the first as held. If the second key is *also* an `LT()` key pointing to a *different* layer, it also registers as held — activating its own layer and preventing it from emitting a keycode.

If both keys share the same layer, the second key's hold attempt is a no-op (layer already active), so it behaves correctly as a chord target.

```c
// CORRECT — K0 and K2 share _TOP_HOLD:
LT(_TOP_HOLD, KC_F22)   // K0
LT(_TOP_HOLD, KC_F23)   // K2

[_TOP_HOLD] = LAYOUT(...,
    KC_F14, KC_TRNS, KC_F14,   // both K0 and K2 positions → same output
    ...
)

// WRONG — separate layers cause K2 to also register as held:
LT(_TOP_LEFT_HOLD,  KC_F22)   // K0 → activates layer 3
LT(_TOP_RIGHT_HOLD, KC_F23)   // K2 → activates layer 4 simultaneously → broken
```

### 3. Hold detection settings (config.h)

Always include both in `config.h` for reliable chord detection:

```c
#define HOLD_ON_OTHER_KEY_PRESS   // register hold the instant another key is pressed
#define PERMISSIVE_HOLD           // also register hold if another key completes a full press+release
```

Without these, chords require holding past the tapping term (200ms default) before pressing the chord target — feels sluggish and unreliable.

### 4. Avoid these F-keys on macOS

These conflict with system brightness controls and should never be used as hotkeys:

| F-key | Issue |
|-------|-------|
| F14 | Brightness down |
| F15 | Brightness up |
| F17 | Brightness (some configs / external displays) |

Raycast also does not recognise F21 and above as recordable hotkeys — stay within F13–F20.

**Safe F-key range for Raycast hotkeys:** F13, F16, F18, F19, F20  
(F14, F15, F17 avoided for brightness; F21+ not supported by Raycast)

### 5. When to use HYPR+key vs F-key for chord outputs

Use `HYPR+key` when:
- The binding already exists in Raycast (e.g. user has `Hyper+Return` for full screen)
- No safe F-key is available
- e.g. `HYPR(KC_0)`, `HYPR(KC_ENT)`, `HYPR(KC_BSLS)`

Use F-keys (F13–F20, excluding F14/F15/F17) when:
- Creating new Raycast bindings from scratch
- Cleaner to have a dedicated key with no modifier

### 6. Confirm Raycast can record a keycode before shipping

After building, always manually trigger each chord in Raycast's shortcut recording field to confirm the key is received. Some keycodes (F21+, certain media keys) are silently ignored by Raycast and will never bind. If recording doesn't respond, the keycode is unsupported — pick a different one.

### 7. Build process reminder

```bash
qmk compile -kb <path> -km matt   # always compile before flashing
qmk flash   -kb <path> -km matt   # or drag .uf2 onto RPI-RP2 drive
```

After any keymap change: rebuild → test on hardware → copy `.uf2` back to `firmware/` → commit → push.
