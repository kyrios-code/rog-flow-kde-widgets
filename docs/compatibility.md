# Compatibility and dependency boundaries

## Supported target and verification status

The package metadata declares Plasma API minimum version `6.0` and package structure `Plasma/Applet`. The interface and hardware assumptions target a Linux ROG Flow Z13 environment using `z13ctl`.

No real Plasma session or ROG hardware was available for this migration. The baseline is not a claim of compatibility with every Z13 model, GPU, distribution, kernel, `z13ctl` release, or display server. In particular, labels such as `Radeon 8060S` and `32 GiB` are hard-coded baseline values.

| Area | Requirement or limitation |
| --- | --- |
| Repository workflow | Python 3.12+ standard library and Make; no widget runtime or hardware required to package sources |
| Installation | `kpackagetool6`, running as the target desktop user |
| Desktop | Plasma 6 with Qt Quick, Qt Quick Controls, Qt Quick Layouts, and the KDE modules used by the QML |
| KDE imports | `org.kde.plasma.plasmoid`, `org.kde.plasma.core`, `org.kde.plasma.plasma5support`; Kirigami for the System UI and settings pages |
| Helper execution | `python3` visible to the Plasma session; System requires Python 3.12+; executable DataSource support |
| Hardware integration | Working, separately installed `z13ctl` on the Plasma session's `PATH`, with existing permissions to perform requested operations |
| System telemetry | Linux `/proc` and `/sys`; utilities `ip`, `df`, `free`, and `ps` for their respective readings |
| Fonts | Optional installed `Bulky Pixels` and `Noto Sans`; fallback fonts can change geometry |
| Live runtime tests | Required separately; no result is implied by package or syntax checks |

There is no vendored `z13ctl`, driver, privileged daemon, policy rule, font, or session manager. The installer does not configure any of them. Plasma 5 and non-Linux systems are outside the declared target.

The preserved System helper contains f-string expressions that require Python 3.12's syntax. Use Python 3.12+ for all repository tests and the System runtime. The installer rejects System/all installation with an older `python3`. Control and Gaming may run on older Python versions, but this migration validates them on Python 3.12 and does not establish a lower supported version.

## `z13ctl` contract

The supplied helpers parse human-readable CLI output with regular expressions. They do not negotiate an API version or use a documented structured-output contract in this baseline. A working command in a terminal does not alone prove that its text matches these parsers.

- System reads `status` and `undervolt --get`.
- Control reads `status`, `autoswitch --get`, and `profile --list`; user actions call `profile --set` or `apply`.
- Gaming reads `profile --list` and `profile --get`; launching can call `profile --set`.

No exact `z13ctl` version compatibility matrix is established. Capture the actual version and sanitized command output when investigating failures. The helpers run with the desktop user's environment and do not add `sudo`.

Without `z13ctl`, System can still show some generic Linux metrics, Control cannot supply its core function, and Gaming can still read Steam/Bluetooth information but cannot provide a working profile-based Gaming Mode launch.

## Gaming integrations

### Steam data

Steam is optional for the rest of the widget package. The helper searches these local roots:

```text
~/.local/share/Steam
~/.steam/steam
~/.var/app/com.valvesoftware.Steam/.local/share/Steam
```

It reads `config/libraryfolders.vdf` or `steamapps/libraryfolders.vdf`, follows listed library paths, and looks for `steamapps/appmanifest_*.acf`. Recent-game information comes from `userdata/*/config/localconfig.vdf`; cover art comes from `appcache/librarycache` if available. This is local file inspection, not Steam account authentication or a Steam Web API integration.

Flatpak's default Steam data location is recognized, but sandbox/session-launch compatibility is not established. Additional/nonstandard Steam roots have no configuration UI in this baseline. Recent-game parsing has a known limitation documented in [troubleshooting](troubleshooting.md).

### Bluetooth controllers

BlueZ's `bluetoothctl` is optional. Without it, the controller list is empty. The helper reads connected devices and their information; it does not pair devices or manage Bluetooth power. Battery percentages are shown only if present in the parsed output, otherwise the UI displays a dash.

Controller detection is heuristic and can accept non-controller HID devices. USB-only controllers are not enumerated by this implementation.

### Gamescope session

Gaming Mode launch requires an already working distribution/session integration providing `steamos-session-select gamescope`, as well as `z13ctl`. Having a standalone `gamescope` binary is insufficient for this launch path. The repository does not install, configure, or validate a Gamescope session automatically.

If `steamos-session-select` is absent, the helper reports that condition before applying a profile. Other later failures can occur after a profile change. The launch action is not a general Steam executable launcher.

## Source/package checks versus runtime validation

Python, XML, JSON, SVG, archive, checksum, and mocked helper checks can verify important properties without running a desktop. Qt 6 `qmlformat` parsing can check QML syntax when that tool is available, but it does not prove that Plasma-specific imports resolve, bindings work, windows render, or hardware responds correctly.

The available local `qmllint` wrapper had no usable Qt executable during migration; local Qt parsing was therefore unavailable. CI is configured to provide Qt 6 syntax validation. Check the actual CI result for the commit under review before calling that stage passed.

Real-world verification should record distribution, Plasma/Qt versions, Wayland or X11, display scale, kernel, model/GPU, `z13ctl` version, and optional Steam/BlueZ/session integration versions. Keep screenshots and logs from those runs separate from unverified design assumptions.
