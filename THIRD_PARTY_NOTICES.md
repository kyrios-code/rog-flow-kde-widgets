# Third-party notices and source provenance

The repository's [MIT license](LICENSE) covers project code. It does not replace the notices applicable to third-party artwork or grant rights to third-party trademarks. The original metadata for all three widgets identifies its code license as MIT.

## Original input archives

These files are retained without modification in `baselines/`, with checksums in `baselines/SHA256SUMS`:

| Archive | Root directory inside the archive | Migrated source |
| --- | --- | --- |
| `rog-system-widget-v13(1).zip` | `rog-system-widget-v13/` | `widgets/rog-system/` |
| `rog-control-hud-v12(1).zip` | `rog-control-hud-v12/` | `widgets/rog-control/` |
| `rog-gaming-hud-v10(1).zip` | `rog-gaming-hud-v10/` | `widgets/rog-gaming/` |

The archive-root `telemetry.py`, `rog-control-helper.py`, and `rog-gaming-helper.py` were moved into the corresponding widget's `scripts/` directory. Each archive's `package/` is the source of its widget's `package/`. Byte-identical common image files also have canonical build-time copies under `shared/icons/`, which overlay `contents/images/` when packaging; the original widget-local image copies remain for comparison. Original archive `install.sh` files remain available inside the retained ZIPs; the monorepo uses its own installation tooling.

The original `README.md` files remain in each widget directory. The original attribution files remain at:

- `widgets/rog-system/LOGO-ATTRIBUTION.txt`
- `widgets/rog-control/LOGO-ATTRIBUTION.txt`
- `widgets/rog-gaming/STEAM_LOGO_ATTRIBUTION.txt`

## ASUS Republic of Gamers eye mark

Files:

- `shared/icons/rog-eye-amber.svg`
- `shared/icons/rog-eye-cyan.svg`
- `shared/icons/rog-eye-emerald.svg`
- `shared/icons/rog-eye-purple.svg`

These were supplied as `package/contents/images/rog-eye-*.svg` in the original archives. They are bundled into the corresponding location in each built widget.

The preserved System and Control attribution notices identify the source as [The SVG: Republic of Gamers](https://thesvg.org/icon/republic-of-gamers), described in those notices as a CC0 listing. They state that monochrome variants preserve the original path geometry and that ASUS/ROG names and marks may be trademarks of ASUSTeK Computer Inc. That source/licensing statement is recorded from the supplied notices, not independently re-certified by this migration.

This project is not affiliated with ASUS. A copyright dedication does not itself remove trademark restrictions.

## Steam symbol

File: `widgets/rog-gaming/package/contents/images/steam-symbol.svg`.

The original Gaming archive supplies this same path and `STEAM_LOGO_ATTRIBUTION.txt`. The SVG's embedded notice identifies Font Awesome Free 6.7.2, copyright 2024 Fonticons, Inc. The attribution file identifies the source artwork as Font Awesome Free `brands/steam-symbol.svg`, licensed for icons under Creative Commons Attribution 4.0.

- Source project: [Font Awesome](https://fontawesome.com/)
- License information: [Font Awesome Free license](https://fontawesome.com/license/free)
- Icon license: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

The supplied SVG uses a white fill. No artwork changes are introduced by the repository migration. Preserve the embedded notice and attribution when redistributing the asset. Steam and its logo are trademarks of Valve Corporation; this project is not affiliated with Valve.

## Other supplied SVG assets

The remaining icons are carried forward from the original `package/contents/images/` directories. `shared/assets.json` gives the exact filenames with canonical build-time copies in `shared/icons/`; original widget-local copies remain under their package-relative image paths. This migration does not introduce new icon geometry or substitute an external icon library.

The input archives do not provide separate third-party attributions for those remaining icons. Their presence is not evidence of a separately verified upstream provenance. Review provenance before any broader redistribution that requires it.

## Fonts, game art, and runtime dependencies

- QML requests the font families `Bulky Pixels` and `Noto Sans`. No font files are included; installed fonts or Qt fallback fonts determine rendering. This repository does not grant a license to separately obtained fonts.
- The Gaming helper reads cover art already present in the user's local Steam cache. Game cover art is not bundled in the source repository or packages; its rights remain with the respective holders.
- KDE Plasma, Qt, Kirigami, Python, `z13ctl`, Steam, BlueZ, Gamescope, and `steamos-session-select` are external dependencies or integrations. They are not vendored by this repository and retain their own licenses and terms.
