# Changelog

All notable changes to MarchyBar are documented here. This project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

- Rename the plugin ID from `marchybar.touchbar` to `io.github.thomasbrugman.marchybar`, the namespaced form the Omarchy plugin marketplace asks for. `marchybar update` finds installs under either folder name. Existing installs need to re-enable the plugin or reinstall; see the README. Not tested on a running Omarchy install or hardware.
- Support Omarchy 4.5 per-monitor workspaces: when Omarchy's `monitor-workspaces` state file exists, the Touch Bar workspace widget shows only the focused monitor's workspaces, labelled 1-10 like the Omarchy bar, and taps still focus the global workspace id. Omarchy 4.0.x behavior is unchanged. Verified from the Omarchy v4.5.0-rc1 source and unit tests only, not on hardware.
- Update the repository owner in plugin metadata, install instructions, and CODEOWNERS to `thomasbrugman` after the GitHub username change.
- Document the compatibility review for Omarchy 4.0.5, 4.0.6 and 4.5.0-rc1 (source review only, no hardware).
- Add Dependabot updates for npm and GitHub Actions.
- Keep every editor text field permanently read-only at the Qt level and handle keyboard edits without clipboard reads, preventing unsolicited Wayland clipboard offers from blocking the shared shell or exhausting memory. Clipboard paste and input-method composition are temporarily unavailable; typing, selection, navigation and numeric validation remain supported.
- Raise the minimum Node version to 22.22.2 (or 24.15.0, or 26 and later) to match node-gyp 13, which builds the native renderer on first launch. Older Node 22 releases are no longer supported. CI already runs the latest Node 22 and 24.

## 1.0.2 — 2026-10-07

Security release for the privileged device broker. Administrators must install the matching reviewed `marchybar-system-1.0.2-1` package and run **Set up Touch Bar** again to update the installed helper.

- Authenticate Unix peer credentials and require an active local logind session before the first blocking request read, closing unauthorized idle connections immediately.
- Limit concurrent handlers to eight before thread creation, including authorization checks, and bound the accept backlog to eight to prevent unbounded privileged thread allocation. Return slots after disconnects, handler errors, and failed thread creation.
- Preserve per-operation session checks, inactive-owner release, and disconnect cleanup; add regressions covering peer authorization, real Unix-socket idle exhaustion, slot reuse, and inactive-owner cleanup.
- Refresh broker/helper/launcher integrity hashes for the hardened broker. Synchronize the plugin and system package versions at 1.0.2 and reset the package release to 1.

## 1.0.1 — 2026-09-19

- Correct the plugin author metadata to the repository owner (`Githubguy132010`) so the marketplace listing attributes MarchyBar correctly.

## 1.0.0 — 2026-09-19

First stable release. The release version now follows Semantic Versioning, with `package.json` as the single source of truth mirrored into the plugin manifest and the system package.

- Support Omarchy 4.0.4: T2 Macs stay on `linux-t2` while other machines move to `linux-omarchy`. Hardware diagnostics now detect a non-T2 kernel on supported models, report a `wrong-kernel` status with a boot/`linux-t2-headers` recovery hint, and refuse hardware enablement until the T2 kernel is running. The editor surfaces the note in the Device tab.
- Restore backend startup and setup/update paths on Omarchy 4.0.3 by resolving the plugin directory relative to its QML file.
- Read lock state through public IPC, preserving fail-closed behavior when the shell is unavailable, instead of accessing its now-private authentication service.
- Add `npm run version:bump`/`npm run version:check` tooling, enforce version consistency in CI, and publish GitHub releases from `vX.Y.Z` tags.

## 0.1.0 — 2026-09-05

First public release of MarchyBar for Omarchy on Intel T2 MacBook Pro computers.

- Native preset editor with six bundled layouts, pages, Fn alternate pages, draft editing, undo/redo, import/export, and automatic app rules.
- Live widgets and sliders, Omarchy theme integration, and a rendered preview with a 20-second trial and rollback.
- User-session renderer and a separately installed device helper with active-session checks, temporary device access, and firmware restoration.
- Touch Bar brightness in percent, including 0%, with edits preserved during live updates.

Physically tested on MacBookPro15,1. Other supported model identifiers and both display geometries are handled in code; additional physical models and full suspend/resume cycles still need testing. See [validation](docs/VALIDATION.md).
