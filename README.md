<div align="center">

# ROG Flow KDE Widgets

### Three native KDE Plasma 6 dashboards for the ASUS ROG Flow Z13

**System telemetry · Power and RGB controls · Steam Gaming Mode**

**CachyOS** · **KDE Plasma 6** · **ROG Flow Z13** · **MIT License**

</div>

> **Status: private preview / release candidate.** Tested visually on one ROG Flow Z13 with CachyOS and a configured Gamescope session. This is an unofficial community project, not affiliated with ASUS or Valve. The downloadable release installer is not published yet.

## Three widgets. One desktop.

Turn your ROG Flow Z13 into a transparent, themeable desktop dashboard. Install any one widget or all three; each has independent settings and can be moved and resized using Plasma Edit Mode.

| Widget | What it does | Current source version |
| --- | --- | --- |
| **ROG System Widget** | CPU/GPU usage, RAM, battery, APU temperature, fan RPM, TDP, storage, network graph and active power profile | 1.3.0 |
| **ROG Control HUD** | Switch `z13ctl` performance profiles, view AC/battery autoswitch targets, control keyboard and lightbar RGB | 1.2.0 |
| **ROG Gaming HUD** | Steam Game Mode launcher, four Bluetooth controller slots with battery readings, recently played games, and power-profile selection | 1.0.0 |

### Desktop showcase

![ROG Flow Z13 CachyOS desktop with all three KDE widgets](screenshots/desktop-overview.png)

The screenshots below will appear automatically when the matching PNG files are uploaded to the repository's `screenshots/` folder.

## Quick install

### Recommended: download and run

The intended public release will provide a **complete ZIP** with all three prebuilt widgets and a root-level `install.sh`. Once that bundle is published:

1. Open [Releases](../../releases) and download the complete bundle.
2. Extract the ZIP.
3. Open a terminal inside the extracted folder and run:

```bash
bash install.sh
```

4. Open **KDE Plasma → Edit Mode → Add Widgets**, then search for **ROG System Widget**, **ROG Control HUD**, or **ROG Gaming HUD**.

**The release ZIP is not available yet.** Until then, use the source installation below; do not expect `bash install.sh` to work from the repository root.

![Find all three widgets in KDE Plasma Add Widgets](screenshots/plasma-widget-picker.png)

### Available now: install from source

Requires Python 3.12+, Make, and `kpackagetool6`:

```bash
git clone https://github.com/jsmola01/rog-flow-kde-widgets.git
cd rog-flow-kde-widgets
make test
make install
```

Or install individually with `make install-system`, `make install-control`, or `make install-gaming`. No `sudo` is needed. Existing user-level widget packages are backed up before upgrades. See [installation and recovery](docs/installation.md).

## Install z13ctl first (required)

**These widgets rely on [z13ctl by dahui](https://github.com/dahui/z13ctl) for ROG Flow hardware integration.** On CachyOS (Arch-based), install its prebuilt AUR package:

```bash
yay -S z13ctl-bin
```

Follow the upstream [z13ctl installation guide](https://dahui.github.io/z13ctl/installation/) to complete its systemd/permission setup, then verify:

```bash
z13ctl status
z13ctl profile --list
```

For a graphical hardware-control app, [z13gui](https://github.com/dahui/z13gui) is an optional companion, **not required** for these widgets. The upstream author recommends it for users who prefer a GUI. These widgets do not install z13ctl, z13gui, or change system permissions automatically.

## Requirements

This project initially targets **CachyOS + KDE Plasma 6 + ASUS ROG Flow Z13**, rather than every Linux distribution or ROG model.

| Requirement | Used for |
| --- | --- |
| KDE Plasma 6, `kpackagetool6` | Installing and running the widgets |
| Python 3.12+ | System telemetry helper and source workflow |
| `z13ctl` installed on the Plasma session's `PATH` | Hardware telemetry, power profiles, and RGB |
| Steam | Local library and recently played information |
| `steamos-session-select gamescope` | Switching into an existing Gaming Mode session |
| BlueZ / `bluetoothctl` | Bluetooth controller connection and battery status |
| [**Bulky Pixels** font](https://www.1001fonts.com/bulky-pixels-font.html) | Download and install separately for the intended pixel-style appearance |

Gamescope and Steam must already be configured independently. Download [Bulky Pixels by Smoking Drum](https://www.1001fonts.com/bulky-pixels-font.html), install the TTF using KDE Font Management, then reopen the widgets if necessary. The font is not bundled.

The installer installs the widgets for the current signed-in desktop user. Steam libraries are discovered automatically from Steam's local configuration.

## System HUD

![ROG System HUD full view](screenshots/system-hud.png)

Monitor your ROG Flow's utilization, battery, cooling, power limits, graphics memory, storage, network traffic and active profile without opening a terminal. Choose a coordinated color theme, adjust glass transparency, and select Full or Semi-Compact display.

## Control HUD

![ROG Control HUD power profiles and lighting](screenshots/control-hud.png)

Switch between firmware and custom `z13ctl` profiles, including profiles named for gaming, battery use, or extreme performance. The current profile is highlighted. The profile list scrolls when necessary and firmware modes can be hidden. Keyboard and lightbar lighting can be controlled independently.

**Changing a profile or lighting setting changes the actual hardware configuration.**

## Gaming HUD

**Full view**

![ROG Gaming HUD full display](screenshots/gaming-hud-full.png)

**Compact view**

![ROG Gaming HUD compact display](screenshots/gaming-hud-compact.png)

![Gaming Mode profile selector](screenshots/gaming-profile-selector.png)

A square **Game Mode** card opens a frameless power-profile selector. It distinguishes **currently running** from **selected for launch**, so you can choose a profile before entering Gamescope. The HUD also shows up to four Bluetooth controllers and their reported battery levels.

Choose **Full**, **Semi-Compact**, or **Compact**:

- **Full:** header, launch card, controllers, recent games and installed-game count
- **Semi-Compact:** header, launch card and controllers
- **Compact:** launch card and controllers only

**Save your work before launching Gaming Mode:** session switching may close your desktop session.

> **Known Gaming metadata limitation:** The current baseline may count Steam tools/runtimes as games, miss recently played activity, or lack local cover art. These issues are being addressed before public release.

## Personalize the look

![ROG theme and transparency settings](screenshots/gaming-theme-settings.png)

<details>
<summary>More configuration screenshots</summary>

**Gaming display modes**

![Gaming display mode settings](screenshots/gaming-display-settings.png)

**Profile visibility**

![Gaming profile settings](screenshots/gaming-profile-settings.png)

</details>

All three widgets use the same four palettes:

| Theme | Accent | Complementary icons |
| --- | --- | --- |
| Cyan Glass | Cyan | Warm amber |
| Purple Nebula | Purple | Mint teal |
| Emerald Circuit | Emerald | Soft violet |
| Amber ROG | Amber | Electric blue |

Each widget independently supports glass opacity. Open **Configure Widget → Appearance** to choose a theme and transparency; use **Display** and **Profiles** where available for layout and visibility settings.

## Troubleshooting and development

- [Installation, upgrades and rollback](docs/installation.md)
- [Configuration and behavior](docs/configuration.md)
- [Compatibility and dependency details](docs/compatibility.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Review handoff and known issues](docs/review-handoff.md)

Developers can build standalone packages with `make build`, or individually with `make build-system`, `make build-control`, and `make build-gaming`. Generated `.plasmoid` files appear in `dist/`. The original working ZIP baselines are retained under `baselines/`.

## Credits and license

Project code is [MIT licensed](LICENSE). Third-party icons, trademarks, and fonts retain their own rights; see [third-party notices](THIRD_PARTY_NOTICES.md). ASUS ROG and Steam marks belong to their respective owners.

**Made for the ROG Flow Z13 community.** Contributions and forks are welcome when the repository becomes public.
