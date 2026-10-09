# Troubleshooting

This baseline preserves existing widget behavior. Diagnose package/environment problems separately from the inherited issues below, and keep a known-good installation until the target desktop has been checked.

## Build or validation fails

- Run commands from the repository root with Python 3.12+ and Make available. Older Python cannot parse the preserved System helper's f-string expressions.
- Use `make validate` to distinguish malformed Python/JSON/XML/SVG/shell or package metadata from runtime issues.
- Check `(cd baselines && sha256sum -c SHA256SUMS)` if retained input checksums differ. Do not replace the checksum manifest merely to hide an unexpected input change.
- If `--require-qml` fails because `qmlformat` is missing, supply a working Qt 6 installation and its actual `QMLFORMAT` path. A command wrapper without its Qt executable is insufficient.
- A Qt parser pass does not establish that Plasma-specific modules are installed. Node.js is needed only for the exact JavaScript quoting regression test, not for the widgets themselves.

## Widget does not appear or load

Confirm that installation used the intended desktop user and data directory:

```sh
command -v kpackagetool6
kpackagetool6 --type Plasma/Applet --list
```

Look for `io.rog.systemwidget`, `io.rog.controlhud`, or `io.rog.gaminghud`. Check the installer output for an error or restore operation.

Build and install the generated `.plasmoid`, not the raw source `package/` directory. The source directory alone lacks bundled helpers and bypasses the shared-asset overlay. Confirm Plasma 6, Kirigami, Qt Quick Controls, and `org.kde.plasma.plasma5support` are available on the target system.

If a previously loaded widget still shows old QML, reload the instance or restart the desktop session when convenient. No automatic Plasma restart is part of installation. On desktops using the relevant systemd user service, its recent log can help:

```sh
journalctl --user -u plasma-plasmashell.service -b --no-pager -n 150
```

That unit may not exist on every distribution. Use the distribution's session logging if it does not. Sanitize usernames, paths, network/device identifiers, and Steam data before sharing logs outside the private review.

## Missing telemetry, profiles, or actions

Check read-only prerequisites from the target desktop account:

```sh
command -v python3
command -v z13ctl
z13ctl status
z13ctl profile --list
z13ctl profile --get
```

The widgets inherit Plasma's environment, which can differ from an interactive shell's `PATH`. Do not repair a missing helper by copying a script to `~/.local/bin`: the generated package resolves its own bundled file. Check that `contents/scripts/` exists in the installed package instead.

`z13ctl` failures can reflect missing software, permissions, unsupported hardware, timeouts, or output that no longer matches the baseline parsers. Preserve the exact error and relevant sanitized output. The repository does not add privilege rules or run `sudo` on your behalf.

If all firmware profiles are missing from Control's list, check Configure → Profile visibility: Quiet, Balanced, and Performance are hidden by default. The literal manual-state name `custom` is deliberately filtered from selectable profiles.

Missing generic System values can also come from unavailable Linux `/proc`/`/sys` entries or `ip`, `df`, `free`, or `ps`. A dash is often a missing reading. The hard-coded BIOS/GPU labels should not be interpreted as successful detection.

## Steam information or controller slots are empty

- Confirm Steam data is in one of the [recognized roots](compatibility.md#steam-data) and the desktop user can read its app manifests and local configuration.
- Only installed games discovered from local manifests participate in the recent list. Missing cached artwork can produce a placeholder.
- Check `command -v bluetoothctl` and `bluetoothctl devices Connected`. This implementation does not enumerate USB-only devices or perform pairing.
- A controller battery dash means no parsed value was available; it does not mean a measured 0%.
- The widget polls Gaming information every 30 seconds, so external changes may not appear immediately.

## Gaming Mode does not start

Check `command -v steamos-session-select` and whether your distribution already supports a working Gamescope session. A `gamescope` executable alone does not satisfy this integration.

The helper checks for the session selector before changing the profile. Later failures may leave the requested profile applied, and no rollback is implemented. A “Switching to Gaming Mode” message confirms only that the process was spawned; it does not verify the new session's success.

Save work before retrying a launch. Avoid repeated launch attempts merely to diagnose installation. Inspect the profile and relevant session logs first. The baseline uses an imperfect substring test for active-profile confirmation, described below.

## Inherited issues preserved for review

These are source-inspection findings, not newly introduced migration features or claims of live reproduction. Behavioral fixes are deferred so the packaging baseline remains reviewable.

| Area | Baseline limitation | Review direction |
| --- | --- | --- |
| System BIOS VRAM | `widgets/rog-system/scripts/telemetry.py` sets `biosVram='32 GiB'` unconditionally | Discover a trustworthy value or label it unknown/configured; do not present a constant as telemetry |
| System GPU label | `widgets/rog-system/package/contents/ui/HyrulePanel.qml` labels the GPU `Radeon 8060S` | Make device identity accurate for the actual hardware |
| System sampling caches | The helper writes predictable `/tmp/hyrule-z13-net-<uid>.json` and `/tmp/hyrule-z13-cpu-<uid>.json` files; instances share them | Review safe file handling, cache lifetime, permissions, and multi-instance sampling interference |
| Gaming recency | `recent()` searches up to 1,400 characters beyond an app block opening without parsing its closing boundary | Parse nested VDF structure so a neighboring app's `LastPlayed` cannot be borrowed |
| Gaming controller filtering | `controllers()` accepts a matching name or any `Human Interface Device` detail | Distinguish game controllers from keyboards and other HID devices |
| Gaming profile confirmation | `launch()` checks `mode in active.stdout`; `quiet` can therefore match `quiet-extra` | Compare the parsed active profile exactly; a regression test currently records the desired behavior as an expected failure |
| Gaming appearance previews | Its `ConfigAppearance.qml` refers to `fan-0.svg` through `fan-3.svg`, which are absent from the Gaming baseline assets | Confirm missing previews in Plasma and decide whether to supply icons or change that preview |
| Gaming settings | `showInstalled` is declared but unused by the current QML | Decide the intended option behavior separately from migration |
| Error visibility | Some UI modes may conceal useful feedback; stdout-less failures can leave stale content or poor feedback | Exercise missing executables, timeout, malformed output, compact layouts, and recovery paths in real Plasma |
| Text parsing and polling | Helpers parse human-readable CLI/VDF output and run several subprocesses per refresh | Add representative fixtures and measure behavior under slow/failing tools before refactoring |

The frameless Gaming selector also needs live Wayland/X11 testing for focus, positioning, Escape/close, repeated opening, long profile lists, scaling, and keeping the HUD's own size stable. It is not established that a syntax-valid QML window behaves correctly under the compositor.

## Information to include in a review report

Record the repository commit, widget ID/version, built artifact name, distribution, Plasma/Qt versions, Wayland or X11, display scale, model/GPU, kernel, `z13ctl` version, and the shortest reproducible steps. State whether the problem also occurs with the retained original archive. Separate static observations, mocked-test evidence, and real-hardware observations.
