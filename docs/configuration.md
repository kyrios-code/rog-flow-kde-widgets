# Configuration and runtime behavior

Open each installed widget's Configure dialog through Plasma. Settings are independent per widget instance. No central configuration service is introduced by this migration, and existing configuration key names are preserved.

## Appearance

All three widgets use the same four baseline palettes:

| `themeIndex` | Theme | Accent | Icon color |
| --- | --- | --- | --- |
| `0` | Cyan Glass | `#50cfff` | Warm amber |
| `1` | Purple Nebula | `#b38cff` | Mint teal |
| `2` | Emerald Circuit | `#48e5bc` | Soft violet |
| `3` | Amber ROG | `#ffbb66` | Electric blue |

The default is `themeIndex=0`. `backgroundOpacity` defaults to `0`; the settings slider offers 0–90% in 5% steps. Zero is transparent. The opacity setting affects the widget's own surfaces, not the desktop wallpaper or compositor.

Palettes remain in widget-local QML. Shared source icons are bundled into each built package, so installing another widget is unnecessary.

## Layout

All widgets default to `displayMode=0`.

| Widget | Stored value | UI label and content |
| --- | --- | --- |
| System | `0` | Full: header and telemetry cards |
| System | `1` | Semi-Compact: cards with the header hidden |
| Control | `0` | Full: header, profiles, lighting |
| Control | `1` | Semi-Compact: profile and lighting cards with the header hidden |
| Gaming | `0` | Full: header, launch tile, controllers, recent games |
| Gaming | `2` | Semi-Compact: header, launch tile, controllers |
| Gaming | `1` | Compact: launch tile and four controller slots |

Gaming's numeric ordering differs from its visual settings order; preserve these values when reviewing configuration compatibility.

## Profile visibility

Control and Gaming expose `showFirmware`, default `false`. Enable it to show the firmware names Quiet, Balanced, and Performance among selectable profiles. Custom named `z13ctl` profiles are populated from `z13ctl profile --list`; the special literal profile name `custom` is filtered out of the selectable lists.

Control displays the AC and battery autoswitch targets, even when firmware choices are hidden. It reads those targets but does not provide an autoswitch-configuration editor. Gaming keeps its currently running profile visible in the chooser even if that profile is a hidden firmware mode.

Gaming also retains a `showInstalled=true` configuration entry from the baseline. The current QML does not use it as a settings toggle; the installed-game count appears in the full layout footer. Do not treat this key as an implemented option or remove it during an unrelated migration.

## Actions and their effects

### System Widget

The widget polls every two seconds. It reads Linux `/proc` and `/sys` data and invokes read-oriented utilities, including `z13ctl status` and `z13ctl undervolt --get`. Its helper writes per-user CPU/network sampling caches under `/tmp`. It does not expose a profile-setting or lighting action.

The displayed BIOS VRAM amount is the inherited hard-coded `32 GiB`, and the GPU card labels itself `Radeon 8060S`. These are not discoveries about the running machine; see [known limitations](troubleshooting.md#inherited-issues-preserved-for-review).

### Control HUD

The widget polls status every four seconds. Clicking a profile card immediately requests `z13ctl profile --set PROFILE`; it is a hardware-affecting action, not a preview.

Lighting controls offer:

- Target: Keyboard, Lightbar, or Both (`keyboard`, `lightbar`, `all`)
- Effect: `static`, `breathe`, `cycle`, `rainbow`, or `strobe`
- Brightness: `off`, `low`, `medium`, or `high`
- Color: one of the supplied RGB swatches

The Apply button requests `z13ctl apply` with the selected values. The current UI always passes speed `normal`; the helper also accepts `slow` and `fast`. Lighting selections are runtime QML state, not persisted configuration entries. Their initial values are keyboard/static/high/`50CFFF`; those defaults do not prove the hardware currently has those settings.

### Gaming HUD

The widget polls every 30 seconds. It reads locally installed Steam app manifests, attempts to rank recent games from local Steam configuration, and lists up to four qualifying connected Bluetooth devices.

Clicking GAME MODE opens a separate, frameless Qt Quick window. Selecting a profile changes the launch selection only. Pressing the launch button:

1. Checks that the selected profile is available.
2. Checks that `steamos-session-select` is on `PATH`.
3. Applies the chosen power profile using `z13ctl`.
4. Reads back the profile using the baseline confirmation check.
5. Starts `steamos-session-select gamescope`.

This action can leave the desktop session. Save work first. A profile can already have changed if a later verification or session-launch step fails; there is no rollback. The helper's success message reports that the session-switch command was spawned, not that a working Gamescope session was independently confirmed.

Close the selector with its close button or Escape to leave without launching. Window positioning, focus, and repeated open/close behavior still require real Plasma/Wayland testing.
