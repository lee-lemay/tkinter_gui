"""Simple YAML configuration loader for application startup."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - runtime import error handled by caller
    yaml = None  # fallback when PyYAML is not installed


DEFAULT_CONFIG: Dict[str, Any] = {
    "ForceUpdate": False,
    "MetricMethod": "Haversine",
    "DistanceThreshold": 1000,
    "DatasetDirectory": None,
    "RecentDirectories": [],
}


class ConfigLoader:
    """Loads a YAML config file and provides access to values."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)

    def load(self, path: Path) -> Dict[str, Any]:
        """Load a YAML config from the given path. Returns defaults if missing."""
        config: Dict[str, Any] = DEFAULT_CONFIG.copy()
        try:
            if not path.exists():
                self.logger.warning(f"Config file not found at {path}. Using defaults.")
                return config

            if yaml is None:
                self.logger.warning(
                    "PyYAML is not installed. Skipping config load and using defaults."
                )
                return config

            with path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

            if not isinstance(data, dict):
                self.logger.warning("Config file did not contain a mapping. Using defaults.")
                return config

            # Merge known keys only
            for key in DEFAULT_CONFIG.keys():
                if key in data:
                    config[key] = data[key]

            # Normalize DatasetDirectory to Path if present
            if config.get("DatasetDirectory"):
                try:
                    config["DatasetDirectory"] = Path(config["DatasetDirectory"]).expanduser()
                except Exception:
                    self.logger.warning("Invalid DatasetDirectory in config. Ignoring.")
                    config["DatasetDirectory"] = None

            return config
        except Exception as exc:  # pragma: no cover - defensive
            self.logger.error(f"Failed to load config: {exc}")
            return config

    def save(self, path: Path, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save updates to the YAML config while preserving other keys.
        Returns the resulting config dict.
        """
        try:
            current = self.load(path)
            # Merge current + updates first
            to_save: Dict[str, Any] = {}
            to_save.update(current)
            to_save.update(updates)

            # Convert any Path objects (including those from 'current') to strings recursively
            def _serialize(val: Any) -> Any:
                if isinstance(val, Path):
                    return str(val)
                if isinstance(val, list):
                    return [_serialize(x) for x in val]
                if isinstance(val, dict):
                    return {k: _serialize(v) for k, v in val.items()}
                return val
            to_save = _serialize(to_save)

            # Ensure only known keys are persisted to keep file tidy
            ordered: Dict[str, Any] = {k: to_save.get(k, DEFAULT_CONFIG[k]) for k in DEFAULT_CONFIG.keys()}

            path.parent.mkdir(parents=True, exist_ok=True)
            import yaml as _yaml  # local import for save
            with path.open("w", encoding="utf-8") as f:
                _yaml.safe_dump(ordered, f, sort_keys=False)

            self.logger.debug(f"Saved configuration to {path}")
            # Return unified with normalized DatasetDirectory as Path
            result = self.load(path)
            return result
        except Exception as exc:
            self.logger.error(f"Failed to save config: {exc}")
            return self.load(path)
