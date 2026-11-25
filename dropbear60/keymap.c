// Dropbear 60 (solder PCB, in the Hot Rod / Pink Slip HHKB case): the master keymap,
// ported from the Rama Works Kara (see the "Master Keymap" artifact).
// Runs QMK's kkatano/bakeneko60 definition. Uses the 8-key ANSI bottom-row macro because the
// HHKB case only exposes ⌥ ⌘ Space ⌘ ⌃; the right-hand keys sit at matrix 4,11 / 4,12 (as the
// board's own VIA setup had them), 4,10 is unused and 4,13 doubles as Ctrl.
//
// Base: home row mods on S/D/F and J/K/L, Shift mod-taps on A and ;, Hyper on Esc, Enter, G and H.
// Fn (key right of Right Shift): every symbol on the letter rows, mirrored brackets,
//   math under the right hand (* on Y and - on P, matching the Nav numpad), HHKB arrows,
//   media on F7-F12, ⏭ on Backspace and ⏯ on Enter, ? on comma, and Vol+ / Mute / Vol- on Right Shift / right Cmd / right Ctrl.
// Nav (hold Space): Backspace on Esc, arrows, Home/End, PgUp/PgDn, Cmd+H on Tab; numpad on the right hand,
//   0 on N, = on /, and . on the right Cmd. Both Shifts stay Shift.
// No lighting on this board, so layer 3 is spare. Bootloader: hold Esc while plugging in.

#include QMK_KEYBOARD_H

enum layers {
    _BASE,
    _FN,
    _NAV,
    _SPARE,
};

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    [_BASE] = LAYOUT_60_ansi_split_bs_rshift(
        KC_ESC,         KC_1,          KC_2,          KC_3,          KC_4,          KC_5,    KC_6,    KC_7,          KC_8,          KC_9,          KC_0,            KC_MINS, KC_EQL,  KC_BSLS, KC_DEL,
        KC_TAB,         KC_Q,          KC_W,          KC_E,          KC_R,          KC_T,    KC_Y,    KC_U,          KC_I,          KC_O,          KC_P,            KC_LBRC, KC_RBRC, KC_BSPC,
        HYPR_T(KC_ESC), LSFT_T(KC_A),  LCTL_T(KC_S),  LALT_T(KC_D),  LGUI_T(KC_F),  HYPR_T(KC_G), HYPR_T(KC_H), RGUI_T(KC_J),  RALT_T(KC_K),  RCTL_T(KC_L),  RSFT_T(KC_SCLN), KC_QUOT,          HYPR_T(KC_ENT),
        KC_LSFT,                       KC_Z,          KC_X,          KC_C,          KC_V,    KC_B,    KC_N,          KC_M,          KC_COMM,       KC_DOT,          KC_SLSH, KC_RSFT, MO(_FN),
        KC_NO,          KC_LALT,       KC_LGUI,                                     LT(_NAV, KC_SPC),                                              KC_NO,           KC_RGUI, KC_RCTL, KC_RCTL
    ),

    [_FN] = LAYOUT_60_ansi_split_bs_rshift(
        KC_GRV,  KC_F1,   KC_F2,   KC_F3,   KC_F4,   KC_F5,   KC_F6,   KC_MPRV, KC_MPLY, KC_MNXT, KC_F10,  KC_VOLD, KC_VOLU, KC_INS,  KC_DEL,
        KC_GRV,  KC_EXLM, KC_AT,   KC_HASH, KC_DLR,  KC_PERC, KC_ASTR, KC_SLSH, KC_PLUS, KC_UNDS, KC_MINS, KC_UP,   KC_CIRC, KC_MNXT,
        KC_TILD, KC_AMPR, KC_LBRC, KC_LCBR, KC_LPRN, KC_QUOT, KC_DQUO, KC_RPRN, KC_RCBR, KC_RBRC, KC_LEFT, KC_RGHT,          KC_MPLY,
        _______,          KC_BSLS, KC_PIPE, KC_COLN, KC_LABK, KC_SCLN, KC_EQL,  KC_RABK, KC_QUES, KC_DOT,  KC_DOWN, KC_VOLU, _______,
        _______, _______, _______,                            _______,                            _______, KC_MUTE, KC_VOLD, KC_VOLD
    ),

    [_NAV] = LAYOUT_60_ansi_split_bs_rshift(
        KC_BSPC,    _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______,
        LGUI(KC_H), KC_HOME, KC_UP,   KC_END,  _______, _______, KC_ASTR, KC_7,    KC_8,    KC_9,    KC_MINS, _______, _______, _______,
        KC_ENT,     KC_LEFT, KC_DOWN, KC_RGHT, _______, _______, KC_SLSH, KC_4,    KC_5,    KC_6,    KC_PLUS, _______,          _______,
        _______,             KC_PGUP, _______, KC_PGDN, _______, _______, KC_0,    KC_1,    KC_2,    KC_3,    KC_EQL,  _______, _______,
        _______,    _______, _______,                            _______,                            _______, KC_DOT,  _______, _______
    ),

    [_SPARE] = LAYOUT_60_ansi_split_bs_rshift(
        _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______,          _______,
        _______,          _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______,
        _______, _______, _______,                            _______,                            _______, _______, _______, _______
    ),
};
