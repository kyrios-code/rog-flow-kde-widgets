#!/usr/bin/env bash
set -euo pipefail
command -v kpackagetool6 >/dev/null || { echo 'Plasma 6 kpackagetool6 is required' >&2; exit 1; }
case "${1:-all}" in
 all) ids=(io.rog.systemwidget io.rog.controlhud io.rog.gaminghud);;
 system) ids=(io.rog.systemwidget);; control) ids=(io.rog.controlhud);; gaming) ids=(io.rog.gaminghud);;
 *) echo 'Usage: uninstall.sh [all|system|control|gaming]' >&2; exit 2;;
esac
DATA="${XDG_DATA_HOME:-$HOME/.local/share}"
status=0
for id in "${ids[@]}"; do
  if [[ ! -e "$DATA/plasma/plasmoids/$id" ]]; then
    echo "Skipped $id (not installed for this user)"
    continue
  fi
  if ! kpackagetool6 --type Plasma/Applet --remove "$id"; then
    echo "Could not remove $id" >&2
    status=1
  fi
done
exit "$status"
# Deliberately retain settings, original ~/.local/bin helpers, and backups.
