#!/bin/bash
set -euo pipefail

# Parse the whole workflow before updating the checkout that contains this script.
update() {
  if (( $# > 1 )) || [[ ${1:-} != "" && ${1:-} != "--with-omarchy" ]]; then
    echo 'Usage: marchybar update [--with-omarchy]' >&2
    return 2
  fi
  # Installs made before the ID change live in the old folder, and Omarchy names the folder after the ID.
  local plugin_id="" plugin_dir="" candidate
  local before after rc=0
  for candidate in io.github.thomasbrugman.marchybar marchybar.touchbar; do
    if [[ -d "$HOME/.config/omarchy/plugins/$candidate/.git" ]]; then plugin_id=$candidate; plugin_dir="$HOME/.config/omarchy/plugins/$candidate"; break; fi
  done
  [[ -n $plugin_dir ]] || { echo 'Install MarchyBar with omarchy plugin add before updating.' >&2; return 1; }
  exec 9>"${XDG_RUNTIME_DIR:?}/marchybar-update.lock"
  flock -n 9 || { echo 'A MarchyBar update is already running.' >&2; return 1; }

  before=$(git -C "$plugin_dir" rev-parse HEAD)
  omarchy plugin update "$plugin_id" 9>&- || rc=$?
  after=$(git -C "$plugin_dir" rev-parse HEAD)
  if [[ $before != "$after" ]]; then
    echo 'Restarting the shell to load MarchyBar. Saved Touch Bar settings will be restored after unlock.'
    if ! omarchy restart shell 9>&-; then
      echo 'MarchyBar changed on disk, but the shell could not restart. Unlock the desktop and run: omarchy restart shell' >&2
      return 1
    fi
    echo 'If this release changes the device helper, run Set up Touch Bar in Device settings.'
  fi
  if (( rc != 0 )); then
    echo 'The MarchyBar update did not finish successfully. Review the errors above.' >&2
    return "$rc"
  fi
  # Omarchy can offer a reboot, so finish activating the plugin before that step.
  if [[ ${1:-} == "--with-omarchy" ]]; then
    omarchy update 9>&- || return $?
  fi
  return "$rc"
}
update "$@"
