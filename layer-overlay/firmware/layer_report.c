#include "layer_report.h"
#ifdef CONSOLE_ENABLE
#    include "print.h"
#endif

static layer_state_t last_sent;
static bool          sent_any;

__attribute__((weak)) void layer_report_emit(uint8_t highest, layer_state_t state) {
#ifdef CONSOLE_ENABLE
    uprintf("LAYER %u %08lX\n", highest, (unsigned long)state);
#endif
}

// Runs every scan from housekeeping, so it sends only when the state changes.
// Only the half on USB sends: it owns layer_state on a split board.
void layer_report_task(void) {
    if (!is_keyboard_master()) return;
    layer_state_t state = layer_state;
    if (sent_any && state == last_sent) return;
    last_sent = state;
    sent_any  = true;
    layer_report_emit(get_highest_layer(state), state);
}
