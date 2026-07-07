"""Tests for domain-to-control-ID resolution in the evaluation agent."""

from unittest import mock

from src.agent.run import resolve_control_ids


def test_resolve_control_ids_maps_domain_to_section_controls() -> None:
    framework_json = [
        (
            "1_Data_Governance",
            {"controls": [{"id": "DG.1.1"}, {"id": "DG.1.2"}]},
        ),
        (
            "2_Data_Catalog",
            {"controls": [{"id": "DC.1.1"}]},
        ),
    ]
    with mock.patch(
        "src.agent.run.list_framework_jsons",
        return_value=framework_json,
    ):
        resolved = resolve_control_ids(
            "NDI",
            ["1_Data_Governance", "2_Data_Catalog", "unknown_domain"],
        )

    assert resolved == ["DG.1.1,DG.1.2", "DC.1.1", "unknown_domain"]
