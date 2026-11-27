// Layer report: tells a host app which layers are active.
// Each change goes out on the QMK console (HID usage page 0xFF31) as one text line:
//   "LAYER <highest> <state as 8 hex digits>\n"   e.g. "LAYER 2 00000006"
// The console is its own USB interface, so Vial, VIA and the raw HID scripts never see it.
// Use: add layer_report.c to SRC, set CONSOLE_ENABLE = yes, and call layer_report_task()
// from housekeeping_task_user().
#pragma once
#include "quantum.h"

void layer_report_task(void);
// Sends one report. Weak, so tests can capture reports instead.
void layer_report_emit(uint8_t highest, layer_state_t state);
