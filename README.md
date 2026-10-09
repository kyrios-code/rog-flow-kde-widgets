# ROG Flow KDE Widgets

Three independently installable Plasma 6 widgets for a Linux ROG Flow Z13 setup. This repository brings the supplied widget archives into one maintainable baseline without redesigning their interfaces or changing their hardware behavior.

| Widget | Preserved plugin ID | Baseline version | Purpose |
| --- | --- | --- | --- |
| ROG System Widget | `io.rog.systemwidget` | `1.3.0` | CPU/GPU, memory, battery, storage, network, and `z13ctl` telemetry |
| ROG Control HUD | `io.rog.controlhud` | `1.2.0` | `z13ctl` power-profile selection and RGB lighting |
| ROG Gaming HUD | `io.rog.gaminghud` | `1.0.0` | Local Steam library, connected Bluetooth devices, and Gaming Mode launch |

**Status:** migration baseline, with inherited limitations documented for review. Live Plasma rendering, installation on a real desktop, and ROG hardware behavior have not been verified here. Passing source/package tests would not establish hardware compatibility. See [compatibility](docs/compatibility.md) and the [review handoff](docs/review-handoff.md).

## Build and install

Use Python 3.12+ and Make for the repository workflow. The System helper requires Python 3.12+. Installing needs a Plasma 6 desktop with `kpackagetool6`; the runtime also needs the Qt/KDE QML modules described in [installation](docs/installation.md).

```sh
git clone https://github.com/jsmola01/rog-flow-kde-widgets.git
cd rog-flow-kde-widgets
make test
make build
```

The repository is private, so cloning requires access. Generated `.plasmoid` packages are written to `dist/`, which is excluded from version control.

Install all three for your current user:

```sh
make install
```

Or build and install just one:

```sh
make build-system
make install-system
```

Replace `system` with `control` or `gaming` for the other widgets. Add a widget from Plasma's Edit Mode → Add Widgets after installation. Do not run the installer with `sudo`.

| Command | Action |
| --- | --- |
| `make build` | Build all three standalone packages |
| `make build-system`, `make build-control`, `make build-gaming` | Build one package |
| `make validate` | Validate sources, baseline checksums, and package layout |
| `make test` | Run the repository's automated checks |
| `make install` | Build/install or update all three user-level packages |
| `make install-system`, `make install-control`, `make install-gaming` | Build/install or update one user-level package |
| `make uninstall-system`, `make uninstall-control`, `make uninstall-gaming` | Remove one user-level package; `make uninstall` removes all three |
| `make clean` | Remove generated build output |

The installer backs up an existing user-level package before updating it. It does not change a power profile, apply lighting, switch desktop sessions, install system dependencies, or restart Plasma. The Control and Gaming widgets can perform those first three actions later when you use their controls; see [configuration](docs/configuration.md).

## Standalone packages

Each generated package contains its own Python helper under `contents/scripts/` and all supplied image assets. QML resolves the bundled helper with `Qt.resolvedUrl` and invokes `python3` with a shell-quoted path. No helper in `~/.local/bin` and no other installed ROG widget is required. The inherited missing Gaming theme-preview icons are documented in [troubleshooting](docs/troubleshooting.md).

`z13ctl` is an external runtime dependency discovered through the Plasma session's `PATH`; it is not bundled. Steam data, BlueZ's `bluetoothctl`, and an existing Gamescope session integration provide optional Gaming HUD features. The Gaming Mode action specifically needs `steamos-session-select`, not just the `gamescope` executable.

## Repository layout

```text
baselines/                   Original ZIP archives and SHA256SUMS
widgets/
  rog-system/
    package/                 Plasma package metadata, QML, configuration, local assets
    scripts/telemetry.py
  rog-control/
    package/
    scripts/rog-control-helper.py
  rog-gaming/
    package/
    scripts/rog-gaming-helper.py
shared/
  assets.json                Shared icon manifest
  icons/                     Byte-identical baseline assets, bundled at build time
  helpers/                   Notes on deferred helper consolidation
  themes/                    Notes on deferred theme consolidation
tools/                       Build, installation, and validation tooling
tests/                       Automated regression/package checks
docs/                        Installation, configuration, compatibility, review notes
screenshots/                 Guidance for future real-desktop captures
.github/workflows/           Automated source/package validation
dist/                        Generated packages; ignored by Git
```

Shared assets are a source-organization detail. The build overlays the canonical shared copies into each package; original widget-local copies remain for straightforward baseline comparison. Widget helpers and theme palettes remain widget-local so this migration does not silently unify different behaviors.

## Documentation and provenance

- [Installation and recovery](docs/installation.md)
- [Settings and runtime behavior](docs/configuration.md)
- [Dependencies and compatibility limits](docs/compatibility.md)
- [Troubleshooting and inherited issues](docs/troubleshooting.md)
- [Review handoff for the next conversation](docs/review-handoff.md)
- [Changelog](CHANGELOG.md)
- [Third-party notices](THIRD_PARTY_NOTICES.md)

The original ZIPs are retained in `baselines/`; verify their bytes with:

```sh
(cd baselines && sha256sum -c SHA256SUMS)
```

The small per-widget READMEs are preserved historical source material. Their displayed versions and `bash install.sh` instructions are stale. Use this root README, the current metadata versions above, and the `make` commands for this repository.

Project code is provided under [MIT](LICENSE). Third-party asset notices and trademark qualifications remain applicable; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). This project is not affiliated with ASUS or Valve.
