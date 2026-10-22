import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

// Omarchy 4.5 gives every physical monitor its own block of ten workspaces
// (first monitor 1-10, next 11-20, ...) and records that in this state file.
export const BLOCK_SIZE = 10;

export function perMonitorStateFile(env = process.env) {
  const state = env.XDG_STATE_HOME || path.join(env.HOME || os.homedir(), '.local', 'state');
  return path.join(state, 'omarchy', 'monitor-workspaces');
}

export function usesPerMonitorWorkspaces(file = perMonitorStateFile()) {
  try { return fs.statSync(file).isFile(); } catch { return false; }
}

// Pick the workspaces to show on the Touch Bar. Omarchy 4.0 keeps one global
// list. With per-monitor workspaces only the focused monitor's workspaces are
// shown, labelled 1-10 like the Omarchy bar. The id stays global because it is
// the focus target.
export function visibleWorkspaces(workspaces, active, perMonitor) {
  const list = workspaces.filter(w => w.id > 0).sort((a, b) => a.id - b.id);
  const label = w => (/^\d+$/.test(w.name) ? w.id : w.name);
  if (!perMonitor || !active || active.id <= 0) return list.map(w => ({ id: w.id, name: label(w), windows: w.windows }));
  const offset = Math.floor((active.id - 1) / BLOCK_SIZE) * BLOCK_SIZE;
  const sameMonitor = w => active.monitorID !== undefined && w.monitorID !== undefined && w.monitorID === active.monitorID;
  const inBlock = w => w.id > offset && w.id <= offset + BLOCK_SIZE;
  return list.filter(w => sameMonitor(w) || inBlock(w)).map(w => ({
    id: w.id,
    name: inBlock(w) && /^\d+$/.test(w.name) ? w.id - offset : label(w),
    windows: w.windows,
  }));
}
