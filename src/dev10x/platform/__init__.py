"""Platform registry — abstracts per-platform install paths for AI assistants.

Dev10x originally shipped for Claude Code only; Copilot CLI arrived as an
ad-hoc second target. This registry gives every supported platform the same
surface: a human-readable name, install path, config file, and optional
playbook override. Adding a new platform is a single catalog entry — no
per-user path editing, no symlinks (so Windows stays safe).
"""

from __future__ import annotations

from dev10x.platform.registry import PlatformConfig, Registry, known_platforms

__all__ = ["PlatformConfig", "Registry", "known_platforms"]
