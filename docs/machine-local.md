# Machine-Local Configuration

Use machine-local files when you run a personal blueprint such as
`nicholasadamou/dotfiles` and want per-host settings without committing them
to your fork or blocking `smu update`.

## Quick start

```bash
smu local init
smu local doctor --json
```

Add `local` to the `TAGS` line in `dotfiles/rcrc`, place overrides under
`$SMU_HOME_DIR/dotfiles/local/`, then run `rcup`.

Nothing under the default ignored paths needs to be committed. Updates ignore
those paths when deciding whether the blueprint checkout is dirty.

## What stays out of git

set-me-up treats these blueprint paths as machine-local by default:

- `dotfiles/local/`
- `dotfiles/tag-local/`
- `dotfiles/tag-smu/`

Additional paths can be listed in `SMU_IGNORED_PATHS` using `|` separators.
Paths are relative to `$SMU_HOME_DIR` (usually `~/set-me-up`).

Persist extra ignored paths in `~/.config/set-me-up/local.env`:

```bash
export SMU_IGNORED_PATHS="dotfiles/local|dotfiles/secrets|private/"
```

Bootstrap installers pass through the same variable.

## Profile overrides outside the blueprint

Theme, prompt, and preset choices can also live outside the blueprint in
`~/.config/set-me-up/`:

```toml
# ~/.config/set-me-up/theme.toml
theme = "nord"

# ~/.config/set-me-up/prompt.toml
prompt = "classic"
```

See [Catalogs And Adapters](catalogs-and-adapters.md) for the full resolution
order.

## rcm layout for machine-local dotfiles

Use the same tag layout as the rest of your blueprint. Example:

```text
dotfiles/local/shell/zshrc/zshrc
dotfiles/local/git/gitconfig.local
```

Then ensure `dotfiles/rcrc` includes the tag:

```text
TAGS="example smu local"
```

Optional but recommended: add `dotfiles/local/` to your blueprint `.gitignore`
so local files are harder to commit accidentally. Update checks already ignore
the directory even when it is untracked.

## Update behavior

`smu update blueprint`, `smu update doctor`, and the bootstrap installer only
block on non-ignored changes. Edits under ignored paths do not require
`--force-reset`.

Tracked edits outside ignored paths still block updates until you commit,
stash, or reset them.

## set-me-up development hub

If you also use the `set-me-up` coordinator checkout for development, keep
machine-specific changes out of managed child repos (`home/.config/*`,
`modules/*`, and similar). Those repos are updated by `./scripts/update.sh`,
which skips any checkout with uncommitted work.

Use your installed blueprint at `~/set-me-up` for host-specific dotfiles and
`~/.config/set-me-up/` for profile overrides instead of editing child
checkouts directly.

## Commands

```bash
smu local init [--json]
smu local doctor [--json]
smu update doctor --json
```

`smu local doctor` reports whether machine-local paths are configured, whether
`rcrc` includes the `local` tag, and whether non-local changes would still
block updates.
