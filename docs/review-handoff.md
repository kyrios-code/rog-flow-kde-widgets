# Review handoff

## Goal and scope

Review this repository as a migration baseline for three existing widgets. The private destination is `jsmola01/rog-flow-kde-widgets`. A later conversation can review the baseline and propose focused fixes without first reconstructing three unrelated ZIP layouts.

This migration changes source organization, packaging, installation, validation, and documentation. It deliberately does not redesign the widgets, consolidate divergent helper behavior, repair inherited hardware/data bugs, or assert new device support.

Preserved identities:

| Widget | Plugin ID | Version |
| --- | --- | --- |
| System | `io.rog.systemwidget` | `1.3.0` |
| Control | `io.rog.controlhud` | `1.2.0` |
| Gaming | `io.rog.gaminghud` | `1.0.0` |

Use current metadata for versions. Historical per-widget README headings refer to older versions and remain unchanged as source evidence.

## Inputs and exact source mapping

All original archives are retained under `baselines/` and covered by `baselines/SHA256SUMS`:

| Retained archive | Original root | Current widget root |
| --- | --- | --- |
| `rog-system-widget-v13(1).zip` | `rog-system-widget-v13/` | `widgets/rog-system/` |
| `rog-control-hud-v12(1).zip` | `rog-control-hud-v12/` | `widgets/rog-control/` |
| `rog-gaming-hud-v10(1).zip` | `rog-gaming-hud-v10/` | `widgets/rog-gaming/` |

For each original root:

- `package/metadata.json` and `package/contents/config/` map to the same relative paths under the current widget root. IDs, versions, and configuration keys/defaults are preserved.
- `package/contents/ui/` maps to the same location. Each `main.qml` changes only helper-path resolution/invocation for standalone packaging; compare it directly against the original when reviewing this boundary.
- System's `telemetry.py` maps to `widgets/rog-system/scripts/telemetry.py`.
- Control's `rog-control-helper.py` maps to `widgets/rog-control/scripts/rog-control-helper.py`.
- Gaming's `rog-gaming-helper.py` maps to `widgets/rog-gaming/scripts/rog-gaming-helper.py`.
- Original `README.md`, `LOGO-ATTRIBUTION.txt` (System/Control), and `STEAM_LOGO_ATTRIBUTION.txt` (Gaming) are retained under their corresponding widget roots.
- Original `install.sh` remains inside each retained ZIP. `tools/install.sh` is the new common installation path; it is not a claimed byte-for-byte port of those scripts.
- Original `package/contents/images/` assets that are byte-identical across all three widgets also have canonical build-time copies in `shared/icons/`. Their exact names are listed in `shared/assets.json`. Original widget-local copies remain for straightforward comparison, and the builder overlays shared copies into each package's `contents/images/` directory.

The shared set comprises four numbered variants each of `bolt`, `gamepad`, `leaf`, `moon`, and `profile`, plus the four `rog-eye-{amber,cyan,emerald,purple}.svg` files. Themes and helpers have not been factored into shared executable code.

See [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md) for the exact asset notices, including ASUS ROG eye provenance and the Gaming `steam-symbol.svg` attribution to Font Awesome Free/Fonticons under CC BY 4.0. The original attribution files and Steam SVG's embedded notice remain authoritative source material to inspect. Font files and Steam game cover art are not redistributed by the build.

## Migration-only changes to inspect first

1. **Standalone package contents.** `tools/build.py` creates `dist/rog-system-1.3.0.plasmoid`, `dist/rog-control-1.2.0.plasmoid`, and `dist/rog-gaming-1.0.0.plasmoid`. Metadata belongs at archive root. The helper, all supplied shared/local assets, license, and notices must travel with each artifact. The original missing Gaming preview icons remain a documented issue. There must be no repository-relative runtime dependency or requirement to install another widget first.
2. **Runtime helper resolution.** The three QML entrypoints use `Qt.resolvedUrl` for `../scripts/<helper>.py`, decode the file URL, and shell-quote the path before passing a `python3` command through Plasma's executable DataSource. Check spaces, apostrophes, and shell metacharacters in installation paths. This migration quotes the helper path; it is not a wholesale redesign of action-command construction.
3. **Original behavior preservation.** Compare helper bytes, configuration, metadata, QML other than helper invocation, and image bytes with the retained archives. Investigate unexplained differences before merging a behavior refactor into this baseline.
4. **Installer failure boundaries.** Check user-only `kpackagetool6` calls, backup creation before update, failure preservation/restoration, same-version replacement, nondefault `XDG_DATA_HOME`, and first-install failure. All-widget installation is sequential. The wrapper must not perform a hardware action or restart Plasma.
5. **Tests that do not touch hardware.** The test loader extracts Control/Gaming declarations without executing their top-level command dispatch. Subprocess calls are mocked; install tests use a temporary home and fake `kpackagetool6`. Confirm no test accidentally calls a real profile setter or session selector.

## Verification layers and their limits

Use Python 3.12+ and run against the exact commit under review:

```sh
(cd baselines && sha256sum -c SHA256SUMS)
make test
make build
```

When Qt 6's syntax tool is available, also run:

```sh
python3 tools/validate.py --require-qml
```

Use `QMLFORMAT=/actual/path/to/qmlformat` if needed. `make test` permits a local Qt-tool skip; the CI workflow explicitly requires Qt 6 syntax parsing.

Coverage includes syntax/metadata/archive validation, retained baseline hashes, mocked profile parsing/action guards, Steam/controller fixtures, helper entrypoint failure behavior, deterministic repeat builds, bundled shared assets/helpers, shell quoting through the QML JavaScript expression when Node.js is available, and isolated installer backup/recovery behavior. Inspect the current tests for the precise cases. Expected failures document three known bugs: exact active-profile confirmation, bounded recent-game parsing, and excluding generic HID keyboards. They must not be counted as repaired behavior.

Migration verification recorded on 2026-10-09: 58 tests completed, with 55 passing and 3 intentional expected failures. All-widget and individual package builds passed, including repeated-build determinism and helper-byte checks. Source JSON/XML/SVG/Python/shell validation and the three original ZIP checksums passed. These results apply to the reviewed migration working tree; rerun for later changes and check the exact published commit's CI.

In the migration environment, the available `qmllint` wrapper had no usable Qt executable and `qmlformat` was unavailable, so local Qt syntax parsing was skipped. No CI result is recorded here yet. A CI `qmlformat` pass would establish syntax only; it would not establish Plasma import/type resolution or runtime correctness. A repository-wide whitespace check also flags one preserved trailing space in the original Control helper; new tooling/documentation whitespace checks were clean.

Not verified here:

- Real `kpackagetool6` installation, same-version upgrade, and restore in a Plasma desktop
- QML rendering, settings persistence, geometry, fonts, asset previews, or compositor behavior
- Real ROG telemetry, power profiles, RGB lighting, or AC/battery behavior
- Steam data variation, physical Bluetooth devices, or a real Gamescope session transition

## Priorities for the next review

### 1. Correctness and safety before visual polish

- Replace Gaming's substring profile confirmation with an exact parsed comparison; `quiet` currently matches `quiet-extra`. Plan a focused fix and update the expected-failure regression test.
- Review what happens when the profile changes successfully but the later confirmation/session-launch step fails. There is no rollback, and a detached process spawn is not session-success confirmation.
- Review predictable System `/tmp` cache files for safe file handling, error handling, and multiple-widget interference.
- Review command validation/quoting end to end. Helpers use argument-vector subprocess calls, while QML's executable DataSource still receives a command string.

### 2. Data that can mislead the user

- System `biosVram='32 GiB'` and the `Radeon 8060S` UI label are constants.
- Gaming `recent()` can read a neighboring app's `LastPlayed` because it scans a 1,400-character window instead of a bounded VDF block.
- Gaming controller filtering can accept a keyboard or other generic HID device.
- Human-readable `z13ctl` parsing has no established version compatibility matrix. Add real sanitized output fixtures before shared-parser extraction.

### 3. Real Plasma UX

- Test all themes, 0%/90% opacity, all layout modes, settings persistence, font fallbacks, and resizing/display scale.
- Check the Gaming appearance page's references to missing `fan-0.svg` through `fan-3.svg`.
- Exercise selector open/close/Escape, focus, repeated clicks, scrolling, active/hidden profiles, and compact-mode error visibility on Wayland and X11 where available.
- Test absent tools, timeouts, invalid/empty stdout, permission errors, stale metrics, and recovery without restarting the entire desktop.
- Confirm whether the unused Gaming `showInstalled` key should become a real option or remain for compatibility.

### 4. Refactor only after coverage

Shared helper parsing and theme palettes are explicitly deferred. Byte-identical assets are already shared at source level without making runtime packages interdependent. Consider deeper consolidation only after fixture coverage and real visual checks establish the behavior to preserve.

## Suggested handoff prompt for another conversation

> Review the private `jsmola01/rog-flow-kde-widgets` repository as a migration-only baseline. Start with `README.md`, `docs/review-handoff.md`, `THIRD_PARTY_NOTICES.md`, the retained original ZIPs/checksums, and the current commit's tests/CI. Confirm the source-to-package mapping, standalone helper/assets, preserved plugin IDs/versions, and installer backup/failure behavior. Separate migration regressions from documented inherited bugs. Report prioritized findings with file/line evidence and verification limits. Do not assume Plasma or ROG hardware behavior from mocked/static checks. Propose focused follow-up fixes rather than silently redesigning behavior or changing package identities.

Record findings with the exact commit, affected widget and file, original-versus-migrated evidence, actual test coverage, impact, and a narrowly scoped next step. Keep any real-device test captures free of unrelated personal information.
