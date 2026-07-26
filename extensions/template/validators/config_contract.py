"""Pure in-memory validation for the example configuration contract."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def validate_config(data: Any) -> dict[str, Any]:
    """Return a stable status and blocker list for one config value."""

    blockers: list[dict[str, str]] = []
    feature = data.get("feature") if isinstance(data, Mapping) else None
    if not isinstance(feature, Mapping):
        blockers.append(
            {
                "code": "MY_EXTENSION_CONFIG_FEATURE_MISSING",
                "path": "feature",
            }
        )
    else:
        if not isinstance(feature.get("enabled"), bool):
            blockers.append(
                {
                    "code": "MY_EXTENSION_CONFIG_ENABLED_INVALID",
                    "path": "feature.enabled",
                }
            )
        if feature.get("report_mode") not in {"concise", "detailed"}:
            blockers.append(
                {
                    "code": "MY_EXTENSION_CONFIG_REPORT_MODE_INVALID",
                    "path": "feature.report_mode",
                }
            )

    return {
        "status": "BLOCKED" if blockers else "PASS",
        "blockers": blockers,
    }
