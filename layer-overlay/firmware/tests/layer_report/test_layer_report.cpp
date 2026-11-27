// Host tests for layer_report.c, run inside QMK's test framework (see ../../run-tests.sh).
#include "keyboard_report_util.hpp"
#include "keycode.h"
#include "test_common.hpp"
#include "action_tapping.h"
#include <utility>
#include <vector>

extern "C" {
#include "layer_report.h"
}

using testing::_;
using Report = std::pair<uint8_t, uint32_t>;
static std::vector<Report> reports;

extern "C" void layer_report_emit(uint8_t highest, layer_state_t state) { reports.push_back({highest, (uint32_t)state}); }
extern "C" void housekeeping_task_user(void) { layer_report_task(); }

class LayerReport : public TestFixture {
   public:
    void SetUp() override {
        TestFixture::SetUp();
        reports.clear();
    }
    // Call after creating the TestDriver: the first scan reports the starting layer.
    void settle() {
        run_one_scan_loop();
        reports.clear();
    }
};

TEST_F(LayerReport, IdleScansReportNothingNew) {
    TestDriver driver;
    settle();
    EXPECT_NO_REPORT(driver);
    idle_for(500);
    VERIFY_AND_CLEAR(driver);
    EXPECT_TRUE(reports.empty());
}

TEST_F(LayerReport, HeldLayerTapReportsLayerThenBase) {
    TestDriver driver;
    auto lt_key = KeymapKey(0, 0, 0, LT(1, KC_SPC));
    set_keymap({lt_key, KeymapKey(1, 0, 0, KC_TRNS)});
    settle();

    EXPECT_NO_REPORT(driver);
    lt_key.press();
    idle_for(TAPPING_TERM + 1);
    VERIFY_AND_CLEAR(driver);
    ASSERT_EQ(reports, std::vector<Report>({{1, 0x2}}));

    EXPECT_EMPTY_REPORT(driver).Times(testing::AnyNumber());
    lt_key.release();
    run_one_scan_loop();
    VERIFY_AND_CLEAR(driver);
    ASSERT_EQ(reports, std::vector<Report>({{1, 0x2}, {0, 0x0}}));
}

TEST_F(LayerReport, TappedLayerTapReportsNothing) {
    TestDriver driver;
    auto lt_key = KeymapKey(0, 0, 0, LT(1, KC_SPC));
    set_keymap({lt_key});
    settle();

    EXPECT_REPORT(driver, (KC_SPC));
    EXPECT_EMPTY_REPORT(driver);
    tap_key(lt_key);
    idle_for(50);
    VERIFY_AND_CLEAR(driver);
    ASSERT_TRUE(reports.empty());
}

TEST_F(LayerReport, StackedLayersReportHighestAndFullState) {
    // The master keymap's two-Space trick: Nav (1) held, then Fn (2) on top.
    TestDriver driver;
    auto nav = KeymapKey(0, 0, 0, MO(1));
    auto fn  = KeymapKey(1, 1, 0, MO(2));
    set_keymap({nav, KeymapKey(0, 1, 0, KC_A), fn, KeymapKey(2, 0, 0, KC_TRNS), KeymapKey(2, 1, 0, KC_TRNS)});
    settle();

    EXPECT_NO_REPORT(driver);
    nav.press();
    run_one_scan_loop();
    fn.press();
    run_one_scan_loop();
    fn.release();
    run_one_scan_loop();
    nav.release();
    run_one_scan_loop();
    VERIFY_AND_CLEAR(driver);
    ASSERT_EQ(reports, std::vector<Report>({{1, 0x2}, {2, 0x6}, {1, 0x2}, {0, 0x0}}));
}

TEST_F(LayerReport, HeldLayerSendsOnlyOnce) {
    TestDriver driver;
    auto nav = KeymapKey(0, 0, 0, MO(1));
    set_keymap({nav});
    settle();

    EXPECT_NO_REPORT(driver);
    nav.press();
    idle_for(3000);
    VERIFY_AND_CLEAR(driver);
    ASSERT_EQ(reports, std::vector<Report>({{1, 0x2}}));
    nav.release();
    run_one_scan_loop();
}
