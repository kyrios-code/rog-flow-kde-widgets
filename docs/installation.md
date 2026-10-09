# Installation, updates, and recovery

## Before you start

Use a normal account on the intended Plasma 6 desktop. Do not use `sudo` for these commands. The installation is user-level, using `kpackagetool6` without a global/system-install flag.

Use Python 3.12+ and Make for building and testing. The System helper requires Python 3.12+, and the installer checks this before System/all installation. Installation requires `kpackagetool6`. Running widgets additionally requires the Plasma/Qt/Kirigami modules described in [compatibility](compatibility.md); hardware features need a working `z13ctl` separately installed and available in the Plasma session's `PATH`.

The installer does not install dependencies, change privilege rules, configure hardware, or restart Plasma. A warning about missing `z13ctl` does not prevent package installation, but the dependent features will not work.

Read [configuration](configuration.md#actions-and-their-effects) before using Control or Gaming actions: they can change power profiles, lighting, or the desktop session.

## Build from source

```sh
git clone https://github.com/jsmola01/rog-flow-kde-widgets.git
cd rog-flow-kde-widgets
make test
make build
```

Repository access is required because this is a private repository. Builds use Python's standard library; no Python package installation is necessary.

Generated outputs are:

```text
dist/rog-system-1.3.0.plasmoid
dist/rog-control-1.2.0.plasmoid
dist/rog-gaming-1.0.0.plasmoid
```

Each is a ZIP-format Plasma package with `metadata.json` at its root, widget QML/configuration/images, its bundled helper in `contents/scripts/`, license/notice material, and no dependency on another installed widget.

Build only one with `make build-system`, `make build-control`, or `make build-gaming`. `make clean` removes `dist/`; it does not uninstall anything or delete retained baselines.

### Validation options

```sh
make validate
make test
```

`make test` first runs validation, then the unittest suite. Tests exercise source/package properties and mocked operations; they do not install into your real home directory or perform hardware actions. The exact JavaScript helper-path quoting test needs Node.js and reports a skip if it is absent.

Local validation skips Qt syntax parsing if `qmlformat` is unavailable. To require it:

```sh
python3 tools/validate.py --require-qml
```

If Qt 6's executable is not on `PATH`, set `QMLFORMAT` to its actual installed location. For example, the CI environment uses:

```sh
QMLFORMAT=/usr/lib/qt6/bin/qmlformat python3 tools/validate.py --require-qml
```

That example path is distribution-specific. Syntax validation does not load the widgets inside Plasma. Three expected failures record inherited Gaming bugs in profile confirmation, recent-game parsing, and controller filtering; they are known open issues, not repaired behavior.

## Install or update

```sh
make install
```

Or choose one:

```sh
make install-system
make install-control
make install-gaming
```

Each target builds its selected package(s) first. The installer reads the plugin ID and version from metadata and invokes `kpackagetool6 --type Plasma/Applet` with `--install` for a new package or `--upgrade` for an existing user-level package. The original plugin IDs and versions are retained, including when replacing an earlier installation from one of the supplied ZIPs.

The normal installation roots are:

```text
${XDG_DATA_HOME:-$HOME/.local/share}/plasma/plasmoids/io.rog.systemwidget
${XDG_DATA_HOME:-$HOME/.local/share}/plasma/plasmoids/io.rog.controlhud
${XDG_DATA_HOME:-$HOME/.local/share}/plasma/plasmoids/io.rog.gaminghud
```

Use the same `XDG_DATA_HOME` as your desktop session; directing installation elsewhere can make the widget invisible to Plasma.

After installation, use Plasma's Edit Mode → Add Widgets and search for the widget's name. An existing loaded instance may keep old QML until reloaded. Save work before choosing to restart Plasma or sign out. The installer does neither automatically.

### Standalone package import

You can also import a generated `.plasmoid` with Plasma's local-widget installation UI. Each artifact contains its helper and shared assets. The monorepo install targets are recommended for updates because they implement the backup/recovery behavior below; a direct GUI or `kpackagetool6` import bypasses that wrapper.

Do not install `widgets/rog-*/package` directly from the checkout: it omits helper files that the build injects, and it bypasses the shared-asset overlay and bundled notices. Do not follow `bash install.sh` in the historical per-widget READMEs; those instructions refer to the original archive layout.

## Backups and failed updates

Before updating an existing user package, the installer copies its directory to:

```text
${XDG_DATA_HOME:-$HOME/.local/share}/rog-flow-widget-backups/<plugin-ID>/<UTC timestamp>-<PID>
```

It prints the exact backup path. Keep that output. The backup covers the installed package directory; it is not a backup of the whole desktop layout, Plasma configuration, hardware state, or unrelated files.

If the `kpackagetool6` update fails, the installer attempts to restore that backup. An incomplete replacement, when present, is moved to a sibling path ending in `-failed` for inspection. The installer exits with an error. Filesystem or permission failures can still prevent restoration, so check the reported outcome and the installed directory instead of assuming success.

An all-widget installation is sequential, not an atomic transaction: widgets already installed successfully are not rolled back if a later widget fails.

For a later manual rollback, first stop/reload the affected widget in a controlled way, confirm the exact plugin ID and backup directory, and preserve the current package before restoring the known-good directory. Avoid deleting all Plasma settings as a repair step. Reverting to a package from the old ZIP may also reintroduce its dependency on an original `~/.local/bin` helper.

## Old standalone helpers

Prior archive installers could create:

```text
~/.local/bin/rog-z13-telemetry
~/.local/bin/rog-control-helper
~/.local/bin/rog-gaming-helper
```

New packages do not use them. Installation and removal leave them untouched because an older package or retained backup may still need them. Their existence does not control which helper the migrated widget runs.

## Removal

Remove a selected user-level package with:

```sh
make uninstall-system
make uninstall-control
make uninstall-gaming
```

`make uninstall` removes all three sequentially using `kpackagetool6`, skipping packages not installed for the current user. Remove any affected widget instances from your desktop as appropriate. The wrapper does not purge settings, old standalone helpers, or retained backups. It does not reset hardware settings or switch sessions.
