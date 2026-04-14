"""Tests for the ensure-scripts feature of update_paths module."""

import json
from pathlib import Path

import pytest

from dev10x.skills.permission import update_paths


class TestScanPluginScripts:
    @pytest.fixture()
    def plugin_root(self, tmp_path: Path) -> Path:
        root = tmp_path / "plugin"
        (root / "bin").mkdir(parents=True)
        (root / "bin" / "mktmp.sh").touch()
        (root / "bin" / "release.sh").touch()
        (root / "hooks" / "scripts").mkdir(parents=True)
        (root / "hooks" / "scripts" / "validate-bash-command.py").touch()
        (root / "skills" / "gh-context" / "scripts").mkdir(parents=True)
        (root / "skills" / "gh-context" / "scripts" / "detect-tracker.sh").touch()
        (root / "skills" / "gh-context" / "scripts" / "gh-pr-detect.sh").touch()
        return root

    def test_finds_bin_scripts(self, plugin_root: Path) -> None:
        result = update_paths.scan_plugin_scripts(plugin_root)

        names = [s.name for s in result]
        assert "mktmp.sh" in names
        assert "release.sh" in names

    def test_finds_hook_scripts(self, plugin_root: Path) -> None:
        result = update_paths.scan_plugin_scripts(plugin_root)

        names = [s.name for s in result]
        assert "validate-bash-command.py" in names

    def test_finds_skill_scripts(self, plugin_root: Path) -> None:
        result = update_paths.scan_plugin_scripts(plugin_root)

        names = [s.name for s in result]
        assert "detect-tracker.sh" in names
        assert "gh-pr-detect.sh" in names

    def test_returns_sorted_unique_paths(self, plugin_root: Path) -> None:
        result = update_paths.scan_plugin_scripts(plugin_root)

        assert result == sorted(set(result))

    def test_returns_empty_for_empty_plugin(self, tmp_path: Path) -> None:
        result = update_paths.scan_plugin_scripts(tmp_path)

        assert result == []


class TestBuildScriptAllowRules:
    def test_builds_bash_allow_rules(self, tmp_path: Path) -> None:
        plugin_root = tmp_path / "plugin"
        (plugin_root / "bin").mkdir(parents=True)
        script = plugin_root / "bin" / "mktmp.sh"
        script.touch()

        rules = update_paths.build_script_allow_rules(
            [script],
            plugin_root=plugin_root,
        )

        assert rules == [f"Bash({plugin_root}/bin/mktmp.sh:*)"]


class TestVerifyScriptCoverage:
    @pytest.fixture()
    def settings_file(self, tmp_path: Path) -> Path:
        return tmp_path / "settings.local.json"

    def test_detects_missing_scripts(self, settings_file: Path) -> None:
        settings_file.write_text(json.dumps({"permissions": {"allow": ["Bash(git log:*)"]}}))

        _covered, missing = update_paths.verify_script_coverage(
            settings_path=settings_file,
            expected_rules=["Bash(/cache/0.58.0/bin/mktmp.sh:*)"],
        )

        assert missing == ["Bash(/cache/0.58.0/bin/mktmp.sh:*)"]

    def test_detects_covered_by_exact_match(self, settings_file: Path) -> None:
        rule = "Bash(/cache/0.58.0/bin/mktmp.sh:*)"
        settings_file.write_text(json.dumps({"permissions": {"allow": [rule]}}))

        covered, missing = update_paths.verify_script_coverage(
            settings_path=settings_file,
            expected_rules=[rule],
        )

        assert covered == [rule]
        assert missing == []

    def test_detects_covered_by_script_name_match(self, settings_file: Path) -> None:
        settings_file.write_text(
            json.dumps({"permissions": {"allow": ["Bash(/old/path/bin/mktmp.sh:*)"]}})
        )

        covered, _missing = update_paths.verify_script_coverage(
            settings_path=settings_file,
            expected_rules=["Bash(/new/path/bin/mktmp.sh:*)"],
        )

        assert len(covered) == 1

    def test_no_false_positive_on_substring_match(self, settings_file: Path) -> None:
        settings_file.write_text(
            json.dumps({"permissions": {"allow": ["Bash(/path/test-utils.sh:*)"]}})
        )

        _covered, missing = update_paths.verify_script_coverage(
            settings_path=settings_file,
            expected_rules=["Bash(/cache/bin/test.sh:*)"],
        )

        assert len(missing) == 1

    def test_handles_invalid_json(self, settings_file: Path) -> None:
        settings_file.write_text("{invalid}")

        _covered, missing = update_paths.verify_script_coverage(
            settings_path=settings_file,
            expected_rules=["Bash(/cache/bin/mktmp.sh:*)"],
        )

        assert len(missing) == 1

    def test_handles_empty_allow_list(self, settings_file: Path) -> None:
        settings_file.write_text(json.dumps({"permissions": {"allow": []}}))

        _covered, missing = update_paths.verify_script_coverage(
            settings_path=settings_file,
            expected_rules=["Bash(/cache/bin/mktmp.sh:*)"],
        )

        assert len(missing) == 1


class TestEnsureScriptRules:
    @pytest.fixture()
    def settings_file(self, tmp_path: Path) -> Path:
        path = tmp_path / "settings.local.json"
        path.write_text(json.dumps({"permissions": {"allow": ["Bash(git log:*)"]}}))
        return path

    def test_adds_missing_rules(self, settings_file: Path) -> None:
        missing = ["Bash(/cache/bin/mktmp.sh:*)"]

        count, messages = update_paths.ensure_script_rules(
            settings_path=settings_file,
            missing_rules=missing,
        )

        assert count == 1
        data = json.loads(settings_file.read_text())
        assert "Bash(/cache/bin/mktmp.sh:*)" in data["permissions"]["allow"]
        assert "Bash(git log:*)" in data["permissions"]["allow"]

    def test_dry_run_does_not_write(self, settings_file: Path) -> None:
        original = settings_file.read_text()
        missing = ["Bash(/cache/bin/mktmp.sh:*)"]

        count, messages = update_paths.ensure_script_rules(
            settings_path=settings_file,
            missing_rules=missing,
            dry_run=True,
        )

        assert count == 1
        assert settings_file.read_text() == original

    def test_returns_zero_when_no_missing(self, settings_file: Path) -> None:
        count, messages = update_paths.ensure_script_rules(
            settings_path=settings_file,
            missing_rules=[],
        )

        assert count == 0
        assert messages == []
