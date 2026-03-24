"""Tests for constants consistency."""
from src.constants import (
    CHARACTER_STATS,
    STAT_DISPLAY,
    BODY_PART_NAMES,
    INVENTORY_SLOTS,
    SLOT_DISPLAY,
    TYPECODE_NAMES,
    LIMB_STATUS,
)


class TestConstantsConsistency:
    def test_every_stat_has_display_name(self):
        missing = [s for s in CHARACTER_STATS if s not in STAT_DISPLAY]
        assert missing == [], f"Stats without display names: {missing}"

    def test_no_extra_display_names(self):
        extra = [s for s in STAT_DISPLAY if s not in CHARACTER_STATS]
        assert extra == [], f"Display names without stats: {extra}"

    def test_body_parts_cover_0_to_6(self):
        assert set(BODY_PART_NAMES.keys()) == set(range(7))

    def test_inventory_slots_have_display_names(self):
        missing = [s for s in INVENTORY_SLOTS if s not in SLOT_DISPLAY]
        assert missing == [], f"Slots without display names: {missing}"

    def test_limb_status_values(self):
        assert 0 in LIMB_STATUS
        assert 1 in LIMB_STATUS
        assert 2 in LIMB_STATUS

    def test_typecode_names_not_empty(self):
        assert len(TYPECODE_NAMES) > 0
        # All values should be non-empty strings
        for tc, name in TYPECODE_NAMES.items():
            assert isinstance(tc, int)
            assert isinstance(name, str) and len(name) > 0
