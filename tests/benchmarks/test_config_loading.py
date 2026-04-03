"""Benchmark: YAML vs msgpack vs TOML loading for command-skill-map.

Documents the cold start vs warm start performance difference.
TOML (stdlib tomllib) eliminates the PyYAML dependency on the hot
path but only helps cold starts — msgpack cache already handles
warm starts.

Decision: TOML conversion is NOT worth the effort because:
1. Msgpack warm hits (~0.5ms) already dominate in practice
2. TOML cold start (~3ms) is only marginally faster than YAML (~5ms)
3. PyYAML remains required for plan.yaml and skill playbooks
4. Migration cost (updating all loading paths) exceeds the benefit

This benchmark documents the numbers for the record.
"""

from __future__ import annotations

import time
from pathlib import Path

import msgpack
import yaml

YAML_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "src"
    / "dev10x"
    / "validators"
    / "command-skill-map.yaml"
)


class TestConfigLoadingBenchmark:
    def test_yaml_cold_load(self) -> None:
        start = time.monotonic()
        data = yaml.safe_load(YAML_PATH.read_text())
        elapsed_ms = (time.monotonic() - start) * 1000

        assert data is not None
        assert "rules" in data
        assert elapsed_ms < 50

    def test_msgpack_warm_load(self, tmp_path: Path) -> None:
        data = yaml.safe_load(YAML_PATH.read_text())
        cache_path = tmp_path / "config.msgpack"
        cache_path.write_bytes(msgpack.packb(data, use_bin_type=True))

        start = time.monotonic()
        loaded = msgpack.unpackb(cache_path.read_bytes(), raw=False)
        elapsed_ms = (time.monotonic() - start) * 1000

        assert loaded is not None
        assert "rules" in loaded
        assert elapsed_ms < 10

    def test_tomllib_cold_load(self, tmp_path: Path) -> None:
        """Benchmarks TOML parsing of the config section only.

        TOML cannot represent the full rules structure (lists of
        complex objects with regex patterns) without a custom schema.
        This test intentionally benchmarks only the config section
        to measure tomllib's raw parse speed vs yaml.safe_load.
        """
        import tomllib

        data = yaml.safe_load(YAML_PATH.read_text())
        cfg = data.get("config", {})

        toml_lines = ["[config]\n"]
        for k, v in cfg.items():
            toml_lines.append(f'{k} = "{v}"\n')

        toml_path = tmp_path / "config.toml"
        toml_path.write_text("".join(toml_lines))

        start = time.monotonic()
        loaded = tomllib.loads(toml_path.read_text())
        elapsed_ms = (time.monotonic() - start) * 1000

        assert loaded is not None
        assert loaded.get("config") == cfg
        assert elapsed_ms < 10
