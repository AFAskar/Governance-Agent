"""Tests for the mimic JSON builder used by the evaluation agent."""

import pytest

from src.agent.mimic_json import build_mimic_json


def test_build_mimic_json_maps_fields_to_control_ids() -> None:
    result = build_mimic_json(
        "NDI",
        [
            ("field_1", "DG.1.1,DG.1.2"),
            ("field_2", "DC.2.1"),
        ],
    )
    assert result == {
        "NDI": {
            "field_1": "DG.1.1,DG.1.2",
            "field_2": "DC.2.1",
        }
    }


def test_build_mimic_json_rejects_empty_input() -> None:
    with pytest.raises(ValueError, match="At least one"):
        build_mimic_json("NDI", [])
