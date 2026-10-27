#include QMK_KEYBOARD_H
#include "keymap_spanish.h"

enum layer_number {
  _QWERTY = 0,
  _LOWER,
  _RAISE,
  _ADJUST,
};

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {

[_QWERTY] = LAYOUT(
  QK_GESC,  KC_1,   KC_2,    KC_3,    KC_4,    KC_5,                     KC_6,    KC_7,    KC_8,    KC_9,    KC_0,    ES_QUOT,
  KC_TAB,   KC_Q,   KC_W,    KC_E,    KC_R,    KC_T,                     KC_Y,    KC_U,    KC_I,    KC_O,    KC_P,    ES_GRV,
  KC_LSFT,  KC_A,   KC_S,    KC_D,    KC_F,    KC_G,                     KC_H,    KC_J,    KC_K,    KC_L,    ES_NTIL, ES_ACUT,
  KC_LCTL,  KC_Z,   KC_X,    KC_C,    KC_V,    KC_B, ES_LCBR,  ES_RCBR,  KC_N,    KC_M,    ES_COMM, ES_DOT,  ES_MINS,  KC_RSFT,
                        KC_LALT, KC_LGUI, MO(_LOWER), KC_SPC, KC_ENT, MO(_RAISE), KC_BSPC, KC_RGUI
),

[_LOWER] = LAYOUT(
  XXXXXXX, LCAG(KC_1), LCAG(KC_2), LCAG(KC_3), LCAG(KC_4), LCAG(KC_5),                   XXXXXXX, ES_BSLS, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
  XXXXXXX, LCAG(KC_Q), LCAG(KC_W), LCAG(KC_E), LCAG(KC_R), LCTL(LSFT(KC_TAB)),        XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, ES_PLUS,
  KC_CAPS, LCAG(KC_A), LCAG(KC_S), LCAG(KC_D), LCAG(KC_F), LCTL(KC_TAB),              LCAG(KC_H), LCAG(KC_J), LCAG(KC_K), LCAG(KC_L), XXXXXXX, ES_CCED,
  XXXXXXX, LCAG(KC_Z), LCAG(KC_X), LCAG(KC_C), LCAG(KC_V), LCAG(KC_B), ES_LBRC, ES_RBRC, XXXXXXX, XXXXXXX, LCAG(ES_COMM), LCAG(ES_DOT), XXXXXXX, XXXXXXX,
                                   XXXXXXX,    XXXXXXX,    XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX
),

[_RAISE] = LAYOUT(
  XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,                     XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
  XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,                     XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
  KC_F1,  KC_F2,    KC_F3,   KC_F4,   KC_F5,   KC_F6,                       KC_LEFT, KC_DOWN, KC_UP,   KC_RGHT, XXXXXXX, XXXXXXX,
  KC_F7,   KC_F8,   KC_F9,   KC_F10,  KC_F11,  KC_F12,   ES_LABK, ES_RABK,  KC_PLUS, KC_MINS, KC_EQL,  KC_LBRC, KC_RBRC, KC_BSLS,
                             XXXXXXX, XXXXXXX, XXXXXXX,  XXXXXXX, XXXXXXX,  XXXXXXX, XXXXXXX, XXXXXXX
),

[_ADJUST] = LAYOUT(
  XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,                   XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
  XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,                   XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
  XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,                   XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
  XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
                             _______, _______, _______, _______, _______,  _______, _______, _______
  )
};

layer_state_t layer_state_set_user(layer_state_t state) {
  return update_tri_layer_state(state, _LOWER, _RAISE, _ADJUST);
}

//SSD1306 OLED update loop, make sure to enable OLED_ENABLE=yes in rules.mk
#ifdef OLED_ENABLE

oled_rotation_t oled_init_user(oled_rotation_t rotation) {
  if (!is_keyboard_master())
    return OLED_ROTATION_180;  // flips the display 180 degrees if offhand
  return rotation;
}

// When you add source files to SRC in rules.mk, you can use functions.
const char *read_layer_state(void);
const char *read_logo(void);
void set_keylog(uint16_t keycode, keyrecord_t *record);
const char *read_keylog(void);
const char *read_keylogs(void);

// const char *read_mode_icon(bool swap);
// const char *read_host_led_state(void);
// void set_timelog(void);
// const char *read_timelog(void);

bool oled_task_user(void) {
  if (is_keyboard_master()) {
    // If you want to change the display of OLED, you need to change here
    oled_write_ln(read_layer_state(), false);
    oled_write_ln(read_keylog(), false);
    oled_write_ln(read_keylogs(), false);
    //oled_write_ln(read_mode_icon(keymap_config.swap_lalt_lgui), false);
    //oled_write_ln(read_host_led_state(), false);
    //oled_write_ln(read_timelog(), false);
  } else {
    oled_write(read_logo(), false);
  }
    return false;
}
#endif // OLED_ENABLE

bool process_record_user(uint16_t keycode, keyrecord_t *record) {
  if (record->event.pressed) {
#ifdef OLED_ENABLE
    set_keylog(keycode, record);
#endif
    // set_timelog();
  }
  return true;
}
