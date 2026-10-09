# ROG System Widget 1.1.0

Settings polish release. Uses KDE Kirigami native form sections, wider theme selector,
a wide opacity slider with percentage readout, and interactive theme swatches.
The HUD layout, telemetry, RGB operations and performance switching are unchanged.

Install: `bash install.sh` after extracting the archive.
Then restart Plasma Shell if QML remains cached:
`systemctl --user restart plasma-plasmashell.service`

The settings page uses actual persisted `cfg_` bindings.
This build has been checked for Python/Bash/XML/ZIP correctness but not rendered in a live Plasma 6 session.
