#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
command -v python3 >/dev/null || { echo 'python3 is required' >&2; exit 1; }
command -v kpackagetool6 >/dev/null || { echo 'Plasma 6 kpackagetool6 is required' >&2; exit 1; }
if ! command -v z13ctl >/dev/null; then echo 'Warning: z13ctl not found on PATH; hardware features will be unavailable.' >&2; fi
selection="${1:-all}"
case "$selection" in all) widgets=(system control gaming);; system|control|gaming) widgets=("$selection");; *) echo 'Usage: install.sh [all|system|control|gaming]' >&2; exit 2;; esac
if [[ "$selection" == all || "$selection" == system ]]; then
  python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 12) else "System baseline requires Python 3.12 or newer")'
fi
DATA="${XDG_DATA_HOME:-$HOME/.local/share}"
for widget in "${widgets[@]}"; do
  read -r id version < <(python3 - "$ROOT/widgets/rog-$widget/package/metadata.json" <<'PY'
import json,sys
m=json.load(open(sys.argv[1]))['KPlugin'];print(m['Id'],m['Version'])
PY
)
  archive="$ROOT/dist/rog-$widget-$version.plasmoid"
  [[ -f "$archive" ]] || { echo "Build first: make build-$widget" >&2; exit 1; }
  destination="$DATA/plasma/plasmoids/$id"
  if [[ -e "$destination" ]]; then
    backup="$DATA/rog-flow-widget-backups/$id/$(date -u +%Y%m%dT%H%M%SZ)-$$"
    mkdir -p "$(dirname "$backup")"
    cp -a -- "$destination" "$backup"
    echo "Backup: $backup"
    if ! kpackagetool6 --type Plasma/Applet --upgrade "$archive"; then
      # KPackage replacement may remove the old directory before failing.
      # Keep any failed replacement for inspection rather than deleting it.
      if [[ -e "$destination" ]]; then mv -- "$destination" "$backup-failed"; fi
      cp -a -- "$backup" "$destination"
      echo "Upgrade failed; restored $destination from $backup" >&2
      exit 1
    fi
  else
    kpackagetool6 --type Plasma/Applet --install "$archive"
  fi
  echo "Installed $id $version. Add/reload the widget in Plasma when ready."
done
