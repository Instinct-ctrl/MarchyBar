import test from 'node:test';
import assert from 'node:assert/strict';
import { visibleWorkspaces, perMonitorStateFile } from '../backend/workspaces.mjs';

const ws = (id, monitorID, name = String(id)) => ({ id, name, monitorID, windows: 1 });

test('Omarchy 4.0 keeps the global list unchanged', () => {
  const out = visibleWorkspaces([ws(2, 0), ws(1, 0), ws(12, 0), { id: -98, name: 'special', monitorID: 0 }], { id: 1, monitorID: 0 }, false);
  assert.deepEqual(out.map(w => [w.id, w.name]), [[1, 1], [2, 2], [12, 12]]);
});

test('per-monitor mode shows only the focused monitor, labelled 1-10', () => {
  const all = [ws(1, 0), ws(3, 0), ws(11, 1), ws(13, 1)];
  assert.deepEqual(visibleWorkspaces(all, { id: 13, monitorID: 1 }, true).map(w => [w.id, w.name]), [[11, 1], [13, 3]]);
  assert.deepEqual(visibleWorkspaces(all, { id: 1, monitorID: 0 }, true).map(w => [w.id, w.name]), [[1, 1], [3, 3]]);
});

test('per-monitor mode keeps guest workspaces on the focused monitor and named workspaces', () => {
  const all = [ws(2, 0), ws(15, 0), ws(4, 0, 'web'), ws(12, 1)];
  const out = visibleWorkspaces(all, { id: 2, monitorID: 0 }, true);
  assert.deepEqual(out.map(w => [w.id, w.name]), [[2, 2], [4, 'web'], [15, 15]]);
});

test('missing monitor ids fall back to the id block', () => {
  const all = [{ id: 2, name: '2' }, { id: 12, name: '12' }];
  assert.deepEqual(visibleWorkspaces(all, { id: 2 }, true).map(w => w.id), [2]);
});

test('state file path honours XDG_STATE_HOME', () => {
  assert.equal(perMonitorStateFile({ XDG_STATE_HOME: '/x' }), '/x/omarchy/monitor-workspaces');
  assert.equal(perMonitorStateFile({ HOME: '/h' }), '/h/.local/state/omarchy/monitor-workspaces');
});
