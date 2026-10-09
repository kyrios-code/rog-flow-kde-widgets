# Changelog

## Migration baseline — 2026-10-09

This entry describes repository and packaging changes. It does not announce a new widget feature release. Metadata versions remain System `1.3.0`, Control `1.2.0`, and Gaming `1.0.0`.

### Added

- One monorepo with three independently buildable and installable Plasma packages.
- Root Make targets for all-widget and per-widget builds and user-level installation.
- Original input ZIPs in `baselines/` with a SHA-256 checksum manifest.
- Source/package validation, regression tests, and a CI workflow.
- Installation, configuration, compatibility, troubleshooting, and review-handoff documentation.
- Consolidated third-party notices alongside preserved original attribution files.

### Changed for packaging

- Python helpers now live in each widget's `scripts/` source directory and are bundled into `contents/scripts/` in the built package.
- QML resolves its bundled helper at runtime with `Qt.resolvedUrl` and constructs a shell-quoted `python3` invocation instead of relying on an installer-replaced absolute helper path in `~/.local/bin`.
- Byte-identical common icons have canonical build-time copies under `shared/icons/`, listed in `shared/assets.json`, and overlaid into each standalone package during its build. Original widget-local copies remain for comparison.
- A common `kpackagetool6`-based user installer replaces the original archive installation workflow and backs up existing user packages before updates.
- Build output is generated under `dist/` and ignored by Git.

### Preserved

- Plugin IDs, metadata versions, configuration keys/defaults, widget layout, theme palettes, and helper behavior.
- The supplied per-widget READMEs and attribution notices, including their historical wording.
- Original archives unchanged for later comparison.
- Existing profile parsing, polling, Steam library handling, Bluetooth filtering, and hardware-control semantics.

### Deferred

- Inherited behavior bugs and hard-coded hardware labels; see [troubleshooting](docs/troubleshooting.md).
- Shared helper/parser and theme extraction.
- Live Plasma 6 rendering, Wayland/X11 behavior, real installation/update/recovery, and ROG hardware tests.

Automated checks and CI are verification mechanisms, not evidence of successful hardware testing. Consult the actual run results for the commit under review; this changelog makes no test-pass claim.
