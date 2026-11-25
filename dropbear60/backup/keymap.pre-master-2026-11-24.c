// Dropbear 60 (solder) — runs QMK's kkatano/bakeneko60 definition.
// Uses the 8-key ANSI bottom row macro because the board's right-hand mods sit at
// matrix 4,10 / 4,11 / 4,12 (4,13 unused) — the tsangan macro has no 4,10.
// Layer 0 mirrors the VIA backup dropbear60_solder__bakeneko_60_v3_hr.layout.json.

#include QMK_KEYBOARD_H

enum layers {
    _BASE,
    _FN,
    _NAV,
    _SPARE,
};

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    [_BASE] = LAYOUT_60_ansi_split_bs_rshift(
        KC_GRV,         KC_1,    KC_2,          KC_3,          KC_4,          KC_5,    KC_6,    KC_7,          KC_8,          KC_9,          KC_0,    KC_MINS, KC_EQL,  KC_BSLS, KC_DEL,
        KC_TAB,         KC_Q,    KC_W,          KC_E,          KC_R,          KC_T,    KC_Y,    KC_U,          KC_I,          KC_O,          KC_P,    KC_LBRC, KC_RBRC, KC_BSPC,
        HYPR_T(KC_ESC), KC_A,    LCTL_T(KC_S),  LALT_T(KC_D),  LGUI_T(KC_F),  KC_G,    KC_H,    RGUI_T(KC_J),  RALT_T(KC_K),  RCTL_T(KC_L),  KC_SCLN, KC_QUOT,          HYPR_T(KC_ENT),
        KC_LSFT,                 KC_Z,          KC_X,          KC_C,          KC_V,    KC_B,    KC_N,          KC_M,          KC_COMM,       KC_DOT,  KC_SLSH, KC_RSFT, MO(_FN),
        KC_NO,          KC_LALT, KC_LGUI,                                     LT(_NAV, KC_SPC),                                                KC_RALT, KC_RGUI, KC_RCTL, KC_NO
    ),

    [_FN] = LAYOUT_60_ansi_split_bs_rshift(
        QK_BOOT, KC_F1,   KC_F2,   KC_F3,   KC_F4,   KC_F5,   KC_F6,   KC_F7,   KC_F8,   KC_F9,   KC_F10,  KC_F11,  KC_F12,  _______, _______,
        _______, KC_NO,   KC_NO,   KC_NO,   KC_NO,   KC_NO,   KC_NO,   KC_NO,   KC_NO,   KC_NO,   KC_NO,   KC_UP,   _______, KC_MNXT,
        _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, KC_LEFT, KC_RGHT,          KC_MPLY,
        _______,          _______, _______, _______, _______, _______, _______, _______, _______, _______, KC_DOWN, KC_VOLU, _______,
        _______, _______, _______,                            _______,                            _______, KC_MRWD, KC_VOLD, KC_MNXT
    ),

    [_NAV] = LAYOUT_60_ansi_split_bs_rshift(
        _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______,
        KC_BSPC, KC_HOME, KC_UP,   KC_END,  _______, _______, _______, _______, _______, _______, _______, _______, _______, _______,
        KC_ENT,  KC_LEFT, KC_DOWN, KC_RGHT, _______, _______, _______, _______, _______, _______, _______, _______,          _______,
        _______,          _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______,                            _______,                            _______, _______, _______, _______
    ),

    [_SPARE] = LAYOUT_60_ansi_split_bs_rshift(
        _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______,          _______,
        _______,          _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______,                            _______,                            _______, _______, _______, _______
    ),
};
